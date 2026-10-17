"""Run the four required models once per base on their respective shared pilot origin."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from discovery_series_temporais.model_pilots import run_all_model_pilots
from discovery_series_temporais.series import build_origin_schedule, load_candidate_target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/generated/model_pilots"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for base_id in range(1, 6):
        candidate = load_candidate_target(base_id, args.processed_dir)
        outputs.append(run_all_model_pilots(candidate, build_origin_schedule(candidate)))
    pilots = pd.concat(outputs, ignore_index=True)
    pilots.to_csv(args.output_dir / "shared_origin_model_pilots.csv", index=False)
    print(pilots.to_string(index=False))


if __name__ == "__main__":
    main()
