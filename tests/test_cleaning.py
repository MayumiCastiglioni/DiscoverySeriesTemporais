"""Tests for deterministic cleaned-dataset transformations and diagnostics."""

from __future__ import annotations

import unittest

import pandas as pd

from discovery_series_temporais.cleaning import _clean_base_2, select_diagnostic_segment


class CleaningTests(unittest.TestCase):
    def test_base_2_consolidates_repeated_hours_deterministically(self) -> None:
        frame = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2024-01-01 00:00", "2024-01-01 00:00"]),
                "traffic_volume": [100, 100],
                "temp": [280.0, 282.0],
                "rain_1h": [0.0, 2.0],
                "snow_1h": [0.0, 0.0],
                "clouds_all": [40, 60],
                "holiday": ["No holiday", "No holiday"],
                "weather_main": ["Clouds", "Clear"],
                "weather_description": ["broken clouds", "clear sky"],
            }
        )
        cleaned, _ = _clean_base_2(frame)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "target"], 100)
        self.assertEqual(cleaned.loc[0, "temp"], 281.0)
        self.assertEqual(cleaned.loc[0, "weather_main"], "Clear")

    def test_diagnostic_segment_does_not_bridge_a_missing_target(self) -> None:
        timestamps = pd.date_range("2024-01-01", periods=30, freq="D")
        target = list(range(30))
        target[10] = None
        segment = select_diagnostic_segment(
            pd.DataFrame({"timestamp": timestamps, "target": target}), base_id=1
        )
        self.assertEqual(len(segment.data), 19)
        self.assertEqual(segment.data["timestamp"].min(), pd.Timestamp("2024-01-12"))


if __name__ == "__main__":
    unittest.main()
