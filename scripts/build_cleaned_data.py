"""Build the five cleaned datasets from the structural inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from discovery_series_temporais.cleaning import build_all_cleaned_datasets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    summaries = build_all_cleaned_datasets(args.processed_dir)
    print(
        json.dumps(
            [
                {
                    "base_id": summary.base_id,
                    "target": summary.target_name,
                    "rows": summary.rows,
                    "columns": summary.columns,
                    "missing_target": summary.missing_target,
                    "output": str(summary.output_path),
                    "actions": list(summary.actions),
                }
                for summary in summaries
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
