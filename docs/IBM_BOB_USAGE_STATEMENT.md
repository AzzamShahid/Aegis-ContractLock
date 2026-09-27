# Aegis ContractLock — IBM Bob Usage Statement

**System:** Aegis ContractLock Clean-Room Modernization
**Workspace:** Final IBM Bob Clean-Room Run (`bob_evidence/`, `bob_sessions/final/`)
**Governing Standard:** `.bobrules`
**Total Captured Bobcoin Expenditure:** `17.30 Bobcoins`

---

## 1. Governance & Bobcoin Provenance Declaration

All generative modernization, contract archaeology, and drift repair activities in the original historical clean room were executed using **IBM Bob**.

> [!IMPORTANT]
> **Explicit Bobcoin Provenance Declaration:**
> Bobcoin consumption values reported in this document are derived directly from captured IBM Bob task-session UI evidence (preserved in `bob_sessions/final/` and `bob_sessions/archive/`) and are **not recomputed by Aegis**. Aegis does not possess runtime token metering for external LLM platforms.

---

## 2. Real Clean-Room Tasks & Evidence Breakdown

The IBM Bob clean-room engagement comprised five distinct task-sessions. Each task was initiated with clear isolation constraints under `.bobrules`, forbidding legacy modification, baseline alteration, or external code importation.

| Task # | Task Description | Primary Bob Agent Role | Preserved Artifacts | Captured Bobcoins |
|---|---|---|---|:---:|
| **Task 1** | Contract Archaeology | Contract Archaeologist | `bob_evidence/aegis_contract_bob_clean_room.yaml`<br>`bob_evidence/baseline/baseline.json`<br>`bob_evidence/docs/contract-archaeology-report.md` | **4.67** |
| **Task 2** | Modernization Architecture | Modernization Architect | `bob_evidence/docs/modernization-plan.md` | **2.15** |
| **Task 3** | Clean-Room Modernization Implementation | Modernization Executor | Preserved candidate evidence & verification reports in `bob_evidence/reports/`<br>`bob_evidence/docs/task3-implementation-report.md` | **5.08** |
| **Task 4** | Controlled Safety Rehearsal & Drift Critic Repair | Drift Critic | `bob_evidence/reports/task4-blocked-verification.json`<br>`bob_evidence/reports/task4-repaired-verification.json`<br>`bob_evidence/docs/task4-drift-diagnosis.md`<br>`bob_evidence/docs/task4-repair-report.md` | **2.25** |
| **Task 5** | Final Evidence Review & Submission Audit | Final Evidence Reviewer | `bob_evidence/docs/task5-bob-evidence-review.md`<br>`bob_evidence/reports/task5-final-verification.json` | **3.15** |
| **Total** | **Full Clean-Room Engagement** | — | — | **17.30** |

*Note on Source Artifacts:* Root directory `modern_app/` reflects the active workspace package at the freeze boundary. Preserved historical clean-room outputs from Task 3 are audited via the frozen bundles and reports in `bob_evidence/reports/` and session screenshots in `bob_sessions/final/`.

---

## 3. Detailed Task Walkthrough & Subagent Transparency

### Task 1: Contract Archaeology (4.67 Bobcoins)
- **Objective:** Interrogate `legacy_app/billing/monolith.py` to extract implicit business rules, boundary conditions, rounding modes, and state transitions without modifying legacy source.
- **Agent Architecture:** Three parallel specialist subagents were deployed:
  - *Subagent 1 (Business Rule Miner):* Extracted tier discounts, coupons, shipping formulas, and regional tax brackets.
  - *Subagent 2 (Boundary & Failure Analyst):* Identified critical boundary values, error types, and exception precedence.
  - *Subagent 3 (State & Side-Effect Analyst):* Cataloged persistence schemas, ledger debits/credits, and audit sequencing.
- **Outcome:** Produced sealed clean-room contract with 47 behavioral cases, 60 workflow steps, and 183 invariants. Legacy baseline sealed at semantic evidence fingerprint `2d9d6ef6b3e1d972e0cf68c504083f239391e1becb939c6726fabdad6d906db5`.

### Task 2: Modernization Architecture (2.15 Bobcoins)
- **Objective:** Define a decoupled, Domain-Driven Design (DDD) architecture for the billing service with 0 legacy imports and an acyclic DAG topology.
- **Outcome:** Authored `bob_evidence/docs/modernization-plan.md`, producing the modular architecture plan and dependency DAG. Adhering strictly to clean-room rules, zero implementation code was written during this task.

### Task 3: Clean-Room Modernization Execution (5.08 Bobcoins)
- **Objective:** Implement the modern candidate from scratch using only the Bob-generated contract and architectural plan.
- **Agent Architecture:** Three implementation subagents worked under primary agent coordination:
  - *Subagent A (Foundation & Input):* Implemented domain exceptions, monetary quantization, and input validation.
  - *Subagent B (Pure Business Policies):* Implemented pricing policies, tax matrix calculations, shipping tables, and refund algorithms.
  - *Subagent C (State, Audit & Idempotency):* Implemented in-memory repository, append-only audit log manager, and idempotency cache.
- **Verification & Analysis:** Primary agent assembled orchestration service. The final AST analyzer recorded 14 analyzed modules across the clean-room package. Verified against sealed baseline:
  - **Verdict:** `ACCEPTED` (47 / 47 cases matched, 0 drifted)
  - **Candidate Semantic Evidence Fingerprint:** `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf`

### Task 4: Controlled Safety Rehearsal & Drift Critic Repair (2.25 Bobcoins)
- **Objective:** Empirically demonstrate verifier sensitivity by injecting a realistic boundary mutation, followed by AI-driven diagnosis and surgical repair.
- **Injected Regression:** Mutated relational inclusivity in `modern_app/billing/pricing.py` line 26:
  $$\text{subtotal} \ge \$1,000.00 \implies \text{subtotal} > \$1,000.00$$
- **Aegis Verification:**
  - **Verdict:** `BLOCKED` (46 / 47 matched, 1 drifted)
  - **Behavioral Counterexample:** `vip_exact_1000_10pct`
  - **Observed Impact:** VIP discount rate dropped from 10% to 7%; grand total increased from \$965.25 to \$997.43 (delta: +\$32.18 overcharge); 24 cascading pipeline diffs recorded in preserved evidence.
- **Subagent Transparency & Known Limitations (Preserved Integrity):**
  > [!WARNING]
  > During Task 4 diagnosis, three read-only diagnostic subagents were dispatched. **Diagnostic subagents A (Counterexample Analyst) and C (Minimal Patch Risk Reviewer) returned malformed/garbled output**. Subagent B (Candidate Root-Cause Investigator) succeeded.
  >
  > The primary IBM Bob agent did not rely on garbled output, did not hallucinate agreement, and **independently re-derived the diagnosis and patch risk assessment directly from the preserved BLOCKED verification evidence**. Unanimous subagent agreement is explicitly not claimed.
- **Surgical Repair:** The primary agent applied a 1 logical-line repair changing `>` back to `>=`.
- **Re-Verification:**
  - **Verdict:** `ACCEPTED` (47 / 47 matched, 0 drifted)
  - **Repaired Candidate Fingerprint:** `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf` (identical to original accepted candidate).

### Task 5: Final Evidence Review & Submission Readiness (3.15 Bobcoins)
- **Objective:** Conduct an independent multi-agent audit across all technical gates, artifacts, and evidence logs.
- **Subagent Transparency & Known Limitations (Preserved Integrity):**
  > [!WARNING]
  > During Task 5 review, **review subagent B (Workflow Provenance Auditor) returned malformed/garbled output**. Subagents A (Behavioral Evidence Auditor) and C (Verifier Adversarial Auditor) succeeded where preserved evidence supports those findings.
  >
  > The primary IBM Bob reviewer completed the provenance audit through **direct, manual file inspection of the workspace artifacts**. Unanimous multi-agent agreement is explicitly not claimed.
- **Outcome:** Confirmed all technical gates passed (`READY`), protected artifacts remained unchanged, and the clean-room run met all standards set forth in `.bobrules`.

---

## 4. Summary of Preserved Limitations

To uphold strict audit honesty, the following constraints remain true of the IBM Bob clean-room run:
1. **Scenario Scope:** The Bob clean-room run was evaluated against the 47-scenario contract (60 workflow steps, 183 invariants, 96.65% statement coverage, 91.67% branch coverage).
2. **Subagent Output Anomalies:** LLM subagent orchestration experienced malformed responses in Tasks 4 and 5; resilience was achieved via primary agent fallback, direct file inspection, and independent evidence re-derivation.
3. **Evidence Corpus Separation:** The 47-scenario clean-room evidence is permanently preserved under `bob_evidence/` and `bob_sessions/final/` and is strictly decoupled from the expanded 86-scenario pre-holdout hardened package.
