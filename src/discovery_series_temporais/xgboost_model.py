"""A deliberately small XGBoost pilot used to validate the specialization path.

This module does not perform the final hyperparameter search or comparative
walk-forward evaluation. It uses target lags only, so it can be executed before
the availability of external variables is approved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .series import CandidateTarget


@dataclass(frozen=True)
class XGBoostPilotSettings:
    """Fixed pilot settings; they are not final model hyperparameters."""

    n_estimators: int = 50
    max_depth: int = 3
    learning_rate: float = 0.05
    subsample: float = 1.0
    colsample_bytree: float = 1.0
    random_state: int = 42
    n_jobs: int = 1


def create_target_lag_design(candidate: CandidateTarget, lags: tuple[int, ...] = (0, 1, 2, 7)) -> pd.DataFrame:
    """Create a one-step-ahead design with no future values in the features."""
    design = candidate.data[["timestamp", "target"]].copy()
    design = design.rename(columns={"target": "observed_target"})
    design["target_timestamp"] = design["timestamp"].shift(-1)
    design["future_target"] = design["observed_target"].shift(-1)
    for lag in lags:
        design[f"target_lag_{lag}"] = design["observed_target"].shift(lag)
    return design


def run_xgboost_pilot(candidate: CandidateTarget, schedule: pd.DataFrame) -> dict[str, object]:
    """Fit once before the first final-test origin and predict that one origin.

    It is a runtime and temporal-contract smoke test. It intentionally is not
    a walk-forward result and must not be used in MAE ranking.
    """
    from xgboost import XGBRegressor

    if schedule.empty:
        raise ValueError("The pilot requires at least one canonical origin.")
    design = create_target_lag_design(candidate)
    first_origin = pd.Timestamp(schedule.iloc[0]["origin_timestamp"])
    feature_columns = [column for column in design.columns if column.startswith("target_lag_")]
    valid_horizon = pd.Series(True, index=design.index)
    if candidate.required_horizon_delta is not None:
        valid_horizon = (design["target_timestamp"] - design["timestamp"]).eq(
            candidate.required_horizon_delta
        )
    train = design.loc[
        (design["timestamp"] < first_origin)
        & valid_horizon
        & design["future_target"].notna()
        & design[feature_columns].notna().all(axis=1)
    ]
    prediction_row = design.loc[design["timestamp"].eq(first_origin)]
    if len(prediction_row) != 1:
        raise ValueError("The pilot origin was not found in its target design.")
    if prediction_row[feature_columns].isna().any(axis=None):
        raise ValueError("The pilot origin lacks required lag values.")

    settings = XGBoostPilotSettings()
    estimator = XGBRegressor(objective="reg:squarederror", tree_method="hist", **asdict(settings))
    estimator.fit(train[feature_columns], train["future_target"])
    prediction = float(estimator.predict(prediction_row[feature_columns])[0])
    actual = float(prediction_row["future_target"].iloc[0])
    return {
        "base_id": candidate.base_id,
        "origin_id": str(schedule.iloc[0]["origin_id"]),
        "origin_timestamp": first_origin.isoformat(),
        "target_timestamp": pd.Timestamp(schedule.iloc[0]["target_timestamp"]).isoformat(),
        "training_rows": int(len(train)),
        "feature_columns": feature_columns,
        "prediction": prediction,
        "actual": actual,
        "absolute_error": abs(prediction - actual),
        "pilot_settings": asdict(settings),
        "scope": "single-origin runtime pilot; not a final walk-forward or MAE result",
    }
