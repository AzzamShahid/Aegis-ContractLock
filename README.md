# IBM Bob Prompt Pack for Aegis ContractLock

This folder contains the reusable IBM Bob workflow prompts for applying Aegis ContractLock to another legacy modernization project.

## Recommended Order

1. `00_project_bootstrap.md`
2. `01_contract_archaeology.md`
3. `10_baseline_readiness.md`
4. Seal the legacy baseline with Aegis
5. `02_modernization_architecture.md`
6. `03_modernization_implementation.md`
7. Run Aegis verification
8. If BLOCKED: `04_drift_critic.md`
9. Re-run Aegis verification
10. `09_adversarial_challenge.md`
11. `05_final_evidence_review.md`
12. For a real pull request: `07_pr_semantic_acceptance.md`
13. After independent evidence: `08_merge_eligibility_review.md`
14. Before release/submission: `06_integrated_audit.md`
15. Optional contract-strength review: `11_contract_sensitivity_review.md`

## Placeholder Variables

Replace placeholders such as:

- `{{LEGACY_ROOT}}`
- `{{MODERN_ROOT}}`
- `{{POLICY_PATHS}}`
- `{{CONTRACT_PATH}}`
- `{{REPORT_DIR}}`
- `{{ARCHITECTURE_REPORT}}`
- `{{VERIFICATION_REPORT}}`
- `{{COUNTEREXAMPLE_REPORT}}`
- `{{GAUNTLET_REPORT}}`
- `{{READINESS_REPORT}}`
- `{{EVIDENCE_CERTIFICATE}}`
- `{{PR_REFERENCE}}`
- `{{PR_DIFF}}`
- `{{PR_ADVERSARIAL_REPORT}}`

with paths/references from the user's own project.

## Core Rule

IBM Bob transforms the system. Aegis independently verifies the evidence. A human retains the final merge decision.

## Acceptance Scope

> Behavioral equivalence demonstrated across the defined contract and executed scenario corpus. This is not a formal proof of complete program equivalence.
