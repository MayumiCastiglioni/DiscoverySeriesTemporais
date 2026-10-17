"""Verify that the 20 separately executed model notebooks share their pilot origin."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from discovery_series_temporais.series import (
    MODEL_NAMES,
    assert_same_origins,
    build_origin_schedule,
    load_cleaned_candidate_target,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--pilot-dir", type=Path, default=Path("reports/generated/training_notebooks")
    )
    args = parser.parse_args()

    summary = []
    for base_id in range(1, 6):
        canonical = build_origin_schedule(
            load_cleaned_candidate_target(base_id, args.processed_dir)
        ).head(1)
        schedules = {}
        for model_name in MODEL_NAMES:
            source = args.pilot_dir / f"base{base_id}_{model_name}_pilot.csv"
            if not source.exists():
                raise FileNotFoundError(f"Training notebook output not found: {source}")
            prediction = pd.read_csv(
                source, parse_dates=["origin_timestamp", "target_timestamp"]
            )
            schedules[model_name] = prediction
        check = assert_same_origins(schedules, canonical)
        summary.append({"base_id": base_id, **check})
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
