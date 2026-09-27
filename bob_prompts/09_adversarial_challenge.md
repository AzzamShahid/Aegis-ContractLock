# Aegis ContractLock — Post-Repair Adversarial Challenge Design

The repaired candidate has already passed the sealed behavioral contract.

Your task is NOT to modify the contract.

Your task is to design a finite, targeted mutation challenge around the semantic surface changed by the pull request.

## Inputs

PR diff:
`{{PR_DIFF}}`

Repaired candidate:
`{{MODERN_ROOT}}`

Contract:
`{{CONTRACT_PATH}}`

Output directory:
`{{ADVERSARIAL_REPORT_DIR}}`

## Goal

Challenge whether the existing contract is sensitive to plausible regressions near the changed code.

## Design Mutations Such As

- inclusive/exclusive boundary flips
- threshold +/- smallest monetary unit
- nearby constant changes
- discount/tax rate perturbations
- tier-routing changes
- branch inversion
- rounding changes
- state transition omissions
- ledger sign/direction corruption
- event omission
- idempotency breakage

Only generate mutations relevant to the changed semantic surface.

For every mutation record:
- mutation ID
- family
- file
- location
- original expression
- mutated expression
- rationale
- whether mutation applied
- whether candidate remained runnable
- whether Aegis detected it
- failing scenario(s)
- timeout/infrastructure status

## Reporting

Report:
- generated
- applied
- runnable
- detected
- survived
- invalid
- timeout

Do not report "100% mutation detection" without the denominator and finite-set qualification.

Preferred wording:

> 100% detection within this finite targeted mutation set.

Never claim exhaustive mutation coverage.
