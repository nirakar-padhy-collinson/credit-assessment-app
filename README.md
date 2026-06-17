# credit-assessment-app

This is a Streamlit-based credit decisioning application that evaluates loan applications using both a rule-based underwriting engine and a machine learning model. The primary interface supports new assessments and portfolio monitoring through a production-style workspace designed to explain decisions.

The historical case review workspace is preserved in the codebase for future governance, audit, explainability, and model/rule comparison workflows, but is hidden from the primary UI to keep the user experience focused.

The workspace now includes a suite command landing, guided scenario library, structured banker brief, governance badges, decision packet export, champion/challenger comparison, what-if simulation, policy override notes, similar-case comparison, model health indicators, and banker task queues.

The bundled sample portfolio is synthetic but domain-calibrated: applicant profiles, income, bureau quality, obligations, FOIR, collateral, policy outcomes, and observed defaults are generated with banking-style relationships rather than arbitrary random values.

For the presenter talk track, use [DEMO_SCRIPT.md](DEMO_SCRIPT.md).
