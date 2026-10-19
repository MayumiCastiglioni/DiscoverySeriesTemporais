"""Build an auditable common feature matrix for one explicitly chosen horizon.

This script deliberately requires ``--horizon``.  It creates no model result
and does not approve the horizon itself; its purpose is to make the exact rows
eligible for the common final walk-forward schedule inspectable before fitting.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from discovery_series_temporais.features import build_feature_matrix


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=int, required=True, choices=range(1, 6))
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/features"))
    parser.add_argument(
        "--policy-path", type=Path, default=Path("configs/feature_availability_policy.json")
    )
    args = parser.parse_args()
    matrix = build_feature_matrix(
        args.base, args.horizon, args.processed_dir, args.policy_path
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"base{args.base}_h{args.horizon}"
    data_path = args.output_dir / f"{prefix}_common_features.csv"
    metadata_path = args.output_dir / f"{prefix}_common_features.metadata.json"
    matrix.data.to_csv(data_path, index=False)
    metadata_path.write_text(
        json.dumps(
            {
                "base_id": args.base,
                "horizon_steps": args.horizon,
                "rows": int(len(matrix.data)),
                "eligible_rows": int(matrix.eligibility_mask.sum()),
                "feature_columns": list(matrix.feature_columns),
                "external_feature_columns": list(matrix.external_feature_columns),
                "policy_notes": matrix.policy.notes,
                "policy_sha256": _file_hash(args.policy_path),
                "scope": "feature construction only; not a tuned model or final walk-forward result",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"features": str(data_path), "metadata": str(metadata_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
