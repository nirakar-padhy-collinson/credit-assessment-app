from __future__ import annotations

from pathlib import Path
from typing import Dict

import altair as alt
import pandas as pd
import streamlit as st

from assets.styles import CUSTOM_CSS
from models.contracts import CreditApplication, EngineOutput
from scoring.ml_engine import MLDecisionEngine
from scoring.rule_engine import RuleBasedDecisionEngine
from utils.data_loader import build_application_from_row, load_or_create_data, generate_synthetic_dataset

st.set_page_config(page_title="Credit Assessment Studio", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = Path("data/historical_loan_applications.csv")


@st.cache_data(show_spinner=False)
def get_data(path_str: str) -> pd.DataFrame:
    return load_or_create_data(Path(path_str))


@st.cache_resource(show_spinner=False)
def get_ml_engine(df: pd.DataFrame) -> MLDecisionEngine:
    engine = MLDecisionEngine(model_dir="artifacts")
    if not engine.load():
        engine.train(df)
    return engine


def get_engines(df: pd.DataFrame) -> Dict[str, object]:
    return {
        "Rule-Based Decision Engine": RuleBasedDecisionEngine(),
        "Machine Learning Decision Engine": get_ml_engine(df),
    }


def fmt_currency(value: float) -> str:
    return f"₹{value:,.0f}"


def short_decision_label(decision: str) -> str:
    return {
        "Approve": "Approve",
        "Approve with Conditions": "Approve w/ Conditions",
        "Manual Review": "Manual Review",
        "Decline": "Decline",
    }.get(decision, decision)


def decision_badge(decision: str) -> str:
    css = {
        "Approve": "badge-approve",
        "Approve with Conditions": "badge-conditional",
        "Manual Review": "badge-review",
        "Decline": "badge-decline",
    }.get(decision, "badge-review")
    return f'<span class="decision-badge {css}">{decision}</span>'


def risk_class(risk_band: str) -> str:
    mapping = {
        "Low Risk": "risk-low",
        "Moderate Risk": "risk-moderate",
        "Elevated Risk": "risk-elevated",
        "High Risk": "risk-high",
    }
    return mapping.get(risk_band, "risk-moderate")


def render_stat_card(label: str, value: str, description: str, tone: str = "", compact: bool = False):
    tone_class = f" {tone}" if tone else ""
    compact_class = " stat-card-compact" if compact else ""
    st.markdown(
        f"""
        <div class="stat-card{tone_class}{compact_class}">
            <div class="stat-card-label">{label}</div>
            <div class="stat-card-value">{value}</div>
            <div class="stat-card-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_gap():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)


def dataframe_height(row_count: int, *, max_rows_visible: int = 8) -> int:
    visible_rows = max(1, min(row_count, max_rows_visible))
    return 44 + (visible_rows * 42)


def render_result_explainer(output: EngineOutput):
    with st.expander("How to interpret this result", expanded=True):
        st.markdown(
            """
            - `Score`: Overall credit assessment score produced by the selected engine. Higher is generally better.
            - `Risk Probability`: Estimated likelihood that the application falls into a riskier repayment outcome. Lower is better.
            - `Risk Band`: Summary risk segment used to make the decision easier to interpret.
            - `Next Step`: Recommended underwriting action based on the current assessment.
            - `EMI`: Estimated Equated Monthly Instalment for the requested loan terms.
            - `FOIR`: Fixed Obligation to Income Ratio. It compares existing obligations plus the new EMI against monthly income. Lower usually indicates stronger repayment capacity.
            - `Loan / Income`: Requested loan amount divided by annualized income proxy. Higher values indicate more leverage.
            - `LTV`: Loan-to-Value ratio. It compares the requested loan against collateral value when collateral exists. Lower is typically safer.
            """
        )
        if output.engine_name == "Machine Learning Decision Engine":
            st.caption("Model Insight shows which features carried the most influence for this prediction.")
        else:
            st.caption("Rule Rationale shows the strongest policy-style checks that pushed the recommendation up or down.")


def render_driver_item(text: str, tone: str):
    st.markdown(
        f"""
        <div class="driver-item driver-{tone}">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    portfolio_health = "Portfolio-ready analytics"
    if "df" in st.session_state:
        df = st.session_state["df"]
        approval_rate = (df["historical_decision"].isin(["Approve", "Approve with Conditions"]).mean() * 100) if len(df) else 0
        avg_ticket = df["requested_loan_amount"].mean() if len(df) else 0
        portfolio_health = f"{approval_rate:.1f}% policy-fit approvals • Avg ticket {fmt_currency(avg_ticket)}"
    st.markdown(
        """
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <div class="hero-eyebrow">Credit Assessment Studio</div>
                    <h1>Premium underwriting intelligence for modern credit teams.</h1>
                    <p>Review applications, explain outcomes with confidence, and monitor portfolio quality through a single decisioning workspace designed for credit teams and business stakeholders.</p>
                </div>
                <div class="hero-panel">
                    <div class="hero-panel-label">Portfolio Snapshot</div>
                    <div class="hero-panel-value">Credit Assessment Studio</div>
                    <div class="hero-panel-copy">"""
        + portfolio_health
        + """</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_guide():
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Workspace Flow</div>
            <div class="workflow-grid">
                <div class="workflow-step">
                    <div class="workflow-step-number">01</div>
                    <div class="workflow-step-title">New Assessment</div>
                    <p>Capture borrower details and generate a recommendation with clear rationale.</p>
                </div>
                <div class="workflow-step">
                    <div class="workflow-step-number">02</div>
                    <div class="workflow-step-title">Case Review</div>
                    <p>Benchmark a live case against historical applications and stored outcomes.</p>
                </div>
                <div class="workflow-step">
                    <div class="workflow-step-number">03</div>
                    <div class="workflow-step-title">Portfolio Overview</div>
                    <p>Monitor approval mix, risk concentration, and lending patterns at a glance.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_section_gap()


def render_metric_cards(df: pd.DataFrame):
    total = len(df)
    approval_rate = (df["historical_decision"].isin(["Approve", "Approve with Conditions"]).mean() * 100) if total else 0
    review_rate = (df["historical_decision"].eq("Manual Review").mean() * 100) if total else 0
    decline_rate = (df["historical_decision"].eq("Decline").mean() * 100) if total else 0
    avg_loan = df["requested_loan_amount"].mean() if total else 0
    cards = [
        ("Total Applications", f"{total:,}", "Portfolio volume"),
        ("Approval Rate", f"{approval_rate:.1f}%", "Approve + conditional"),
        ("Manual Review Rate", f"{review_rate:.1f}%", "Requires underwriter"),
        ("Decline Rate", f"{decline_rate:.1f}%", "High initial risk"),
        ("Average Ticket", fmt_currency(avg_loan), "Ticket size"),
    ]
    cols = st.columns(5, gap="medium")
    for col, (label, value, sub) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>',
                unsafe_allow_html=True,
            )


def application_form(defaults: dict | None = None, form_key: str = "new") -> CreditApplication:
    defaults = defaults or {}
    with st.form(form_key):
        st.markdown(
            """
            <div class="form-intro">
                <div>
                    <div class="section-title">Borrower & Facility Inputs</div>
                    <p>Use the existing flow below. The fields stay familiar, with added guidance to make underwriting inputs easier to understand.</p>
                </div>
                <div class="form-chip">Decision-ready intake</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="form-section-label">Borrower Profile & Credit Inputs</div>', unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2, gap="medium")
        with r1c1:
            loan_id = st.text_input("Loan ID", value=str(defaults.get("loan_id", "LNNEW001")), help="Unique application reference.")
        with r1c2:
            annual_interest_rate = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=36.0, value=float(defaults.get("annual_interest_rate", 14.0)), step=0.1, format="%.1f", help="Indicative annual interest rate for the proposed facility.")

        r2c1, r2c2 = st.columns(2, gap="medium")
        with r2c1:
            applicant_id = st.text_input("Applicant ID", value=str(defaults.get("applicant_id", "APNEW001")), help="Customer reference used for search and tracking.")
        with r2c2:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=int(defaults.get("credit_score", 720)), help="Bureau-style credit score. Higher values typically indicate lower credit risk.")

        r3c1, r3c2 = st.columns(2, gap="medium")
        with r3c1:
            age = st.number_input("Age", min_value=18, max_value=75, value=int(defaults.get("age", 32)), help="Applicant age in years.")
        with r3c2:
            prior_delinquency_count_24m = st.number_input("Prior Delinquency Count (24m)", min_value=0, max_value=12, value=int(defaults.get("prior_delinquency_count_24m", 0)), help="Number of late-payment or delinquency events in the last 24 months.")

        r4c1, r4c2 = st.columns(2, gap="medium")
        with r4c1:
            employment_type = st.selectbox("Employment Type", ["Salaried", "Self-Employed", "Contract", "Professional"], index=["Salaried", "Self-Employed", "Contract", "Professional"].index(defaults.get("employment_type", "Salaried")), help="Primary income source category used in repayment capacity assessment.")
        with r4c2:
            bounced_payments_12m = st.number_input("Bounced Payments (12m)", min_value=0, max_value=12, value=int(defaults.get("bounced_payments_12m", 0)), help="Count of bounced or failed payments observed over the last 12 months.")

        r5c1, r5c2 = st.columns(2, gap="medium")
        with r5c1:
            years_in_current_job = st.number_input("Years in Current Job", min_value=0.0, max_value=40.0, value=float(defaults.get("years_in_current_job", 4.0)), step=0.5, format="%.1f", help="Length of time in the current employment or business arrangement.")
        with r5c2:
            existing_customer_flag = st.selectbox("Existing Customer", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No", index=0 if int(defaults.get("existing_customer_flag", 0)) == 1 else 1, help="Indicates whether the borrower already has a relationship with the institution.")

        r6c1, r6c2 = st.columns(2, gap="medium")
        with r6c1:
            tenure_months = st.selectbox("Tenure (Months)", [12, 24, 36, 48, 60, 72], index=[12, 24, 36, 48, 60, 72].index(int(defaults.get("tenure_months", 36))), help="Requested repayment period for the new facility.")
        with r6c2:
            kyc_complete_flag = st.selectbox("KYC Complete", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No", index=0 if int(defaults.get("kyc_complete_flag", 1)) == 1 else 1, help="Shows whether Know Your Customer verification is complete.")

        r7c1, r7c2 = st.columns(2, gap="medium")
        with r7c1:
            monthly_income = st.number_input("Monthly Income", min_value=0.0, value=float(defaults.get("monthly_income", 90000.0)), step=5000.0, format="%.0f", help="Net or documented monthly income used at first-stage underwriting.")
        with r7c2:
            has_collateral_flag = st.selectbox("Collateral Available", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No", index=1 if int(defaults.get("has_collateral_flag", 0)) == 1 else 0, help="Indicates whether the facility is backed by any pledged collateral.")

        r8c1, r8c2 = st.columns(2, gap="medium")
        with r8c1:
            existing_monthly_obligations = st.number_input("Existing Monthly Obligations", min_value=0.0, value=float(defaults.get("existing_monthly_obligations", 18000.0)), step=1000.0, format="%.0f", help="Current monthly commitments such as existing EMIs, rent, or other fixed repayment obligations.")
        with r8c2:
            collateral_value = st.number_input("Collateral Value", min_value=0.0, value=float(defaults.get("collateral_value", 0.0)), step=10000.0, format="%.0f", help="Only relevant for secured applications.")

        r9c1, r9c2 = st.columns(2, gap="medium")
        with r9c1:
            loan_purpose = st.selectbox("Loan Purpose", ["Personal", "Auto", "Home Improvement", "Education", "Consumer Durable", "Business Support"], index=["Personal", "Auto", "Home Improvement", "Education", "Consumer Durable", "Business Support"].index(defaults.get("loan_purpose", "Personal")), help="Intended use of the facility.")
        with r9c2:
            residence_type = st.selectbox("Residence Type", ["Owned", "Rented", "Family"], index=["Owned", "Rented", "Family"].index(defaults.get("residence_type", "Rented")), help="Residential stability indicator based on living arrangement.")

        r10c1, r10c2 = st.columns(2, gap="medium")
        with r10c1:
            requested_loan_amount = st.number_input("Requested Loan Amount", min_value=10000.0, value=float(defaults.get("requested_loan_amount", 500000.0)), step=10000.0, format="%.0f", help="Principal amount being requested.")
        with r10c2:
            city_tier = st.selectbox("City Tier", ["Tier 1", "Tier 2", "Tier 3"], index=["Tier 1", "Tier 2", "Tier 3"].index(defaults.get("city_tier", "Tier 1")), help="Optional context variable, used carefully and not as a protected proxy.")

        submitted = st.form_submit_button("Run Credit Assessment", use_container_width=True)

    app = CreditApplication(
        loan_id=loan_id,
        applicant_id=applicant_id,
        applicant_name=str(defaults.get("applicant_name", "")),
        age=int(age),
        monthly_income=float(monthly_income),
        employment_type=employment_type,
        years_in_current_job=float(years_in_current_job),
        existing_monthly_obligations=float(existing_monthly_obligations),
        requested_loan_amount=float(requested_loan_amount),
        loan_purpose=loan_purpose,
        tenure_months=int(tenure_months),
        annual_interest_rate=float(annual_interest_rate),
        credit_score=int(credit_score),
        prior_delinquency_count_24m=int(prior_delinquency_count_24m),
        bounced_payments_12m=int(bounced_payments_12m),
        existing_customer_flag=int(existing_customer_flag),
        kyc_complete_flag=int(kyc_complete_flag),
        has_collateral_flag=int(has_collateral_flag),
        collateral_value=float(collateral_value),
        residence_type=residence_type,
        city_tier=city_tier,
    )
    return app, submitted


def render_engine_output(output: EngineOutput):
    is_ml_output = output.engine_name == "Machine Learning Decision Engine"

    st.markdown('<div class="section-title">Assessment Summary</div>', unsafe_allow_html=True)
    st.markdown(f"### Decision Outcome")
    st.markdown(decision_badge(output.decision), unsafe_allow_html=True)
    st.markdown(f"<div class='small-note' style='margin-top:0.7rem;'>Engine: {output.engine_name}</div>", unsafe_allow_html=True)
    m1, m2 = st.columns(2, gap="medium")
    with m1:
        render_stat_card("Score", f"{output.score:.1f}", "Overall credit assessment score from the selected engine.")
    with m2:
        render_stat_card("Risk Probability", f"{output.risk_probability:.1%}", "Estimated likelihood that the case falls into a riskier repayment outcome.")
    m3, m4 = st.columns(2, gap="medium")
    with m3:
        render_stat_card("Risk Band", output.risk_band, "Summary risk segment used to simplify interpretation.", tone=risk_class(output.risk_band))
    with m4:
        render_stat_card("Next Step", output.recommended_next_step, "Recommended underwriting action based on the current result.")

    render_section_gap()
    st.markdown("### Underwriting Metrics")
    a, b = st.columns(2, gap="medium")
    with a:
        render_stat_card("EMI", fmt_currency(output.emi), "Estimated monthly installment.", compact=True)
    with b:
        render_stat_card("FOIR", f"{output.foir:.1%}", "Obligations as a share of income.", compact=True)
    c, d = st.columns(2, gap="medium")
    with c:
        render_stat_card("Loan / Income", f"{output.loan_to_income:.2f}x", "Requested leverage versus income.", compact=True)
    with d:
        render_stat_card("LTV", f"{output.ltv:.1%}" if output.ltv is not None else "N/A", "Collateral coverage ratio.", compact=True)

    render_section_gap()
    st.markdown("### Decision Drivers")
    st.caption("Supportive factors improve the case; adverse factors increase caution or may trigger a review or decline.")
    if output.top_positive_reasons:
        st.markdown("**Supportive factors**")
        for item in output.top_positive_reasons:
            render_driver_item(item, "supportive")
    if output.top_negative_reasons:
        st.markdown("**Adverse factors**")
        for item in output.top_negative_reasons:
            render_driver_item(item, "adverse")
    if output.notes:
        for note in output.notes:
            st.caption(note)

    render_section_gap()
    render_result_explainer(output)

    render_section_gap()
    st.markdown("### Factor Contributions")
    contrib_df = pd.DataFrame([
        {"Factor": c.factor, "Direction": c.impact_direction, "Points": c.points, "Description": c.description}
        for c in output.factor_contributions
    ])
    st.dataframe(
        contrib_df,
        use_container_width=True,
        hide_index=True,
        height=dataframe_height(len(contrib_df)),
        column_config={
            "Factor": st.column_config.TextColumn(width="medium"),
            "Direction": st.column_config.TextColumn(width="small"),
            "Points": st.column_config.NumberColumn(width="small", format="%.0f"),
            "Description": st.column_config.TextColumn(width="large"),
        },
    )

    render_section_gap()
    if is_ml_output:
        st.markdown("### Model Insight")
        feat_df = pd.DataFrame(output.feature_importance)
        if not feat_df.empty:
            feat_df["feature"] = feat_df["feature"].astype(str)
            metric_col = "relative_importance" if "relative_importance" in feat_df.columns else feat_df.columns[1]
            chart = alt.Chart(feat_df.head(10)).mark_bar(cornerRadiusTopLeft=6, cornerRadiusBottomLeft=6).encode(
                x=alt.X(f"{metric_col}:Q", title="Relative Importance"),
                y=alt.Y("feature:N", sort='-x', title="Feature"),
                tooltip=list(feat_df.columns),
            ).properties(height=320)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Model insight is not available for this prediction.")
    else:
        st.markdown("### Rule Rationale")
        rationale_df = pd.DataFrame([
            {
                "Rule Area": c.factor,
                "Assessment": c.description,
                "Impact": "Supportive" if c.impact_direction == "Positive" else "Adverse",
                "Points": c.points,
            }
            for c in output.factor_contributions[:8]
        ])
        st.caption("This view shows the strongest policy-style rules that influenced the recommendation.")
        st.dataframe(
            rationale_df,
            use_container_width=True,
            hide_index=True,
            height=dataframe_height(len(rationale_df)),
            column_config={
                "Rule Area": st.column_config.TextColumn(width="medium"),
                "Assessment": st.column_config.TextColumn(width="large"),
                "Impact": st.column_config.TextColumn(width="small"),
                "Points": st.column_config.NumberColumn(width="small", format="%.0f"),
            },
        )


def new_application_tab(df: pd.DataFrame, engines: Dict[str, object], selected_engine: str):
    st.markdown('<div class="section-title">New Assessment</div>', unsafe_allow_html=True)
    st.caption("Enter the applicant and facility details below to generate a credit recommendation and supporting rationale.")
    st.markdown(f'<div class="section-banner">Active engine: <strong>{selected_engine}</strong></div>', unsafe_allow_html=True)
    app, submitted = application_form(form_key="new_application_form")
    if submitted:
        output = engines[selected_engine].evaluate(app)
        render_engine_output(output)


def historical_applications_tab(df: pd.DataFrame, engines: Dict[str, object], selected_engine: str):
    st.markdown('<div class="section-title">Case Review</div>', unsafe_allow_html=True)
    st.caption("Search the existing application history to compare a prior decision with the current engine output.")
    st.markdown(f'<div class="section-banner">Comparison engine: <strong>{selected_engine}</strong></div>', unsafe_allow_html=True)

    search_term = st.text_input(
        "Search by Applicant ID or Loan ID",
        value="",
        placeholder="Example: AP00012 or LN00012",
        help="Search across the currently loaded application history.",
    )

    with st.expander("Application history source", expanded=False):
        st.write(
            "The workspace starts with the built-in application history stored with the app. "
            "If an authorized user needs to review a different portfolio extract for the current session, "
            "they can upload a replacement CSV here."
        )
        uploaded = st.file_uploader("Replace session history with CSV", type=["csv"], help="Optional. This only affects the current session.")

    working_df = df.copy()
    if uploaded is not None:
        working_df = pd.read_csv(uploaded)
        st.success("Application history updated for this session.")

    if search_term:
        filtered = working_df[
            working_df["applicant_id"].astype(str).str.contains(search_term, case=False, na=False)
            | working_df["loan_id"].astype(str).str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered = working_df.head(30)

    selected_row = None
    if not filtered.empty:
        option_map = {f"{row.loan_id} | {row.applicant_id}": idx for idx, row in filtered.iterrows()}
        selected_key = st.selectbox("Select application", list(option_map.keys()))
        selected_row = working_df.loc[option_map[selected_key]]
    else:
        st.warning("No matching applications were found in the current history.")

    if selected_row is not None:
        app = build_application_from_row(selected_row)
        historical = {
            "Decision": selected_row.get("historical_decision", "N/A"),
            "Risk Band": selected_row.get("historical_risk_band", "N/A"),
            "Score": selected_row.get("historical_score", "N/A"),
            "Risk Probability": selected_row.get("historical_risk_probability", "N/A"),
            "Explanation": selected_row.get("historical_explanation", "N/A"),
        }
        current_output = engines[selected_engine].evaluate(app)

        st.markdown("### Recorded Decision vs Current Result")
        st.caption("This compares the decision stored in the application history with the result produced by the currently selected engine.")
        compare_df = pd.DataFrame([
            ["Decision", historical["Decision"], current_output.decision],
            ["Risk Band", historical["Risk Band"], current_output.risk_band],
            ["Score", historical["Score"], current_output.score],
            ["Risk Probability", historical["Risk Probability"], current_output.risk_probability],
            ["Explanation", historical["Explanation"], " | ".join(current_output.top_negative_reasons[:2] + current_output.top_positive_reasons[:2])],
        ], columns=["Measure", "Recorded History", "Current Engine Result"])
        st.dataframe(compare_df, hide_index=True, use_container_width=True, height=dataframe_height(len(compare_df), max_rows_visible=8))

        render_section_gap()
        st.markdown("### Original Application Details")
        display_fields = pd.DataFrame({"Field": list(app.to_dict().keys()), "Value": list(app.to_dict().values())})
        st.dataframe(display_fields, hide_index=True, use_container_width=True, height=dataframe_height(len(display_fields), max_rows_visible=10))

        render_section_gap()
        render_engine_output(current_output)


def portfolio_overview_tab(df: pd.DataFrame):
    st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)
    st.caption("Filter the live application history to understand decision quality, mix, and concentration across the portfolio.")
    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        loan_types = st.multiselect("Loan Type", sorted(df["loan_purpose"].dropna().unique()), default=[])
    with f2:
        decisions = st.multiselect("Decision", sorted(df["historical_decision"].dropna().unique()), default=[])
    with f3:
        risk_bands = st.multiselect("Risk Band", sorted(df["historical_risk_band"].dropna().unique()), default=[])

    f4, f5 = st.columns(2, gap="medium")
    with f4:
        emp_types = st.multiselect("Employment Type", sorted(df["employment_type"].dropna().unique()), default=[])
    with f5:
        existing_customer = st.multiselect("Existing Customer", [0, 1], default=[], format_func=lambda x: "Yes" if x == 1 else "No")

    filtered = df.copy()
    if loan_types:
        filtered = filtered[filtered["loan_purpose"].isin(loan_types)]
    if decisions:
        filtered = filtered[filtered["historical_decision"].isin(decisions)]
    if risk_bands:
        filtered = filtered[filtered["historical_risk_band"].isin(risk_bands)]
    if emp_types:
        filtered = filtered[filtered["employment_type"].isin(emp_types)]
    if existing_customer:
        filtered = filtered[filtered["existing_customer_flag"].isin(existing_customer)]

    render_metric_cards(filtered)
    render_section_gap()

    left, right = st.columns(2, gap="large")
    with left:
        risk_dist = filtered["historical_risk_band"].value_counts().reset_index()
        risk_dist.columns = ["risk_band", "count"]
        chart = alt.Chart(risk_dist).mark_arc(innerRadius=65).encode(theta="count:Q", color="risk_band:N", tooltip=["risk_band", "count"]).properties(height=320)
        st.markdown("### Risk Band Distribution")
        st.altair_chart(chart, use_container_width=True)
    with right:
        st.markdown("### Score Distribution")
        hist = alt.Chart(filtered).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            alt.X("historical_score:Q", bin=alt.Bin(maxbins=20), title="Historical Score"),
            alt.Y("count():Q", title="Applications"),
            tooltip=[alt.Tooltip("count():Q", title="Applications")],
        ).properties(height=320)
        st.altair_chart(hist, use_container_width=True)

    render_section_gap()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### Decision Mix")
        decision_dist = filtered["historical_decision"].value_counts().reset_index()
        decision_dist.columns = ["decision", "count"]
        decision_dist["decision_label"] = decision_dist["decision"].map(short_decision_label)
        st.altair_chart(
            alt.Chart(decision_dist).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6).encode(
                x=alt.X("count:Q", title="Applications"),
                y=alt.Y("decision_label:N", sort='-x', title=None, axis=alt.Axis(labelLimit=220)),
                tooltip=[
                    alt.Tooltip("decision:N", title="Decision"),
                    alt.Tooltip("count:Q", title="Applications", format=","),
                ],
            ).properties(height=260),
            use_container_width=True,
        )
    with c2:
        st.markdown("### Average Requested Loan by Purpose")
        avg_ticket = filtered.groupby("loan_purpose", as_index=False)["requested_loan_amount"].mean()
        st.altair_chart(
            alt.Chart(avg_ticket).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6).encode(
                x=alt.X("requested_loan_amount:Q", title="Average Loan Amount"),
                y=alt.Y("loan_purpose:N", sort="-x", title=None, axis=alt.Axis(labelLimit=240)),
                tooltip=[
                    alt.Tooltip("loan_purpose:N", title="Loan Purpose"),
                    alt.Tooltip("requested_loan_amount:Q", title="Average Loan Amount", format=",.0f"),
                ],
            ).properties(height=260),
            use_container_width=True,
        )

    render_section_gap()
    st.markdown("### Portfolio Table")
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=420)


def sidebar_controls(df: pd.DataFrame):
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-eyebrow">Credit Platform</div>
            <div class="sidebar-brand-title">Credit Assessment Studio</div>
            <div class="sidebar-brand-copy">A premium decisioning workspace for underwriting walkthroughs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("## Decision Settings")
    st.sidebar.caption("Choose which decisioning engine should be used throughout the workspace.")
    selected_engine = st.sidebar.radio("Decision engine", ["Rule-Based Decision Engine", "Machine Learning Decision Engine"])
    st.sidebar.caption("The selected engine is used in New Assessment and Case Review.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Portfolio Data")
    if st.sidebar.button("Refresh sample portfolio", use_container_width=True, help="Rebuild the bundled sample application history used by the workspace."):
        generate_synthetic_dataset(DATA_FILE, n_rows=800, seed=42)
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    st.sidebar.download_button(
        label="Download current application history",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="application_history.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This workspace supports three jobs: run a new decision, review an existing case, and monitor portfolio trends.\n\n"
        "All assessments intentionally exclude protected attributes from the underwriting inputs."
    )
    return selected_engine


def main():
    df = get_data(str(DATA_FILE))
    st.session_state["df"] = df
    render_header()
    selected_engine = sidebar_controls(df)
    engines = get_engines(df)
    render_workflow_guide()

    tabs = st.tabs(["New Assessment", "Case Review", "Portfolio Overview"])
    with tabs[0]:
        new_application_tab(df, engines, selected_engine)
    with tabs[1]:
        historical_applications_tab(df, engines, selected_engine)
    with tabs[2]:
        portfolio_overview_tab(df)


if __name__ == "__main__":
    main()
