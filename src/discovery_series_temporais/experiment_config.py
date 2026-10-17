"""Load and validate the group-approved rules for each experiment base."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


DEFAULT_RULES_PATH = Path("configs/base_experiment_rules.json")


@dataclass(frozen=True)
class BaseExperimentRule:
    """Fixed group rules used by all model runners for a base."""

    base_id: int
    group: str
    source_url: str
    granularity: str
    random_state: int
    train_fraction: float
    test_fraction: float
    target_rule: str


def load_experiment_rules(path: Path = DEFAULT_RULES_PATH) -> dict[int, BaseExperimentRule]:
    """Read the versioned rule file and reject incomplete split definitions."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    rules: dict[int, BaseExperimentRule] = {}
    for item in payload["bases"]:
        rule = BaseExperimentRule(
            base_id=int(item["base_id"]),
            group=str(item["group"]),
            source_url=str(item["source_url"]),
            granularity=str(item["granularity"]),
            random_state=int(item["random_state"]),
            train_fraction=float(item["train_fraction"]),
            test_fraction=float(item["test_fraction"]),
            target_rule=str(item["target_rule"]),
        )
        if not 0 < rule.train_fraction < 1 or not 0 < rule.test_fraction < 1:
            raise ValueError(f"Base {rule.base_id}: split fractions must be between zero and one.")
        if abs((rule.train_fraction + rule.test_fraction) - 1.0) > 1e-12:
            raise ValueError(f"Base {rule.base_id}: train and test fractions must sum to one.")
        if rule.base_id in rules:
            raise ValueError(f"Repeated configuration for base {rule.base_id}.")
        rules[rule.base_id] = rule
    if set(rules) != {1, 2, 3, 4, 5}:
        raise ValueError("The rule file must configure each base from 1 to 5 exactly once.")
    return rules


def get_experiment_rule(base_id: int, path: Path = DEFAULT_RULES_PATH) -> BaseExperimentRule:
    """Return the configured rule for one base."""
    try:
        return load_experiment_rules(path)[base_id]
    except KeyError as error:
        raise ValueError(f"No rule configured for base {base_id}.") from error
