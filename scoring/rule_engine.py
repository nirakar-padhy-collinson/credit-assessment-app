from __future__ import annotations

from typing import List

from models.contracts import CreditApplication, EngineOutput, FactorContribution
from utils.helpers import (
    band_from_probability,
    calculate_emi,
    clamp,
    compute_ltv,
    decision_from_probability,
    safe_divide,
    step_from_decision,
)


class RuleBasedDecisionEngine:
    name = "Rule-Based Decision Engine"

    def evaluate(self, app: CreditApplication) -> EngineOutput:
        emi = calculate_emi(app.requested_loan_amount, app.annual_interest_rate, app.tenure_months)
        foir = safe_divide(app.existing_monthly_obligations + emi, app.monthly_income)
        ltv = compute_ltv(app.requested_loan_amount, app.has_collateral_flag, app.collateral_value)
        loan_to_income = safe_divide(app.requested_loan_amount, app.monthly_income * 12)

        score = 55.0
        contributions: List[FactorContribution] = []

        def add(factor: str, points: float, description: str):
            nonlocal score
            score += points
            contributions.append(
                FactorContribution(
                    factor=factor,
                    impact_direction="Positive" if points >= 0 else "Negative",
                    points=round(points, 1),
                    description=description,
                )
            )

        if foir <= 0.35:
            add("Repayment burden", 14, f"FOIR at {foir:.0%} is comfortably within policy tolerance.")
        elif foir <= 0.5:
            add("Repayment burden", 6, f"FOIR at {foir:.0%} is manageable but leaves moderate cushion.")
        elif foir <= 0.65:
            add("Repayment burden", -10, f"FOIR at {foir:.0%} indicates stretched repayment capacity.")
        else:
            add("Repayment burden", -20, f"FOIR at {foir:.0%} is above prudent first-stage thresholds.")

        if app.credit_score >= 780:
            add("Credit bureau score", 16, f"Credit score of {app.credit_score} reflects strong repayment behaviour.")
        elif app.credit_score >= 730:
            add("Credit bureau score", 10, f"Credit score of {app.credit_score} is above portfolio average.")
        elif app.credit_score >= 680:
            add("Credit bureau score", 3, f"Credit score of {app.credit_score} is acceptable for initial screening.")
        elif app.credit_score >= 620:
            add("Credit bureau score", -10, f"Credit score of {app.credit_score} requires tighter monitoring.")
        else:
            add("Credit bureau score", -22, f"Credit score of {app.credit_score} is weak for retail underwriting.")

        if app.prior_delinquency_count_24m == 0:
            add("Recent delinquency history", 8, "No delinquency in the last 24 months.")
        elif app.prior_delinquency_count_24m <= 1:
            add("Recent delinquency history", -6, "One delinquency in the last 24 months raises caution.")
        else:
            add("Recent delinquency history", -16, f"{app.prior_delinquency_count_24m} delinquencies in the last 24 months materially elevate risk.")

        if app.bounced_payments_12m == 0:
            add("Payment bounce behaviour", 6, "No bounced payments observed in the last 12 months.")
        elif app.bounced_payments_12m <= 2:
            add("Payment bounce behaviour", -4, "A few payment bounces indicate mild cash-flow stress.")
        else:
            add("Payment bounce behaviour", -12, f"{app.bounced_payments_12m} bounced payments suggest unstable repayment behaviour.")

        if app.years_in_current_job >= 5:
            add("Employment stability", 8, f"{app.years_in_current_job:.1f} years in current job supports income stability.")
        elif app.years_in_current_job >= 2:
            add("Employment stability", 4, f"{app.years_in_current_job:.1f} years in current job is acceptable.")
        elif app.years_in_current_job >= 1:
            add("Employment stability", -2, f"{app.years_in_current_job:.1f} years in current job is still seasoning.")
        else:
            add("Employment stability", -8, f"Only {app.years_in_current_job:.1f} years in current job limits confidence in stable earnings.")

        if app.existing_customer_flag:
            add("Banking relationship", 5, "Existing customer relationship improves trust and observability.")

        if not app.kyc_complete_flag:
            add("Documentation completeness", -8, "KYC package is incomplete and requires remediation before disbursal.")
        else:
            add("Documentation completeness", 3, "KYC package is complete.")

        if loan_to_income <= 0.35:
            add("Loan size vs income", 8, f"Loan-to-annual-income at {loan_to_income:.2f}x is conservative.")
        elif loan_to_income <= 0.6:
            add("Loan size vs income", 2, f"Loan-to-annual-income at {loan_to_income:.2f}x is within common retail ranges.")
        elif loan_to_income <= 1.0:
            add("Loan size vs income", -7, f"Loan-to-annual-income at {loan_to_income:.2f}x is relatively high.")
        else:
            add("Loan size vs income", -15, f"Loan-to-annual-income at {loan_to_income:.2f}x is aggressive for first-stage approval.")

        if app.has_collateral_flag:
            if ltv is not None and ltv <= 0.65:
                add("Collateral support", 10, f"LTV at {ltv:.0%} is strong and well covered by collateral.")
            elif ltv is not None and ltv <= 0.85:
                add("Collateral support", 4, f"LTV at {ltv:.0%} provides moderate collateral support.")
            elif ltv is not None:
                add("Collateral support", -8, f"LTV at {ltv:.0%} is thin for secured lending comfort.")

        score = clamp(score, 0, 100)
        risk_probability = clamp((100 - score) / 100 * 0.55, 0.03, 0.65)
        risk_band = band_from_probability(risk_probability)
        decision = decision_from_probability(risk_probability, app.kyc_complete_flag)
        next_step = step_from_decision(decision)

        ordered = sorted(contributions, key=lambda x: abs(x.points), reverse=True)
        positives = [c.description for c in ordered if c.points > 0][:4]
        negatives = [c.description for c in ordered if c.points < 0][:4]

        return EngineOutput(
            engine_name=self.name,
            score=round(score, 1),
            risk_probability=round(risk_probability, 4),
            risk_band=risk_band,
            decision=decision,
            recommended_next_step=next_step,
            emi=round(emi, 2),
            foir=round(foir, 4),
            loan_to_income=round(loan_to_income, 4),
            ltv=round(ltv, 4) if ltv is not None else None,
            top_positive_reasons=positives,
            top_negative_reasons=negatives,
            factor_contributions=ordered,
            confidence=round(max(0.55, 1 - risk_probability), 4),
            notes=["Rule weights are modular and can be moved to configuration later."],
        )
