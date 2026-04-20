from __future__ import annotations

import math
from typing import Dict, List, Optional


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return principal / tenure_months
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1
    return numerator / denominator if denominator else 0.0


def safe_divide(a: float, b: float) -> float:
    if b in (0, None):
        return 0.0
    return a / b


def compute_ltv(requested_loan_amount: float, has_collateral_flag: int, collateral_value: float) -> Optional[float]:
    if not has_collateral_flag or collateral_value <= 0:
        return None
    return requested_loan_amount / collateral_value


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def band_from_probability(prob: float, bands: Optional[List[Dict[str, float | str]]] = None) -> str:
    bands = bands or [
        {"max": 0.12, "label": "Low Risk"},
        {"max": 0.22, "label": "Moderate Risk"},
        {"max": 0.35, "label": "Elevated Risk"},
        {"label": "High Risk"},
    ]
    for band in bands:
        max_threshold = band.get("max")
        if max_threshold is None or prob < float(max_threshold):
            return str(band["label"])
    return str(bands[-1]["label"])


def decision_from_probability(prob: float, kyc_complete_flag: int, decision_policy: Optional[Dict] = None) -> str:
    policy = decision_policy or {
        "kyc_incomplete_decision": "Approve with Conditions",
        "bands": [
            {"max": 0.11, "decision": "Approve"},
            {"max": 0.22, "decision": "Approve with Conditions"},
            {"max": 0.33, "decision": "Manual Review"},
            {"decision": "Decline"},
        ],
    }
    if not kyc_complete_flag:
        return str(policy["kyc_incomplete_decision"])

    for band in policy["bands"]:
        max_threshold = band.get("max")
        if max_threshold is None or prob < float(max_threshold):
            return str(band["decision"])
    return str(policy["bands"][-1]["decision"])


def step_from_decision(decision: str, mapping: Optional[Dict[str, str]] = None) -> str:
    mapping = mapping or {
        "Approve": "Approve",
        "Approve with Conditions": "Approve with Conditions",
        "Manual Review": "Send to underwriter for review",
        "Decline": "Decline",
    }
    return mapping.get(decision, decision)
