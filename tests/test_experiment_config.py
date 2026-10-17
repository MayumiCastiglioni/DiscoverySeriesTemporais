"""Tests for the group-supplied experiment configuration."""

from __future__ import annotations

import unittest

from discovery_series_temporais.experiment_config import load_experiment_rules


class ExperimentConfigurationTests(unittest.TestCase):
    def test_all_five_group_rules_are_present_and_valid(self) -> None:
        rules = load_experiment_rules()

        self.assertEqual(set(rules), {1, 2, 3, 4, 5})
        self.assertEqual((rules[1].train_fraction, rules[1].test_fraction), (0.7, 0.3))
        self.assertEqual((rules[2].random_state, rules[2].test_fraction), (67, 0.2))
        self.assertEqual((rules[5].train_fraction, rules[5].test_fraction), (0.75, 0.25))
        self.assertIn("weekly", rules[5].granularity)


if __name__ == "__main__":
    unittest.main()
