# Aegis ContractLock

> **Evidence-gated AI legacy modernization with IBM Bob**

[![Aegis Gate](https://img.shields.io/badge/Aegis%20Gate-READY-brightgreen)](#judge-quick-start)
[![Legacy Contract Coverage](https://img.shields.io/badge/Legacy%20Contract%20Coverage-100%25%20Statements-brightgreen)](reports/contract-coverage.md)
[![Branch Coverage](https://img.shields.io/badge/Branches-98.96%25-brightgreen)](reports/contract-coverage.md)
[![Mutation Audit](https://img.shields.io/badge/Seeded%20Regressions-21%2F21%20Detected-blue)](reports/gauntlet-report.md)
[![IBM Bob](https://img.shields.io/badge/IBM%20Bob-5%20Captured%20Sessions-informational)](bob_sessions/final/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI can refactor legacy software quickly. The harder question is:
> **How do we know the modernization did not silently change the business?**

Aegis ContractLock separates **generation** from **acceptance**. **IBM Bob reasons about and transforms the system. Aegis independently executes the legacy and modern implementations against a sealed behavioral contract and decides whether the candidate can be accepted.**

---

# Judge Quick Start

If you have only a few minutes, inspect these in order:

| What to inspect | Location |
|---|---|
| Real IBM Bob task captures | [`bob_sessions/final/`](bob_sessions/final/) |
| Bob clean-room evidence review | [`bob_evidence/docs/task5-bob-evidence-review.md`](bob_evidence/docs/task5-bob-evidence-review.md) |
| Hardened behavioral contract | [`aegis_contract.yaml`](aegis_contract.yaml) |
| Hardened verification report | [`reports/verification.md`](reports/verification.md) |
| Mutation audit | [`reports/gauntlet-report.md`](reports/gauntlet-report.md) |
| Architecture comparison | [`reports/architecture-comparison.md`](reports/architecture-comparison.md) |
| Final readiness report | [`reports/readiness.md`](reports/readiness.md) |
| Interactive evidence dashboard | [`reports/dashboard.html`](reports/dashboard.html) |

### Fast reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests
python -m aegis.cli coverage
python -m aegis.cli verify
python -m aegis.cli architecture
python -m aegis.cli gauntlet
python -m aegis.cli readiness
```

Expected final state:
```text
Behavioral verification  ACCEPTED
Architecture             PASS
Mutation audit           PASS
Readiness                READY
```

---

## The 60-Second Story

The central demonstration is deliberately simple.

```text
IBM Bob modernization
       │
       ▼
 47 / 47 behavioral contract cases ACCEPTED
       │
       │  Controlled Safety Rehearsal
       │  one-character semantic regression
       │  >= → >
       ▼
 46 / 47 BLOCKED
       │
       ▼
 First failing behavioral counterexample
 VIP customer subtotal = $1000.00
 Legacy discount rate 10%
 Regressed candidate 7%
 Legacy grand total $965.25
 Candidate grand total $997.43
 Difference $32.18
       │
       ▼
 IBM Bob Drift Critic
 pricing.py 1 logical line repaired
       │
       ▼
 47 / 47 ACCEPTED
 Original accepted semantic evidence fingerprint restored
```

The point is not that the injected regression was difficult to write.
The point is that Aegis independently detected the semantic drift, produced a concrete behavioral counterexample, and gave IBM Bob enough evidence to repair the candidate without weakening the contract, baseline, legacy source, or verifier.

---

## Real IBM Bob Clean-Room Run

The repository contains a separate, genuine IBM Bob clean-room reproduction of the workflow.

This evidence was produced in:
`AEGIS_BOB_FINAL_RUN`

and is preserved under:
`bob_evidence/`
`bob_sessions/final/`

### Captured IBM Bob workflow

| Stage | Result |
|---|---|
| Task 1 — Contract Archaeologist | Bob independently reconstructed a 47-case behavioral contract |
| Task 2 — Modernization Architect | Bob designed the modular target architecture |
| Task 3 — Modernization Executor | Bob implemented the candidate; 47/47 ACCEPTED |
| Controlled Safety Rehearsal | Intentional `>=` → `>` regression; 46/47 BLOCKED |
| Task 4 — Drift Critic & Repair | Bob diagnosed and repaired one logical line; 47/47 ACCEPTED |
| Task 5 — Final Evidence Review | Re-ran technical gates and reconciled the evidence chain |

### Clean-room contract evidence

| Metric | Result |
|---|---|
| Behavioral contract cases | 47 |
| Unique case IDs | 47 |
| Workflow steps | 60 |
| Invariant declarations | 183 |
| Baseline invariant failures | 0 |
| Legacy statement coverage | 96.65% |
| Legacy branch coverage | 91.67% |
| Readiness | READY |

### Clean-room modernization evidence

| Metric | Result |
|---|---|
| Initial modernization | 47 / 47 ACCEPTED |
| Controlled regression | 46 / 47 BLOCKED |
| Repaired modernization | 47 / 47 ACCEPTED |
| Modern imports from legacy | 0 |
| Dependency cycles | 0 |
| Legacy analyzed modules | 1 |
| Modern analyzed modules | 14 |
| Largest legacy module | 381 LOC |
| Largest modern module | 147 LOC |

### Semantic evidence lifecycle

```text
Task 3 accepted
f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf
       ↓
Controlled regression BLOCKED
d569d131fdbe2f23dd9943431f72c435138fa06f4cab4be5bf3959f43a5fd654
       ↓  One-line Bob repair
Task 4 repaired
f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf
```

The repaired candidate returned to the same semantic evidence fingerprint as the originally accepted Bob candidate.

> SHA-256 values here are evidence/integrity fingerprints. They are not proofs of correctness, digital signatures, or authorship claims.

### IBM Bob captures

- [`01_contract_archaeologist.png`](bob_sessions/final/01_contract_archaeologist.png)
- [`02_modernization_architect.png`](bob_sessions/final/02_modernization_architect.png)
- [`03_modernization_executor.png`](bob_sessions/final/03_modernization_executor.png)
- [`04_drift_critic_repair.png`](bob_sessions/final/04_drift_critic_repair.png)
- [`05_final_evidence_review.png`](bob_sessions/final/05_final_evidence_review.png)

The five captured task-session UIs show a combined 17.30 Bobcoins.
Bobcoin values come from IBM Bob UI captures and are not recomputed by Aegis.

For subagent-output limitations and full provenance disclosure, see:
[`bob_evidence/docs/task5-bob-evidence-review.md`](bob_evidence/docs/task5-bob-evidence-review.md)

---

## Hardened Public Validation Package

The root repository is the broader hardened validation package.
It is intentionally separate from the 47-case IBM Bob clean-room run.

| Metric | Hardened Result |
|---|---|
| Behavioral contract cases | 86 |
| Workflow steps | 100 |
| Contract invariants | 231 |
| Legacy statement coverage | 100.00% |
| Legacy branch coverage | 98.96% |
| Modernization verification | 86 / 86 ACCEPTED |
| Seeded semantic regressions | 21 |
| Regressions detected | 21 / 21 |
| Modern imports from legacy | 0 |
| Dependency cycles | 0 |
| Overall readiness | READY |

### Why two evidence tracks?

They answer different questions.

#### IBM Bob clean-room run
Demonstrates that the modernization lifecycle was genuinely executed in IBM Bob:
> legacy system → contract archaeology → architecture → implementation → independent rejection → diagnosis → repair → re-verification

#### Hardened public validation package
Provides a broader contract corpus and additional verifier-validation fixtures:
- 86 behavioral contract cases
- 100 workflow steps
- 231 invariants
- 21 seeded negative controls

The two corpora are deliberately not merged into synthetic metrics.
The IBM Bob clean-room run and the separately hardened public validation package are distinct evidence corpora. Their metrics and fingerprints remain separately attributed.

---

## How Aegis Works

```text
                     AEGIS CONTRACTLOCK
                ┌────────────────────────────┐
                │    Behavioral Contract     │
                │ cases + steps + invariants │
                └──────────────┬─────────────┘
                               │ identical scenario inputs
               ┌───────────────┴────────────────┐
               │                                │
               ▼                                ▼
    ┌────────────────────────┐      ┌────────────────────────┐
    │     Legacy System      │      │    Modern Candidate    │
    │   legacy_app.billing   │      │   modern_app.billing   │
    └────────────┬───────────┘      └────────────┬───────────┘
                 │                               │
                 ▼                               ▼
    ┌────────────────────────┐      ┌────────────────────────┐
    │   Baseline Evidence    │      │   Candidate Evidence   │
    │  results + state +     │      │  results + state +     │
    │    ledger + audit      │      │    ledger + audit      │
    └────────────┬───────────┘      └────────────┬───────────┘
                 │                               │
                 └──────────────┬────────────────┘
                                ▼
                    ┌─────────────────────┐
                    │ Semantic Comparator │
                    │ + invariant engine  │
                    └──────────┬──────────┘
                               │
                      ┌────────┴────────┐
                      ▼                 ▼
                  ACCEPTED           BLOCKED
                                        │
                                        ▼
                            Behavioral counterexample
                                        │
                                        ▼
                                 IBM Bob repair
```

Aegis compares observable behavior including:
- return values
- normalized exceptions
- persistent state
- invoice/refund state transitions
- ledger effects
- audit events
- idempotency behavior
- explicit contract invariants

---

## Architecture Evolution

The hardened public package modernizes the billing monolith into an isolated modular design.

| Architectural Dimension | Legacy | Hardened Modern |
|---|---:|---:|
| Analyzed Python modules | 1 | 11 |
| Largest module LOC | 381 | 205 |
| Total non-comment LOC | 381 | 453 |
| Functions | 12 | 32 |
| Classes | 6 | 8 |
| Internal dependency edges | 0 | 18 |
| Dependency cycles | 0 | 0 |
| Imports from legacy_app | N/A | 0 |

### Hardened modern modules

`modern_app/billing/`
- `api.py` — public facade
- `service.py` — workflow orchestration
- `pricing_policy.py` — stepped tier discounts and coupon rules
- `tax_policy.py` — regional/category tax rules
- `shipping_policy.py` — shipping thresholds
- `refund_policy.py` — refund policy
- `storage.py` — isolated in-memory persistence
- `events.py` — audit events
- `money.py` — deterministic decimal handling
- `errors.py` — domain exceptions
- `__init__.py` — public package interface

---

## Judge Evidence Map

### IBM Bob clean-room evidence

| Artifact | Purpose |
|---|---|
| [`bob_sessions/final/`](bob_sessions/final/) | Five genuine IBM Bob task captures |
| [`bob_evidence/aegis_contract_bob_clean_room.yaml`](bob_evidence/aegis_contract_bob_clean_room.yaml) | Bob-generated 47-case contract |
| [`bob_evidence/docs/contract-archaeology-report.md`](bob_evidence/docs/contract-archaeology-report.md) | Bob contract reconstruction |
| [`bob_evidence/docs/modernization-plan.md`](bob_evidence/docs/modernization-plan.md) | Bob architecture plan |
| [`bob_evidence/docs/task3-implementation-report.md`](bob_evidence/docs/task3-implementation-report.md) | Bob implementation evidence |
| [`bob_evidence/reports/task4-blocked-verification.md`](bob_evidence/reports/task4-blocked-verification.md) | Preserved BLOCKED result |
| [`bob_evidence/docs/task4-drift-diagnosis.md`](bob_evidence/docs/task4-drift-diagnosis.md) | Drift diagnosis |
| [`bob_evidence/docs/task4-repair-report.md`](bob_evidence/docs/task4-repair-report.md) | One-line repair evidence |
| [`bob_evidence/reports/task4-repaired-verification.md`](bob_evidence/reports/task4-repaired-verification.md) | Repaired ACCEPTED result |
| [`bob_evidence/docs/task5-bob-evidence-review.md`](bob_evidence/docs/task5-bob-evidence-review.md) | Final clean-room evidence audit |

### Hardened public validation evidence

| Artifact | Purpose |
|---|---|
| [`aegis_contract.yaml`](aegis_contract.yaml) | 86-case behavioral contract |
| [`docs/CONTRACT_SCHEMA_GUIDE.md`](docs/CONTRACT_SCHEMA_GUIDE.md) | Contract schema |
| [`docs/contract-archaeology-report.md`](docs/contract-archaeology-report.md) | Hardened archaeology report |
| [`docs/modernization-plan.md`](docs/modernization-plan.md) | Architecture plan |
| [`docs/controlled-safety-rehearsal.md`](docs/controlled-safety-rehearsal.md) | Controlled regression record |
| [`docs/verifier-adversarial-audit.md`](docs/verifier-adversarial-audit.md) | Mutation audit |
| [`docs/validation-fixture-provenance.md`](docs/validation-fixture-provenance.md) | Fixture provenance |
| [`docs/final-evidence-review.md`](docs/final-evidence-review.md) | Hardened final review |
| [`reports/contract-coverage.md`](reports/contract-coverage.md) | Legacy behavioral-contract coverage |
| [`reports/architecture-comparison.md`](reports/architecture-comparison.md) | Structural comparison |
| [`reports/gauntlet-report.md`](reports/gauntlet-report.md) | 21-regression detection matrix |
| [`reports/readiness.md`](reports/readiness.md) | Automated readiness gate |
| [`reports/evidence-certificate.md`](reports/evidence-certificate.md) | Evidence fingerprints and zero-drift result |
| [`reports/dashboard.html`](reports/dashboard.html) | Standalone evidence dashboard |

---

## One-Command Judge Verification

After installing the dependencies, a judge can validate the complete hardened submission with one command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\verify_submission.ps1
```

`verify_submission.ps1` runs all six submission gates:

```text
Engine tests
Contract coverage
Behavioral equality
Architecture integrity
Mutation gauntlet
Evidence readiness
```

Expected final result:

```text
Engine tests               PASS
Contract coverage          PASS
Behavioral equality        PASS
Architecture               PASS
Mutation gauntlet          PASS
Evidence readiness         PASS
------------------------------------------------------------
FINAL: READY
```

The script temporarily backs up generated evidence artifacts and restores them after verification, so running the judge check does not permanently rewrite the sealed submission evidence.

---
## Reproduction Commands

### Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run engine tests
```powershell
python -m pytest tests
```
*Expected:*
```text
7 passed
```

### Measure legacy behavioral-contract coverage
```powershell
python -m aegis.cli coverage
```
*Expected hardened package result:*
```text
Statement coverage: 100.00%
Branch coverage: 98.96%
```

### Verify hardened modern candidate
```powershell
python -m aegis.cli verify
```
*Expected:*
```text
86 / 86 matched
VERDICT: ACCEPTED
```

### Run architecture analysis
```powershell
python -m aegis.cli architecture
```
*Expected:*
```text
Modern modules: 11
Modern imports from legacy: 0
Dependency cycles: 0
```

### Run verifier mutation audit
```powershell
python -m aegis.cli gauntlet
```
*Expected:*
```text
Seeded regressions: 21
Detected: 21
Escaped: 0
```

### Run complete readiness gate
```powershell
python -m aegis.cli readiness
```
*Expected:*
```text
SUBMISSION READINESS: READY
```

---

## Testing Layers

Aegis deliberately separates three different types of evidence.

### 1. Behavioral-contract validation
- 86 behavioral contract cases
- 100 workflow steps
- 231 explicit invariants

This evaluates observable legacy-versus-modern behavior.

### 2. Aegis engine test suite
- 7 automated tests

These exercise verification infrastructure and integration behavior.

### 3. Verifier mutation audit
- 21 seeded semantic regressions
- 21 detected
- 0 escaped

These negative controls test whether the verifier can go red when known business semantics are altered.

The mutation audit is a seeded negative-control suite, not an automatically generated exhaustive mutation score.

---

## Evidence Integrity

Aegis uses SHA-256 in several places.

The terminology matters:

- **Semantic evidence fingerprint**: A canonical fingerprint over normalized execution evidence. Used to compare observable behavior while excluding metadata such as timestamps.
- **Artifact / source fingerprint**: A SHA-256 value used to detect whether a specific artifact changed.

### Counterexample terminology

Aegis presents a detected mismatch as a **behavioral counterexample** (or first failing behavioral counterexample). It does not claim mathematical minimization of that counterexample.

Historical preserved verification artifacts may retain older renderer wording such as `MINIMAL COUNTEREXAMPLE`. Those files are intentionally preserved as historical evidence rather than rewritten after the fact; the public submission terminology is **behavioral counterexample**.

### What SHA-256 does not establish
A hash alone does not prove:
- correctness
- authorship
- provenance by a specific person
- formal program equivalence
- immutability of an external storage system

It provides a deterministic integrity/evidence fingerprint relative to the recorded artifact or canonical semantic payload.

---

## What Aegis Demonstrates — and What It Does Not

Aegis demonstrates:
- Behavioral equivalence across the defined contract and executed scenario corpus.

It does not establish formal or exhaustive program equivalence.

Important limitations:
- behavior outside the contract corpus is not evaluated
- contract quality limits verifier coverage
- the demo target is a controlled in-memory billing system
- the hardened mutation audit uses deliberately selected negative controls
- the current candidate execution model is not a hardened hostile-code sandbox
- hashes are integrity fingerprints, not signatures or correctness proofs
- coverage values refer specifically to legacy behavioral-contract coverage, not whole-repository test coverage

This scope is intentional and explicitly documented.

---

## Clean-Room and Fixture Provenance

The modernization workflow and verifier-validation fixtures are kept conceptually separate.

The hardened submission package documents that mutation fixtures were introduced as negative controls for verifier validation, not as an answer key for the modernization agent.

See:
[`docs/validation-fixture-provenance.md`](docs/validation-fixture-provenance.md)

The genuine IBM Bob run is preserved independently under:
[`bob_evidence/`](bob_evidence/)

This prevents its 47-case clean-room metrics from being confused with the broader 86-case hardened corpus.

---

## Project Structure

```text
Aegis-ContractLock/
│
├── aegis/                          # Verification engine
├── legacy_app/                     # Legacy billing monolith
├── modern_app/                     # Hardened modular modernization
├── baseline/                       # Hardened semantic baseline
├── tests/                          # Aegis engine tests
├── rehearsal_mutations/            # Seeded negative controls
│
├── bob_prompts/                    # IBM Bob workflow prompts
├── bob_sessions/
│   ├── final/                      # 5 genuine final Bob captures
│   └── archive/                    # Historical exploratory captures
│
├── bob_evidence/                   # Separate IBM Bob clean-room corpus
│   ├── aegis_contract_bob_clean_room.yaml
│   ├── baseline/
│   ├── docs/
│   └── reports/
│
├── docs/                           # Hardened engineering/audit reports
├── reports/                        # Hardened generated evidence
│
├── aegis_contract.yaml             # Hardened 86-case contract
├── requirements.txt
├── verify_submission.ps1           # One-command submission verification
├── .bobrules
├── .gitignore
├── THIRD_PARTY_NOTICES.md
├── LICENSE                         # MIT License
└── README.md
```

---

## Third-Party Software

Third-party dependencies retain their own licenses.

See:
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

---

## License

Aegis ContractLock original project code and project-authored materials are licensed under the [MIT License](LICENSE).

---

## Submission Thesis

Most AI developer workflows optimize generation speed. Aegis focuses on the acceptance problem: IBM Bob transforms the system; Aegis independently checks whether that transformation preserved the behavior represented by the sealed contract.
