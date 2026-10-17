"""Apply only documented, target-independent structural preparation to frozen inputs.

This script never alters files in data/raw. It intentionally leaves decisions about
target selection, feature availability, imputation, scaling, and model-specific
feature engineering to later, time-safe stages.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAW_FILENAMES = {base_id: f"base{base_id}.csv" for base_id in range(1, 6)}


def require_no_invalid_timestamps(timestamps: pd.Series, base_id: int) -> None:
    invalid_count = int(timestamps.isna().sum())
    if invalid_count:
        raise ValueError(f"Base {base_id} has {invalid_count} invalid timestamp(s).")


def load_base_1(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    timestamps = pd.to_datetime(frame.pop("Date"), errors="coerce")
    require_no_invalid_timestamps(timestamps, 1)
    frame.insert(0, "timestamp", timestamps)
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    return frame, ["normalized timestamp from Date", "sorted chronologically"]


def load_base_2(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    timestamps = pd.to_datetime(frame.pop("date_time"), errors="coerce")
    require_no_invalid_timestamps(timestamps, 2)
    frame.insert(0, "timestamp", timestamps)
    missing_holidays = int(frame["holiday"].isna().sum())
    frame["holiday"] = frame["holiday"].fillna("No holiday")
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    return frame, [
        "normalized timestamp from date_time",
        f"replaced {missing_holidays} blank holiday values with the normalized label No holiday",
        "kept repeated timestamps for the documented aggregation decision",
    ]


def load_base_3(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    timestamps = pd.to_datetime(frame[["year", "month", "day", "hour"]], errors="coerce")
    require_no_invalid_timestamps(timestamps, 3)
    frame.insert(0, "timestamp", timestamps)
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    return frame, [
        "created timestamp from year, month, day, and hour",
        "sorted chronologically",
        "preserved missing values for fold-safe treatment later",
    ]


def load_base_4(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    timestamps = pd.to_datetime(
        frame.pop("Date Time"), format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )
    require_no_invalid_timestamps(timestamps, 4)
    frame.insert(0, "timestamp", timestamps)
    before_deduplication = len(frame)
    frame = frame.drop_duplicates().sort_values("timestamp", kind="stable").reset_index(drop=True)
    removed_duplicates = before_deduplication - len(frame)
    sentinel_counts = {}
    for column in ("wv (m/s)", "max. wv (m/s)"):
        sentinel_counts[column] = int((frame[column] == -9999).sum())
        frame[column] = frame[column].replace(-9999, np.nan)
    return frame, [
        "normalized timestamp from Date Time",
        f"removed {removed_duplicates} exact duplicate rows",
        "sorted chronologically",
        "replaced -9999 sentinel values with missing values: "
        + ", ".join(f"{column}={count}" for column, count in sentinel_counts.items()),
    ]


def load_base_5(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    timestamps = pd.to_datetime(frame.pop("DATE"), errors="coerce")
    require_no_invalid_timestamps(timestamps, 5)
    frame.insert(0, "timestamp", timestamps)
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    return frame, [
        "normalized timestamp from DATE",
        "sorted chronologically",
        "preserved pre-engineered columns for audit only; they are not approved model inputs",
    ]


LOADERS = {
    1: load_base_1,
    2: load_base_2,
    3: load_base_3,
    4: load_base_4,
    5: load_base_5,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for base_id, filename in RAW_FILENAMES.items():
        source = args.raw_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"Frozen input not found: {source}")
        prepared, actions = LOADERS[base_id](source)
        destination = args.output_dir / f"base{base_id}_structural.csv"
        prepared.to_csv(destination, index=False)
        summaries.append(
            {
                "base": base_id,
                "input_rows": int(sum(1 for _ in source.open(encoding="utf-8")) - 1),
                "output_rows": int(len(prepared)),
                "output_columns": int(prepared.shape[1]),
                "output": str(destination),
                "actions": actions,
            }
        )
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
