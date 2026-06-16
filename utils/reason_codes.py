from __future__ import annotations

import re


REASON_CODE_MAP = {
    "Affordability hard stop": "AFFORDABILITY_HARD_STOP",
    "Bureau hard stop": "BUREAU_SCORE_BELOW_MINIMUM",
    "Collateral support": "COLLATERAL_SUPPORT",
    "Collateral validation": "COLLATERAL_VALUE_MISSING",
    "Credit bureau score": "BUREAU_SCORE",
    "Documentation completeness": "DOCUMENTATION_KYC",
    "Employment stability": "EMPLOYMENT_STABILITY",
    "Income validation": "INCOME_MISSING_OR_ZERO",
    "Loan amount validation": "LOAN_AMOUNT_INVALID",
    "Loan size vs income": "LOAN_TO_INCOME",
    "Payment bounce behaviour": "PAYMENT_BOUNCE_HISTORY",
    "Recent delinquency history": "RECENT_DELINQUENCY",
    "Repayment burden": "FOIR_REPAYMENT_BURDEN",
    "Repayment conduct hard stop": "SEVERE_REPAYMENT_CONDUCT",
}


def reason_code_for_factor(factor: str) -> str:
    if factor in REASON_CODE_MAP:
        return REASON_CODE_MAP[factor]
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", factor.strip()).strip("_").upper()
    return normalized or "UNMAPPED_REASON"
