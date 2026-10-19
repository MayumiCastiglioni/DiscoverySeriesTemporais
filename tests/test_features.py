"""Tests for the leakage-safe common feature matrix."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from discovery_series_temporais.features import MIN_HOLT_CONTIGUOUS_HISTORY, build_feature_matrix


class FeatureMatrixTests(unittest.TestCase):
    def _write_base_1_fixture(self, root: Path) -> None:
        timestamps = pd.date_range("2024-01-01", periods=30, freq="D")
        frame = pd.DataFrame(
            {
                "timestamp": timestamps,
                "target": range(30),
                "Open": range(100, 130),
                "High": range(200, 230),
                "Low": range(50, 80),
                "Volume": range(1000, 1030),
            }
        )
        frame.to_csv(root / "base1_cleaned.csv", index=False)

    def _write_policy(self, root: Path) -> Path:
        bases = []
        for base_id in range(1, 6):
            bases.append(
                {
                    "base_id": base_id,
                    "numeric_lag_1": ["Open", "High", "Low", "Volume"] if base_id == 1 else [],
                    "excluded": [],
                    "notes": "test",
                }
            )
        path = root / "policy.json"
        path.write_text(json.dumps({"bases": bases}), encoding="utf-8")
        return path

    def test_external_values_are_lagged_and_calendar_uses_the_target_time(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self._write_base_1_fixture(root)
            matrix = build_feature_matrix(1, 2, root, self._write_policy(root))
            row = matrix.data.iloc[10]
            self.assertEqual(row["target_timestamp"], pd.Timestamp("2024-01-13"))
            self.assertEqual(row["future_target"], 12)
            self.assertEqual(row["external_lag_1__Open"], 109)
            self.assertTrue(row["eligible_for_common_schedule"])

    def test_a_missing_external_value_does_not_move_the_common_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self._write_base_1_fixture(root)
            fixture = pd.read_csv(root / "base1_cleaned.csv")
            fixture.loc[10, "Open"] = None
            fixture.to_csv(root / "base1_cleaned.csv", index=False)
            matrix = build_feature_matrix(1, 1, root, self._write_policy(root))
            self.assertTrue(matrix.data.loc[11, "eligible_for_common_schedule"])
            self.assertTrue(pd.isna(matrix.data.loc[11, "external_lag_1__Open"]))

    def test_a_gap_in_the_target_rejects_only_affected_label_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self._write_base_1_fixture(root)
            fixture = pd.read_csv(root / "base1_cleaned.csv")
            fixture.loc[9, "target"] = None
            fixture.to_csv(root / "base1_cleaned.csv", index=False)
            matrix = build_feature_matrix(1, 1, root, self._write_policy(root))
            self.assertFalse(matrix.data.loc[8, "eligible_for_common_schedule"])
            self.assertFalse(matrix.data.loc[9, "eligible_for_common_schedule"])
            self.assertFalse(matrix.data.loc[10, "eligible_for_common_schedule"])
            self.assertFalse(matrix.data.loc[11, "eligible_for_common_schedule"])
            self.assertTrue(matrix.data.loc[12, "eligible_for_common_schedule"])
            self.assertEqual(matrix.data.loc[12, "contiguous_target_history"], MIN_HOLT_CONTIGUOUS_HISTORY)


if __name__ == "__main__":
    unittest.main()
