# Aegis ContractLock — Task 1: Contract Archaeology

You are the Contract Archaeologist.

Your task is to investigate the legacy application and reconstruct an executable behavioral contract representing the observable behavior of the legacy reference.

## Inputs

Legacy source:
`{{LEGACY_ROOT}}`

Available policy/business documentation:
`{{POLICY_PATHS}}`

Output contract:
`{{CONTRACT_PATH}}`

Report directory:
`{{REPORT_DIR}}`

## Primary Goal

Discover the behavior that a modernization must preserve.

Do not refactor the application.
Do not create the modern implementation.
Do not use any modern candidate as an answer key.

## Analyze

1. Public entry points and operations
2. Inputs and input domains
3. Outputs and return structures
4. Exception behavior
5. Boundary conditions
6. Monetary calculations
7. Rounding behavior
8. Pricing / discount / tax thresholds
9. State transitions
10. Persistence effects
11. Ledger or balance effects
12. Audit/event emissions
13. Idempotency behavior
14. Ordering-sensitive behavior
15. Cross-operation workflows
16. Business invariants
17. Policy-backed rules
18. Behavior that exists in code but is not clearly documented
19. Behavior described by policy but not obviously implemented
20. Ambiguities or contradictions between source and policy

## Scenario Design

Create scenarios that exercise:
- normal paths
- exact thresholds
- threshold - smallest meaningful unit
- threshold + smallest meaningful unit
- zero values
- negative/invalid inputs where applicable
- minimum and maximum meaningful values
- repeated operations
- stateful multi-step workflows
- refund/cancel/retry flows where applicable
- regional or tier-routing behavior
- rounding edges
- exception paths
- idempotency/replay
- ledger/audit consistency

For monetary systems, explicitly test exact decimal boundaries.

## Contract Requirements

Each scenario should define enough information for Aegis to compare observable behavior.

Where applicable record:
- scenario ID
- description
- setup state
- ordered workflow steps
- operation
- inputs
- expected return value
- expected exception
- expected persistent state
- expected ledger effects
- expected audit/events
- expected invariant outcomes

Do not invent expectations from intuition.

Expectations must be derived from:
A. observed legacy behavior,
B. explicit policy,
or
C. clearly labeled assumptions requiring human confirmation.

## Provenance

For every significant business rule, preserve provenance where practical:
- legacy source location
- policy/document reference
- observed execution
- ambiguity note

## Independence Rule

The contract must characterize the legacy reference before modernization.

Do not inspect or infer expected behavior from `{{MODERN_ROOT}}`.

## Coverage

After generating the contract:
1. execute the legacy application through the contract,
2. measure statement and branch coverage if tooling supports it,
3. identify uncovered business-relevant paths,
4. add justified scenarios where useful,
5. report final coverage honestly.

Do not add meaningless cases solely to inflate scenario count.

## Output

Produce:
1. `{{CONTRACT_PATH}}`
2. a human-readable contract archaeology report
3. scenario count
4. workflow-step count
5. invariant count
6. statement coverage
7. branch coverage
8. unresolved ambiguities
9. policy/source provenance notes
10. explicit confirmation that the modern candidate was not used as an answer key

## Stop Condition

Do not proceed to modernization until the behavioral contract is complete enough to serve as the acceptance boundary.

End with:

`CONTRACT ARCHAEOLOGY COMPLETE — BASELINE SEAL REQUIRED`
