from __future__ import annotations

from typing import List

from scoring.rule_engine_config import load_rule_engine_config
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

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self.config = load_rule_engine_config(config_path)

    @staticmethod
    def _matches_when(app: CreditApplication, rule: dict) -> bool:
        when = rule.get("when")
        if not when:
            return True
        field_name = when.get("app_field") or rule.get("metric_key")
        return getattr(app, field_name) == when.get("equals")

    @staticmethod
    def _select_band(value: float | None, bands: list[dict]) -> dict | None:
        if value is None:
            return None

        # First matching band wins, so config order defines policy precedence.
        for band in bands:
            min_threshold = band.get("min")
            max_threshold = band.get("max")
            min_ok = min_threshold is None or value >= float(min_threshold)
            max_ok = max_threshold is None or value <= float(max_threshold)
            if min_ok and max_ok:
                return band
        return None

    @staticmethod
    def _build_context(app: CreditApplication, metrics: dict) -> dict:
        context = app.to_dict()
        context.update(metrics)
        context["foir_pct"] = f"{metrics['foir']:.0%}"
        context["ltv_pct"] = f"{metrics['ltv']:.0%}" if metrics["ltv"] is not None else "N/A"
        return context

    def _apply_rule(self, app: CreditApplication, rule: dict, context: dict, add) -> None:
        if not self._matches_when(app, rule):
            return

        factor = rule["factor"]
        metric_key = rule["metric_key"]
        metric_value = context.get(metric_key)

        if "when_true" in rule and "when_false" in rule:
            outcome = rule["when_true"] if bool(metric_value) else rule["when_false"]
            add(factor, outcome["points"], outcome["description"].format(**context))
            return

        if "points" in rule and "description" in rule:
            add(factor, rule["points"], rule["description"].format(**context))
            return

        # Rationale text stays in config so policy owners can tune thresholds and explanations together.
        band = self._select_band(metric_value, rule.get("bands", []))
        if band:
            add(factor, band["points"], band["description"].format(**context))

    def evaluate(self, app: CreditApplication) -> EngineOutput:
        emi = calculate_emi(app.requested_loan_amount, app.annual_interest_rate, app.tenure_months)
        foir = safe_divide(app.existing_monthly_obligations + emi, app.monthly_income)
        ltv = compute_ltv(app.requested_loan_amount, app.has_collateral_flag, app.collateral_value)
        loan_to_income = safe_divide(app.requested_loan_amount, app.monthly_income * 12)

        metrics = {
            "foir": foir,
            "ltv": ltv,
            "loan_to_income": loan_to_income,
        }
        context = self._build_context(app, metrics)
        score = float(self.config["base_score"])
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

        for rule in self.config["rules"].values():
            self._apply_rule(app, rule, context, add)

        score_bounds = self.config["score_bounds"]
        score = clamp(score, float(score_bounds["min"]), float(score_bounds["max"]))
        risk_cfg = self.config["risk_probability"]
        risk_probability = clamp(
            ((100 - score) / 100) * float(risk_cfg["score_to_probability_multiplier"]),
            float(risk_cfg["min"]),
            float(risk_cfg["max"]),
        )
        risk_band = band_from_probability(risk_probability, self.config["risk_bands"])
        decision = decision_from_probability(risk_probability, app.kyc_complete_flag, self.config["decision_policy"])
        next_step = step_from_decision(decision, self.config["next_steps"])

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
            notes=["Rule weights and thresholds are loaded from scoring/rule_engine_config.json."],
        )
