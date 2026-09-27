# Aegis ContractLock — Contract Sensitivity Review

Act as an adversarial reviewer of the behavioral contract.

Do not modify the modern candidate.

Your objective is to determine whether the contract is likely to detect meaningful semantic regressions rather than merely exercise happy paths.

Inspect:

`{{CONTRACT_PATH}}`

Evaluate coverage of:
- exact thresholds
- +/- boundary cases
- financial rounding
- tier routing
- taxes
- discounts
- state transitions
- refunds/cancellations
- ledger changes
- audit events
- exception behavior
- idempotency
- multi-step workflows
- persistence
- invalid inputs

Identify areas where a plausible semantic mutation might survive.

Do not silently add expectations unsupported by legacy or policy evidence.

Produce:
- sensitivity strengths
- blind spots
- recommended additional scenarios
- rationale
- provenance needed before adding each scenario

Do not backfit the contract to known candidate behavior.
