# Aegis ContractLock — Tool Provenance & Attribution Statement

**System:** Aegis ContractLock Modernization Engine
**Evidence Baseline:** `aegis-holdout-freeze-20260927`
**Governing Standard:** `.bobrules` and Submission Integrity Standards

---

## 1. Executive Attribution Framework

To establish clear and audit-honest attribution for judges and technical reviewers, this document delineates the four distinct phases and governing actors involved in the Aegis ContractLock lifecycle.

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                             PROVENANCE LIFECYCLE MODEL                                │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE A: IBM BOB CLEAN-ROOM HISTORICAL RUN                                            │
│ • Task 1: Contract Archaeologist (clean-room contract mining: 47 cases, 60 steps)      │
│ • Task 2: Modernization Architect (modular architecture plan and dependency DAG)       │
│ • Task 3: Modernization Executor (clean-room candidate implementation)                │
│ • Task 4: Controlled Safety Rehearsal (deliberate boundary mutation & 1-line repair)   │
│ • Task 5: Final Evidence Review (independent clean-room audit, 17.30 Bobcoins)         │
│ • Preserved Artifacts: bob_evidence/ and bob_sessions/final/                          │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE B: PRE-HOLDOUT HARDENED / PUBLIC PACKAGE                                        │
│ • Hardened contract expansion: 86 behavioral cases, 100 workflow steps, 231 invariants │
│ • Coverage optimization: 100.00% legacy statement, 98.96% legacy branch coverage       │
│ • Curated Negative Controls: 21/21 seeded regression gauntlet (100.00% detection)    │
│ • Hardened Public Architecture: 1 -> 11 modules (381 -> 205 LOC, 0 cycles, 0 imports) │
│ • Historical Status: ALREADY PRESENT at freeze boundary (aegis-holdout-freeze-20260927│
│ • Provenance Principle: Preserved as existing pre-freeze state; unassigned to current │
│   post-freeze lanes to avoid retroactive attribution.                                 │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE C: POST-FREEZE ANTIGRAVITY CHALLENGE / HARDENING                                │
│ • Lane A: Repository integrity, environment sanitization, and security hygiene        │
│ • Lane B: Verifier self-validation tests and disclosed findings                       │
│ • Lane C: Generated holdout mutation challenger (65 generated, 63 runnable, 54 detected│
│           9 survived contract, 85.71% runnable detection rate; survivors disclosed)   │
│ • Lane D: Judge UX, chronological story dashboard, trace matrix, demo.ps1             │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE D: HUMAN REVIEW / INTEGRATION / GOVERNANCE                                      │
│ • Multi-agent output review and discrepancy auditing (subagent output reconciliation) │
│ • Cryptographic Git baseline anchoring and freeze tagging                             │
│ • Final merge decisions, gate validation, and packaging                               │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Strict Non-Conflation Principles:**
> 1. Work performed during post-freeze Antigravity lanes must **never be represented as IBM Bob output**.
> 2. Historical IBM Bob clean-room evidence must **never be overwritten, retroactively altered, or merged** with later hardening corpora.
> 3. Pre-holdout package assets that existed prior to `aegis-holdout-freeze-20260927` must **never be misattributed to the post-freeze Antigravity lanes**.

---

## 2. Phase-by-Phase Attribution Detail

### Phase A: IBM Bob Clean-Room Historical Run
- **Platform:** IBM Bob (generative agent platform) executed across five sequential task-sessions.
- **Governing Constraints:** Executed within an isolated clean-room environment governed by `.bobrules`. Initial workspace state contained only `legacy_app/` and the initial verifier framework.
- **Real Clean-Room Tasks:**
  1. *Task 1 (Contract Archaeologist):* Mined `legacy_app/billing/monolith.py` to extract implicit business rules, sealing the clean-room contract (`bob_evidence/aegis_contract_bob_clean_room.yaml`: 47 cases, 60 workflow steps, 183 invariants) and legacy baseline (`bob_evidence/baseline/baseline.json`).
  2. *Task 2 (Modernization Architect):* Produced the modular architecture plan and dependency DAG (`bob_evidence/docs/modernization-plan.md`). No implementation code was written.
  3. *Task 3 (Modernization Executor):* Implemented the modernized billing application from scratch. Verified 47 / 47 cases matched (`ACCEPTED`), semantic evidence fingerprint: `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf`.
  4. *Task 4 (Controlled Safety Rehearsal & Drift Critic):* Injected a deliberate relational inclusivity regression (`subtotal >= 1000.00` to `subtotal > 1000.00`), confirmed verifier blocking (`46 / 47 BLOCKED`, counterexample `vip_exact_1000_10pct`), and applied a 1 logical-line repair restoring `47 / 47 ACCEPTED`.
  5. *Task 5 (Final Evidence Review):* Audited clean-room gates, confirming 47/47 passing cases and clean-room decoupling.
- **Captured Bobcoin Expenditure:** Total **17.30 Bobcoins** (Task 1: 4.67, Task 2: 2.15, Task 3: 5.08, Task 4: 2.25, Task 5: 3.15). Values come directly from captured IBM Bob task-session UI evidence and are not recomputed by Aegis.
- **Preserved Archive:** All original artifacts are permanently preserved under `bob_evidence/` and `bob_sessions/final/`.

### Phase B: Pre-Holdout Hardened / Public Package
- **Origin & Freeze Status:** This package was **already present at the freeze boundary** (`aegis-holdout-freeze-20260927`). Repository provenance records this state prior to the launch of post-freeze Antigravity challenger lanes. To avoid speculative or retroactive attribution, repository maintainers record these assets as the frozen pre-holdout baseline rather than attributing them to subsequent agents.
- **Package Specifications:**
  - *Hardened Contract:* 86 behavioral cases, 100 workflow steps, 231 contract invariants in `aegis_contract.yaml`.
  - *Full Coverage Gate:* 100.00% legacy statement coverage (209/209) and 98.96% legacy branch coverage (95/96) in `reports/contract-coverage.json`.
  - *Curated Negative Controls:* 21 synthetic regression mutants in `rehearsal_mutations/` and 21/21 detection rate in `reports/gauntlet-report.json`.
  - *Hardened Public Architecture:* 1 monolith (381 LOC) modernized into 11 cohesive domain modules (largest module 205 LOC), 0 legacy imports, 0 cycles in `reports/architecture-comparison.json`.
  - *Packaging & Harness:* `aegis.cli`, `aegis.readiness`, `verify_submission.ps1`, and associated reports.

### Phase C: Post-Freeze Antigravity Challenge & Hardening
- **Platform:** Google Antigravity (advanced agentic coding assistant) operating exclusively post-freeze across four targeted lanes:
  - **Lane A (Repository & Security Hygiene):** Git hygiene, artifact integrity audits, and environment path sanitization.
  - **Lane B (Verifier Self-Validation):** Verifier self-validation tests (`tests/test_rehearsal.py`), verifier adversarial audits, and disclosed findings.
  - **Lane C (Holdout Mutation Challenger):** Automated generation and execution of 65 adversarial holdout mutants against the frozen pre-holdout contract.
    - *Mutants Generated:* 65
    - *Mutants Applied:* 65
    - *Runnable Mutants:* 63 (2 unrunnable/invalid excluded)
    - *Detected Mutants:* 54
    - *Surviving Mutants:* 9 (disclosed finite-coverage boundaries, e.g., MUT-GEN-06)
    - *Raw Detection Rate:* **85.71%** over runnable mutants
    - *Methodological Rule:* The contract was frozen prior to mutant generation. Surviving mutants were documented and disclosed rather than backfitted to preserve experimental validity.
  - **Lane D (Judge UX & Evidence Story):** Story-driven dashboard (`aegis/dashboard.py`, `reports/dashboard.html`), structured summary (`reports/bob-clean-room-summary.json`), guided non-destructive demo (`demo.ps1`), end-to-end traceability matrix (`docs/TRACEABILITY_MATRIX.md`), problem/solution statement (`docs/PROBLEM_SOLUTION_STATEMENT.md`), IBM Bob usage statement (`docs/IBM_BOB_USAGE_STATEMENT.md`), and this provenance document (`docs/TOOL_PROVENANCE.md`).

### Phase D: Human Review, Integration & Governance
- **Actor:** Human Engineers & Contest Participants.
- **Responsibilities:**
  - Establishing and enforcing `.bobrules` during clean-room activities.
  - Reviewing agent and subagent outputs, including reconciling the malformed outputs encountered in Tasks 4 and 5.
  - Creating and verifying baseline freeze tags (`aegis-pre-hardening-freeze-20260927`, `aegis-holdout-freeze-20260927`).
  - Final integration, merge decisions, and submission sign-off.

---

## 3. Strict Evidence Corpus Separation

Aegis ContractLock strictly separates historical clean-room evidence from the pre-holdout public package:

| Dimension | IBM Bob Clean-Room Historical Corpus | Pre-Holdout Hardened / Public Corpus |
|---|---|---|
| **Preserved Root** | `bob_evidence/`, `bob_sessions/final/` | `reports/`, `aegis_contract.yaml`, `baseline/` |
| **Contract File** | `bob_evidence/aegis_contract_bob_clean_room.yaml` | `aegis_contract.yaml` |
| **Behavioral Cases** | **47** cases | **86** cases |
| **Workflow Steps** | **60** steps | **100** steps |
| **Contract Invariants** | **183** invariants | **231** invariants |
| **Legacy Statement Coverage** | **96.65%** (202 / 209) | **100.00%** (209 / 209) |
| **Legacy Branch Coverage** | **91.67%** (88 / 96) | **98.96%** (95 / 96) |
| **Regression Controls** | Controlled rehearsal boundary injection | **21 / 21** curated seeded controls detected |
| **Modern Architecture** | 14 analyzed modules (clean-room tree) | **11** domain modules (`modern_app/billing/`) |
| **Baseline Fingerprint** | `2d9d6ef6b3e1d972e0cf68c504083f239391e1becb939c6726fabdad6d906db5` | `2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7` |
| **Accepted Candidate Fingerprint** | `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf` | `d919b4055c09e30ee9654d92e302aa64c46195716d53525d57023e1430216c99` |
| **Blocked Rehearsal Fingerprint** | `d569d131fdbe2f23dd9943431f72c435138fa06f4cab4be5bf3959f43a5fd654` | `1ea9f7929341101d0d81b50a441e39df44bbd823ffa48176af93744ae67fd4ac` |

> [!CAUTION]
> **No Synthetic Aggregation:**
> The 47-case clean-room corpus and the 86-case hardened corpus represent two distinct evaluation scopes. They are **never aggregated, averaged, or synthesized into composite totals**. Each stands independently on its own preserved evidence.

---

## 4. Cryptographic Hash Terminology Standard

To prevent misleading claims of mathematical proof or authorship, Aegis adheres to strict hash terminology:

1. **Semantic Evidence Fingerprint:** The SHA-256 digest computed across canonicalized JSON representations of executed behavioral cases, state deltas, and invariant outcomes (excluding non-deterministic timestamp metadata). This fingerprint verifies that two runs produced identical observable runtime behavior across the contract.
2. **Artifact / Source SHA-256:** The SHA-256 digest computed across raw file bytes on disk (e.g., Python source files, YAML definitions). This hash certifies byte-for-byte file immutability.
3. **Scope Clarification:** Hashes identify evidence bundles and files. They are **never called proofs of human/agent authorship, nor proofs of complete formal program equivalence** beyond the executed scenario corpus.
