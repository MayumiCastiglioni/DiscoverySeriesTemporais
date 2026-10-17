"""Single-origin pilots for all required models.

The pilots prove that every model adapter can consume the same canonical origin.
They are not a substitute for hyperparameter tuning or final walk-forward MAE.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from .series import ORIGIN_COLUMNS, CandidateTarget, assert_same_origins
from .xgboost_model import create_target_lag_design, run_xgboost_pilot


def _pilot_schedule(canonical_schedule: pd.DataFrame) -> pd.DataFrame:
    if canonical_schedule.empty:
        raise ValueError("A pilot needs at least one canonical origin.")
    return canonical_schedule.head(1).copy()


def _history_until_origin(candidate: CandidateTarget, origin_position: int) -> pd.Series:
    history = candidate.data.iloc[: origin_position + 1]["target"].dropna()
    if len(history) < 20:
        raise ValueError(f"Base {candidate.base_id}: fewer than 20 observed values before pilot origin.")
    return history


def _forecast_sarimax(history: pd.Series) -> float:
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fitted = SARIMAX(
            history.to_numpy(),
            order=(1, 1, 0),
            trend="c",
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False, maxiter=50)
    return float(np.asarray(fitted.forecast(steps=1))[0])


def _forecast_holt_winters(history: pd.Series) -> float:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fitted = ExponentialSmoothing(
            history.to_numpy(), trend="add", seasonal=None, initialization_method="estimated"
        ).fit(optimized=True)
    return float(np.asarray(fitted.forecast(1))[0])


def _forecast_random_forest(candidate: CandidateTarget, origin_timestamp: pd.Timestamp) -> tuple[float, int]:
    from sklearn.ensemble import RandomForestRegressor

    design = create_target_lag_design(candidate)
    feature_columns = [column for column in design.columns if column.startswith("target_lag_")]
    valid_horizon = pd.Series(True, index=design.index)
    if candidate.required_horizon_delta is not None:
        valid_horizon = (design["target_timestamp"] - design["timestamp"]).eq(
            candidate.required_horizon_delta
        )
    train = design.loc[
        (design["timestamp"] < origin_timestamp)
        & valid_horizon
        & design["future_target"].notna()
        & design[feature_columns].notna().all(axis=1)
    ]
    prediction_row = design.loc[design["timestamp"].eq(origin_timestamp)]
    if len(prediction_row) != 1 or prediction_row[feature_columns].isna().any(axis=None):
        raise ValueError("Random Forest pilot origin does not have a complete lag design.")
    estimator = RandomForestRegressor(
        n_estimators=100, max_depth=8, random_state=candidate.random_state, n_jobs=1
    )
    estimator.fit(train[feature_columns], train["future_target"])
    return float(estimator.predict(prediction_row[feature_columns])[0]), int(len(train))


def run_model_pilot(
    candidate: CandidateTarget, canonical_schedule: pd.DataFrame, model_name: str
) -> pd.DataFrame:
    """Run exactly one model on the first shared pilot origin for a base."""
    if model_name not in {"sarimax", "holt_winters", "random_forest", "xgboost"}:
        raise ValueError(f"Unsupported model pilot: {model_name}.")
    pilot_schedule = _pilot_schedule(canonical_schedule)
    if not pilot_schedule["horizon_steps"].eq(1).all():
        raise ValueError("The model pilots support only the provisional one-step horizon.")
    origin = pilot_schedule.iloc[0]
    history = _history_until_origin(candidate, int(origin["origin_position"]))
    actual = float(candidate.data.iloc[int(origin["target_position"])]["target"])
    origin_timestamp = pd.Timestamp(origin["origin_timestamp"])

    if model_name == "sarimax":
        prediction, training_rows = _forecast_sarimax(history), int(len(history))
    elif model_name == "holt_winters":
        prediction, training_rows = _forecast_holt_winters(history), int(len(history))
    elif model_name == "random_forest":
        prediction, training_rows = _forecast_random_forest(candidate, origin_timestamp)
    else:
        xgboost_result = run_xgboost_pilot(candidate, pilot_schedule)
        prediction = float(xgboost_result["prediction"])
        training_rows = int(xgboost_result["training_rows"])

    record = {column: origin[column] for column in ORIGIN_COLUMNS}
    record.update(
        {
            "model": model_name,
            "prediction": prediction,
            "actual": actual,
            "absolute_error": abs(prediction - actual),
            "training_rows": training_rows,
            "random_state": candidate.random_state if model_name in {"random_forest", "xgboost"} else None,
            "scope": "single shared-origin pilot; not a final walk-forward or MAE result",
        }
    )
    result = pd.DataFrame([record])
    if not result[ORIGIN_COLUMNS].reset_index(drop=True).equals(
        pilot_schedule[ORIGIN_COLUMNS].reset_index(drop=True)
    ):
        raise ValueError(f"{model_name}: pilot prediction does not preserve its shared origin.")
    return result


def run_all_model_pilots(candidate: CandidateTarget, canonical_schedule: pd.DataFrame) -> pd.DataFrame:
    """Run all four models on the same first canonical origin and validate it."""
    pilot_schedule = _pilot_schedule(canonical_schedule)
    model_names = ("sarimax", "holt_winters", "random_forest", "xgboost")
    result = pd.concat(
        [run_model_pilot(candidate, canonical_schedule, model_name) for model_name in model_names],
        ignore_index=True,
    )
    assert_same_origins(
        {model: result.loc[result["model"].eq(model), ORIGIN_COLUMNS] for model in model_names},
        pilot_schedule,
    )
    return result
