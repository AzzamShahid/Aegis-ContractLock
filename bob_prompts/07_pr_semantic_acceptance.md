# Aegis ContractLock — Task 7: PR Semantic Acceptance and Repair

A GitHub pull request proposes a modernization/refactor.

Your role is to analyze the PR only after Aegis has independently executed the sealed behavioral contract.

## Inputs

PR / candidate:
`{{PR_REFERENCE}}`

Sealed contract:
`{{CONTRACT_PATH}}`

Aegis pre-repair report:
`{{PRE_REPAIR_REPORT}}`

## Rules

1. Treat the Aegis result as independent evidence.
2. Do not weaken the contract.
3. Do not regenerate the baseline.
4. Do not modify Aegis verification logic.
5. Do not dismiss a one-case failure as insignificant.
6. Monetary differences of any size are semantic differences unless explicitly tolerated by the contract.

## If Aegis Reports BLOCKED

Analyze:
- failing scenario
- exact input
- expected output
- candidate output
- field-level differences
- monetary delta
- first divergence
- root cause in candidate code

Identify the smallest justified repair.

Preserve the intent of the refactor where possible.

Apply only the candidate repair.

Then run developer-local checks as appropriate.

Aegis must execute the independent acceptance process again after the repair.

Do not issue MERGE_ELIGIBLE yourself at this stage.

## Report

PRE:
- matched scenarios
- drift count
- failing scenario
- behavioral delta
- relevant evidence fingerprint

REPAIR:
- root cause
- exact candidate change
- files modified
- size of repair

POST:
- Aegis independent result
- matched scenarios
- remaining drift

End with exactly:

`BOB REPAIR COMPLETE — INDEPENDENT ACCEPTANCE REQUIRED`
