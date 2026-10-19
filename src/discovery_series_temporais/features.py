"""Leakage-safe, common feature matrices for final time-series experiments.

The feature row at ``origin_timestamp`` only contains observations available at
or before that origin.  Its label is the target at the separately recorded
``target_timestamp``.  The module deliberately keeps missing external values:
they are imputed inside each training fold, never with information from the
future.  This lets every model receive the same origin schedule without
silently moving the test period.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .cleaning import STEP_DELTAS, STL_PERIODS, load_cleaned_dataset


DEFAULT_FEATURE_POLICY_PATH = Path("configs/feature_availability_policy.json")
MIN_HOLT_CONTIGUOUS_HISTORY = 3


@dataclass(frozen=True)
class FeaturePolicy:
    """Versioned availability decision for one base."""

    base_id: int
    numeric_lag_1: tuple[str, ...]
    excluded: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class FeatureMatrix:
    """The supervised data and its auditable common-origin eligibility mask."""

    base_id: int
    horizon_steps: int
    data: pd.DataFrame
    feature_columns: tuple[str, ...]
    external_feature_columns: tuple[str, ...]
    policy: FeaturePolicy

    @property
    def eligibility_mask(self) -> pd.Series:
        return self.data["eligible_for_common_schedule"].astype(bool)


def load_feature_policies(
    path: Path = DEFAULT_FEATURE_POLICY_PATH,
) -> dict[int, FeaturePolicy]:
    """Load the approved availability catalogue and reject incomplete policies."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    policies: dict[int, FeaturePolicy] = {}
    for item in payload["bases"]:
        policy = FeaturePolicy(
            base_id=int(item["base_id"]),
            numeric_lag_1=tuple(str(name) for name in item["numeric_lag_1"]),
            excluded=tuple(str(name) for name in item["excluded"]),
            notes=str(item["notes"]),
        )
        if policy.base_id in policies:
            raise ValueError(f"Repeated feature policy for base {policy.base_id}.")
        policies[policy.base_id] = policy
    if set(policies) != {1, 2, 3, 4, 5}:
        raise ValueError("The feature policy must define every base from 1 to 5 exactly once.")
    return policies


def _calendar_features(target_timestamps: pd.Series, base_id: int) -> pd.DataFrame:
    """Return only calendar covariates known for the future target timestamp."""
    timestamps = pd.DatetimeIndex(target_timestamps)
    result = pd.DataFrame(index=target_timestamps.index)
    if base_id in {2, 3, 4}:
        hour = timestamps.hour
        result["calendar_hour_sin"] = np.sin(2 * np.pi * hour / 24)
        result["calendar_hour_cos"] = np.cos(2 * np.pi * hour / 24)
    if base_id in {1, 2, 3, 4}:
        day_of_week = timestamps.dayofweek
        result["calendar_dow_sin"] = np.sin(2 * np.pi * day_of_week / 7)
        result["calendar_dow_cos"] = np.cos(2 * np.pi * day_of_week / 7)
    if base_id == 5:
        week = timestamps.isocalendar().week.astype(int)
        result["calendar_week_sin"] = np.sin(2 * np.pi * week / 52)
        result["calendar_week_cos"] = np.cos(2 * np.pi * week / 52)
    return result


def build_feature_matrix(
    base_id: int,
    horizon_steps: int,
    processed_dir: Path = Path("data/processed"),
    policy_path: Path = DEFAULT_FEATURE_POLICY_PATH,
) -> FeatureMatrix:
    """Build a common supervised matrix without fitting or imputing anything.

    ``horizon_steps`` is intentionally an explicit input rather than a default:
    the final horizon is a methodological decision that must be versioned before
    predictions, MAE, rankings, or the final report are produced.
    """
    if not isinstance(horizon_steps, int) or isinstance(horizon_steps, bool) or horizon_steps < 1:
        raise ValueError("horizon_steps must be a positive integer.")
    if base_id not in STEP_DELTAS:
        raise ValueError("base_id must be an integer from 1 to 5.")

    policies = load_feature_policies(policy_path)
    policy = policies[base_id]
    cleaned = load_cleaned_dataset(base_id, processed_dir).copy()
    missing_columns = sorted(set(policy.numeric_lag_1).difference(cleaned.columns))
    if missing_columns:
        raise ValueError(
            f"Base {base_id}: policy references columns absent from cleaned data: {missing_columns}."
        )

    frame = cleaned.loc[:, ["timestamp", "target", *policy.numeric_lag_1]].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        raise ValueError(f"Base {base_id}: cleaned timestamps must be unique.")

    expected_target_timestamp = frame["timestamp"] + STEP_DELTAS[base_id] * horizon_steps
    actual_target_timestamp = frame["timestamp"].shift(-horizon_steps)
    frame["target_timestamp"] = actual_target_timestamp
    frame["future_target"] = pd.to_numeric(frame["target"], errors="coerce").shift(-horizon_steps)
    frame["horizon_is_regular"] = actual_target_timestamp.eq(expected_target_timestamp)

    target = pd.to_numeric(frame["target"], errors="coerce")
    observed_target = target.notna()
    contiguous_history = (
        observed_target.groupby((~observed_target).cumsum()).cumsum().where(observed_target, 0)
    )
    frame["contiguous_target_history"] = contiguous_history.astype(int)
    seasonal_period = STL_PERIODS[base_id]
    target_feature_columns = []
    for lag in (1, 2, seasonal_period):
        name = f"target_lag_{lag}"
        frame[name] = target.shift(lag)
        target_feature_columns.append(name)
    frame["target_rolling_mean"] = target.shift(1).rolling(seasonal_period, min_periods=seasonal_period).mean()
    frame["target_rolling_std"] = target.shift(1).rolling(seasonal_period, min_periods=seasonal_period).std()
    target_feature_columns.extend(["target_rolling_mean", "target_rolling_std"])

    external_feature_columns = []
    for column in policy.numeric_lag_1:
        feature_name = f"external_lag_1__{column}"
        frame[feature_name] = pd.to_numeric(frame[column], errors="coerce").shift(1)
        external_feature_columns.append(feature_name)
    frame = frame.drop(columns=list(policy.numeric_lag_1))

    calendar = _calendar_features(expected_target_timestamp, base_id)
    frame = pd.concat([frame, calendar], axis=1)
    calendar_columns = list(calendar.columns)
    feature_columns = tuple([*target_feature_columns, *external_feature_columns, *calendar_columns])

    # An origin needs an observed current target, an observed label, a regular
    # calendar horizon, and at least the minimum consecutive target history
    # required by the Holt-Winters reference.  This model precondition is part
    # of the *common* contract, rather than a reason for Holt-Winters alone to
    # omit a prediction.  A gap in a lag, rolling, or external feature does
    # not erase an otherwise valid target pair: that feature is imputed inside
    # the fold with training data only.  Requiring a complete 52-week rolling
    # window here would eliminate every otherwise valid Base-5 origin merely
    # because its historical weekly source has intermittent missing weeks.
    frame["eligible_for_common_schedule"] = (
        frame["horizon_is_regular"]
        & frame["target"].notna()
        & frame["future_target"].notna()
        & frame["contiguous_target_history"].ge(MIN_HOLT_CONTIGUOUS_HISTORY)
    )

    ordered_columns = [
        "timestamp",
        "target_timestamp",
        "target",
        "future_target",
        "horizon_is_regular",
        "contiguous_target_history",
        "eligible_for_common_schedule",
        *feature_columns,
    ]
    return FeatureMatrix(
        base_id=base_id,
        horizon_steps=horizon_steps,
        data=frame.loc[:, ordered_columns],
        feature_columns=feature_columns,
        external_feature_columns=tuple(external_feature_columns),
        policy=policy,
    )
