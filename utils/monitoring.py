from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from scoring.ml_engine import MLDecisionEngine
from scoring.rule_engine import RuleBasedDecisionEngine
from utils.data_loader import build_application_from_row


def approval_mix(df: pd.DataFrame) -> dict[str, float]:
    total = max(len(df), 1)
    decisions = df["historical_decision"].value_counts(dropna=False)
    return {str(decision): round(float(count / total), 4) for decision, count in decisions.items()}


def calibration_table(df: pd.DataFrame, bins: int = 5) -> pd.DataFrame:
    required = {"historical_risk_probability", "defaulted_flag"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    labeled = df[list(required)].dropna().copy()
    if labeled.empty:
        return pd.DataFrame()

    labeled["risk_bin"] = pd.qcut(
        labeled["historical_risk_probability"].rank(method="first"),
        q=min(bins, len(labeled)),
        duplicates="drop",
    )
    table = (
        labeled.groupby("risk_bin", observed=True)
        .agg(
            applications=("defaulted_flag", "count"),
            avg_predicted_pd=("historical_risk_probability", "mean"),
            observed_default_rate=("defaulted_flag", "mean"),
        )
        .reset_index(drop=True)
    )
    return table


def auc_score(df: pd.DataFrame) -> float | None:
    if "historical_risk_probability" not in df.columns or "defaulted_flag" not in df.columns:
        return None
    labeled = df[["historical_risk_probability", "defaulted_flag"]].dropna()
    if labeled["defaulted_flag"].nunique() < 2:
        return None
    try:
        from sklearn.metrics import roc_auc_score

        return round(float(roc_auc_score(labeled["defaulted_flag"], labeled["historical_risk_probability"])), 4)
    except Exception:
        return None


def branch_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    grouped = (
        df.groupby("branch_id", as_index=False)
        .agg(
            applications=("loan_id", "count"),
            approval_rate=("approval_outcome", "mean"),
            avg_score=("historical_score", "mean"),
            avg_risk_probability=("historical_risk_probability", "mean"),
            observed_default_rate=("defaulted_flag", "mean"),
        )
    )
    grouped["risk_adjusted_approval"] = grouped["approval_rate"] * (1 - grouped["avg_risk_probability"].fillna(0))
    return grouped.sort_values(["risk_adjusted_approval", "applications"], ascending=[False, False])


def population_stability_index(
    expected: Iterable[float],
    actual: Iterable[float],
    bins: int = 10,
) -> float:
    expected_series = pd.Series(expected).dropna().astype(float)
    actual_series = pd.Series(actual).dropna().astype(float)
    if expected_series.empty or actual_series.empty:
        return 0.0
    quantiles = np.linspace(0, 1, bins + 1)
    breakpoints = np.unique(expected_series.quantile(quantiles).to_numpy())
    if len(breakpoints) < 3:
        return 0.0
    expected_counts = pd.cut(expected_series, breakpoints, include_lowest=True).value_counts(normalize=True)
    actual_counts = pd.cut(actual_series, breakpoints, include_lowest=True).value_counts(normalize=True)
    expected_pct = expected_counts.sort_index().replace(0, 0.0001)
    actual_pct = actual_counts.reindex(expected_pct.index, fill_value=0.0001).replace(0, 0.0001)
    psi = ((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)).sum()
    return round(float(psi), 4)


def drift_report(df: pd.DataFrame, reference_fraction: float = 0.5) -> dict[str, float]:
    if df.empty:
        return {}
    split = max(1, int(len(df) * reference_fraction))
    reference = df.iloc[:split]
    actual = df.iloc[split:] if split < len(df) else df.iloc[:split]
    features = ["monthly_income", "credit_score", "existing_monthly_obligations", "requested_loan_amount"]
    return {
        feature: population_stability_index(reference[feature], actual[feature])
        for feature in features
        if feature in df.columns
    }


def fairness_proxy_table(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or ["employment_type", "city_tier", "residence_type"]
    rows: list[dict[str, object]] = []
    for column in columns:
        if column not in df.columns:
            continue
        for segment, group in df.groupby(column, dropna=False):
            rows.append(
                {
                    "proxy_attribute": column,
                    "segment": str(segment),
                    "applications": len(group),
                    "approval_rate": float(group["approval_outcome"].mean()) if "approval_outcome" in group else np.nan,
                    "avg_risk_probability": float(group["historical_risk_probability"].mean()) if "historical_risk_probability" in group else np.nan,
                    "observed_default_rate": float(group["defaulted_flag"].mean()) if "defaulted_flag" in group else np.nan,
                }
            )
    return pd.DataFrame(rows)


def challenger_comparison(df: pd.DataFrame, limit: int = 50) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    rule_engine = RuleBasedDecisionEngine()
    ml_engine = MLDecisionEngine()
    ml_loaded = ml_engine.load()
    rows: list[dict[str, object]] = []
    for _, row in df.head(limit).iterrows():
        app = build_application_from_row(row)
        rule_output = rule_engine.evaluate(app)
        challenger = ml_engine.evaluate(app) if ml_loaded else rule_output
        rows.append(
            {
                "loan_id": app.loan_id,
                "applicant_id": app.applicant_id,
                "recorded_decision": row.get("historical_decision"),
                "rule_decision": rule_output.decision,
                "ml_decision": challenger.decision,
                "rule_score": rule_output.score,
                "ml_score": challenger.score,
                "rule_risk_probability": rule_output.risk_probability,
                "ml_risk_probability": challenger.risk_probability,
            }
        )
    return pd.DataFrame(rows)


def portfolio_report(df: pd.DataFrame) -> dict[str, object]:
    labeled = df[df["defaulted_flag"].notna()].copy() if "defaulted_flag" in df else df
    return {
        "applications": int(len(df)),
        "approval_mix": approval_mix(df),
        "auc": auc_score(labeled),
        "default_rate": round(float(labeled["defaulted_flag"].mean()), 4) if "defaulted_flag" in labeled and len(labeled) else None,
        "avg_risk_probability": round(float(df["historical_risk_probability"].mean()), 4) if "historical_risk_probability" in df else None,
        "drift_psi": drift_report(df),
        "branch_quality": branch_quality_table(df).to_dict(orient="records"),
        "calibration": calibration_table(df).to_dict(orient="records"),
        "fairness_proxy": fairness_proxy_table(df).to_dict(orient="records"),
    }
