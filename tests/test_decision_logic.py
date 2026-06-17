from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from models.contracts import CreditApplication
from scoring.ml_engine import MLDecisionEngine
from scoring.rule_engine import RuleBasedDecisionEngine
from utils.data_loader import generate_synthetic_dataset, validate_history_schema
from utils.monitoring import portfolio_report


def strong_application(**overrides) -> CreditApplication:
    payload = {
        "loan_id": "LNTEST",
        "applicant_id": "APTEST",
        "monthly_income": 250000.0,
        "existing_monthly_obligations": 10000.0,
        "requested_loan_amount": 300000.0,
        "tenure_months": 36,
        "annual_interest_rate": 10.0,
        "credit_score": 820,
        "prior_delinquency_count_24m": 0,
        "bounced_payments_12m": 0,
        "existing_customer_flag": 1,
        "kyc_complete_flag": 1,
        "has_collateral_flag": 1,
        "collateral_value": 900000.0,
        "years_in_current_job": 8.0,
        "employment_type": "Salaried",
        "residence_type": "Owned",
    }
    payload.update(overrides)
    return CreditApplication(**payload)


class CreditDecisionLogicTests(unittest.TestCase):
    def test_rule_engine_declines_zero_income(self):
        output = RuleBasedDecisionEngine().evaluate(
            strong_application(monthly_income=0.0, requested_loan_amount=500000.0)
        )

        self.assertEqual(output.decision, "Decline")
        self.assertEqual(output.risk_band, "High Risk")
        self.assertTrue(any(c.factor == "Income validation" for c in output.factor_contributions))
        self.assertTrue(any(c.reason_code == "INCOME_MISSING_OR_ZERO" for c in output.factor_contributions))
        self.assertEqual(output.fulfillment_status, "Not eligible for fulfillment")

    def test_rule_engine_incomplete_kyc_blocks_clean_final_approval(self):
        output = RuleBasedDecisionEngine().evaluate(strong_application(kyc_complete_flag=0))

        self.assertEqual(output.decision, "Approve with Conditions")
        self.assertNotEqual(output.decision, "Approve")
        self.assertEqual(output.documentation_status, "KYC remediation required before disbursal")
        self.assertEqual(output.fulfillment_status, "Documentation hold")

    def test_rule_engine_incomplete_kyc_does_not_rescue_bad_credit(self):
        output = RuleBasedDecisionEngine().evaluate(
            strong_application(
                kyc_complete_flag=0,
                credit_score=560,
                prior_delinquency_count_24m=5,
                bounced_payments_12m=6,
            )
        )

        self.assertIn(output.decision, {"Manual Review", "Decline"})
        self.assertNotEqual(output.decision, "Approve with Conditions")

    def test_ml_fallback_declines_zero_income(self):
        with tempfile.TemporaryDirectory() as model_dir:
            output = MLDecisionEngine(model_dir=model_dir).evaluate(
                strong_application(monthly_income=0.0, requested_loan_amount=500000.0)
            )

        self.assertEqual(output.decision, "Decline")
        self.assertTrue(any(c.factor == "Income validation" for c in output.factor_contributions))

    def test_rule_engine_uses_calibrated_probability_anchors(self):
        output = RuleBasedDecisionEngine().evaluate(strong_application())

        self.assertLessEqual(output.risk_probability, 0.08)
        self.assertGreaterEqual(output.risk_probability, 0.03)

    def test_generated_dataset_matches_demo_schema_and_contains_golden_cases(self):
        with tempfile.TemporaryDirectory() as data_dir:
            df = generate_synthetic_dataset(Path(data_dir) / "history.csv", n_rows=220, seed=7)

        self.assertEqual(validate_history_schema(df), [])
        self.assertFalse(df["applicant_name"].str.contains("Applicant ").any())
        self.assertFalse(df["applicant_name"].str.contains("Golden -").any())
        self.assertGreater((df["credit_score"] < 620).mean(), 0.02)
        self.assertGreater(df["monthly_income"].quantile(0.95), df["monthly_income"].quantile(0.50) * 1.35)
        self.assertTrue((df["requested_loan_amount"] % 5000 == 0).all())

    def test_portfolio_report_contains_model_risk_evidence(self):
        with tempfile.TemporaryDirectory() as data_dir:
            df = generate_synthetic_dataset(Path(data_dir) / "history.csv", n_rows=40, seed=11)

        report = portfolio_report(df)

        self.assertIn("approval_mix", report)
        self.assertIn("calibration", report)
        self.assertIn("fairness_proxy", report)
        self.assertGreater(report["applications"], 0)


if __name__ == "__main__":
    unittest.main()
