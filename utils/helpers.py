from __future__ import annotations

import math
from typing import Optional


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


def band_from_probability(prob: float) -> str:
    if prob < 0.12:
        return "Low Risk"
    if prob < 0.22:
        return "Moderate Risk"
    if prob < 0.35:
        return "Elevated Risk"
    return "High Risk"


def decision_from_probability(prob: float, kyc_complete_flag: int) -> str:
    if not kyc_complete_flag:
        return "Approve with Conditions"
    if prob < 0.11:
        return "Approve"
    if prob < 0.22:
        return "Approve with Conditions"
    if prob < 0.33:
        return "Manual Review"
    return "Decline"


def step_from_decision(decision: str) -> str:
    mapping = {
        "Approve": "Approve",
        "Approve with Conditions": "Approve with Conditions",
        "Manual Review": "Send to underwriter for review",
        "Decline": "Decline",
    }
    return mapping.get(decision, decision)
