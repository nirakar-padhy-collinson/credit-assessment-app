from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class CreditApplication:
    loan_id: str
    applicant_id: str
    applicant_name: str = ""
    age: int = 30
    monthly_income: float = 0.0
    employment_type: str = "Salaried"
    years_in_current_job: float = 0.0
    existing_monthly_obligations: float = 0.0
    requested_loan_amount: float = 0.0
    loan_purpose: str = "Personal"
    tenure_months: int = 12
    annual_interest_rate: float = 14.0
    credit_score: int = 700
    prior_delinquency_count_24m: int = 0
    bounced_payments_12m: int = 0
    existing_customer_flag: int = 0
    kyc_complete_flag: int = 1
    has_collateral_flag: int = 0
    collateral_value: float = 0.0
    residence_type: str = "Rented"
    city_tier: str = "Tier 1"

    # Protected/sensitive attributes intentionally excluded from the first-stage model.
    # Examples not used: gender, religion, marital status, caste, ethnicity.

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FactorContribution:
    factor: str
    impact_direction: str
    points: float
    description: str


@dataclass
class EngineOutput:
    engine_name: str
    score: float
    risk_probability: float
    risk_band: str
    decision: str
    recommended_next_step: str
    emi: float
    foir: float
    loan_to_income: float
    ltv: Optional[float]
    top_positive_reasons: List[str] = field(default_factory=list)
    top_negative_reasons: List[str] = field(default_factory=list)
    factor_contributions: List[FactorContribution] = field(default_factory=list)
    feature_importance: List[Dict[str, Any]] = field(default_factory=list)
    confidence: Optional[float] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload
