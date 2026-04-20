from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


DEFAULT_RULE_ENGINE_CONFIG_PATH = Path("scoring/rule_engine_config.json")


@lru_cache(maxsize=1)
def load_rule_engine_config(path_str: str | None = None) -> Dict[str, Any]:
    path = Path(path_str) if path_str else DEFAULT_RULE_ENGINE_CONFIG_PATH
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    validate_rule_engine_config(config)
    return config


def validate_rule_engine_config(config: Dict[str, Any]) -> None:
    required_top_level = [
        "base_score",
        "score_bounds",
        "risk_probability",
        "risk_bands",
        "decision_policy",
        "next_steps",
        "rules",
    ]
    missing = [key for key in required_top_level if key not in config]
    if missing:
        raise ValueError(f"Rule engine config is missing keys: {', '.join(missing)}")

    if not isinstance(config["rules"], dict) or not config["rules"]:
        raise ValueError("Rule engine config requires at least one rule definition.")
