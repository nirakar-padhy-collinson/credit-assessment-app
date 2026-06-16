# Credit Assessment Demo Script

## One-Line Positioning

An explainable AI/ML credit decisioning workspace that helps bankers assess applications, understand risk drivers, simulate policy changes, and monitor the underwriting portfolio.

## Summary Pointers

- Problem statement: Credit teams need faster underwriting without sacrificing policy control, explainability, or audit readiness.
- Current reality: Many lenders still rely on manual checks, spreadsheet scorecards, fragmented bureau data, and inconsistent underwriter notes.
- Business impact: Slow decisions increase customer drop-off, inconsistent approvals increase risk, and weak explanations create compliance pressure.
- Platform promise: Combine policy rules, ML risk scoring, reason codes, what-if simulation, and portfolio queues in one banker-friendly workspace.
- Buyer relevance: Small banks and fintechs can show modern digital underwriting while preserving human oversight and policy transparency.

## Personas To Mention

- Credit officer: Wants consistent decisions and fewer manual calculations.
- Underwriter: Wants clear risk drivers, next steps, and evidence for exceptions.
- Risk leader: Wants portfolio monitoring, model health, and policy pressure indicators.
- Compliance team: Wants explainability, audit packets, and governance controls.
- Business head: Wants faster turnaround time and scalable growth without hidden risk.

## Banking Domain Signals To Highlight

- Affordability: Call out FOIR, EMI, monthly income, existing obligations, and loan-to-income as repayment-capacity checks, not just numeric fields.
- Credit conduct: Refer to credit score, prior delinquencies, bounced payments, and risk probability as behavior and bureau signals.
- Policy fit: Point to KYC, collateral, LTV, employment stability, residence type, loan purpose, and conditional approval logic.
- Risk operations: Use terms like manual review queue, exception handling, underwriter workload, policy pressure, and branch-level portfolio monitoring.
- Governance: Highlight reason codes, banker notes, decision packet export, champion/challenger comparison, and model health as model-risk-management controls.
- Responsible AI: Mention that underwriting should avoid protected attributes and should keep explainability available for adverse or conditional outcomes.

## Banker Language To Use

- "This is testing repayment capacity, not just scoring an applicant."
- "The decision is aligned to credit policy and risk appetite."
- "Manual review is not a failure; it is a controlled escalation path."
- "The packet gives risk, operations, and compliance the same evidence trail."

## Opening Talk Track

"In credit underwriting, the challenge is not only predicting risk. The challenge is making a decision that is fast, consistent, explainable, and acceptable to policy and compliance. This workspace shows how a bank can combine rules, ML, and banker judgment in one production-style flow."

## Step-By-Step Walkthrough

1. Open the app and start on `Suite Command`.
   - Say: "This is the command landing for the credit decisioning function."
   - Point out model and policy health, data quality, average PD, and banker task queues.
   - Value point: Leadership gets a live operating view, not just a single application screen.
   - Domain cue: "This is how a credit head would monitor portfolio risk, policy pressure, and underwriter workload in one place."

2. Explain the decision engine selector in the sidebar.
   - Say: "The bank can run a rule-based decision engine or an ML decision engine."
   - Value point: This supports champion/challenger testing and gives risk teams a controlled migration path from rules to AI/ML.

3. Show `Champion vs Challenger`.
   - Say: "This lets the bank compare current policy logic against the ML challenger before changing production behavior."
   - Value point: Banks can test model lift and decision differences before approving a rollout.

4. Open `What-if Simulator`.
   - Change one or two risk inputs such as credit score, income, obligations, or loan amount.
   - Say: "Underwriters can test how policy and affordability changes affect the decision before finalizing a case."
   - Value point: This creates a powerful explainability moment for bankers and risk teams.
   - Domain cue: "Use this to show repayment capacity sensitivity, such as how higher obligations or a larger ticket changes FOIR and risk posture."

5. Move to `New Assessment`.
   - Pick a scenario from the scenario library, such as strong approval, KYC hold, affordability review, or conduct decline.
   - Say: "The scenario library lets us quickly demonstrate clean approvals, conditional approvals, manual review, and decline behavior."

6. Run an assessment.
   - Point out the decision, score, risk probability, risk band, FOIR, EMI, and next step.
   - Say: "The output is not just a score. It translates risk into an operational underwriting action."
   - Domain cue: "Mention that FOIR, EMI, bureau behavior, KYC, and collateral signals are the kind of evidence credit teams expect to see."

7. Show the AI banker brief.
   - Say: "This summarizes the decision in language an underwriter or branch banker can use."
   - Value point: It reduces interpretation effort and makes the decision easier to communicate internally.

8. Show governance and reason codes.
   - Point out KYC, affordability, collateral, conduct, and confidence-related signals.
   - Say: "Every decision is supported by clear positive and adverse drivers."
   - Value point: This is where compliance and risk teams see control.
   - Domain cue: "This is useful for explaining approvals with conditions, manual review referrals, or adverse outcomes without relying on a black-box score."

9. Show `Download Decision Packet`.
   - Say: "The decision packet creates portable evidence for audit, escalation, or case documentation."
   - Value point: This makes the demo feel operational, not just analytical.

10. Open `Policy Override / Banker Notes`.
    - Say: "Human judgment is preserved. Bankers can add rationale for exception handling or escalation."
    - Value point: The system supports governed human-in-the-loop decisions.

11. Move to `Portfolio Overview`.
    - Use filters such as branch, loan purpose, decision, risk band, or employment type.
    - Say: "Risk managers can move from one case to portfolio-level monitoring."

12. Show portfolio command center and task queues.
    - Point out manual review pressure, high-risk share, average PD, and banker queues.
    - Say: "This helps operations leaders understand where underwriter capacity and policy pressure are building."
    - Domain cue: "A credit operations lead can see whether the bottleneck is KYC, affordability, conduct risk, or high-risk declines."

13. Show charts and portfolio table.
    - Say: "The portfolio view helps leaders inspect decision mix, risk bands, branch performance, and individual applications."
    - Value point: It supports both daily operations and executive review.

## Demo Moments That Should Land

- "This is not a black box; the decision is explainable."
- "Rules and ML can coexist, which reduces adoption risk."
- "The same screen supports case-level action and portfolio-level oversight."
- "Bankers get a next step, not just a probability."
- "Audit evidence can be exported at the point of decision."
- "The app uses credit-domain controls like affordability, KYC, conduct, collateral, and policy exceptions."

## Buyer Objections And Responses

- Objection: "Our policy is different."
  - Response: "The rule layer, thresholds, policy templates, and reason codes are designed to be configured for each lender."

- Objection: "We cannot rely fully on ML."
  - Response: "The app supports rule-based decisions, ML decisions, and champion/challenger comparison, so adoption can be gradual."

- Objection: "Compliance will ask why a case was declined."
  - Response: "The output includes risk bands, reason codes, governance signals, notes, and downloadable decision packets."

- Objection: "Our risk team will ask whether this fits our credit policy."
  - Response: "The demo is intentionally structured around policy fit, FOIR, LTV, KYC, bureau conduct, manual review, and configurable thresholds."

- Objection: "Our underwriters already know what to do."
  - Response: "The value is consistency, speed, portfolio visibility, and evidence capture across all underwriters and branches."

## Closing Talk Track

"This credit workspace gives the bank a controlled path to AI-assisted underwriting. It speeds up decisions, keeps credit policy visible, explains repayment-capacity and conduct drivers, and gives leaders a portfolio view of risk and workload. That is the difference between a model demo and a real banking decisioning workflow."
