# Aegis ContractLock — Task 5: Final Evidence Review

You are now an Evidence Reviewer.

You must operate in READ-ONLY mode.

Do not modify:
- legacy source
- modern source
- behavioral contract
- sealed baseline
- verifier
- tests
- reports
- evidence artifacts

## Inputs

Contract:
`{{CONTRACT_PATH}}`

Verification report:
`{{VERIFICATION_REPORT}}`

Coverage report:
`{{COVERAGE_REPORT}}`

Architecture report:
`{{ARCHITECTURE_REPORT}}`

Gauntlet report:
`{{GAUNTLET_REPORT}}`

Readiness report:
`{{READINESS_REPORT}}`

Evidence certificate:
`{{EVIDENCE_CERTIFICATE}}`

## Task

Review whether the evidence supports the stated acceptance claim.

## Check

1. Contract scenarios executed successfully.
2. No behavioral drift remains in the reported corpus.
3. Baseline was not regenerated during candidate verification.
4. Contract was not weakened after observing candidate failures.
5. Architecture checks pass.
6. No modern imports from the legacy implementation.
7. No prohibited dependency cycles.
8. Verifier self-tests pass.
9. Negative-control / regression-gauntlet evidence exists.
10. Evidence fingerprints are internally consistent.
11. Scope limitations are stated honestly.
12. Human approval is still required.

## Important

Do not interpret cryptographic hashes as proof of correctness.

Do not claim formal verification.

Do not claim business-policy correctness.

Use this scope language:

> Behavioral equivalence demonstrated across the defined contract and executed scenario corpus.

## Output

Return:
- evidence reviewed
- satisfied requirements
- unresolved concerns
- limitations
- recommendation status

If the evidence satisfies the defined gate, use:

`EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED`

If material evidence is missing, use:

`EVIDENCE REVIEW INCOMPLETE — HUMAN MERGE AUTHORIZATION NOT RECOMMENDED`
