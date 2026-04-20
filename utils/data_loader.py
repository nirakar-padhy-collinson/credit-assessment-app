from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from models.contracts import CreditApplication, EngineOutput
from scoring.rule_engine import RuleBasedDecisionEngine


DATA_PATH = Path("data/historical_loan_applications.csv")
EMPLOYEE_BRANCH_MAP = {
    "BR0001": [f"EM{i:04d}" for i in range(1, 6)],
    "BR0002": [f"EM{i:04d}" for i in range(6, 11)],
}
ALL_BRANCH_IDS = list(EMPLOYEE_BRANCH_MAP.keys())
ID_PATTERNS = {
    "loan_id": "LN",
    "applicant_id": "AP",
    "employee_id": "EM",
    "branch_id": "BR",
}
HISTORY_COLUMNS = [
    "loan_id",
    "applicant_id",
    "employee_id",
    "branch_id",
    "applicant_name",
    "age",
    "monthly_income",
    "employment_type",
    "years_in_current_job",
    "existing_monthly_obligations",
    "requested_loan_amount",
    "loan_purpose",
    "tenure_months",
    "annual_interest_rate",
    "credit_score",
    "prior_delinquency_count_24m",
    "bounced_payments_12m",
    "existing_customer_flag",
    "kyc_complete_flag",
    "has_collateral_flag",
    "collateral_value",
    "residence_type",
    "city_tier",
    "historical_engine",
    "historical_decision",
    "historical_risk_band",
    "historical_score",
    "historical_risk_probability",
    "historical_explanation",
    "defaulted_flag",
    "approval_outcome",
]


def _choice(rng: np.random.Generator, values, probs=None, size=None):
    return rng.choice(values, p=probs, size=size)


def _weighted_choice(rng: np.random.Generator, mapping: dict[str, float]) -> str:
    values = list(mapping.keys())
    weights = np.array(list(mapping.values()), dtype=float)
    weights = weights / weights.sum()
    return str(rng.choice(values, p=weights))


def format_entity_id(prefix: str, value: int) -> str:
    return f"{prefix}{value:04d}"


def _extract_numeric_suffix(value: object, prefix: str) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    match = re.search(rf"{prefix}\s*0*(\d+)$", str(value).strip(), flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def next_entity_id(df: pd.DataFrame, column_name: str, prefix: str) -> str:
    if column_name not in df.columns or df.empty:
        return format_entity_id(prefix, 1)

    existing = [_extract_numeric_suffix(value, prefix) for value in df[column_name].tolist()]
    max_value = max((value for value in existing if value is not None), default=0)
    return format_entity_id(prefix, max_value + 1)


def branch_employee_options() -> dict[str, list[str]]:
    return {branch_id: employee_ids[:] for branch_id, employee_ids in EMPLOYEE_BRANCH_MAP.items()}


def _assign_branch_and_employee(row_number: int) -> tuple[str, str]:
    branch_id = ALL_BRANCH_IDS[(row_number - 1) % len(ALL_BRANCH_IDS)]
    employee_pool = EMPLOYEE_BRANCH_MAP[branch_id]
    employee_id = employee_pool[((row_number - 1) // len(ALL_BRANCH_IDS)) % len(employee_pool)]
    return branch_id, employee_id


def _normalize_identifier_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column_name, prefix in ID_PATTERNS.items():
        if column_name in out.columns:
            out[column_name] = [
                format_entity_id(prefix, numeric) if numeric is not None else ""
                for numeric in (_extract_numeric_suffix(value, prefix) for value in out[column_name])
            ]
    return out


def ensure_history_schema(df: pd.DataFrame) -> pd.DataFrame:
    out = _normalize_identifier_columns(df)

    if "branch_id" not in out.columns or "employee_id" not in out.columns:
        branch_ids: list[str] = []
        employee_ids: list[str] = []
        for row_number in range(1, len(out) + 1):
            branch_id, employee_id = _assign_branch_and_employee(row_number)
            branch_ids.append(branch_id)
            employee_ids.append(employee_id)
        if "branch_id" not in out.columns:
            out["branch_id"] = branch_ids
        if "employee_id" not in out.columns:
            out["employee_id"] = employee_ids

    if "historical_engine" not in out.columns:
        out["historical_engine"] = "Rule-Based Decision Engine"

    if "approval_outcome" not in out.columns and "historical_decision" in out.columns:
        out["approval_outcome"] = out["historical_decision"].isin(["Approve", "Approve with Conditions"]).astype(int)

    for column_name in HISTORY_COLUMNS:
        if column_name not in out.columns:
            out[column_name] = pd.NA

    out = out[HISTORY_COLUMNS]
    return out


def _sample_profile(rng: np.random.Generator) -> dict[str, object]:
    age = int(np.clip(rng.normal(34, 8), 21, 62))

    if age < 27:
        employment_type = _weighted_choice(rng, {"Salaried": 0.52, "Contract": 0.24, "Professional": 0.08, "Self-Employed": 0.16})
    elif age < 40:
        employment_type = _weighted_choice(rng, {"Salaried": 0.56, "Self-Employed": 0.18, "Contract": 0.12, "Professional": 0.14})
    else:
        employment_type = _weighted_choice(rng, {"Salaried": 0.46, "Self-Employed": 0.24, "Contract": 0.08, "Professional": 0.22})

    max_experience = max(0.4, age - 20)
    tenure_mean = {"Salaried": 4.8, "Self-Employed": 6.2, "Contract": 2.4, "Professional": 5.4}[employment_type]
    tenure_sd = {"Salaried": 2.4, "Self-Employed": 3.0, "Contract": 1.5, "Professional": 2.6}[employment_type]
    years_in_current_job = float(np.clip(rng.normal(tenure_mean, tenure_sd), 0.3, max_experience))

    base_income = {"Salaried": 85000, "Self-Employed": 105000, "Contract": 72000, "Professional": 125000}[employment_type]
    income_age_adj = (age - 30) * 1800
    income_tenure_adj = years_in_current_job * {"Salaried": 3200, "Self-Employed": 4200, "Contract": 1800, "Professional": 4500}[employment_type]
    monthly_income = float(np.clip(rng.normal(base_income + income_age_adj + income_tenure_adj, 18000), 25000, 350000))

    if age < 28:
        residence_type = _weighted_choice(rng, {"Rented": 0.58, "Family": 0.28, "Owned": 0.14})
    elif age < 40:
        residence_type = _weighted_choice(rng, {"Rented": 0.46, "Family": 0.18, "Owned": 0.36})
    else:
        residence_type = _weighted_choice(rng, {"Owned": 0.54, "Rented": 0.28, "Family": 0.18})

    if monthly_income >= 140000:
        city_tier = _weighted_choice(rng, {"Tier 1": 0.62, "Tier 2": 0.28, "Tier 3": 0.10})
    elif monthly_income >= 80000:
        city_tier = _weighted_choice(rng, {"Tier 1": 0.44, "Tier 2": 0.36, "Tier 3": 0.20})
    else:
        city_tier = _weighted_choice(rng, {"Tier 2": 0.42, "Tier 3": 0.36, "Tier 1": 0.22})

    existing_customer_prob = 0.22 + min(years_in_current_job / 20, 0.18) + (0.10 if age >= 32 else 0) + (0.08 if monthly_income >= 100000 else 0)
    existing_customer = int(rng.random() < min(existing_customer_prob, 0.78))
    kyc_complete = int(rng.random() < (0.985 if existing_customer else 0.91))

    return {
        "age": age,
        "employment_type": employment_type,
        "years_in_current_job": round(years_in_current_job, 1),
        "monthly_income": round(monthly_income, 2),
        "residence_type": residence_type,
        "city_tier": city_tier,
        "existing_customer": existing_customer,
        "kyc_complete": kyc_complete,
    }


def _sample_credit_behavior(
    rng: np.random.Generator,
    *,
    employment_type: str,
    years_in_current_job: float,
    monthly_income: float,
    existing_customer: int,
) -> dict[str, object]:
    stress = 0.0
    stress += {"Contract": 0.10, "Self-Employed": 0.05, "Salaried": -0.02, "Professional": -0.04}[employment_type]
    stress += -min(years_in_current_job / 12, 0.10)
    stress += -0.05 if existing_customer else 0.03
    stress += -0.04 if monthly_income >= 140000 else (0.02 if monthly_income < 50000 else 0.0)

    delinquency_lambda = float(np.clip(0.45 + stress * 2.2, 0.08, 1.4))
    bounce_lambda = float(np.clip(0.60 + stress * 2.6, 0.10, 1.8))

    delinquency = int(np.clip(rng.poisson(delinquency_lambda), 0, 5))
    bounces = int(np.clip(rng.poisson(bounce_lambda), 0, 6))

    score_base = 722
    score_base += {"Professional": 16, "Salaried": 7, "Self-Employed": -5, "Contract": -12}[employment_type]
    score_base += min(years_in_current_job * 2.2, 18)
    score_base += 10 if existing_customer else -4
    score_base += 8 if monthly_income >= 140000 else (-8 if monthly_income < 50000 else 0)
    score_base -= delinquency * 25
    score_base -= bounces * 12

    credit_score = int(np.clip(rng.normal(score_base, 28), 540, 860))
    return {
        "credit_score": credit_score,
        "prior_delinquency_count_24m": delinquency,
        "bounced_payments_12m": bounces,
    }


def _sample_loan_terms(
    rng: np.random.Generator,
    *,
    age: int,
    employment_type: str,
    monthly_income: float,
    credit_score: int,
    residence_type: str,
) -> dict[str, object]:
    if employment_type == "Self-Employed":
        purpose_weights = {
            "Business Support": 0.28,
            "Personal": 0.22,
            "Auto": 0.14,
            "Home Improvement": 0.14,
            "Consumer Durable": 0.12,
            "Education": 0.10,
        }
    elif age < 28:
        purpose_weights = {
            "Personal": 0.26,
            "Auto": 0.18,
            "Education": 0.20,
            "Consumer Durable": 0.16,
            "Home Improvement": 0.08,
            "Business Support": 0.12,
        }
    else:
        purpose_weights = {
            "Personal": 0.30,
            "Auto": 0.18,
            "Home Improvement": 0.17,
            "Education": 0.08,
            "Consumer Durable": 0.12,
            "Business Support": 0.15,
        }

    loan_purpose = _weighted_choice(rng, purpose_weights)

    tenure_choices = {
        "Personal": ([12, 24, 36, 48, 60], [0.16, 0.26, 0.30, 0.18, 0.10]),
        "Auto": ([24, 36, 48, 60, 72], [0.10, 0.28, 0.30, 0.24, 0.08]),
        "Home Improvement": ([12, 24, 36, 48, 60], [0.10, 0.20, 0.28, 0.24, 0.18]),
        "Education": ([24, 36, 48, 60, 72], [0.12, 0.22, 0.24, 0.24, 0.18]),
        "Consumer Durable": ([12, 24, 36], [0.34, 0.42, 0.24]),
        "Business Support": ([12, 24, 36, 48], [0.24, 0.34, 0.28, 0.14]),
    }
    tenure_months = int(_choice(rng, tenure_choices[loan_purpose][0], probs=tenure_choices[loan_purpose][1]))

    multiplier_ranges = {
        "Personal": (2.0, 8.5),
        "Auto": (4.0, 10.5),
        "Home Improvement": (3.0, 9.5),
        "Education": (2.5, 7.5),
        "Consumer Durable": (0.8, 2.8),
        "Business Support": (4.0, 13.0),
    }
    low_mult, high_mult = multiplier_ranges[loan_purpose]
    if credit_score >= 760:
        high_mult += 1.4
    elif credit_score < 650:
        high_mult -= 1.2

    loan_amount = float(np.clip(monthly_income * rng.uniform(low_mult, max(low_mult + 0.5, high_mult)), 50000, 4000000))

    secured_purposes = {"Auto": 0.72, "Home Improvement": 0.42, "Business Support": 0.32, "Personal": 0.10, "Education": 0.06, "Consumer Durable": 0.14}
    collateral_boost = 0.10 if residence_type == "Owned" else 0.0
    has_collateral = int(rng.random() < min(secured_purposes[loan_purpose] + collateral_boost, 0.82))
    collateral_value = 0.0
    if has_collateral:
        ltv_target = rng.uniform(0.50, 0.88 if credit_score >= 680 else 0.78)
        collateral_value = float(np.clip(loan_amount / ltv_target, loan_amount * 1.05, loan_amount * 2.4))

    obligations_ratio = rng.uniform(0.06, 0.32)
    if age >= 38:
        obligations_ratio += 0.03
    if residence_type == "Rented":
        obligations_ratio += 0.04
    existing_monthly_obligations = float(np.clip(monthly_income * obligations_ratio, 0, monthly_income * 0.62))

    annual_rate = float(np.clip(
        18.5
        - ((credit_score - 600) / 28)
        + {"Consumer Durable": 1.0, "Personal": 0.5, "Business Support": 0.6, "Education": -0.4, "Auto": -0.6, "Home Improvement": -0.3}[loan_purpose]
        - (0.8 if has_collateral else 0.0)
        + rng.normal(0, 0.6),
        8.5,
        24.0,
    ))

    return {
        "loan_purpose": loan_purpose,
        "tenure_months": tenure_months,
        "requested_loan_amount": round(loan_amount, 2),
        "has_collateral_flag": has_collateral,
        "collateral_value": round(collateral_value, 2),
        "existing_monthly_obligations": round(existing_monthly_obligations, 2),
        "annual_interest_rate": round(annual_rate, 2),
    }


def generate_synthetic_dataset(path: Path = DATA_PATH, n_rows: int = 800, seed: int = 42) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    rows = []
    rule_engine = RuleBasedDecisionEngine()

    for i in range(1, n_rows + 1):
        branch_id, employee_id = _assign_branch_and_employee(i)
        profile = _sample_profile(rng)
        credit = _sample_credit_behavior(
            rng,
            employment_type=str(profile["employment_type"]),
            years_in_current_job=float(profile["years_in_current_job"]),
            monthly_income=float(profile["monthly_income"]),
            existing_customer=int(profile["existing_customer"]),
        )
        loan = _sample_loan_terms(
            rng,
            age=int(profile["age"]),
            employment_type=str(profile["employment_type"]),
            monthly_income=float(profile["monthly_income"]),
            credit_score=int(credit["credit_score"]),
            residence_type=str(profile["residence_type"]),
        )

        app = CreditApplication(
            loan_id=format_entity_id("LN", i),
            applicant_id=format_entity_id("AP", i),
            employee_id=employee_id,
            branch_id=branch_id,
            applicant_name=f"Applicant {i}",
            age=int(profile["age"]),
            monthly_income=float(profile["monthly_income"]),
            employment_type=str(profile["employment_type"]),
            years_in_current_job=float(profile["years_in_current_job"]),
            existing_monthly_obligations=float(loan["existing_monthly_obligations"]),
            requested_loan_amount=float(loan["requested_loan_amount"]),
            loan_purpose=str(loan["loan_purpose"]),
            tenure_months=int(loan["tenure_months"]),
            annual_interest_rate=float(loan["annual_interest_rate"]),
            credit_score=int(credit["credit_score"]),
            prior_delinquency_count_24m=int(credit["prior_delinquency_count_24m"]),
            bounced_payments_12m=int(credit["bounced_payments_12m"]),
            existing_customer_flag=int(profile["existing_customer"]),
            kyc_complete_flag=int(profile["kyc_complete"]),
            has_collateral_flag=int(loan["has_collateral_flag"]),
            collateral_value=float(loan["collateral_value"]),
            residence_type=str(profile["residence_type"]),
            city_tier=str(profile["city_tier"]),
        )
        decision = rule_engine.evaluate(app)
        prob = decision.risk_probability

        defaulted_prob = np.clip(
            prob
            + max(0, 690 - app.credit_score) / 1400
            + app.prior_delinquency_count_24m * 0.035
            + app.bounced_payments_12m * 0.018
            - (0.04 if app.existing_customer_flag else 0)
            - (0.03 if app.has_collateral_flag else 0),
            0.01,
            0.75,
        )
        defaulted_flag = int(rng.random() < defaulted_prob)
        approval_outcome = int(decision.decision in {"Approve", "Approve with Conditions"})

        rows.append(
            {
                **app.to_dict(),
                "historical_engine": decision.engine_name,
                "historical_decision": decision.decision,
                "historical_risk_band": decision.risk_band,
                "historical_score": decision.score,
                "historical_risk_probability": decision.risk_probability,
                "historical_explanation": " | ".join(decision.top_negative_reasons[:2] + decision.top_positive_reasons[:2]),
                "defaulted_flag": defaulted_flag,
                "approval_outcome": approval_outcome,
            }
        )

    df = ensure_history_schema(pd.DataFrame(rows))
    df.to_csv(path, index=False)
    return df


def load_or_create_data(path: Path = DATA_PATH, n_rows: int = 800) -> pd.DataFrame:
    if path.exists():
        df = ensure_history_schema(pd.read_csv(path))
        df.to_csv(path, index=False)
        return df
    return generate_synthetic_dataset(path=path, n_rows=n_rows)


def build_application_from_row(row: pd.Series) -> CreditApplication:
    payload = row.to_dict()
    return CreditApplication(
        loan_id=str(payload.get("loan_id", "")),
        applicant_id=str(payload.get("applicant_id", "")),
        employee_id=str(payload.get("employee_id", "")),
        branch_id=str(payload.get("branch_id", "")),
        applicant_name=str(payload.get("applicant_name", "")),
        age=int(payload.get("age", 30)),
        monthly_income=float(payload.get("monthly_income", 0)),
        employment_type=str(payload.get("employment_type", "Salaried")),
        years_in_current_job=float(payload.get("years_in_current_job", 0)),
        existing_monthly_obligations=float(payload.get("existing_monthly_obligations", 0)),
        requested_loan_amount=float(payload.get("requested_loan_amount", 0)),
        loan_purpose=str(payload.get("loan_purpose", "Personal")),
        tenure_months=int(payload.get("tenure_months", 12)),
        annual_interest_rate=float(payload.get("annual_interest_rate", 14)),
        credit_score=int(payload.get("credit_score", 700)),
        prior_delinquency_count_24m=int(payload.get("prior_delinquency_count_24m", 0)),
        bounced_payments_12m=int(payload.get("bounced_payments_12m", 0)),
        existing_customer_flag=int(payload.get("existing_customer_flag", 0)),
        kyc_complete_flag=int(payload.get("kyc_complete_flag", 1)),
        has_collateral_flag=int(payload.get("has_collateral_flag", 0)),
        collateral_value=float(payload.get("collateral_value", 0)),
        residence_type=str(payload.get("residence_type", "Rented")),
        city_tier=str(payload.get("city_tier", "Tier 1")),
    )


def append_assessment_to_history(
    app: CreditApplication,
    output: EngineOutput,
    path: Path = DATA_PATH,
) -> pd.DataFrame:
    existing_df = load_or_create_data(path)
    row = {
        **app.to_dict(),
        "historical_engine": output.engine_name,
        "historical_decision": output.decision,
        "historical_risk_band": output.risk_band,
        "historical_score": output.score,
        "historical_risk_probability": output.risk_probability,
        "historical_explanation": " | ".join(output.top_negative_reasons[:2] + output.top_positive_reasons[:2]),
        "defaulted_flag": pd.NA,
        "approval_outcome": int(output.decision in {"Approve", "Approve with Conditions"}),
    }
    updated_df = ensure_history_schema(pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True))
    updated_df.to_csv(path, index=False)
    return updated_df
