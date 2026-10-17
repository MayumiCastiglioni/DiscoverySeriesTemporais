"""Generate and verify provisional shared origin schedules for all five bases."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from discovery_series_temporais.series import write_target_only_origin_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("reports/generated/origin_schedules")
    )
    args = parser.parse_args()
    print(write_target_only_origin_artifacts(args.processed_dir, args.output_dir).to_string(index=False))


if __name__ == "__main__":
    main()
