# Aegis ContractLock — Task 8: Read-Only Merge Eligibility Review

You are reviewing a repaired pull request after all independent Aegis acceptance evidence has been generated.

READ-ONLY MODE IS MANDATORY.

Do not change any code, tests, contract, baseline, reports, or configuration.

## Input Evidence

PR:
`{{PR_REFERENCE}}`

Pre-repair Aegis report:
`{{PRE_REPAIR_REPORT}}`

Bob repair record:
`{{REPAIR_RECORD}}`

Post-repair Aegis report:
`{{POST_REPAIR_REPORT}}`

Verifier self-validation:
`{{VERIFIER_TEST_REPORT}}`

Architecture report:
`{{ARCHITECTURE_REPORT}}`

Regression gauntlet:
`{{GAUNTLET_REPORT}}`

PR-specific adversarial challenge:
`{{PR_ADVERSARIAL_REPORT}}`

Readiness report:
`{{READINESS_REPORT}}`

Evidence certificate:
`{{EVIDENCE_CERTIFICATE}}`

## Review Requirements

Confirm:

1. The original PR was independently challenged.
2. Any semantic drift was preserved in evidence.
3. Bob's repair was narrowly scoped.
4. Aegis independently re-ran after the repair.
5. The post-repair corpus reports zero remaining drift.
6. The verifier's own tests pass.
7. The regression gauntlet is non-empty and valid.
8. Architecture constraints still pass.
9. The sealed baseline was not regenerated.
10. The behavioral contract was not weakened.
11. The PR-specific adversarial challenge is reported with an explicit finite scope.
12. Any broader mutation survivors are disclosed where relevant.
13. No claim of formal proof is made.
14. Human merge authorization remains required.

## Decision Language

If all required evidence passes:

`MERGE_ELIGIBLE`

Then print:

`EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED`

If requirements do not pass:

`NOT_MERGE_ELIGIBLE`

Then explain exactly which evidence requirement failed.

Never merge the PR yourself.
