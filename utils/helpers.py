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


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    if b in (0, None):
        return default
    return a / b


def compute_ltv(requested_loan_amount: float, has_collateral_flag: int, collateral_value: float) -> Optional[float]:
    if not has_collateral_flag or collateral_value <= 0:
        return None
    return requested_loan_amount / collateral_value


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def risk_probability_from_score(score: float, risk_cfg: Optional[Dict] = None) -> float:
    risk_cfg = risk_cfg or {}
    anchors = risk_cfg.get(
        "calibration_anchors",
        [
            {"score": 0, "probability": 0.65},
            {"score": 40, "probability": 0.42},
            {"score": 55, "probability": 0.27},
            {"score": 70, "probability": 0.15},
            {"score": 85, "probability": 0.08},
            {"score": 100, "probability": 0.03},
        ],
    )
    ordered = sorted(anchors, key=lambda item: float(item["score"]))
    score = clamp(score, float(ordered[0]["score"]), float(ordered[-1]["score"]))

    for lower, upper in zip(ordered, ordered[1:]):
        lower_score = float(lower["score"])
        upper_score = float(upper["score"])
        if lower_score <= score <= upper_score:
            span = upper_score - lower_score
            weight = 0.0 if span == 0 else (score - lower_score) / span
            lower_prob = float(lower["probability"])
            upper_prob = float(upper["probability"])
            probability = lower_prob + (upper_prob - lower_prob) * weight
            return clamp(
                probability,
                float(risk_cfg.get("min", 0.03)),
                float(risk_cfg.get("max", 0.65)),
            )

    return float(ordered[-1]["probability"])


def documentation_status(kyc_complete_flag: int) -> str:
    return "KYC complete" if kyc_complete_flag else "KYC remediation required before disbursal"


def fulfillment_status(decision: str, kyc_complete_flag: int) -> str:
    if decision == "Decline":
        return "Not eligible for fulfillment"
    if decision == "Manual Review":
        return "Underwriter review required"
    if not kyc_complete_flag:
        return "Documentation hold"
    return "Ready for fulfillment"


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
    base_decision = str(policy["bands"][-1]["decision"])
    for band in policy["bands"]:
        max_threshold = band.get("max")
        if max_threshold is None or prob < float(max_threshold):
            base_decision = str(band["decision"])
            break

    if not kyc_complete_flag:
        if base_decision == "Approve":
            return str(policy.get("kyc_incomplete_decision", "Approve with Conditions"))
        if base_decision == "Approve with Conditions":
            return "Manual Review"
        return base_decision

    return base_decision


def step_from_decision(decision: str, mapping: Optional[Dict[str, str]] = None) -> str:
    mapping = mapping or {
        "Approve": "Approve",
        "Approve with Conditions": "Approve with Conditions",
        "Manual Review": "Send to underwriter for review",
        "Decline": "Decline",
    }
    return mapping.get(decision, decision)
