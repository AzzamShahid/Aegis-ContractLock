# IBM Bob PR Semantic Acceptance Workflow

## Core idea

> Don't trust a green PR. Prove it deserves to merge.

This package records the real PR acceptance workflow used for Aegis ContractLock.

IBM Bob was allowed to diagnose and repair the PR, but Bob was not allowed to approve its own repair.

---

## Pull Request Chain

- PR: `#1`
- Branch: `demo/bob-pr-acceptance-gate`
- Risky PR commit: `5276fa24a3f7c9e8025fe22d9995ea528fe2691e`
- Bob repair commit: `fabc7b7a3a960fd1df7b7c6e51c44a27f797f95a`
- Repair freeze tag: `aegis-pr-repair-freeze-20260927`
- Human merge commit: `1f79baf`

---

## Task 7 — IBM Bob PR Semantic Acceptance Agent

The PR refactored pricing thresholds into named constants.

The original PR introduced this semantic defect:

    if subtotal > VIP_PREMIUM_THRESHOLD:

The preserved legacy behavior required:

    if subtotal >= VIP_PREMIUM_THRESHOLD:

### Pre-repair result

- 85 / 86 cases matched
- 1 case drifted
- Verdict: `BLOCKED`
- Behavioral counterexample: `bnd_vip_subtotal_1000_00`

Expected:

- discount rate: 10%
- discount: $100.00
- grand total: $965.25

Defective PR:

- discount rate: 7%
- discount: $70.00
- grand total: $997.43

Customer impact: **+$32.18**

### Bob repair

Bob changed only one comparison operator:

    >  ->  >=

The named-constant refactor itself remained intact.

Post-repair:

- 86 / 86 matched
- 0 drifted
- `ACCEPTED`

Bob then stopped with:

> BOB REPAIR COMPLETE — INDEPENDENT ACCEPTANCE REQUIRED

---

## Independent Acceptance

After Bob relinquished repair authority, the candidate was independently verified.

Results:

- verifier tests: 27 / 27
- behavioral cases: 86 / 86
- drifted cases: 0
- workflow steps: 100
- statement coverage: 100.00%
- branch coverage: 98.96%
- curated seeded regressions: 21 / 21 detected
- escaped curated regressions: 0
- largest module: 381 -> 205 LOC
- analyzed modules: 1 -> 11
- modern imports from legacy: 0
- dependency cycles: 0
- submission readiness: `READY`
- final result: `READY`

Evidence:

`reports/pr_acceptance/independent-core-gate.txt`

---

## PR-Specific Post-Repair Adversarial Challenge

The repaired candidate was frozen before this experiment.

Frozen candidate:

`aegis-pr-repair-freeze-20260927`
-> `fabc7b7a3a960fd1df7b7c6e51c44a27f797f95a`

Control:

- 86 / 86
- `ACCEPTED`

Targeted challenge:

- 24 generated
- 24 runnable
- 24 detected / BLOCKED
- 0 survivors
- 0 invalid / unrunnable
- 0 infrastructure failures
- 100.00% detection within this finite targeted PR-specific set

Mutation families covered:

- inclusive/exclusive boundaries
- threshold values +/- $0.01
- discount rates
- tier routing

Evidence:

- `reports/pr_acceptance/pr-adversarial-audit.md`
- `reports/pr_acceptance/pr-adversarial-audit.json`

The 24/24 result applies only to this finite targeted mutation set. It is not an exhaustive mutation score or formal proof.

---

## Historical Holdout Challenge

The earlier post-freeze generated challenge is a separate experiment:

- 65 generated
- 63 runnable
- 54 detected
- 9 survivors disclosed
- 2 invalid / unrunnable
- 0 infrastructure failures
- 85.71% detection over runnable mutants

That historical challenge did **not** test commit `fabc7b7`.

Its nine survivors remain disclosed as evidence of finite contract coverage boundaries.

---

## Task 8 — IBM Bob Read-Only Merge Evidence Review

Task 8 gave Bob no repair authority.

Bob reviewed:

- Git provenance
- Task 7 repair
- repair freeze
- independent core verification
- PR-specific adversarial evidence
- historical holdout evidence
- scope and limitations

All 12 documented merge-policy requirements were satisfied.

Final verdict:

`MERGE_ELIGIBLE`

Bob ended with:

> EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED

---

## Human Merge

Only after Task 8 returned `MERGE_ELIGIBLE` did the human reviewer merge PR #1.

Merge commit:

`1f79baf`

Workflow:

    Risky PR
        |
        v
    IBM Bob Task 7
    Detect + Diagnose + Repair
        |
        v
    Bob Stops
        |
        v
    Independent Aegis Gate
    27/27 + 86/86 + 21/21 + READY
        |
        v
    Freeze Repaired Candidate
        |
        v
    PR-Specific Challenge
    24/24 Targeted Mutations Blocked
        |
        v
    IBM Bob Task 8
    Read-Only Evidence Review
        |
        v
    MERGE_ELIGIBLE
        |
        v
    Human Authorization
        |
        v
    Merged

---

## Scope

Aegis demonstrates behavioral equivalence across the defined contract and executed scenario corpus.

It does not establish:

- formal proof of complete program equivalence
- exhaustive mutation sensitivity
- zero risk
- behavioral coverage outside the contract
- correctness merely from SHA-256 fingerprints

The 24/24 result applies only to the finite targeted PR-specific mutation set.
