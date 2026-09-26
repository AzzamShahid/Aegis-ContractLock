# Modernization Plan — Aegis ContractLock Billing System

**Date:** Task 2 Architecture (Modernization Architect)
**Sources inspected:**
- `legacy_app/billing/monolith.py`
- `legacy_app/docs/BILLING_POLICY.md`
- `aegis_contract.yaml`
- `docs/contract-archaeology-report.md`
- `reports/contract-coverage.md`
- `aegis/architecture.py` (for compatibility interface)
- `aegis/runner.py` (for compatibility interface)
- `.bobrules` (governance constraints)

**Methodology:** Three parallel subagents (Responsibility Decomposer, Dependency & Boundary Architect, Behavioral Risk Guardian) analyzed the legacy source and contract independently. Findings were then reconciled into this plan.

---

## 1. Current Monolith Assessment

### Physical structure

| Metric | Value | Method |
|--------|-------|--------|
| Total source lines (including blanks) | 469 | PowerShell line count of `monolith.py` |
| Non-blank, non-comment LOC | 381 | Lines where `line.strip() != ""` and not starting with `#` (Aegis `analyze_python_tree` method) |
| Python modules | 1 | `monolith.py` only |
| Python classes | 1 | `LegacyBillingSystem` |
| Python functions | 9 | `_money`, `_money_s`, `__init__`, `execute`, `snapshot_state`, `_create_invoice`, `_discount_rate`, `_shipping`, `_calculate_tax`, `_refund_invoice`, `_emit` (11 including module-level) |
| Factory function | 1 | `create_service()` |

**LOC counting method:** Non-blank, non-comment physical source lines, consistent with the `aegis/architecture.py` `analyze_python_tree` counter. All LOC figures in this document use this method unless explicitly noted otherwise.

### Major responsibilities (21 distinct, currently tangled)

| # | Responsibility |
|---|----------------|
| R1 | Input validation — operation_id, customer fields, item schema |
| R2 | Idempotency enforcement — cache lookup and result replay |
| R3 | Line-item computation — qty × unit_price with ROUND_HALF_UP per line |
| R4 | Subtotal aggregation — sum of rounded line totals |
| R5 | Tier discount lookup — stepped rate table by tier and subtotal band |
| R6 | Coupon adjustment — WELCOME10 (pct additive) and FIXED25 (flat conditional) |
| R7 | Combined discount computation — merge tier + coupon with ROUND_HALF_EVEN |
| R8 | Shipping resolution — region × pre-discount subtotal threshold table |
| R9 | Tax computation — proportional discount allocation, per-line tax, residual correction |
| R10 | Service fee computation — CARD surcharge when conditions met, ROUND_HALF_UP |
| R11 | Grand-total assembly — discounted_subtotal + shipping + tax + service_fee, ROUND_HALF_UP |
| R12 | Invoice record creation and in-memory persistence |
| R13 | Ledger DEBIT write — append-only on invoice creation |
| R14 | Refund eligibility and status determination — hours_since_purchase → APPROVED/MANUAL_REVIEW |
| R15 | Refund fee and amount computation — ROUND_HALF_EVEN on fee, ROUND_HALF_UP on amount |
| R16 | Invoice status mutation — OPEN → REFUNDED on APPROVED refund |
| R17 | Ledger CREDIT write — append-only on APPROVED refund |
| R18 | Refund record creation and in-memory persistence |
| R19 | Audit event emission — seq-numbered, append-only |
| R20 | Operation dispatch — route `execute()` string to internal handler |
| R21 | State snapshot export — deep-copy of all stores |

### Mutable state stores (5, all in-memory)

| Store | Type | Mutation pattern |
|-------|------|-----------------|
| `_invoices` | `Dict[str, Dict]` | Write on create; in-place status mutation on approved refund |
| `_refunds` | `Dict[str, Dict]` | Write on refund record creation |
| `_ledger` | `List[Dict]` | Append-only (DEBIT and CREDIT entries) |
| `_audit` | `List[Dict]` | Append-only (all event types) |
| `_idempotency` | `Dict[str, Dict]` | Write after each successful operation; read at start of each operation |
| `_audit_seq` | `int` | Increment on each audit emission |

Note: `_idempotency` and `_audit_seq` are intentionally excluded from `snapshot_state()`.

### Public operations

| Operation string | Handler |
|------------------|---------|
| `"create_invoice"` | `_create_invoice(payload)` |
| `"refund_invoice"` | `_refund_invoice(payload)` |
| Any other | Raises `ValidationError("Unsupported operation: ...")` |

### Coupling concerns

- All 21 responsibilities are implemented inside a single class with no internal module boundary.
- Idempotency read and write are woven into each handler rather than wrapped by the dispatcher.
- Audit emission is called as a side-effect inside business handlers rather than by the coordinator.
- Policy computations (discount, tax, shipping, fee) share the same code scope as persistence and state mutation.
- Rounding modes vary across 5 operations and are applied inline without named constants or isolated helpers.

---

## 2. Proposed Modern Architecture

The structure is derived from the 21 responsibilities and the 5 mutable state stores. No module count was predetermined.

```
modern_app/
└── billing/
    ├── __init__.py          (entry point — exposes create_service())
    ├── errors.py            (domain exception hierarchy)
    ├── money.py             (Decimal helpers and MONEY constant)
    ├── validation.py        (payload schema and business-rule validation)
    ├── pricing.py           (line totals, subtotal, tier discount, coupon, combined discount)
    ├── shipping_policy.py   (region × pre-discount subtotal → shipping charge)
    ├── tax_policy.py        (proportional discount allocation, per-line tax, residual)
    ├── fee_policy.py        (CARD service fee conditional)
    ├── refund_policy.py     (hours → status, refund fee and amount computation)
    ├── invoice_store.py     (invoice + refund records, ledger, grand-total assembly)
    ├── audit.py             (append-only seq-numbered audit log)
    ├── idempotency.py       (keyed result cache)
    └── billing_service.py   (coordinator / façade: execute() + snapshot_state())
```

Total proposed modules: **13** (12 source files + 1 `__init__.py`)

### Module specifications

#### `errors.py`
- **Responsibility:** Define the domain exception hierarchy with `code` class attributes.
- **Inputs:** None (class definitions only)
- **Outputs:** Exception classes: `BillingError`, `ValidationError`, `AccountSuspendedError`, `InvoiceNotFoundError`, `RefundAlreadyProcessedError`
- **Allowed dependencies:** None (foundation layer — no imports from this package)
- **Prohibited:** Must not import any other `modern_app` module; must not import `legacy_app`
- **Notes:** Exception class names, `code` attribute values, and exception message patterns must match legacy exactly, because Aegis normalizes exceptions via `type(exc).__name__` and `getattr(exc, "code", ...)`.

#### `money.py`
- **Responsibility:** Provide the `MONEY` quantizer constant and the two helper functions `_money()` and `_money_s()` with their exact rounding semantics.
- **Inputs:** Raw numeric values
- **Outputs:** `Decimal` values quantized to 0.01
- **Allowed dependencies:** `errors.py` (foundation layer only; stdlib `decimal` only)
- **Prohibited:** Must not import any policy or storage module
- **Notes:** `_money()` defaults to `ROUND_HALF_UP`. `_money_s()` always applies `ROUND_HALF_UP`. These are the only two shared monetary helpers; all other rounding decisions are made inline in the policy module that owns the operation.

#### `validation.py`
- **Responsibility:** Parse and validate raw payload dicts for both `create_invoice` and `refund_invoice` operations. Raise typed errors on any invalid input. Return nothing on success (caller proceeds; validated fields extracted inline in coordinator).
- **Inputs:** Raw `payload: dict`, `operation: str`
- **Outputs:** Raises `ValidationError` or `AccountSuspendedError` on any violation; returns nothing (or a typed data object) on success
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not access any state store; must not import policy modules; must not import `legacy_app`
- **Notes:** Validation is ordered: field presence → enum validity → business constraint. All validation must complete before any state mutation occurs (atomicity).

#### `pricing.py`
- **Responsibility:** Pure pricing arithmetic — compute line totals, subtotal, tier discount rate, coupon adjustment, combined discount, and discounted subtotal. No I/O or state.
- **Inputs:** `items: list[dict]`, `tier: str`, `subtotal: Decimal` (or items list to compute from), `coupon: str | None`
- **Outputs:** `PricingResult` (namedtuple or dataclass): `normalized_lines`, `subtotal`, `discount_rate`, `combined_discount`, `discounted_subtotal`
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import any storage or orchestration module; must not import `legacy_app`; must not perform I/O
- **Notes:** Contains R3, R4, R5, R6, R7. Discount rate lookup (`_discount_rate` equivalent) is a function within this module. Coupon resolution and combination are functions within this module. Rounding: line totals ROUND_HALF_UP, pct_discount ROUND_HALF_EVEN, combined discount ROUND_HALF_EVEN.

#### `shipping_policy.py`
- **Responsibility:** Stateless lookup — region × pre-discount subtotal → shipping charge.
- **Inputs:** `region: str`, `pre_discount_subtotal: Decimal`
- **Outputs:** `shipping: Decimal`
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import any other policy module; must not import storage or orchestration modules; must not import `legacy_app`
- **Notes:** Threshold is based on **pre-discount subtotal** (critical — see Section 7). Returns exact Decimal values (12.00, 18.00, 35.00, 0.00).

#### `tax_policy.py`
- **Responsibility:** Per-line tax computation with proportional discount allocation and residual correction.
- **Inputs:** `region: str`, `lines: list[dict]` (with `line_total` and `category`), `subtotal: Decimal`, `total_discount: Decimal`
- **Outputs:** `(total_tax: Decimal, tax_breakdown: list[dict])`
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import pricing, shipping, fee, or refund modules; must not import storage; must not import `legacy_app`
- **Notes:** Proportional allocation: all lines except last use ROUND_HALF_EVEN; last line receives residual. Per-line taxable base uses ROUND_HALF_UP. Per-line tax uses ROUND_HALF_UP. Tax rates are constants inside this module.

#### `fee_policy.py`
- **Responsibility:** Compute CARD service fee — single conditional with one rounding step.
- **Inputs:** `payment_method: str`, `discounted_subtotal: Decimal`
- **Outputs:** `service_fee: Decimal`
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import any other policy module; must not import storage; must not import `legacy_app`
- **Notes:** Threshold uses **discounted subtotal** (post-discount — critical distinction from shipping). Fee = `discounted_subtotal × 0.015`, ROUND_HALF_UP.

#### `refund_policy.py`
- **Responsibility:** Determine refund status and compute refund fee and net refund amount.
- **Inputs:** `hours_since_purchase: int`, `original_total: Decimal`
- **Outputs:** `status: str` (APPROVED/MANUAL_REVIEW), `fee_rate: Decimal`, `fee: Decimal`, `refund_amount: Decimal`
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import any other policy module; must not access any state store; must not import `legacy_app`
- **Notes:** Fee uses ROUND_HALF_EVEN (NOT ROUND_HALF_UP). Refund amount uses ROUND_HALF_UP. MANUAL_REVIEW always has refund_amount = 0.00. All thresholds are inclusive (`<=`).

#### `invoice_store.py`
- **Responsibility:** Own the three persistent state stores (`_invoices`, `_refunds`, `_ledger`). Assemble grand total. Write invoice and refund records. Append ledger entries. Expose read methods to coordinator.
- **Inputs:** Computed pricing, tax, shipping, fee values; customer metadata; refund decision; invoice dict for status mutation
- **Outputs:** Invoice dict, refund dict, ledger entries (appended in-place); state snapshot data
- **Allowed dependencies:** `errors.py`, `money.py`
- **Prohibited:** Must not import any policy module (pricing, tax, shipping, fee, refund); must not import audit or idempotency; must not import `legacy_app`
- **Notes:** Grand total assembled here using ROUND_HALF_UP on the sum of components. Invoice status mutation (`"REFUNDED"`) occurs in this module, not in the coordinator. Contains R11, R12, R13, R16, R17, R18.

#### `audit.py`
- **Responsibility:** Maintain the append-only, seq-numbered audit log.
- **Inputs:** `event_type: str`, `data: dict`
- **Outputs:** Side effect (append to `_audit`); seq counter maintained internally
- **Allowed dependencies:** `errors.py` (for potential future use); stdlib only
- **Prohibited:** Must not import any policy or storage module; must not import `legacy_app`
- **Notes:** Seq counter starts at 1. Must be strictly monotonically incrementing. Audit is never rolled back; emission happens only after successful state writes.

#### `idempotency.py`
- **Responsibility:** Keyed result cache. Read (cache-miss returns `None`), write after operation completes.
- **Inputs:** `key: str` (namespaced), `result: dict` (on write)
- **Outputs:** Cached result dict (deepcopy) or `None`
- **Allowed dependencies:** stdlib only (no intra-package imports required)
- **Prohibited:** Must not import any policy or storage module; must not import `legacy_app`
- **Notes:** Keys are namespaced per operation type: `"create_invoice:{operation_id}"` and `"refund_invoice:{operation_id}"`. Same `operation_id` string may be reused across operation types independently. Idempotency store is NOT exposed in `snapshot_state()`. Cache must not be included in the state snapshot.

#### `billing_service.py`
- **Responsibility:** Coordinator and façade. Owns the public `execute()` and `snapshot_state()` methods. Wires together validation, idempotency, policy modules, storage, and audit. Contains no business logic of its own.
- **Inputs:** `operation: str`, `payload: dict` (public API)
- **Outputs:** Result dict (from handlers); state dict (from snapshot)
- **Allowed dependencies:** All L0–L3 modules (`errors`, `money`, `validation`, `pricing`, `shipping_policy`, `tax_policy`, `fee_policy`, `refund_policy`, `invoice_store`, `audit`, `idempotency`)
- **Prohibited:** Must not import `legacy_app`; must not contain inline business policy calculations
- **Notes:** The idempotency check/write and audit emission patterns are applied here uniformly for all operations. The coordinator dispatches to handlers for each operation, ensuring that validation, idempotency, business logic (via policy modules), persistence, audit, and idempotency write happen in the correct order.

#### `__init__.py`
- **Responsibility:** Expose the public factory function `create_service()` only.
- **Inputs:** None
- **Outputs:** `BillingService` instance (or equivalent) with `execute()` and `snapshot_state()`
- **Allowed dependencies:** `billing_service.py` only
- **Prohibited:** Must not expose any internal module; must not import `legacy_app`
- **Notes:** This is the entry point Aegis uses: `candidate_factory: modern_app.billing.create_service`.

---

## 3. Dependency Direction

### Layer model

```
L0 Foundation    errors.py, money.py
L1 Input         validation.py
L2 Policy        pricing.py, shipping_policy.py, tax_policy.py,
                 fee_policy.py, refund_policy.py
L3 Storage       invoice_store.py, audit.py, idempotency.py
L4 Orchestration billing_service.py
L5 Entry Point   __init__.py
```

### One-way dependency diagram

```
__init__.py
    └─► billing_service.py
            ├─► errors.py
            ├─► money.py
            ├─► validation.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► pricing.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► shipping_policy.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► tax_policy.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► fee_policy.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► refund_policy.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► invoice_store.py
            │       ├─► errors.py
            │       └─► money.py
            ├─► audit.py
            └─► idempotency.py
```

All dependency edges flow strictly from higher layer numbers to lower layer numbers. No edge connects a module to a module in the same layer or a higher layer. This structure is a DAG by construction.

### Constraints

| Constraint | Enforcement |
|------------|-------------|
| No `modern_app` import from `legacy_app` | Prohibited by `.bobrules` rule 8; verified by `aegis architecture` check |
| No dependency cycles | DAG construction; verified by `aegis architecture` check |
| Policy modules do not own persistence | L2 modules have no imports from L3 |
| Storage does not contain business policy | L3 modules have no imports from L2 |
| Public compatibility surface is small | Only `execute()` and `snapshot_state()` exposed through `__init__.py` |
| No lateral imports within L2 | No policy module imports another policy module |
| No lateral imports within L3 | No storage module imports another storage module |

---

## 4. Compatibility Interface

### Aegis runner requirements (from `aegis/runner.py`)

The Aegis runner:
1. Resolves `candidate_factory` from `aegis_contract.yaml` (`subject.candidate_factory`) as a Python dotted import path.
2. Calls the factory function: `service = factory()`
3. Verifies the returned object has `execute` and `snapshot_state` attributes (raises `TypeError` if not).
4. Calls `service.execute(operation, deepcopy(resolved_input))` for each step.
5. Calls `service.snapshot_state()` before and after each step.
6. Captures exceptions via `_normalize_exception(exc)` which reads `type(exc).__name__`, `getattr(exc, "code", ...)`, and `str(exc)`.

### Aegis architecture check requirements (from `aegis/architecture.py`)

`compare_architecture()` calls `analyze_python_tree("modern_app/billing")` and checks:
- Zero imports from `legacy_app` in any `modern_app/billing/**/*.py` file
- Zero circular dependency cycles in the `modern_app/billing/` package

### Required interface

```
candidate_factory: modern_app.billing.create_service

modern_app/billing/__init__.py must expose:
    def create_service() -> <object with execute() and snapshot_state()>

The returned service object must implement:
    def execute(self, operation: str, payload: dict) -> dict
    def snapshot_state(self) -> dict
```

### `execute()` contract

| Input | Constraint |
|-------|-----------|
| `operation` | String; `"create_invoice"` and `"refund_invoice"` must be handled; any other must raise `ValidationError` with message `"Unsupported operation: {operation}"` |
| `payload` | Dict; passed by deepcopy from runner |

| Output | Constraint |
|--------|-----------|
| Success | Returns result dict matching legacy schema exactly |
| Failure | Raises exception with matching `type(exc).__name__` and `exc.code` attribute |

### `snapshot_state()` contract

Must return a dict with exactly these keys:
```python
{
    "invoices": [...],   # list of invoice dicts, sorted by invoice_id
    "refunds": [...],    # list of refund dicts, sorted by refund_id
    "ledger": [...],     # list of ledger entries in append order
    "audit": [...],      # list of audit events in append order
}
```

The `_idempotency` cache must NOT appear in the snapshot. This is by design in the legacy system and must be preserved.

### Exception normalization contract

Aegis compares exceptions as:
```python
{
    "type": type(exc).__name__,
    "code": getattr(exc, "code", type(exc).__name__),
    "message": str(exc),
}
```

The modern exception classes must:
- Have the same class names as legacy: `ValidationError`, `AccountSuspendedError`, `InvoiceNotFoundError`, `RefundAlreadyProcessedError`
- Have the same `code` string attributes: `"VALIDATION_ERROR"`, `"ACCOUNT_SUSPENDED"`, `"INVOICE_NOT_FOUND"`, `"REFUND_ALREADY_PROCESSED"`
- Produce the same message strings for contract-tested error cases

---

## 5. State Ownership

### Ownership table

| Store | Owner module | Allowed readers | Mutation pattern |
|-------|-------------|-----------------|-----------------|
| `_invoices` | `invoice_store.py` | `billing_service.py` (via store methods) | Created on `create_invoice`; status mutated in-place on `APPROVED` refund |
| `_refunds` | `invoice_store.py` | `billing_service.py` (via store methods) | Created on `refund_invoice` |
| `_ledger` | `invoice_store.py` | `billing_service.py` (via snapshot) | Append-only: DEBIT on invoice, CREDIT on APPROVED refund only |
| `_audit` / `_audit_seq` | `audit.py` | `billing_service.py` (via snapshot) | Append-only; seq increments monotonically |
| `_idempotency` | `idempotency.py` | `billing_service.py` (coordinator) | Read-then-write per operation; never in snapshot |

### State flow rules

- Policy modules (`pricing`, `shipping_policy`, `tax_policy`, `fee_policy`, `refund_policy`) receive all inputs as function arguments. They return computed values. They never read from or write to any store.
- `invoice_store.py` owns `_invoices`, `_refunds`, and `_ledger` exclusively. No other module reads these stores directly; the coordinator accesses them through methods defined on the store.
- `audit.py` owns `_audit` and `_audit_seq`. The coordinator calls the emit method; no policy module calls it directly.
- `idempotency.py` owns `_idempotency`. The coordinator wraps every operation with a read-before/write-after pattern. Handlers do not call idempotency directly.
- The coordinator (`billing_service.py`) assembles the snapshot from both `invoice_store` and `audit`; idempotency state is excluded from the snapshot.

### Explicit state passing

Across module boundaries, state is passed as explicit function arguments and return values — not as shared mutable globals, module-level variables, or monkey-patched attributes. This preserves the behavioral contract while making dependencies visible.

---

## 6. Behavioral Risk Register

| # | Risk | Legacy behavior to preserve | Likely modernization failure | Architectural mitigation |
|---|------|-----------------------------|------------------------------|--------------------------|
| R-01 | Inclusive threshold boundaries in tier discount | `>=` comparisons: VIP 500→7%, 1000→10%; BUSINESS 1000→4%, 2000→6% | Using `>` instead of `>=`; off-by-one cent errors | `pricing.py` owns all threshold constants; contract has critical_boundary cases at each exact threshold |
| R-02 | Shipping uses pre-discount subtotal | Shipping threshold evaluated against `subtotal`, NOT `discounted_subtotal` | Passing the wrong subtotal variable to `_shipping` | `shipping_policy.py` receives `pre_discount_subtotal` explicitly named; coordinator passes `pricing_result.subtotal`, not `pricing_result.discounted_subtotal` |
| R-03 | Service fee uses post-discount subtotal | Fee threshold evaluated against `discounted_subtotal` (>= 1500) | Passing pre-discount subtotal to fee policy | `fee_policy.py` receives `discounted_subtotal` explicitly named; coordinator passes `pricing_result.discounted_subtotal` |
| R-04 | Percentage discount uses ROUND_HALF_EVEN | `(subtotal × rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)` | Applying ROUND_HALF_UP (the default helper) instead | `pricing.py` must NOT use `_money()` (which defaults to HALF_UP) for pct_discount; must apply HALF_EVEN explicitly |
| R-05 | Refund fee uses ROUND_HALF_EVEN | `(original_total × fee_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)` | Using ROUND_HALF_UP by default; copy-paste from service fee (which IS HALF_UP) | `refund_policy.py` must apply HALF_EVEN for fee; separate from service fee in `fee_policy.py` which uses HALF_UP |
| R-06 | Proportional discount allocation: last line = residual | All lines except last: HALF_EVEN share; last line: `total_discount - allocated` (no rounding quantize on residual beyond HALF_EVEN final) | Rounding every line including last; changing iteration order; not tracking `allocated` accumulator | `tax_policy.py` must implement the residual pattern exactly; iteration order must match original (sequential); last-line check: `idx == len(lines) - 1` |
| R-07 | MANUAL_REVIEW: no ledger entry, no invoice status change | MANUAL_REVIEW refund writes refund record and emits `REFUND_MANUAL_REVIEW` only; no CREDIT ledger entry; invoice stays OPEN | Writing a ledger entry on MANUAL_REVIEW; mutating invoice status; branching on wrong condition | `billing_service.py` coordinator gates ledger write and invoice mutation behind `status == "APPROVED"` only; `invoice_store.py` exposes separate methods for approved vs manual paths |
| R-08 | MANUAL_REVIEW does not block subsequent refund | `RefundAlreadyProcessedError` guard checks `refund["status"] == "APPROVED"`; MANUAL_REVIEW refunds do not trigger it | Using presence of any refund record (instead of checking status) as the guard | `invoice_store.py` duplicate-refund guard must check status field; test: sequence of MANUAL_REVIEW then new APPROVED refund must succeed |
| R-09 | Idempotency namespace isolation | Keys: `"create_invoice:{op_id}"` and `"refund_invoice:{op_id}"`; same `op_id` is independent across operation types | Using `op_id` alone as key (no operation prefix); sharing namespace between operations | `idempotency.py` constructs key as `f"{operation}:{operation_id}"` only; coordinator passes the full namespaced key |
| R-10 | Idempotency retry: no new side effects | Retry returns `deepcopy(cached_result)` with NO new invoice, refund, ledger, or audit state | Repeating validation or business logic on retry; emitting a duplicate audit event | Coordinator checks idempotency cache BEFORE any validation execution — actually before or immediately after presence check; any execution path hit before the cache write must not produce side effects |
| R-11 | Validation failure atomicity | Any `ValidationError`, `AccountSuspendedError`, etc. must produce zero side effects | Running any state mutation before all validation completes; partial writes before a later validation fails | All validation happens in `validation.py` before any call to policy or storage modules; coordinator orders: validate → idempotency-check → policy → store → audit → idempotency-write |
| R-12 | FIXED25 silent no-op below threshold | `FIXED25` with subtotal < 250.00 applies zero deduction and raises no error | Raising `ValidationError` when FIXED25 is submitted below threshold | `pricing.py` coupon handler: check subtotal before applying; silently keep `fixed_coupon = Decimal("0.00")` if below threshold |
| R-13 | WELCOME10 cap is cumulative, not additive independent | `min(discount_rate + 0.10, 0.15)` — the 15% cap applies to the combined rate | Applying WELCOME10 separately and adding to tier discount without cap; applying 10% as an independent discount | `pricing.py` computes combined rate as `min(tier_rate + Decimal("0.10"), Decimal("0.15"))` exactly |
| R-14 | Refund timing window boundaries | hours <= 24 → full; hours <= 72 (and > 24) → 5% fee; hours > 72 → MANUAL_REVIEW; all inclusive | Using `< 24` instead of `<= 24`; using `< 72` instead of `<= 72` | `refund_policy.py` must use `<=` exactly; contract has critical_boundary cases at 24, 25, 72, 73 |
| R-15 | Grand total rounding applied to assembled sum | ROUND_HALF_UP applied to the complete sum `discounted_subtotal + shipping + tax + service_fee`, not to components individually | Rounding components before summing | `invoice_store.py` assembles grand total by summing all components then calling `.quantize(MONEY, ROUND_HALF_UP)` once |
| R-16 | Audit seq starts at 1, is monotonic | `_audit_seq` initialized to 0; incremented before append; first event has seq=1 | Starting at 0; incrementing after append; not incrementing on retry | `audit.py` must pre-increment `_audit_seq` before each append; idempotent retries must not call `audit.emit()` |
| R-17 | Invoice ID deterministic derivation | `"INV-" + sha256(operation_id.encode()).hexdigest()[:10].upper()` | Using a different hash, different slice, lowercase, or different prefix | `billing_service.py` or `invoice_store.py` must implement the exact formula; no UUIDs or random IDs |

---

## 7. Monetary Semantics

Each rounding operation in the system is distinct and must be preserved exactly as documented.

### Rounding operations and ownership

| Operation | Rounding mode | Module that owns it | Notes |
|-----------|---------------|---------------------|-------|
| Input unit price normalization | ROUND_HALF_UP | `pricing.py` | Applied before any multiplication |
| Line total (unit_price × qty) | ROUND_HALF_UP | `pricing.py` | Applied per line before adding to subtotal |
| Percentage discount (subtotal × rate) | **ROUND_HALF_EVEN** | `pricing.py` | Banker's rounding — must NOT use `_money()` default |
| Combined discount min(subtotal, pct+fixed) | **ROUND_HALF_EVEN** | `pricing.py` | Same mode as pct_discount |
| Discounted subtotal (subtotal − discount) | ROUND_HALF_UP | `pricing.py` | Standard half-up after subtraction |
| Discount share allocation per line (except last) | **ROUND_HALF_EVEN** | `tax_policy.py` | All-but-last lines |
| Discount share — last line | Residual (no rounding on assignment) | `tax_policy.py` | `total_discount − allocated_so_far` |
| Taxable base per line (line_total − discount_share) | ROUND_HALF_UP | `tax_policy.py` | After discount subtracted from line total |
| Tax per line (taxable_base × rate) | ROUND_HALF_UP | `tax_policy.py` | Applied independently per line |
| Total tax (sum of line taxes) | ROUND_HALF_UP (on final sum) | `tax_policy.py` | Aggregate after all line taxes computed |
| Service fee (discounted_subtotal × 0.015) | ROUND_HALF_UP | `fee_policy.py` | Uses HALF_UP — different from refund fee |
| Grand total (sum of components) | ROUND_HALF_UP | `invoice_store.py` | Applied once to the complete assembled sum |
| Refund fee (original_total × fee_rate) | **ROUND_HALF_EVEN** | `refund_policy.py` | Must NOT use same mode as service fee |
| Refund amount (original_total − fee) | ROUND_HALF_UP | `refund_policy.py` | Standard half-up after subtraction |

### Critical distinctions

- Percentage discount uses ROUND_HALF_EVEN; service fee uses ROUND_HALF_UP. These are different operations in different modules. Using a uniform rounding helper for both would break the contract.
- Refund fee uses ROUND_HALF_EVEN; refund amount uses ROUND_HALF_UP. These are adjacent lines in the refund computation. They must not be normalized to the same mode.
- The `_money()` helper defaults to ROUND_HALF_UP and must not be used where ROUND_HALF_EVEN is required. Callers that need HALF_EVEN must quantize explicitly.
- No floating-point arithmetic (`float`) may be used for any monetary calculation. All monetary values must use `decimal.Decimal`.

---

## 8. Side-Effect Semantics

Side effects are treated as first-class behavioral requirements, not implementation details.

### Invoice creation side effects (all three must occur, no partial writes)

| Order | Effect | Condition |
|-------|--------|-----------|
| 1 | Store invoice record in `_invoices[invoice_id]` with `status="OPEN"` | After all validation passes |
| 2 | Append DEBIT ledger entry: `{type: "INVOICE_CHARGE", invoice_id, amount: grand_total, direction: "DEBIT"}` | Same as above |
| 3 | Emit `INVOICE_CREATED` audit event: `{invoice_id, customer_id, amount: grand_total}` | Same as above |
| 4 | Write result to idempotency cache: `"create_invoice:{operation_id}"` | After all of the above |

### Refund side effects (APPROVED)

| Order | Effect | Condition |
|-------|--------|-----------|
| 1 | Store refund record in `_refunds[refund_id]` | After all validation and duplicate check |
| 2 | Mutate `_invoices[invoice_id]["status"] = "REFUNDED"` | APPROVED only |
| 3 | Append CREDIT ledger entry: `{type: "REFUND", invoice_id, refund_id, amount: refund_amount, direction: "CREDIT"}` | APPROVED only |
| 4 | Emit `REFUND_APPROVED` audit event: `{invoice_id, refund_id, amount: refund_amount}` | APPROVED only |
| 5 | Write result to idempotency cache: `"refund_invoice:{operation_id}"` | After all of the above |

### Refund side effects (MANUAL_REVIEW)

| Order | Effect | Condition |
|-------|--------|-----------|
| 1 | Store refund record in `_refunds[refund_id]` with `refund_amount="0.00"` | Always for MANUAL_REVIEW |
| 2 | NO invoice status mutation | By design |
| 3 | NO ledger entry | By design |
| 4 | Emit `REFUND_MANUAL_REVIEW` audit event: `{invoice_id, refund_id, amount: "0.00"}` | Always for MANUAL_REVIEW |
| 5 | Write result to idempotency cache | After all of the above |

### Atomic failure behavior

- If any validation fails, **none** of the above side effects occur.
- If a validation error is raised, no invoice record, no refund record, no ledger entry, no audit event, and no idempotency cache entry is created.
- There is no partial-write recovery; the system is in-memory and single-threaded. Validation must complete before any mutation begins.

### Idempotent retry behavior

- On a retry (idempotency cache hit), the cached result is returned as a `deepcopy`.
- No invoice record, refund record, ledger entry, or audit event is created on a retry.
- The idempotency check occurs at the start of the operation, after the `operation_id` presence check and before any business logic.
- Audit sequence numbers are not consumed on retry.

---

## 9. Implementation Sequence

The following order is safe for Task 3 implementation. It ensures each module only imports already-completed modules.

### Phase 1 — Foundation (fully parallel, no inter-module dependencies)

| Module | Dependencies | Can be parallelized |
|--------|-------------|---------------------|
| `errors.py` | None | Yes — independent of all others |
| `money.py` | stdlib `decimal` only | Yes — independent |

### Phase 2 — Input (depends on Phase 1 only)

| Module | Dependencies |
|--------|-------------|
| `validation.py` | `errors.py`, `money.py` |

### Phase 3 — Pure policy (each depends on Phase 1 only; all parallel with each other)

| Module | Dependencies | Can be parallelized |
|--------|-------------|---------------------|
| `pricing.py` | `errors.py`, `money.py` | Yes |
| `shipping_policy.py` | `errors.py`, `money.py` | Yes |
| `tax_policy.py` | `errors.py`, `money.py` | Yes |
| `fee_policy.py` | `errors.py`, `money.py` | Yes |
| `refund_policy.py` | `errors.py`, `money.py` | Yes |

### Phase 4 — Storage and events (parallel, each depends on Phase 1 only)

| Module | Dependencies | Can be parallelized |
|--------|-------------|---------------------|
| `invoice_store.py` | `errors.py`, `money.py` | Yes |
| `audit.py` | stdlib only | Yes |
| `idempotency.py` | stdlib only | Yes |

### Phase 5 — Orchestration (depends on all prior phases)

| Module | Dependencies |
|--------|-------------|
| `billing_service.py` | All L0–L3 modules |

### Phase 6 — Entry point

| Module | Dependencies |
|--------|-------------|
| `__init__.py` | `billing_service.py` |

### Phase 7 — Verification

```
python -m aegis.cli verify
python -m aegis.cli architecture
```

### Parallelization opportunities for Task 3

- Phase 1 (2 modules) and Phase 2 (1 module) can be assigned to one implementer.
- Phase 3 (5 pure policy modules) can be split across up to 5 independent implementers with no shared file edits.
- Phase 4 (3 storage/event modules) can be split across 3 independent implementers.
- Phase 5 (billing_service.py) must be implemented last, by one implementer, after Phase 3 and 4 are stable.
- `__init__.py` is a trivial one-liner after Phase 5.

**Modules that must NOT be implemented by the same agent editing the same file simultaneously:**
- `billing_service.py` is the single integration point and must be implemented last, not in parallel.
- `invoice_store.py` owns three stores; its interface must be stable before `billing_service.py` is written.

---

## 10. Acceptance Gates

Task 3 is not complete until all of the following gates pass:

### Gate 1 — Import integrity

```
python -m aegis.cli architecture
```

Must report:
- Modern imports from legacy: **0**
- Modern cycles: **0**

### Gate 2 — Behavioral equivalence

```
python -m aegis.cli verify
```

Must produce verdict: **ACCEPTED**

This means the candidate passes all 183 invariants across all 47 scenarios.

### Gate 3 — Full readiness

```
python -m aegis.cli readiness
```

Must report: **READY**

### Acceptance criteria summary

| Gate | Command | Required result |
|------|---------|-----------------|
| Python import/compile | `python -c "from modern_app.billing import create_service"` | No ImportError |
| Behavioral verdict | `python -m aegis.cli verify` | `ACCEPTED` |
| Architecture checks | `python -m aegis.cli architecture` | 0 legacy imports, 0 cycles |
| Full readiness | `python -m aegis.cli readiness` | `READY` |

### If verification is BLOCKED

If `verify` returns `REJECTED`:

1. Read the verification report in `reports/verification.md` — it identifies the failing invariants and the counterexample.
2. Diagnose the candidate implementation for the failing case.
3. Fix the candidate code only — do NOT alter `aegis_contract.yaml`, `baseline/baseline.json`, `legacy_app/`, or any Aegis module.
4. Refer to the Behavioral Risk Register in Section 6 for the most likely failure modes.
5. Rerun `verify` after each fix.

---

## Appendix A — Threshold Constants Reference

All threshold constants should live in the module that owns the policy rule, not duplicated across modules.

| Constant | Value | Owner module |
|----------|-------|-------------|
| `VIP_TIER_1_THRESHOLD` | 500.00 | `pricing.py` |
| `VIP_TIER_2_THRESHOLD` | 1000.00 | `pricing.py` |
| `BUSINESS_TIER_1_THRESHOLD` | 1000.00 | `pricing.py` |
| `BUSINESS_TIER_2_THRESHOLD` | 2000.00 | `pricing.py` |
| `WELCOME10_CAP` | 0.15 | `pricing.py` |
| `FIXED25_MIN_SUBTOTAL` | 250.00 | `pricing.py` |
| `US_FREE_SHIPPING_THRESHOLD` | 150.00 | `shipping_policy.py` |
| `EU_UK_FREE_SHIPPING_THRESHOLD` | 250.00 | `shipping_policy.py` |
| `CARD_FEE_THRESHOLD` | 1500.00 | `fee_policy.py` |
| `REFUND_FULL_HOURS_MAX` | 24 | `refund_policy.py` |
| `REFUND_FEE_HOURS_MAX` | 72 | `refund_policy.py` |

---

## Appendix B — Contract Candidate Factory Path

From `aegis_contract.yaml`:
```yaml
subject:
  candidate_factory: modern_app.billing.create_service
```

The modern application must be importable at `modern_app.billing.create_service`.
This requires `modern_app/__init__.py` and `modern_app/billing/__init__.py` to exist
with `create_service` exported from `modern_app/billing/__init__.py`.

---

*This task defines a modernization architecture. Behavioral equivalence must be demonstrated later by executing the implementation against the sealed Aegis contract.*
