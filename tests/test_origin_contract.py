"""Tests for the shared-origin comparability contract."""

from __future__ import annotations

import unittest

import pandas as pd

from discovery_series_temporais.series import (
    MODEL_NAMES,
    CandidateTarget,
    assert_same_origins,
    build_origin_schedule,
)


class OriginContractTests(unittest.TestCase):
    def setUp(self) -> None:
        timestamps = pd.date_range("2024-01-01", periods=20, freq="D")
        target = pd.DataFrame({"timestamp": timestamps, "target": range(20)})
        self.candidate = CandidateTarget(99, "synthetic_target", target, "daily", pd.Timedelta(days=1))
        self.schedule = build_origin_schedule(self.candidate)

    def test_same_schedule_is_accepted_for_every_model(self) -> None:
        result = assert_same_origins({model: self.schedule for model in MODEL_NAMES}, self.schedule)
        self.assertEqual(result["origin_count"], len(self.schedule))
        self.assertEqual(len(result["origin_signature"]), 64)

    def test_changed_schedule_is_rejected(self) -> None:
        changed = self.schedule.iloc[:-1].copy()
        schedules = {model: self.schedule for model in MODEL_NAMES}
        schedules["xgboost"] = changed
        with self.assertRaisesRegex(ValueError, "origins differ"):
            assert_same_origins(schedules, self.schedule)

    def test_regular_horizon_skips_calendar_gap(self) -> None:
        data = self.candidate.data.drop(index=10).reset_index(drop=True)
        gapped = CandidateTarget(99, "synthetic_target", data, "daily", pd.Timedelta(days=1))
        schedule = build_origin_schedule(gapped)
        gaps = schedule["target_timestamp"] - schedule["origin_timestamp"]
        self.assertTrue(gaps.eq(pd.Timedelta(days=1)).all())

    def test_multiple_steps_require_the_matching_calendar_delta(self) -> None:
        schedule = build_origin_schedule(self.candidate, horizon_steps=2)
        gaps = schedule["target_timestamp"] - schedule["origin_timestamp"]
        self.assertTrue(gaps.eq(pd.Timedelta(days=2)).all())
        self.assertTrue(schedule["horizon_steps"].eq(2).all())


if __name__ == "__main__":
    unittest.main()
