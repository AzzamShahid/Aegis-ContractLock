# IBM Bob Prompt Pack — Aegis ContractLock

> **Bring your legacy application. Let IBM Bob modernize it. Let Aegis independently decide whether the evidence passes. Keep the final merge decision human.**

This folder contains the reusable IBM Bob workflow used by **Aegis ContractLock** for evidence-gated legacy modernization.

It is designed so another developer can apply the same modernization process to a different legacy system without copying our billing demo.

---

## What This Prompt Pack Does

The prompt pack guides IBM Bob through the complete modernization lifecycle:

```text
YOUR LEGACY APPLICATION
        |
        v
00  Project Bootstrap
        |
        v
01  Contract Archaeology
        |
        v
10  Baseline Readiness
        |
        v
AEGIS SEALS LEGACY REFERENCE BEHAVIOR
        |
        v
02  Modernization Architecture
        |
        v
03  Modernization Implementation
        |
        v
AEGIS TWIN-RUN VERIFICATION
        |
   +----+----+
   |         |
   v         v
ACCEPTED   BLOCKED
             |
             v
04  Drift Critic / Repair
             |
             v
      AEGIS RE-VERIFIES
             |
             v
09  Adversarial Challenge
             |
             v
05  Final Evidence Review
             |
             v
08  Merge Eligibility Review
             |
             v
      HUMAN MERGE DECISION
```

For real GitHub pull requests, use `07_pr_semantic_acceptance.md`.

Before release or submission, use `06_integrated_audit.md`.

For additional contract-strength analysis, use `11_contract_sensitivity_review.md`.

---

# The Three Authorities

Aegis ContractLock deliberately separates who is allowed to **change**, **verify**, and **approve** software.

## IBM Bob

IBM Bob may:

- investigate the legacy system
- reconstruct the behavioral contract
- design the modernization architecture
- implement the modern candidate
- analyze Aegis counterexamples
- repair candidate behavior
- review final evidence in read-only mode

IBM Bob must **not** approve its own modernization.

## Aegis

Aegis independently:

- seals the legacy reference behavior
- executes the behavioral contract
- twin-runs legacy and modern implementations
- compares observable behavior
- detects semantic drift
- generates behavioral counterexamples
- validates architectural constraints
- executes regression / mutation challenges
- determines whether the defined acceptance evidence passes

## Human Reviewer

The human reviewer retains:

- contract/policy judgment
- approval of intentional baseline changes
- risk acceptance
- final merge/deployment authority

> **IBM Bob transforms the system. Aegis independently verifies the evidence. A human decides whether to merge.**

---

# Before You Start

You should have:

```text
your-project/
├── legacy_app/              # existing legacy implementation
├── policy/                  # optional business / policy documentation
├── modern_app/              # modernization target
├── aegis_contract.yaml      # created during contract archaeology
├── baseline/                # sealed reference evidence
├── reports/                 # Aegis verification evidence
└── bob_prompts/             # this prompt pack
```

Your project may use different directories. Replace the prompt placeholders with your own paths.

---

# Recommended Workflow

## 00 — Project Bootstrap

Use:

[`00_project_bootstrap.md`](00_project_bootstrap.md)

### Purpose

Establish the modernization workspace before Bob changes any code.

Bob should identify:

- legacy entry points
- public operations
- business domains
- mutable state
- persistence boundaries
- external dependencies
- policy/documentation sources
- candidate modernization boundaries
- missing information that prevents safe contract reconstruction

### Important

Do **not** begin modernization during this stage.

---

## 01 — Contract Archaeology

Use:

[`01_contract_archaeology.md`](01_contract_archaeology.md)

### Purpose

IBM Bob investigates the legacy application and reconstructs an executable behavioral contract.

The contract should capture, where applicable:

- return values
- normalized exceptions
- monetary calculations
- exact thresholds
- rounding behavior
- persistent state
- state transitions
- ledger effects
- audit events
- idempotency behavior
- multi-step workflows
- explicit invariants
- source / policy provenance

### Independence Rule

The modern candidate must not be used as an answer key.

The contract is intended to characterize the selected legacy reference **before** modernization acceptance.

---

## 10 — Baseline Readiness

Use:

[`10_baseline_readiness.md`](10_baseline_readiness.md)

### Purpose

Check whether the contract and legacy execution are stable enough to seal the reference baseline.

Review:

- deterministic execution
- stable monetary serialization
- normalized exceptions
- deterministic state snapshots
- unique scenario IDs
- stable ledger/audit ordering
- explicit invariants
- documented ambiguities
- controlled external nondeterminism

After this review, seal the legacy reference baseline using the Aegis project workflow.

### Critical Rule

Once sealed for an ordinary modernization PR:

> **The candidate may change. The acceptance boundary may not.**

The contract, baseline, verifier, and selected legacy reference should not silently move together with the candidate.

---

## 02 — Modernization Architecture

Use:

[`02_modernization_architecture.md`](02_modernization_architecture.md)

### Purpose

IBM Bob designs the target architecture without changing the acceptance boundary.

Bob should analyze:

- monolithic responsibilities
- coupling
- state ownership
- dependency direction
- candidate module boundaries
- public compatibility strategy
- high-risk semantic areas

Typical target domains may include:

```text
domain/
pricing/
tax/
billing/
ledger/
refund/
persistence/
audit/
errors/
orchestration/
```

Only introduce domains justified by the actual application.

### Architectural Goals

- preserve represented observable behavior
- remove modern imports from the legacy package
- avoid dependency cycles
- reduce responsibility concentration
- keep financial logic deterministic
- preserve state/event semantics

---

## 03 — Modernization Implementation

Use:

[`03_modernization_implementation.md`](03_modernization_implementation.md)

### Purpose

IBM Bob implements the modern candidate.

### Bob Must Not

- modify the sealed baseline
- weaken the behavioral contract
- delete failing scenarios
- import the legacy implementation
- bypass difficult workflows
- rewrite expected behavior just to pass

### Recommended Development Loop

```text
Implement a domain slice
        |
        v
Run focused checks
        |
        v
Run relevant Aegis scenarios
        |
        v
Inspect semantic differences
        |
        v
Repair candidate implementation
```

When implementation is complete, Aegis—not Bob—must perform the independent acceptance run.

---

# Aegis Verification

After modernization, run the project's Aegis verification workflow.

Possible outcomes:

```text
ACCEPTED
```

or:

```text
BLOCKED
```

## If ACCEPTED

Proceed to:

1. adversarial challenge
2. evidence review
3. human merge decision

## If BLOCKED

Preserve the counterexample and use Task 04.

Never remove the failing evidence merely to make the candidate green.

---

## 04 — Behavioral Drift Critic

Use:

[`04_drift_critic.md`](04_drift_critic.md)

### Purpose

IBM Bob diagnoses a candidate after Aegis independently reports semantic drift.

Bob receives:

- failing scenario
- expected behavior
- candidate behavior
- field-level differences
- state/event differences
- monetary delta
- verification report

Bob should identify the **smallest justified semantic cause** and repair only the modern candidate.

Possible causes include:

- inclusive/exclusive boundary
- threshold
- discount/tax rate
- rounding
- tier routing
- state transition
- persistence ordering
- ledger mutation
- audit/event behavior
- exception behavior
- idempotency

### Bob Must Not

- modify the legacy reference
- modify the sealed baseline
- weaken Aegis
- delete the failing scenario
- add a scenario-ID-specific hack
- self-certify acceptance

The task ends with:

```text
BOB REPAIR COMPLETE — INDEPENDENT ACCEPTANCE REQUIRED
```

Aegis must then re-run independently.

---

## 09 — Adversarial Challenge

Use:

[`09_adversarial_challenge.md`](09_adversarial_challenge.md)

### Purpose

Challenge a repaired candidate with a finite targeted mutation set around the changed semantic surface.

Useful mutation families include:

- `>=` ↔ `>`
- `<=` ↔ `<`
- threshold ± smallest monetary unit
- nearby constant corruption
- discount/tax rate perturbation
- tier-routing corruption
- branch inversion
- rounding changes
- missing state transition
- ledger sign/direction corruption
- event omission
- idempotency breakage

### Report Exact Denominators

Always report:

- generated
- applied
- runnable
- detected
- survived
- invalid
- timeout

Correct wording:

> **100% detection within this finite targeted mutation set.**

Incorrect wording:

> “Aegis detects every possible regression.”

---

## 05 — Final Evidence Review

Use:

[`05_final_evidence_review.md`](05_final_evidence_review.md)

### Mode

**READ ONLY**

Bob reviews the evidence after independent Aegis verification.

Review:

- behavioral verification
- coverage
- architecture
- regression gauntlet
- readiness
- evidence certificate
- baseline integrity
- scope limitations

Bob should not change code, tests, the contract, the baseline, or reports during this stage.

A successful review ends with:

```text
EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED
```

---

# Real Pull Request Workflow

## 07 — PR Semantic Acceptance and Repair

Use:

[`07_pr_semantic_acceptance.md`](07_pr_semantic_acceptance.md)

Use this when a real GitHub pull request has already been independently evaluated by Aegis.

### If Aegis Reports BLOCKED

Bob analyzes:

- failing scenario
- exact input
- expected output
- candidate output
- first observable divergence
- candidate root cause

Bob repairs the candidate while preserving the intent of the refactor.

Aegis then independently re-runs acceptance.

Bob must not issue merge eligibility during the repair stage.

---

## 08 — Merge Eligibility Review

Use:

[`08_merge_eligibility_review.md`](08_merge_eligibility_review.md)

### Mode

**READ ONLY**

Use only after:

- pre-repair evidence exists
- Bob's repair is recorded
- Aegis has independently re-verified
- verifier self-tests pass
- architecture checks pass
- mutation / regression evidence exists
- baseline integrity is established

If the defined evidence requirements pass, Bob may return:

```text
MERGE_ELIGIBLE
```

followed by:

```text
EVIDENCE REVIEW COMPLETE — HUMAN MERGE AUTHORIZATION REQUIRED
```

Bob must never merge the pull request itself.

---

# 06 — Integrated Audit

Use:

[`06_integrated_audit.md`](06_integrated_audit.md)

Run before release, submission, or a major evidence freeze.

The audit checks for:

- stale metrics
- contradictory scenario counts
- mixed evidence corpora
- unsupported claims
- broken references
- baseline regeneration
- architecture violations
- vacuous validation
- malformed contracts
- credentials or secrets
- local absolute paths
- formal-proof overclaims
- unsupported safety guarantees

Findings should be reported by severity:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL
```

---

# 11 — Contract Sensitivity Review

Use:

[`11_contract_sensitivity_review.md`](11_contract_sensitivity_review.md)

This asks a different question:

> **Could a meaningful semantic regression survive the current behavioral contract?**

Review sensitivity around:

- exact thresholds
- ± boundary cases
- monetary rounding
- taxes
- discounts
- tier routing
- refunds/cancellations
- ledger changes
- audit events
- exceptions
- idempotency
- multi-step state
- invalid inputs

Do not backfit the contract to known candidate behavior.

---

# Prompt Order at a Glance

```text
00  Project Bootstrap
        ↓
01  Contract Archaeology
        ↓
10  Baseline Readiness
        ↓
    AEGIS SEAL
        ↓
02  Modernization Architecture
        ↓
03  Modernization Implementation
        ↓
    AEGIS VERIFY
        ↓
   ┌─────────────┐
   │             │
ACCEPTED       BLOCKED
                 ↓
            04 Drift Critic
                 ↓
            AEGIS RE-VERIFY
                 ↓
09  Adversarial Challenge
        ↓
05  Final Evidence Review
        ↓
08  Merge Eligibility Review
        ↓
    HUMAN MERGE
```

For real pull-request work, use `07_pr_semantic_acceptance.md`.

Before release/submission, use `06_integrated_audit.md`.

For optional contract-strength analysis, use `11_contract_sensitivity_review.md`.

---

# Placeholder Variables

Replace placeholders in the prompt files with paths/references from your own project.

| Placeholder | Meaning |
|---|---|
| `{{LEGACY_ROOT}}` | legacy source directory |
| `{{MODERN_ROOT}}` | modern candidate directory |
| `{{POLICY_PATHS}}` | policy/business documentation |
| `{{CONTRACT_PATH}}` | behavioral contract |
| `{{REPORT_DIR}}` | Aegis evidence/report directory |
| `{{ARCHITECTURE_REPORT}}` | approved architecture report |
| `{{VERIFICATION_REPORT}}` | Aegis verification result |
| `{{COUNTEREXAMPLE_REPORT}}` | blocked behavioral evidence |
| `{{GAUNTLET_REPORT}}` | regression/mutation evidence |
| `{{READINESS_REPORT}}` | submission/readiness result |
| `{{EVIDENCE_CERTIFICATE}}` | evidence certificate |
| `{{PR_REFERENCE}}` | pull request / candidate reference |
| `{{PR_DIFF}}` | pull request diff |
| `{{PR_ADVERSARIAL_REPORT}}` | targeted PR challenge evidence |

Example:

```text
{{LEGACY_ROOT}}
```

might become:

```text
legacy_app/
```

and:

```text
{{MODERN_ROOT}}
```

might become:

```text
modern_app/
```

---

# Protected Acceptance Boundary

For an ordinary modernization pull request, the candidate is the evaluated surface.

The acceptance boundary should remain protected.

Typical protected surfaces include:

```text
aegis_contract.yaml
baseline/
legacy_app/
aegis/
tests/
acceptance/security gate scripts
```

Intentional contract/reference changes require a separately reviewed update process.

> **The candidate may change. The acceptance boundary may not.**

---

# Acceptance Scope

Aegis treats the selected legacy implementation as the behavioral reference.

That does **not** establish that the observed legacy behavior itself represents the correct current business policy.

Aegis does not claim:

- formal mathematical proof
- complete whole-program equivalence
- correctness outside the executed contract
- guaranteed detection of every future regression
- hostile-code sandbox security
- correctness or authorship merely because hashes match

The correct assurance statement is:

> **Behavioral equivalence demonstrated across the defined contract and executed scenario corpus. This is not a formal proof of complete program equivalence.**

---

# Quick Start for Another Developer

If you want to apply Aegis ContractLock to your own legacy project:

1. Clone the Aegis project/workflow.
2. Add or point to your legacy source.
3. Add available policy/business documentation.
4. Open the project in IBM Bob.
5. Start with `00_project_bootstrap.md`.
6. Run `01_contract_archaeology.md`.
7. Review baseline readiness with `10_baseline_readiness.md`.
8. Seal the legacy reference behavior with Aegis.
9. Run `02_modernization_architecture.md`.
10. Run `03_modernization_implementation.md`.
11. Let Aegis independently verify the modern candidate.
12. If blocked, use `04_drift_critic.md`.
13. Re-run Aegis.
14. Challenge the frozen repair with `09_adversarial_challenge.md`.
15. Review final evidence.
16. Keep final merge authority human.

---

# The Aegis Rule

> **Generation is not acceptance.**

IBM Bob can be extremely capable at understanding and changing software.

Aegis ContractLock exists because the agent authorized to **change** software should not be the only authority allowed to **accept** that change.
