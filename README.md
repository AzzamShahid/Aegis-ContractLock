# Aegis ContractLock

> **Evidence-gated legacy modernization with IBM Bob.**  
> IBM Bob transforms the system. Aegis independently verifies the evidence. A human decides whether to merge.

**Live demo:** https://aegis-contractlock.vercel.app/  
**Repository:** https://github.com/AzzamShahid/Aegis-ContractLock

---

## What is Aegis ContractLock?

Aegis ContractLock is an end-to-end workflow for modernizing legacy software without asking the same AI agent that changed the system to also certify that the change is safe.

The workflow separates three responsibilities:

- **IBM Bob** investigates the legacy system, reconstructs behavior, designs the modernization, implements the candidate, diagnoses drift, and repairs candidate code.
- **Aegis** independently seals reference behavior, twin-runs the legacy and modern systems, detects semantic drift, validates architecture, and produces evidence.
- **A human reviewer** keeps the final merge decision.

The core idea is simple:

> **Generation is not acceptance.**

A modernized system can look cleaner, have passing unit tests, and still be behaviorally wrong at a boundary, threshold, workflow transition, rounding rule, or state mutation. Aegis makes those differences visible before merge.

---

## The Problem

Legacy modernization is risky because business behavior is often scattered across:

- long functions
- conditionals
- thresholds
- mutable state
- database updates
- audit events
- undocumented conventions
- policy documents
- edge cases that normal happy-path tests do not cover

An AI coding agent can refactor that system quickly, but speed alone does not establish behavioral preservation.

A green pull request is not enough.

Aegis ContractLock adds an independent evidence layer between **AI-generated change** and **human approval**.

---

## How It Works

```text
LEGACY MONOLITH
      |
      v
IBM BOB — CONTRACT ARCHAEOLOGY
      |
      v
AEGIS — BASELINE READINESS + REFERENCE SEAL
      |
      v
IBM BOB — MODERNIZATION ARCHITECTURE
      |
      v
IBM BOB — MODERN IMPLEMENTATION
      |
      v
AEGIS — TWIN-RUN VERIFICATION
      |
   +--+-------------------+
   |                      |
   v                      v
ACCEPTED                BLOCKED
                          |
                          v
                 AEGIS COUNTEREXAMPLE
                          |
                          v
                 IBM BOB — DRIFT REPAIR
                          |
                          v
                 AEGIS — RE-VERIFICATION
                          |
                          v
                 ADVERSARIAL CHALLENGE
                          |
                          v
                 READ-ONLY EVIDENCE REVIEW
                          |
                          v
                 HUMAN MERGE DECISION
```

For ordinary modernization work:

> **The candidate may change. The acceptance boundary may not.**

---

## What Aegis Verifies

Aegis evaluates the modern candidate against a defined behavioral contract and sealed legacy reference evidence.

Depending on the scenario, that can include:

- return values
- monetary values
- discount and tax calculations
- exact threshold behavior
- exception behavior
- persistent state
- state transitions
- ledger effects
- audit events
- multi-step workflows
- idempotency
- invariants
- architecture constraints

Aegis reports the first meaningful behavioral divergence instead of reducing the result to a generic red/green status.

---

# Real PR Evidence: A One-Character Regression

A real pull request refactored pricing thresholds into named policy constants.

The modernization looked reasonable, but one comparison changed from an inclusive threshold to an exclusive one:

```python
# incorrect candidate behavior
if subtotal > VIP_PREMIUM_THRESHOLD:
```

The intended represented behavior was:

```python
if subtotal >= VIP_PREMIUM_THRESHOLD:
```

At the exact VIP boundary of **$1,000.00**, Aegis detected the regression.

### Before Repair

```text
Cases matched : 85 / 86
Cases drifted : 1
VERDICT       : BLOCKED
```

Counterexample:

```text
Scenario: bnd_vip_subtotal_1000_00

Expected discount : 10% / $100.00
Candidate discount:  7% /  $70.00

Expected taxable  : $900.00
Candidate taxable : $930.00

Expected tax      : $65.25
Candidate tax     : $67.43

Expected total    : $965.25
Candidate total   : $997.43

Observed delta    : +$32.18
```

IBM Bob diagnosed the smallest semantic cause and repaired only the candidate:

```text
>  →  >=
```

Bob then stopped with:

```text
BOB REPAIR COMPLETE — INDEPENDENT ACCEPTANCE REQUIRED
```

Aegis independently re-ran the acceptance gate.

### After Repair

```text
Cases matched : 86 / 86
Cases drifted : 0
VERDICT       : ACCEPTED
```

The final merge remained a human decision.

---

# Current Verified Submission State

The final reconciled `main` submission state passed the complete seven-gate verification workflow.

| Evidence | Result |
|---|---:|
| Aegis verifier tests | **32 / 32 passed** |
| Behavioral scenarios | **86 / 86 matched** |
| Workflow steps | **100** |
| Behavioral drift | **0** |
| Legacy statement coverage | **100.00%** |
| Legacy branch coverage | **98.96%** |
| Seeded regression gauntlet | **21 / 21 detected** |
| Escaped seeded regressions | **0** |
| Modern legacy imports | **0** |
| Modern dependency cycles | **0** |
| Largest module LOC | **381 → 205** |
| Python modules | **1 → 11** |
| Submission readiness | **READY** |
| Final verification | **READY** |

Current semantic evidence fingerprints:

```text
Baseline evidence:
2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7

Accepted candidate evidence:
d919b4055c09e30ee9654d92e302aa64c46195716d53525d57023e1430216c99
```

The sealed baseline file was also hashed before and after the final verification run:

```text
D608B27DDD47D6568A0C95B305996E24FFB79F0C9D8A037050B7F420F32773A4
```

The byte hash remained unchanged.

---

# Evidence Layers — Kept Separate

Aegis deliberately does **not** combine different evidence corpora into one inflated test count.

## 1. Current Behavioral Contract

```text
86 scenarios
100 workflow steps
86 / 86 matched
0 drift
```

This is the main current acceptance corpus.

## 2. Verifier Self-Validation

```text
32 / 32 tests passed
```

These validate the Aegis verification machinery itself.

## 3. Curated Seeded Regression Gauntlet

```text
21 seeded regressions
21 detected
0 escaped
```

This is a finite verifier challenge set.

## 4. PR-Specific Adversarial Challenge

A targeted post-repair challenge was generated around the repaired pricing boundary.

```text
24 generated
24 runnable
24 detected
0 survivors
0 invalid
0 timeout
```

Families included:

- boundary mutations
- threshold ± $0.01 mutations
- discount-rate mutations
- tier-routing mutations

The correct claim is:

> **100% detection within this finite targeted mutation set.**

It is not a claim of exhaustive mutation coverage.

## 5. Historical Broad Holdout

A broader historical challenge remained intentionally separate:

```text
65 generated
63 runnable
54 detected
9 survivors
2 invalid
0 timeout
Detection rate: 85.71% of runnable cases
```

The surviving mutations are retained as evidence of contract limitations rather than silently backfitted away.

That imperfection is important: Aegis is designed to expose the strength and limits of its evidence, not hide them.

---

# Historical IBM Bob Clean-Room Modernization

Before the larger current corpus, IBM Bob was exercised through a clean-room modernization sequence.

Historical evidence included:

```text
47 scenarios
60 workflow steps
183 invariant declarations
```

The sequence demonstrated:

1. legacy behavior reconstruction
2. architecture extraction
3. modernization
4. a deliberately controlled threshold defect
5. Aegis blocking the defect
6. IBM Bob repairing the candidate
7. Aegis independently restoring acceptance

The controlled rehearsal moved:

```text
47 / 47
   ↓ deliberate >= → > defect
46 / 47 — BLOCKED
   ↓ Bob repair > → >=
47 / 47 — ACCEPTED
```

This historical corpus is kept separate from the current 86-scenario acceptance corpus.

---

# IBM Bob's Role

IBM Bob is used throughout the modernization lifecycle, but it is never the sole acceptance authority.

## Bob is used for

- repository investigation
- contract archaeology
- responsibility mapping
- modernization architecture
- implementation
- semantic drift diagnosis
- candidate repair
- evidence review
- merge-eligibility review in read-only mode

## Bob is not allowed to

- silently rewrite the sealed baseline
- weaken the behavioral contract to make the candidate pass
- delete failing scenarios
- self-certify a repair
- merge the pull request on its own

That separation is the core design decision behind Aegis ContractLock.

---

# Reusable IBM Bob Prompt Pack

The repository includes a reusable prompt pack under:

```text
bob_prompts/
```

It is designed so another developer can apply the same Bob → Aegis process to a different legacy application.

Recommended order:

| Step | Prompt | Purpose |
|---|---|---|
| 1 | `00_project_bootstrap.md` | Inspect the project and establish boundaries |
| 2 | `01_contract_archaeology.md` | Reconstruct executable legacy behavior |
| 3 | `10_baseline_readiness.md` | Determine whether reference behavior is ready to seal |
| 4 | Aegis seal | Freeze reference evidence |
| 5 | `02_modernization_architecture.md` | Design the modern architecture |
| 6 | `03_modernization_implementation.md` | Implement the candidate |
| 7 | Aegis verify | Run independent twin-run verification |
| 8 | `04_drift_critic.md` | Diagnose and repair blocked behavior |
| 9 | Aegis re-verify | Independently validate the repair |
| 10 | `09_adversarial_challenge.md` | Challenge the repaired semantic surface |
| 11 | `05_final_evidence_review.md` | Perform read-only evidence review |
| 12 | `08_merge_eligibility_review.md` | Review whether defined evidence requirements pass |
| 13 | Human decision | Final merge authorization |

Additional prompts:

- `06_integrated_audit.md` — pre-release / pre-submission evidence audit
- `07_pr_semantic_acceptance.md` — real pull-request acceptance and repair workflow
- `11_contract_sensitivity_review.md` — search for behavioral blind spots

See `bob_prompts/README.md` for the complete reusable workflow.

---

# Protected Acceptance Boundary

Aegis includes a protected-boundary workflow and local protected-path checker.

For ordinary modernization pull requests, protected surfaces include:

```text
aegis_contract.yaml
baseline/
legacy_app/
aegis/
tests/
verify_submission.ps1
security_preflight.ps1
scripts/check_protected_paths.py
.github/workflows/aegis-pr-gate.yml
.github/workflows/aegis-protected-boundary.yml
```

The GitHub protected-boundary workflow uses the trusted base revision and does not execute candidate PR code.

Intentional contract or baseline changes require separate explicit review rather than being bundled silently into a normal modernization candidate.

---

# Architecture

Aegis separates the selected legacy reference, the modern candidate, the verification engine, evidence, and policy boundary.

```text
                    +-----------------------+
                    |   Behavioral Contract |
                    +-----------+-----------+
                                |
                                v
+----------------+      +-------+--------+      +----------------+
| Legacy System  | ---> | Aegis Twin-Run | <--- | Modern System  |
+----------------+      +-------+--------+      +----------------+
                                |
                                v
                    +-----------+-----------+
                    | Normalized Evidence   |
                    | + Drift Comparison    |
                    +-----------+-----------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
             ACCEPTED                       BLOCKED
                                               |
                                               v
                                      Counterexample
                                               |
                                               v
                                         IBM Bob Repair
```

The modern implementation is structurally separated from the legacy implementation:

```text
Modern legacy imports: 0
Modern dependency cycles: 0
```

---

# Repository Guide

Key areas of the repository include:

```text
.github/workflows/     GitHub acceptance / protected-boundary workflows
aegis/                 Aegis verification engine
baseline/              sealed behavioral reference evidence
bob_prompts/           reusable IBM Bob workflow prompts
bob_sessions/          captured IBM Bob task evidence/screenshots
docs/                  verifier findings and technical documentation
legacy_app/            selected legacy behavioral reference
modern_app/            modernized candidate implementation
reports/               verification and evidence reports
scripts/               audits, integrity checks, and challenge tooling
site/                   public Aegis ContractLock landing/demo site
tests/                  verifier and regression tests
aegis_contract.yaml    behavioral acceptance contract
verify_submission.ps1  complete seven-gate local verification
```

---

# Run the Full Verification

From the repository root on Windows PowerShell:

```powershell
.\verify_submission.ps1
```

The final verified run executes seven gates:

```text
1/7 Repository security preflight
2/7 Aegis engine tests
3/7 Legacy behavioral-contract coverage
4/7 Behavioral equivalence
5/7 Architecture integrity
6/7 Seeded regression audit
7/7 Complete submission readiness
```

Expected final result for the frozen submission state:

```text
SECURITY PREFLIGHT: PASS
32 passed
86 / 86 matched
0 drift
100.00% statement coverage
98.96% branch coverage
21 / 21 seeded regressions detected
0 escaped
0 modern legacy imports
0 dependency cycles
SUBMISSION READINESS: READY
FINAL: READY
```

---

# Security and Repository Hygiene

The repository security preflight checks for:

- `.bobignore`
- ignored `.env`
- trackable `.env.example`
- ignored local virtual environments
- tracked private keys/certificates
- cache/venv noise
- exposed credential patterns
- local absolute file URI references
- hard-coded machine-specific user-profile paths
- evidence-directory secret exposure

Security preflight must pass before the rest of the submission verification proceeds.

---

# Threat Model and Scope

Aegis uses the selected legacy implementation as the behavioral reference.

That means Aegis can establish evidence that the modern candidate preserves the behavior represented by the defined contract and executed scenarios.

It does **not** establish that the legacy behavior itself is the correct current business policy.

Aegis also does not claim:

- formal mathematical proof of full program equivalence
- complete behavioral coverage outside the executed contract
- guaranteed detection of every possible future regression
- hostile-code sandbox security
- correctness merely because two hashes match
- authorship or trust merely because an artifact has a SHA-256 fingerprint

The intended assurance statement is:

> **Behavioral equivalence demonstrated across the defined contract and executed scenario corpus. This is not a formal proof of complete program equivalence.**

---

# Why This Matters

AI coding agents are increasingly capable of changing large systems.

The harder problem is deciding when those changes deserve trust.

Aegis ContractLock treats modernization as an evidence problem rather than a code-generation problem.

```text
IBM Bob can propose the change.
Aegis can independently test the evidence.
A human still decides whether that evidence is enough to merge.
```

That is the contract.

---

## Aegis ContractLock

**Legacy → Bob archaeology → Aegis seal → Bob modernization → Aegis verification → drift evidence → Bob repair → Aegis re-verification → human merge.**

> **Don't trust a green PR. Prove it deserves to merge.**
