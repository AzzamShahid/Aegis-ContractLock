# Aegis ContractLock

> **Don't trust a green PR. Prove it deserves to merge.**

[![Aegis Gate](https://img.shields.io/badge/Aegis-READY-brightgreen)](reports/readiness.md)
[![Behavior](https://img.shields.io/badge/Behavior-86%2F86%20ACCEPTED-brightgreen)](reports/verification.md)
[![Coverage](https://img.shields.io/badge/Statements-100.00%25-brightgreen)](reports/contract-coverage.md)
[![Branches](https://img.shields.io/badge/Branches-98.96%25-brightgreen)](reports/contract-coverage.md)
[![Verifier Tests](https://img.shields.io/badge/Verifier%20Tests-32%2F32-brightgreen)](tests/)
[![Seeded Regressions](https://img.shields.io/badge/Seeded%20Regressions-21%2F21-blue)](reports/gauntlet-report.md)
[![PR Challenge](https://img.shields.io/badge/PR%20Challenge-24%2F24%20Blocked-brightgreen)](reports/pr_acceptance/pr-adversarial-audit.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Aegis ContractLock is an end-to-end evidence-gated legacy modernization system built around IBM Bob.**

IBM Bob investigates the legacy system, reconstructs its behavioral contract, modernizes the monolith, diagnoses semantic drift, and applies focused repairs.

Aegis seals the legacy reference behavior, independently twin-runs the legacy and modern implementations against the same contract, and blocks acceptance when observable behavior drifts.

A human retains the final merge decision.

---

## Legacy → Modernization → Independent Acceptance

Aegis is **not just a PR checker**. The core product is the complete modernization control loop:

```text
LEGACY MONOLITH
      |
      v
IBM BOB — CONTRACT ARCHAEOLOGY
reconstruct executable behavioral contract
      |
      v
AEGIS — BASELINE SEAL
returns + exceptions + state + ledger + audit + idempotency + invariants
      |
      v
IBM BOB — MODERNIZATION
monolith -> modular modern candidate
      |
      v
AEGIS — TWIN-RUN VERIFICATION
legacy reference <-> same scenarios <-> modern candidate
      |
      +---- behavior matches ----------------> ACCEPTED
      |
      +---- behavior drifts -----------------> BLOCKED
                                                  |
                                                  v
                                       BEHAVIORAL COUNTEREXAMPLE
                                                  |
                                                  v
                                         IBM BOB — REPAIR
                                                  |
                                                  v
                                        AEGIS — RE-VERIFY
                                                  |
                                                  v
                                        HUMAN MERGE DECISION
```

### What is actually being compared?

Aegis does more than compare function return values. The behavioral evidence can include:

- return values
- normalized exceptions
- persistent state
- invoice and refund state transitions
- ledger effects
- audit events
- idempotency behavior
- explicit contract invariants

### Structural modernization

The hardened demonstration shows that Bob did not merely patch legacy code in place:

| Structural metric | Legacy | Modern candidate |
|---|---:|---:|
| Python modules | 1 | 11 |
| Largest module | 381 LOC | 205 LOC |
| Modern imports from `legacy_app` | — | 0 |
| Dependency cycles | 0 | 0 |

### Authentic IBM Bob execution

The preserved clean-room Bob workflow is a separate historical evidence corpus:

- **47 scenarios**
- **60 workflow steps**
- **183 invariant declarations**
- **47 / 47 ACCEPTED**
- controlled safety rehearsal: **46 / 47 BLOCKED**
- Bob diagnosis + one-line repair
- re-verification: **47 / 47 ACCEPTED**
- Tasks 1–5 captured Bobcoin total: **17.30**

The clean-room 47-case corpus and the hardened 86-case public corpus are intentionally kept separate and are never combined into a synthetic score.

---

## Real PR Proof — 30-Second Story

A real pull request looked safe.

Normal tests were green.

Aegis disagreed.

```text
GitHub PR #1
"Refactor pricing thresholds into named policy constants"
        |
        v
Aegis executes the sealed behavioral contract
        |
        v
85 / 86 matched
1 semantic drift
BLOCKED
        |
        v
VIP subtotal exactly $1000.00

Expected total : $965.25
PR total       : $997.43
Difference     : +$32.18
        |
        v
IBM Bob diagnoses the defect

>   ->   >=

        |
        v
86 / 86 ACCEPTED
        |
        v
Independent post-Bob verification
32 / 32 verifier tests
21 / 21 seeded regressions detected
0 legacy imports
0 dependency cycles
        |
        v
Repair frozen
        |
        v
24 / 24 targeted PR mutations BLOCKED
        |
        v
IBM Bob returns as READ-ONLY evidence reviewer
        |
        v
MERGE_ELIGIBLE
        |
        v
Human authorization
        |
        v
PR MERGED
```

The key idea:

> **IBM Bob repairs the PR. Aegis challenges the repair outside Bob. Bob returns as a read-only evidence reviewer. A human decides whether to merge.**

---

## Judge Quick Start

| Resource | Link |
|---|---|
| **Live application** | https://aegis-contractlock.vercel.app/ |
| **Public repository** | https://github.com/AzzamShahid/Aegis-ContractLock |
| **Real PR acceptance workflow** | [`docs/pr_acceptance/PR_ACCEPTANCE_WORKFLOW.md`](docs/pr_acceptance/PR_ACCEPTANCE_WORKFLOW.md) |
| **Bob Task 7 — detect + repair** | [`task7_bob_pr_semantic_acceptance.png`](bob_evidence/pr_acceptance/task7_bob_pr_semantic_acceptance.png) |
| **Bob Task 8 — read-only merge review** | [`task8_bob_merge_evidence_review.png`](bob_evidence/pr_acceptance/task8_bob_merge_evidence_review.png) |
| **Independent acceptance result** | [`independent-core-gate.txt`](reports/pr_acceptance/independent-core-gate.txt) |
| **PR adversarial challenge** | [`pr-adversarial-audit.md`](reports/pr_acceptance/pr-adversarial-audit.md) |
| **Behavioral verification** | [`reports/verification.md`](reports/verification.md) |
| **Architecture evidence** | [`reports/architecture-comparison.md`](reports/architecture-comparison.md) |
| **Final readiness** | [`reports/readiness.md`](reports/readiness.md) |
| **IBM Bob usage statement** | [`docs/IBM_BOB_USAGE_STATEMENT.md`](docs/IBM_BOB_USAGE_STATEMENT.md) |

### One-command verification

After installing dependencies:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\verify_submission.ps1
```

The final verifier executes **seven gates**:

```text
Security preflight
Engine tests
Contract coverage
Behavioral equality
Architecture integrity
Mutation gauntlet
Evidence readiness
```

Expected result:

```text
Security preflight         PASS
Engine tests               PASS
Contract coverage          PASS
Behavioral equality        PASS
Architecture               PASS
Mutation gauntlet          PASS
Evidence readiness         PASS
------------------------------------------------------------
FINAL: READY
```

The workflow is also executed automatically on pull requests through:

[`/.github/workflows/aegis-pr-gate.yml`](.github/workflows/aegis-pr-gate.yml)

---

## The Problem

AI coding agents can refactor legacy software much faster than traditional modernization workflows.

But speed creates a second problem:

> **Who independently decides that an AI-generated change is safe to accept?**

A green unit-test suite is useful evidence, but it can miss behavioral boundaries, state transitions, legacy side effects, or business rules that were never encoded in those tests.

This becomes especially dangerous during legacy modernization, where the implementation itself may be the only surviving description of years of accumulated behavior.

Aegis focuses on that **acceptance problem**.

---

## The Solution

Aegis ContractLock turns legacy modernization into an evidence-gated control loop and separates three authorities:

### IBM Bob — transformation authority

Bob is used to:

- investigate legacy behavior
- reconstruct behavioral contracts
- design the modernization
- implement the refactor
- diagnose detected drift
- repair the candidate
- review final evidence in read-only mode

### Aegis — acceptance authority

Aegis independently:

- executes the same contract against legacy and candidate systems
- records normalized observable evidence
- compares results, state, events, ledgers and invariants
- blocks semantic drift
- analyzes structural modernization
- challenges the verifier with seeded regressions
- produces acceptance evidence
- gates pull requests in GitHub Actions

### Human — merge authority

Aegis does **not** merge the pull request.

It determines whether the evidence is eligible for human review.

---

## Real PR Acceptance Evidence

The strongest demonstration is GitHub PR #1.

| Stage | Result |
|---|---|
| Original PR commit | `5276fa2` |
| Pre-repair acceptance | **85 / 86 — BLOCKED** |
| Failing case | `bnd_vip_subtotal_1000_00` |
| Expected discount | 10% |
| Defective PR discount | 7% |
| Expected grand total | `$965.25` |
| Defective PR grand total | `$997.43` |
| Customer-impact delta | **+$32.18** |
| Bob diagnosis | inclusive boundary regression |
| Bob repair | `>` → `>=` |
| Repair commit | `fabc7b7a3a960fd1df7b7c6e51c44a27f797f95a` |
| Repair freeze tag | `aegis-pr-repair-freeze-20260927` |
| Post-repair behavior | **86 / 86 — ACCEPTED** |
| Verifier tests | **32 / 32 PASS** |
| Curated seeded regressions | **21 / 21 detected** |
| Targeted PR challenge | **24 / 24 BLOCKED** |
| Targeted survivors | **0** |
| Bob Task 8 | `MERGE_ELIGIBLE` |
| Human merge commit | `1f79baf` |

Evidence:

- [`PR acceptance workflow`](docs/pr_acceptance/PR_ACCEPTANCE_WORKFLOW.md)
- [`Bob Task 7 capture`](bob_evidence/pr_acceptance/task7_bob_pr_semantic_acceptance.png)
- [`Bob Task 8 capture`](bob_evidence/pr_acceptance/task8_bob_merge_evidence_review.png)
- [`Independent core gate`](reports/pr_acceptance/independent-core-gate.txt)
- [`PR-specific adversarial audit`](reports/pr_acceptance/pr-adversarial-audit.md)

### Scope of the 24 / 24 result

The PR challenge is deliberately finite and specific to the pricing-policy surface changed by the PR.

It includes:

- inclusive/exclusive boundary mutations
- threshold values shifted by `$0.01`
- discount-rate changes
- tier-routing changes

All **24 runnable targeted mutations** were blocked.

That means:

> **100% detection within this finite PR-specific mutation set.**

It does **not** mean exhaustive mutation sensitivity or formal program equivalence.

---

## How Aegis Works

```text
                   SEALED BEHAVIORAL CONTRACT
                 cases + steps + invariants
                            |
              identical scenario inputs
                            |
              +-------------+-------------+
              |                           |
              v                           v
       LEGACY SYSTEM              MODERN CANDIDATE
              |                           |
              v                           v
       BASELINE EVIDENCE          CANDIDATE EVIDENCE
              |                           |
              +-------------+-------------+
                            |
                            v
                   SEMANTIC COMPARATOR
                            |
                 +----------+----------+
                 |                     |
                 v                     v
             ACCEPTED               BLOCKED
                                         |
                                         v
                             behavioral counterexample
                                         |
                                         v
                                   IBM Bob repair
```

Observable evidence includes:

- return values
- normalized exceptions
- persistent state
- invoice and refund state transitions
- ledger effects
- audit events
- idempotency behavior
- explicit contract invariants

---

## Sealed Acceptance Boundary

Aegis distinguishes **sealing** from **acceptance**.

```text
SEALING
legacy + contract
      |
      v
baseline evidence
      |
      v
sealed artifact

================ TRUST BOUNDARY ================

ACCEPTANCE
load existing baseline
      |
      v
execute candidate
      |
      v
compare evidence
      |
      +---- ACCEPTED
      |
      +---- BLOCKED
```

Readiness does not regenerate the baseline.

The hardened verifier includes a regression test proving that the baseline remains unchanged during acceptance.

The GitHub Actions PR gate additionally checks that verification does not modify the protected baseline or leave tracked evidence dirty.

---

## Current Hardened Results

| Metric | Result |
|---|---:|
| Behavioral contract scenarios | **86** |
| Workflow steps | **100** |
| Contract invariants | **231** |
| Legacy statement coverage | **100.00%** |
| Legacy branch coverage | **98.96%** |
| Behavioral acceptance | **86 / 86** |
| Behavioral drift | **0** |
| Verifier/self-validation tests | **32 / 32** |
| Curated seeded regressions | **21 / 21 detected** |
| Seeded regressions escaped | **0** |
| Modern imports from `legacy_app` | **0** |
| Modern dependency cycles | **0** |
| Submission readiness | **READY** |
| Security preflight | **PASS** |

Final hardened submission freeze:

`aegis-submission-final-hardened-20260927`

---

## Independent Challenge Results

Aegis intentionally publishes both successful and imperfect adversarial results.

### PR-specific targeted challenge

```text
24 generated
24 runnable
24 detected / BLOCKED
0 survivors
0 invalid
0 timeout
```

This challenge was created specifically around the PR's pricing-policy change surface.

### Broader historical generated holdout

A separate Antigravity-assisted post-freeze challenger produced:

```text
65 generated
63 runnable
54 detected
9 survivors
2 invalid
0 timeout
85.71% detection over runnable mutants
```

The **nine survivors remain disclosed**.

The contract was not modified afterward to make the result look perfect.

Evidence:

- [`HOLDOUT_MUTATION_METHODOLOGY.md`](docs/HOLDOUT_MUTATION_METHODOLOGY.md)
- [`generated-mutation-audit.md`](reports/generated-mutation-audit.md)
- [`VERIFIER_SELF_TEST_FINDINGS.md`](docs/VERIFIER_SELF_TEST_FINDINGS.md)
- [`TOOL_PROVENANCE.md`](docs/TOOL_PROVENANCE.md)

This is finite empirical evidence, not exhaustive proof.

---

## Trust Table

| Claim | Status |
|---|---|
| Bob performed documented modernization/repair work | **Evidenced** |
| PR defect produced 85/86 with one drift | **Measured** |
| Repair restored 86/86 behavior | **Measured** |
| 21 seeded regressions were detected | **Measured** |
| 24 PR-specific targeted mutations were blocked | **Measured within finite set** |
| Broader holdout detected 54/63 runnable mutants | **Measured** |
| Nine broader-holdout survivors exist | **Disclosed** |
| Acceptance reads rather than regenerates sealed baseline | **Enforced + tested** |
| PR verification runs automatically in GitHub Actions | **Enforced** |
| Whole-program semantic equivalence | **Not established** |
| Correctness of the legacy business policy | **Not established** |
| Detection of all future regressions | **Not established** |
| Hardened hostile-code sandboxing | **Not established** |

---

## What Aegis Demonstrates — and What It Does Not

Aegis demonstrates:

> **Behavioral equivalence across the defined contract and executed scenario corpus.**

It does not establish formal or exhaustive program equivalence.

Important limitations:

- behavior outside the contract corpus is not evaluated
- contract quality limits verifier coverage
- the demo target is a controlled in-memory billing system
- the 21-case gauntlet is a deliberately selected negative-control suite
- the PR-specific 24-case challenge is finite
- the broader generated holdout detected 54 of 63 runnable mutations and retained 9 survivors
- the current execution model is not a hardened hostile-code sandbox
- legacy-reference behavior is not independently proven to be correct business policy
- hashes are integrity fingerprints, not signatures or correctness proofs
- coverage values refer to legacy behavioral-contract coverage, not whole-repository coverage

---

## Evidence Integrity

Aegis uses SHA-256 for two different purposes.

### Semantic evidence fingerprint

A canonical fingerprint over normalized execution evidence.

It helps identify whether observable behavior represented by that evidence changed.

### Artifact/source fingerprint

A SHA-256 fingerprint of a specific artifact.

It helps detect whether that artifact changed.

A hash alone does **not** prove:

- correctness
- authorship
- provenance by a specific person
- formal equivalence
- external-storage immutability

### Counterexample terminology

Aegis reports a mismatch as a **behavioral counterexample** or **first failing behavioral counterexample**.

It does not claim mathematical minimization.

Historical preserved artifacts may contain older wording such as `MINIMAL COUNTEREXAMPLE`; those artifacts remain unchanged for provenance.

---

## IBM Bob Evidence Appendix

The real IBM Bob work is preserved separately from the hardened 86-case public verifier corpus.

## Clean-room Bob workflow

The original IBM Bob clean-room lifecycle used a separate **47-case contract**.

Its purpose was to preserve evidence that the modernization workflow itself was genuinely performed through Bob:

```text
legacy investigation
        |
contract archaeology
        |
modernization architecture
        |
implementation
        |
controlled safety rehearsal
        |
BLOCKED
        |
diagnosis + repair
        |
ACCEPTED
        |
final evidence review
```

These metrics are deliberately **not combined** with the 86-case hardened corpus.

### Bob task captures

- [`bob_sessions/final/`](bob_sessions/final/)
- [`01_contract_archaeologist.png`](bob_sessions/final/01_contract_archaeologist.png)
- [`02_modernization_architect.png`](bob_sessions/final/02_modernization_architect.png)
- [`03_modernization_executor.png`](bob_sessions/final/03_modernization_executor.png)
- [`04_drift_diagnosis_and_repair.png`](bob_sessions/final/04_drift_diagnosis_and_repair.png)
- [`05_final_evidence_review.png`](bob_sessions/final/05_final_evidence_review.png)

Additional Bob evidence:

- [`bob_evidence/`](bob_evidence/)
- [`Task 7 — PR semantic acceptance`](bob_evidence/pr_acceptance/task7_bob_pr_semantic_acceptance.png)
- [`Task 8 — merge evidence review`](bob_evidence/pr_acceptance/task8_bob_merge_evidence_review.png)
- [`IBM Bob usage statement`](docs/IBM_BOB_USAGE_STATEMENT.md)

---

## Hardened Public Evidence Appendix

| Artifact | Purpose |
|---|---|
| [`aegis_contract.yaml`](aegis_contract.yaml) | 86-case behavioral contract |
| [`reports/verification.md`](reports/verification.md) | Behavioral comparison |
| [`reports/contract-coverage.md`](reports/contract-coverage.md) | Legacy contract coverage |
| [`reports/gauntlet-report.md`](reports/gauntlet-report.md) | Curated seeded regression results |
| [`reports/architecture-comparison.md`](reports/architecture-comparison.md) | Structural modernization evidence |
| [`reports/evidence-certificate.md`](reports/evidence-certificate.md) | Evidence fingerprints |
| [`reports/readiness.md`](reports/readiness.md) | Final readiness |
| [`reports/dashboard.html`](reports/dashboard.html) | Standalone evidence dashboard |
| [`docs/CONTRACT_SCHEMA_GUIDE.md`](docs/CONTRACT_SCHEMA_GUIDE.md) | Contract format |
| [`docs/validation-fixture-provenance.md`](docs/validation-fixture-provenance.md) | Negative-control provenance |
| [`docs/TOOL_PROVENANCE.md`](docs/TOOL_PROVENANCE.md) | Tool attribution |
| [`SECURITY.MD`](SECURITY.MD) | Security model |

---

## Reproduce Locally

### Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Complete verification

```powershell
.\verify_submission.ps1
```

### Individual gates

```powershell
python -m pytest tests -q
python -m aegis.cli coverage
python -m aegis.cli verify
python -m aegis.cli architecture
python -m aegis.cli gauntlet
python -m aegis.cli readiness
```

---

## Security

Before acceptance, the master verification runs a security preflight that checks:

- `.bobignore`
- ignored `.env`
- trackable `.env.example`
- ignored `.venv`
- tracked private-key/certificate files
- tracked caches and virtual environments
- common exposed credential patterns
- local file-URI links
- local `C:\Users\<username>\...` paths
- sensitive path patterns inside evidence directories

Run directly:

```powershell
.\security_preflight.ps1
```

---

## Project Structure

```text
.github/workflows/         GitHub PR acceptance gate
aegis/                     ContractLock verifier
baseline/                  Sealed baseline evidence
legacy_app/                Legacy billing implementation
modern_app/                Modernized billing implementation
rehearsal_mutations/       Curated negative controls
generated_mutations/       Generated challenger material
reports/                   Verification evidence
docs/                      Methodology and provenance
bob_sessions/              IBM Bob task captures
bob_evidence/              Preserved Bob-generated evidence
tests/                     Verifier and modernization tests
aegis_contract.yaml        Hardened behavioral contract
verify_submission.ps1      Seven-gate submission verifier
security_preflight.ps1     Repository security gate
```

---

## Third-Party Software

Third-party dependencies retain their own licenses.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## License

Aegis ContractLock original project code and project-authored materials are licensed under the [MIT License](LICENSE).

---

## Submission Thesis

> **Most AI developer workflows optimize generation speed. Aegis ContractLock governs the full legacy-modernization lifecycle: IBM Bob reconstructs and modernizes the system; Aegis seals and independently verifies the behavior represented by the contract, detects drift, and gates acceptance; a human retains the final merge decision.**
