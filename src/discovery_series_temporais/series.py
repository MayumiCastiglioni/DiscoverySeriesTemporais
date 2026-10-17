"""Candidate-target loading and shared-origin contracts for time-series evaluation.

The schedules produced here are target-only exploratory artifacts. Before final
evaluation, the same functions must receive the approved common feature
eligibility mask so every compared model is evaluated at exactly the same
origins for a base.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .experiment_config import DEFAULT_RULES_PATH, get_experiment_rule


MODEL_NAMES = ("sarimax", "holt_winters", "random_forest", "xgboost")
ORIGIN_COLUMNS = [
    "origin_id",
    "origin_timestamp",
    "target_timestamp",
    "origin_position",
    "target_position",
    "horizon_steps",
]


@dataclass(frozen=True)
class CandidateTarget:
    """A target series with its approved-for-exploration time interpretation."""

    base_id: int
    target_name: str
    data: pd.DataFrame
    frequency_label: str
    required_horizon_delta: pd.Timedelta | None
    test_fraction: float = 0.20
    random_state: int = 42


def _validate_target_frame(frame: pd.DataFrame, base_id: int) -> pd.DataFrame:
    required = {"timestamp", "target"}
    if set(frame.columns) != required:
        raise ValueError(f"Base {base_id}: expected only {required}, got {set(frame.columns)}.")
    normalized = frame.copy()
    normalized["timestamp"] = pd.to_datetime(normalized["timestamp"], errors="raise")
    normalized = normalized.sort_values("timestamp", kind="stable").reset_index(drop=True)
    if normalized["timestamp"].duplicated().any():
        raise ValueError(f"Base {base_id}: target series has repeated timestamps.")
    if not normalized["timestamp"].is_monotonic_increasing:
        raise ValueError(f"Base {base_id}: timestamps are not chronological.")
    return normalized


def load_candidate_target(
    base_id: int,
    processed_dir: Path = Path("data/processed"),
    rules_path: Path = DEFAULT_RULES_PATH,
) -> CandidateTarget:
    """Load one target candidate without creating features or imputing values."""
    source = processed_dir / f"base{base_id}_structural.csv"
    if not source.exists():
        raise FileNotFoundError(f"Structural input not found: {source}")
    frame = pd.read_csv(source, parse_dates=["timestamp"])
    rule = get_experiment_rule(base_id, rules_path)

    if base_id == 1:
        target = frame[["timestamp", "Close"]].rename(columns={"Close": "target"})
        return CandidateTarget(
            1, "Close", _validate_target_frame(target, 1), rule.granularity,
            pd.Timedelta(days=1), rule.test_fraction, rule.random_state,
        )

    if base_id == 2:
        target_counts = frame.groupby("timestamp")["traffic_volume"].nunique(dropna=False)
        if (target_counts > 1).any():
            raise ValueError("Base 2: repeated timestamps disagree in traffic_volume.")
        target = (
            frame.groupby("timestamp", as_index=False)["traffic_volume"]
            .first()
            .rename(columns={"traffic_volume": "target"})
        )
        return CandidateTarget(
            2,
            "traffic_volume",
            _validate_target_frame(target, 2),
            rule.granularity + " (target-only consolidation)",
            pd.Timedelta(hours=1),
            rule.test_fraction,
            rule.random_state,
        )

    if base_id == 3:
        target = frame[["timestamp", "PM2.5"]].rename(columns={"PM2.5": "target"})
        return CandidateTarget(
            3, "PM2.5", _validate_target_frame(target, 3), rule.granularity,
            pd.Timedelta(hours=1), rule.test_fraction, rule.random_state,
        )

    if base_id == 4:
        target = (
            frame.set_index("timestamp")["T (degC)"]
            .resample("h")
            .mean()
            .rename("target")
            .reset_index()
        )
        return CandidateTarget(
            4,
            "T (degC)",
            _validate_target_frame(target, 4),
            rule.granularity + " mean",
            pd.Timedelta(hours=1),
            rule.test_fraction,
            rule.random_state,
        )

    if base_id == 5:
        target = (
            frame.set_index("timestamp")["GOLD_PRICE"]
            .resample("W-FRI")
            .last()
            .rename("target")
            .reset_index()
        )
        return CandidateTarget(
            5,
            "GOLD_PRICE",
            _validate_target_frame(target, 5),
            rule.granularity + " using last observed price",
            pd.Timedelta(days=7),
            rule.test_fraction,
            rule.random_state,
        )

    raise ValueError(f"Unsupported base: {base_id}. Expected an integer from 1 to 5.")


def _normalize_eligibility_mask(
    target_frame: pd.DataFrame, eligibility_mask: Iterable[bool] | None
) -> pd.Series:
    if eligibility_mask is None:
        return pd.Series(True, index=target_frame.index)
    mask = pd.Series(list(eligibility_mask), index=target_frame.index)
    if mask.isna().any():
        raise ValueError("The common eligibility mask must contain only True or False values.")
    return mask.astype(bool)


def _schedule_signature(schedule: pd.DataFrame) -> str:
    canonical_text = schedule[ORIGIN_COLUMNS].to_csv(index=False, lineterminator="\n")
    return sha256(canonical_text.encode("utf-8")).hexdigest()


def build_origin_schedule(
    candidate: CandidateTarget,
    horizon_steps: int = 1,
    test_fraction: float | None = None,
    eligibility_mask: Iterable[bool] | None = None,
) -> pd.DataFrame:
    """Build the final-test origins once, before a model receives the schedule.

    For regular daily/hourly targets, a one-step horizon also requires the
    target timestamp to be exactly one calendar unit ahead. For Base 5, the
    horizon is the next available trading observation. The optional eligibility
    mask is the intersection of every approved model's required feature rows.
    """
    if horizon_steps != 1:
        raise ValueError("Only the proposed one-step horizon is implemented at this stage.")
    if test_fraction is None:
        test_fraction = candidate.test_fraction
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be strictly between zero and one.")

    frame = candidate.data
    mask = _normalize_eligibility_mask(frame, eligibility_mask)
    target_available = frame["target"].notna()
    next_target_available = target_available.shift(-horizon_steps, fill_value=False)
    valid = mask & target_available & next_target_available

    if candidate.required_horizon_delta is not None:
        expected_target_time = frame["timestamp"] + candidate.required_horizon_delta
        actual_target_time = frame["timestamp"].shift(-horizon_steps)
        valid &= actual_target_time.eq(expected_target_time)

    eligible_positions = np.flatnonzero(valid.to_numpy())
    test_origin_count = int(np.ceil(len(eligible_positions) * test_fraction))
    if test_origin_count < 1:
        raise ValueError(f"Base {candidate.base_id}: no valid final-test origin was found.")
    selected_positions = eligible_positions[-test_origin_count:]

    schedule = pd.DataFrame(
        {
            "origin_timestamp": frame.loc[selected_positions, "timestamp"].to_numpy(),
            "target_timestamp": frame.loc[selected_positions + horizon_steps, "timestamp"].to_numpy(),
            "origin_position": selected_positions,
            "target_position": selected_positions + horizon_steps,
            "horizon_steps": horizon_steps,
        }
    )
    schedule.insert(
        0,
        "origin_id",
        [f"base{candidate.base_id}_h{horizon_steps}_{timestamp:%Y%m%dT%H%M%S}" for timestamp in schedule["origin_timestamp"]],
    )
    validate_origin_schedule(schedule, candidate)
    return schedule


def validate_origin_schedule(schedule: pd.DataFrame, candidate: CandidateTarget) -> None:
    """Reject schedules that would undermine temporal ordering or comparison."""
    if list(schedule.columns) != ORIGIN_COLUMNS:
        raise ValueError("Origin schedule columns do not match the canonical schema.")
    if schedule.empty:
        raise ValueError("Origin schedule cannot be empty.")
    if schedule["origin_id"].duplicated().any() or schedule["origin_timestamp"].duplicated().any():
        raise ValueError("Origin schedule contains repeated origins.")
    if not schedule["origin_timestamp"].is_monotonic_increasing:
        raise ValueError("Origin schedule must be chronological.")
    if not (schedule["target_position"] > schedule["origin_position"]).all():
        raise ValueError("Every target position must be after its origin position.")
    if not (schedule["target_timestamp"] > schedule["origin_timestamp"]).all():
        raise ValueError("Every target timestamp must be after its origin timestamp.")
    if candidate.required_horizon_delta is not None:
        delta = schedule["target_timestamp"] - schedule["origin_timestamp"]
        if not delta.eq(candidate.required_horizon_delta).all():
            raise ValueError("A regular-frequency schedule contains a nonconforming horizon.")


def assert_same_origins(
    schedules_by_model: dict[str, pd.DataFrame], canonical_schedule: pd.DataFrame
) -> dict[str, str | int]:
    """Assert that every model consumes precisely the canonical schedule.

    Model runners must call this function before reporting MAE. It rejects a
    missing model, a reordered schedule, or one with an extra/missing origin.
    """
    supplied_models = set(schedules_by_model)
    expected_models = set(MODEL_NAMES)
    if supplied_models != expected_models:
        raise ValueError(
            f"Expected schedules for {sorted(expected_models)}, received {sorted(supplied_models)}."
        )
    expected = canonical_schedule[ORIGIN_COLUMNS].reset_index(drop=True)
    for model_name, schedule in schedules_by_model.items():
        observed = schedule[ORIGIN_COLUMNS].reset_index(drop=True)
        try:
            pd.testing.assert_frame_equal(observed, expected, check_dtype=False)
        except AssertionError as error:
            raise ValueError(f"{model_name}: origins differ from the canonical schedule.") from error
    return {"origin_count": int(len(expected)), "origin_signature": _schedule_signature(expected)}


def write_target_only_origin_artifacts(
    processed_dir: Path = Path("data/processed"),
    output_dir: Path = Path("reports/generated/origin_schedules"),
    rules_path: Path = DEFAULT_RULES_PATH,
) -> pd.DataFrame:
    """Write provisional target-only schedules and an audit summary for all bases."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for base_id in range(1, 6):
        candidate = load_candidate_target(base_id, processed_dir, rules_path)
        schedule = build_origin_schedule(candidate)
        destination = output_dir / f"base{base_id}_h1_target_only.csv"
        schedule.to_csv(destination, index=False)
        check = assert_same_origins({model: schedule for model in MODEL_NAMES}, schedule)
        summaries.append(
            {
                "base_id": base_id,
                "target": candidate.target_name,
                "frequency_interpretation": candidate.frequency_label,
                "random_state": candidate.random_state,
                "train_fraction": 1 - candidate.test_fraction,
                "test_fraction": candidate.test_fraction,
                "origin_count": check["origin_count"],
                "first_origin": schedule["origin_timestamp"].min().isoformat(),
                "last_origin": schedule["origin_timestamp"].max().isoformat(),
                "origin_signature": check["origin_signature"],
                "scope": "target-only provisional schedule; regenerate after common feature eligibility is approved",
            }
        )
    summary = pd.DataFrame(summaries)
    summary.to_json(output_dir / "target_only_origin_schedule_summary.json", orient="records", indent=2)
    return summary


def load_origin_summary(path: Path) -> list[dict[str, object]]:
    """Read a generated summary for notebooks or a later audit step."""
    return json.loads(path.read_text(encoding="utf-8"))
