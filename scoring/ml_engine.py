from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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


class MLDecisionEngine:
    name = "Machine Learning Decision Engine"

    def __init__(self, model_dir: str = "artifacts"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline_path = self.model_dir / "credit_pipeline.joblib"
        self.feature_columns = [
            "age", "monthly_income", "employment_type", "years_in_current_job",
            "existing_monthly_obligations", "requested_loan_amount", "loan_purpose",
            "tenure_months", "annual_interest_rate", "credit_score",
            "prior_delinquency_count_24m", "bounced_payments_12m",
            "existing_customer_flag", "kyc_complete_flag", "has_collateral_flag",
            "collateral_value", "residence_type", "city_tier",
            "emi", "foir", "loan_to_income", "ltv_filled",
        ]
        self.numeric_features = [
            "age", "monthly_income", "years_in_current_job", "existing_monthly_obligations",
            "requested_loan_amount", "tenure_months", "annual_interest_rate", "credit_score",
            "prior_delinquency_count_24m", "bounced_payments_12m", "existing_customer_flag",
            "kyc_complete_flag", "has_collateral_flag", "collateral_value", "emi", "foir",
            "loan_to_income", "ltv_filled",
        ]
        self.categorical_features = ["employment_type", "loan_purpose", "residence_type", "city_tier"]
        self.pipeline: Optional[Pipeline] = None
        self.fallback_reason = "No trained model loaded; using lightweight surrogate behaviour."

    def _prepare_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["emi"] = out.apply(lambda r: calculate_emi(r["requested_loan_amount"], r["annual_interest_rate"], int(r["tenure_months"])), axis=1)
        out["foir"] = (out["existing_monthly_obligations"] + out["emi"]) / out["monthly_income"].replace(0, np.nan)
        out["foir"] = out["foir"].fillna(0)
        out["loan_to_income"] = out["requested_loan_amount"] / (out["monthly_income"].replace(0, np.nan) * 12)
        out["loan_to_income"] = out["loan_to_income"].fillna(0)
        out["ltv_filled"] = np.where(
            (out["has_collateral_flag"] == 1) & (out["collateral_value"] > 0),
            out["requested_loan_amount"] / out["collateral_value"],
            1.2,
        )
        return out

    def train(self, historical_df: pd.DataFrame) -> Dict[str, float]:
        if "defaulted_flag" not in historical_df.columns:
            raise ValueError("Training data must contain defaulted_flag.")

        df = self._prepare_frame(historical_df)
        X = df[self.feature_columns]
        y = df["defaulted_flag"].astype(int)

        numeric_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, self.numeric_features),
            ("cat", categorical_transformer, self.categorical_features),
        ])

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=500, class_weight="balanced")),
        ])
        pipeline.fit(X, y)
        self.pipeline = pipeline
        joblib.dump(pipeline, self.pipeline_path)

        return {"rows_trained": float(len(df)), "bad_rate": float(y.mean())}

    def load(self) -> bool:
        if self.pipeline_path.exists():
            self.pipeline = joblib.load(self.pipeline_path)
            return True
        return False

    def _fallback_explanation(self, app: CreditApplication, risk_probability: float) -> List[Dict[str, float]]:
        signals = {
            "FOIR": min(1.0, ((app.existing_monthly_obligations + calculate_emi(app.requested_loan_amount, app.annual_interest_rate, app.tenure_months)) / max(app.monthly_income, 1)) / 0.7),
            "Credit score": 1 - min(1.0, max(app.credit_score - 550, 0) / 300),
            "Delinquencies": min(1.0, app.prior_delinquency_count_24m / 4),
            "Payment bounces": min(1.0, app.bounced_payments_12m / 5),
            "Employment stability": 1 - min(1.0, app.years_in_current_job / 6),
        }
        ordered = sorted(signals.items(), key=lambda x: x[1], reverse=True)
        return [{"feature": k, "relative_importance": round(v, 3)} for k, v in ordered]

    def evaluate(self, app: CreditApplication) -> EngineOutput:
        emi = calculate_emi(app.requested_loan_amount, app.annual_interest_rate, app.tenure_months)
        foir = safe_divide(app.existing_monthly_obligations + emi, app.monthly_income)
        ltv = compute_ltv(app.requested_loan_amount, app.has_collateral_flag, app.collateral_value)
        loan_to_income = safe_divide(app.requested_loan_amount, app.monthly_income * 12)

        if self.pipeline is None:
            self.load()

        row = pd.DataFrame([asdict(app)])
        enriched = self._prepare_frame(row)

        if self.pipeline is not None:
            prob = float(self.pipeline.predict_proba(enriched[self.feature_columns])[0, 1])
            model = self.pipeline.named_steps["model"]
            pre = self.pipeline.named_steps["preprocessor"]
            transformed = pre.transform(enriched[self.feature_columns])
            if hasattr(transformed, "toarray"):
                transformed = transformed.toarray()
            coefs = np.abs(model.coef_[0])
            feature_names = pre.get_feature_names_out()
            contribution_values = transformed[0] * model.coef_[0]
            order = np.argsort(np.abs(contribution_values))[::-1][:8]
            feature_importance = [
                {
                    "feature": str(feature_names[i]).replace("num__", "").replace("cat__", ""),
                    "relative_importance": round(float(coefs[i]), 4),
                    "signed_contribution": round(float(contribution_values[i]), 4),
                }
                for i in order
            ]
            factor_contributions = [
                FactorContribution(
                    factor=item["feature"],
                    impact_direction="Negative" if item["signed_contribution"] > 0 else "Positive",
                    points=round(abs(item["signed_contribution"]) * 8, 2),
                    description=(
                        f"{item['feature']} increased estimated risk."
                        if item["signed_contribution"] > 0
                        else f"{item['feature']} improved the model view of the application."
                    ),
                )
                for item in feature_importance
            ]
            notes = ["Prediction generated from logistic regression trained on historical portfolio data."]
        else:
            prob = clamp(
                0.05
                + (foir * 0.28)
                + max(0, (700 - app.credit_score) / 1000)
                + (app.prior_delinquency_count_24m * 0.04)
                + (app.bounced_payments_12m * 0.02)
                - (0.03 if app.existing_customer_flag else 0)
                - (0.04 if app.has_collateral_flag and ltv is not None and ltv < 0.75 else 0),
                0.03,
                0.65,
            )
            feature_importance = self._fallback_explanation(app, prob)
            factor_contributions = [
                FactorContribution(
                    factor=item["feature"],
                    impact_direction="Negative",
                    points=round(item["relative_importance"] * 10, 2),
                    description=f"{item['feature']} is one of the strongest drivers in the current risk estimate.",
                )
                for item in feature_importance
            ]
            notes = [self.fallback_reason]

        score = round(clamp((1 - prob) * 100, 1, 99), 1)
        risk_band = band_from_probability(prob)
        decision = decision_from_probability(prob, app.kyc_complete_flag)

        positives = [f.description for f in factor_contributions if f.impact_direction == "Positive"][:4]
        negatives = [f.description for f in factor_contributions if f.impact_direction == "Negative"][:4]

        return EngineOutput(
            engine_name=self.name,
            score=score,
            risk_probability=round(prob, 4),
            risk_band=risk_band,
            decision=decision,
            recommended_next_step=step_from_decision(decision),
            emi=round(emi, 2),
            foir=round(foir, 4),
            loan_to_income=round(loan_to_income, 4),
            ltv=round(ltv, 4) if ltv is not None else None,
            top_positive_reasons=positives,
            top_negative_reasons=negatives,
            factor_contributions=factor_contributions,
            feature_importance=feature_importance,
            confidence=round(max(prob, 1 - prob), 4),
            notes=notes,
        )
