# IBM Bob Task 2 — Modernization Architect

You are the **Modernization Architect** for Aegis ContractLock.

Task 1 has already reconstructed and sealed the legacy application's behavioral contract.

Your job now is to design a maintainable replacement architecture **without changing implementation yet**.

## Inputs

Analyze:

- `@legacy_app/billing/monolith.py`
- `@aegis_contract.yaml`
- `@docs/contract-archaeology-report.md`
- `@reports/contract-coverage.md`
- `@.bobrules`

The current behavioral baseline is already sealed.

Do not modify:

- `legacy_app/`
- `aegis_contract.yaml`
- `baseline/`
- Aegis verification logic

---

# Objective

Design a modular replacement for the legacy billing monolith while preserving the observable behavioral contract discovered in Task 1.

The modern implementation must eventually live under:

`modern_app/`

but this task is architecture/planning only.

Do not perform the full implementation yet.

---

# Specialized analysis

Use specialized subagents where useful.

## Subagent A — Responsibility Decomposer

Identify every responsibility currently mixed inside the legacy implementation.

Examples to investigate from the actual source include:

- public execution/API boundary;
- validation;
- monetary normalization/rounding;
- tier-discount rules;
- volume-discount rules;
- coupon handling;
- tax calculation by region and category;
- shipping rules;
- payment-method fee handling;
- invoice persistence;
- refund policy, refund fee calculation, and window enforcement;
- ledger debit/credit side effects;
- audit event generation;
- idempotency tracking.

Map which responsibilities belong together and which must be separated.

## Subagent B — Dependency & Boundary Architect

Design a modular target layout under:

`modern_app/billing/`

Define clear domain boundaries.

Establish:

- module responsibilities;
- import direction (unidirectional, zero circular dependencies);
- state ownership;
- persistence abstraction (repository pattern);
- event/audit emission decoupling;
- public interface preservation:
  - factory: `modern_app.billing.api:create_service`
  - service interface: `execute(operation, payload)` and `snapshot_state()`.

Strict constraint: `modern_app` must **never import or delegate to `legacy_app`**.

## Subagent C — Behavioral Invariant Guardian

Audit the discovered contract and legacy implementation for high-risk modernization hazards:

- exact rounding mode per calculation step (HALF_UP vs HALF_EVEN);
- decimal precision preservation;
- strict equality vs inequality boundary conditions;
- coupon stacking order and caps;
- multi-line tax allocation and residual distribution;
- refund window boundary hours and fee calculation;
- ledger balance invariants (debits == credits);
- audit log event payload schemas and ordering.

Specify how the target architecture guarantees these invariants will not drift during implementation.

---

# Deliverable

Produce a comprehensive architecture plan at:

`docs/modernization-plan.md`

Include:
1. Executive Summary & Architectural Goals
2. Legacy Monolith Analysis (LOC, coupling, responsibilities)
3. Target Module Decomposition & Interface Contracts
4. Dependency Flow Diagram & Circular Dependency Prevention
5. Invariant & Precision Preservation Strategy
6. State, Persistence & Idempotency Design
7. Task 3 Implementation Roadmap & Verification Gate
