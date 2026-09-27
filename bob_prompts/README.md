# IBM Bob Prompt Pack — Aegis ContractLock

This folder contains the reusable IBM Bob workflow for applying Aegis ContractLock to another legacy modernization project.

## Core Principle

> **IBM Bob transforms the system. Aegis independently verifies the evidence. A human retains the final merge decision.**

Aegis separates authority:

- **IBM Bob** investigates, designs, modernizes, diagnoses drift, and repairs.
- **Aegis** seals reference behavior, executes independent verification, detects drift, and gates acceptance.
- **The human reviewer** retains final merge/deployment authority.

---

## Recommended Workflow

### 1. Bootstrap the Project

Use `00_project_bootstrap.md`.

Purpose:

- inspect the legacy repository
- identify entry points
- identify business domains
- identify mutable state
- identify policy/documentation sources
- establish modernization boundaries

Do not begin modernization yet.

### 2. Contract Archaeology

Use `01_contract_archaeology.md`.

IBM Bob investigates the legacy implementation and available policy material to reconstruct the executable behavioral contract.

Expected output includes:

- scenario corpus
- workflow steps
- business invariants
- boundary cases
- exception behavior
- state transitions
- ledger/audit effects
- provenance notes

The modern candidate must not be used as an answer key.

### 3. Baseline Readiness Review

Use `10_baseline_readiness.md`.

Before sealing the baseline, review:

- deterministic execution
- stable serialization
- unique scenario IDs
- normalized exceptions
- deterministic state snapshots
- documented ambiguities

Then seal the legacy reference baseline with Aegis.

### 4. Modernization Architecture

Use `02_modernization_architecture.md`.

IBM Bob designs the target architecture while treating the behavioral contract as the external acceptance boundary.

The goal is not to copy the monolith. The goal is to produce a cleaner modular implementation while preserving the behavior represented by the contract.

### 5. Modernization Implementation

Use `03_modernization_implementation.md`.

IBM Bob implements the modern candidate.

Key rules:

- do not modify the sealed baseline
- do not weaken the contract
- do not import the legacy package
- avoid dependency cycles
- preserve represented behavior

### 6. Run Aegis Verification

Run the Aegis verification process against the sealed contract.

The result should be one of:

```text
ACCEPTED
```

or:

```text
BLOCKED
```

If accepted, proceed to independent challenge and review.

If blocked, continue to the Drift Critic.

### 7. Behavioral Drift Critic

Use `04_drift_critic.md`.

IBM Bob receives the Aegis behavioral counterexample and diagnoses the smallest semantic cause.

Bob may repair the modern candidate.

Bob may not:

- modify the contract
- modify the baseline
- weaken the verifier
- delete the failing scenario
- self-certify acceptance

After the repair, Aegis must independently re-run verification.

### 8. Adversarial Challenge

Use `09_adversarial_challenge.md`.

After a repair is frozen, design a finite targeted mutation challenge around the changed semantic surface.

Examples:

- boundary flips
- threshold ± smallest unit
- rate changes
- tier-routing changes
- branch inversions
- rounding changes
- state/ledger corruption

Always report the exact denominator.

Preferred wording:

> **100% detection within this finite targeted mutation set.**

Never claim exhaustive mutation coverage.

### 9. Final Evidence Review

Use `05_final_evidence_review.md`.

IBM Bob now returns in read-only mode.

Review:

- verification
- coverage
- architecture
- gauntlet
- readiness
- evidence certificate
- baseline integrity
- scope limitations

Bob must not modify the system during this review.

---

## Pull Request Workflow

### PR Acceptance and Repair

Use `07_pr_semantic_acceptance.md`.

This is used after Aegis independently evaluates the candidate PR.

If Aegis returns `BLOCKED`, Bob diagnoses and repairs only the candidate.

After repair:

```text
BOB REPAIR COMPLETE — INDEPENDENT ACCEPTANCE REQUIRED
```

### Read-Only Merge Eligibility Review

Use `08_merge_eligibility_review.md`.

This happens only after all independent Aegis evidence exists.

If requirements pass, Bob may report:

```text
MERGE_ELIGIBLE
```

followed by:

```text
EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED
```

Bob must never merge the pull request itself.

---

## Pre-Release Audit

Use `06_integrated_audit.md`.

Run this before release or submission to check:

- stale metrics
- mixed evidence corpora
- unsupported claims
- broken evidence references
- baseline regeneration
- verifier weaknesses
- architecture violations
- credential exposure
- overclaiming

---

## Optional Contract Sensitivity Review

Use `11_contract_sensitivity_review.md`.

This is an adversarial review of the contract itself.

It asks:

> **Could a meaningful semantic regression survive the current contract?**

Use this to identify blind spots without backfitting the contract to known candidate behavior.

---

## Prompt Order

```text
00 Project Bootstrap
        ↓
01 Contract Archaeology
        ↓
10 Baseline Readiness
        ↓
Aegis Baseline Seal
        ↓
02 Modernization Architecture
        ↓
03 Modernization Implementation
        ↓
Aegis Verification
        ↓
   ACCEPTED / BLOCKED
        ↓
04 Drift Critic (if BLOCKED)
        ↓
Aegis Re-Verification
        ↓
09 Adversarial Challenge
        ↓
05 Final Evidence Review
        ↓
08 Merge Eligibility Review
        ↓
HUMAN MERGE DECISION
```

For pull-request-specific work, also use `07_pr_semantic_acceptance.md`.

Before final release/submission, use `06_integrated_audit.md`.

---

## Placeholder Variables

The prompts use reusable placeholders such as:

```text
{{LEGACY_ROOT}}
{{MODERN_ROOT}}
{{POLICY_PATHS}}
{{CONTRACT_PATH}}
{{REPORT_DIR}}
{{ARCHITECTURE_REPORT}}
{{VERIFICATION_REPORT}}
{{COUNTEREXAMPLE_REPORT}}
{{GAUNTLET_REPORT}}
{{READINESS_REPORT}}
{{EVIDENCE_CERTIFICATE}}
{{PR_REFERENCE}}
{{PR_DIFF}}
{{PR_ADVERSARIAL_REPORT}}
```

Replace them with paths and references from your own project.

---

## Acceptance Scope

Aegis uses the selected legacy implementation as the behavioral reference.

It does **not** prove that the legacy business policy itself is correct.

The correct assurance statement is:

> **Behavioral equivalence demonstrated across the defined contract and executed scenario corpus. This is not a formal proof of complete program equivalence.**

---

## What Another Developer Needs

To reuse Aegis ContractLock:

1. bring a legacy application
2. provide available policy/business documentation
3. open the repository in IBM Bob
4. begin with `00_project_bootstrap.md`
5. follow the prompt sequence
6. let Aegis seal and verify independently
7. let IBM Bob repair only when Aegis produces evidence
8. retain final merge authority as a human reviewer

That is the reusable Aegis ContractLock workflow.
