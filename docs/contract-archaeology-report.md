# Aegis ContractLock — Contract Archaeology Report

**System:** Legacy Billing Monolith (`legacy_app/billing/monolith.py`)  
**Workspace:** Clean-room workspace (`04_ANTIGRAVITY_BOB_RUN`)  
**Role:** Contract Archaeologist  
**Status:** Verification Baseline Sealed & Coverage Gate Passed (`READY`)  
**Baseline Evidence SHA-256:** `2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7`

---

## 1. Executive Summary

This report documents the behavioral reconstruction of the legacy billing system. Through parallel analysis conducted by three specialized research subagents (Business Rule Miner, Boundary & Failure Analyst, State & Side-Effect Analyst), the legacy application's executable behavioral surface was fully uncovered, characterized, and locked into an executable Aegis contract (`aegis_contract.yaml`).

The resulting behavioral contract comprises:
- **86 behavioral scenarios** across 14 rule families
- **100 workflow steps**
- **231 automated invariants** (zero failures)
- **100.00% statement coverage** of `legacy_app/billing/monolith.py` (209/209 statements)
- **98.96% branch coverage** of `legacy_app/billing/monolith.py` (95/96 branches; remaining 1 branch is demonstrably unreachable defensive code)
- **Contract Readiness:** `READY`

---

## 2. Documentation vs Implementation Discrepancies

The legacy documentation (`legacy_app/docs/BILLING_POLICY.md`), the schema guide (`docs/CONTRACT_SCHEMA_GUIDE.md`), and the actual executable implementation (`legacy_app/billing/monolith.py`) exhibit several critical divergence points. Rather than silently reconciling these divergences, the contract explicitly locks the implemented executable behavior.

### Discrepancy 1: Refund Operation Name
- **Documented Behavior:** `docs/CONTRACT_SCHEMA_GUIDE.md` (lines 86, 106, 117) documents the refund operation as `process_refund`.
- **Implemented Behavior:** `monolith.py` (line 72) implements `refund_invoice`. Submitting `process_refund` raises `ValidationError: Unsupported operation: process_refund`.
- **Source Location:** `legacy_app/billing/monolith.py#L69-L75`
- **Contract Treatment:** The contract defines refund scenarios strictly with `operation: refund_invoice`. Negative validation case `val_unsupported_operation` confirms that passing `process_refund` raises `VALIDATION_ERROR`.
- **Risk during Modernization:** High. A modernizer relying solely on the schema guide would expose `process_refund`, causing immediate verifier failure against the legacy service.

### Discrepancy 2: Refund Request Schema & Fee Computation
- **Documented Behavior:** `docs/CONTRACT_SCHEMA_GUIDE.md` (lines 107-112) specifies refund payload fields as `operation_id`, `invoice_id`, `amount`, `reason`, `requested_at`.
- **Implemented Behavior:** `monolith.py` (lines 366-375) requires `operation_id`, `invoice_id`, and `hours_since_purchase` (an integer $\ge 0$). Refund amounts are not supplied by the caller; they are calculated deterministically from the original invoice's `grand_total` and `hours_since_purchase`.
- **Source Location:** `legacy_app/billing/monolith.py#L366-L376`
- **Contract Treatment:** All contract refund cases specify `operation_id`, `invoice_id`, and `hours_since_purchase`.
- **Risk during Modernization:** High. Attempting to parse `amount` or `requested_at` in the candidate while neglecting `hours_since_purchase` will break refund tier classification and fee calculation.

### Discrepancy 3: Coupon Payload Field Name
- **Documented Behavior:** `docs/CONTRACT_SCHEMA_GUIDE.md` (line 116) specifies optional payload field `coupon_code`.
- **Implemented Behavior:** `monolith.py` (line 102) accesses `payload.get("coupon")`. If a caller provides `coupon_code`, it is silently ignored, granting $0.00 coupon discount.
- **Source Location:** `legacy_app/billing/monolith.py#L102`
- **Contract Treatment:** Contract scenarios provide coupon codes under the key `coupon`.
- **Risk during Modernization:** Medium. A modernizer refactoring to `coupon_code` would silently drop coupon discounts when verified against legacy inputs.

### Discrepancy 4: Asymmetric Rounding Between Fee Calculations
- **Documented Behavior:** `BILLING_POLICY.md` Sec. 2 states that input prices use `HALF_UP`, line totals are rounded before subtotaling, and percentage discounts use `HALF_EVEN`. It does not mention fee rounding modes.
- **Implemented Behavior:** 
  - Invoice CARD service fee (1.5%) uses `ROUND_HALF_UP` (`monolith.py#L197`).
  - Refund fee (5.0%) uses `ROUND_HALF_EVEN` (Banker's rounding) (`monolith.py#L403`).
- **Source Location:** `legacy_app/billing/monolith.py#L196-L198`, `legacy_app/billing/monolith.py#L403`
- **Contract Treatment:** Dedicated boundary scenarios `fee_card_at_1500_00` and `rounding_refund_fee_half_even` lock both rounding modes independently (e.g., verifying that $50.10 at 5% refund fee rounds to $2.50 via Banker's rounding, whereas $2.505 would round to $2.51 under HALF_UP).
- **Risk during Modernization:** Critical. Modernizers unifying all calculations under `ROUND_HALF_UP` or standard floating-point arithmetic will drift on exact half-cent refund fee boundaries.

### Discrepancy 5: FIXED25 Coupon Below Threshold Behavior
- **Documented Behavior:** `BILLING_POLICY.md` Sec. 1 states: "`FIXED25` deducts 25.00 only when the pre-discount merchandise subtotal is at least 250.00." It does not state what happens if subtotal < 250.00.
- **Implemented Behavior:** `monolith.py` lines 162-164 silently sets `fixed_coupon = Decimal("0.00")` without raising an error or rejecting the invoice.
- **Source Location:** `legacy_app/billing/monolith.py#L162-L164`
- **Contract Treatment:** Contract case `coupon_fixed25_below_249_99` verifies that `FIXED25` on a $249.99 subtotal succeeds with `discount: "0.00"`.
- **Risk during Modernization:** Medium. A modernizer might assume subtotal < 250.00 with `FIXED25` should throw a `ValidationError`.

### Discrepancy 6: Subsequent Refund Attempts after MANUAL_REVIEW
- **Documented Behavior:** `BILLING_POLICY.md` Sec. 6 states: "A second independently identified approved refund for an already-refunded invoice is rejected."
- **Implemented Behavior:** `monolith.py` line 385 checks `if refund["invoice_id"] == invoice_id and refund["status"] == "APPROVED": raise RefundAlreadyProcessedError`. If a prior refund resulted in `status == "MANUAL_REVIEW"`, subsequent refund requests for that invoice are **not** rejected and can be approved.
- **Source Location:** `legacy_app/billing/monolith.py#L384-L386`
- **Contract Treatment:** Scenario `refund_after_manual_review_allowed` tests a multi-step sequence: invoice created -> refund at 80h (enters `MANUAL_REVIEW`) -> refund at 12h (successfully `APPROVED`).
- **Risk during Modernization:** Medium. Modern architectures implementing a single refund per invoice constraint would reject the second request, causing drift.

---

## 3. Discovered Behavioral Families Catalog

1. **Customer Classification & Account State:**
   - Tiers: `RETAIL` (default, 0% discount), `BUSINESS`, `VIP`. Case-insensitive. Unknown tiers trigger `VALIDATION_ERROR`.
   - Account Status: Defaults to `ACTIVE`. Status `SUSPENDED` triggers `ACCOUNT_SUSPENDED`.
   - Customer ID: Required non-empty string.
2. **Tier-Based Volume Discounts:**
   - VIP: < $500.00 (3%), $500.00-$999.99 (7%), $\ge$ $1,000.00 (10%).
   - Business: < $1,000.00 (0%), $1,000.00-$1,999.99 (4%), $\ge$ $2,000.00 (6%).
   - Retail: 0% across all subtotals.
   - Formatted to 4 decimal places (`f"{rate:.4f}"`).
3. **Coupons & Stacking Rules:**
   - `WELCOME10`: Adds 10 percentage points to tier rate, capped at a maximum of 15% (0.1500).
   - `FIXED25`: Fixed $25.00 discount if subtotal $\ge$ $250.00; silently $0.00 if below.
   - Total discount capped at merchandise subtotal (`min(subtotal, ...)`).
   - Unknown coupon codes trigger `VALIDATION_ERROR`.
4. **Monetary Precision & Rounding Pipeline:**
   - Step 1: Input prices quantized with `ROUND_HALF_UP` to cents.
   - Step 2: Line total = `(unit_price * qty).quantize(ROUND_HALF_UP)`.
   - Step 3: Subtotal = sum of rounded line totals.
   - Step 4: Percentage discount = `(subtotal * discount_rate).quantize(ROUND_HALF_EVEN)` (Banker's rounding).
   - Step 5: Total discount = `min(subtotal, (pct_discount + fixed_coupon).quantize(ROUND_HALF_EVEN))`.
   - Step 6: Proportional line discount allocation for tax uses `ROUND_HALF_EVEN` for lines $0 \dots N-2$, with line $N-1$ taking the exact residual.
   - Step 7: Grand total = `(discounted_subtotal + shipping + tax + service_fee).quantize(ROUND_HALF_UP)`.
5. **Item Validation & Default Values:**
   - SKU: Required non-empty string.
   - Category: `GOODS` (default), `DIGITAL`, `ESSENTIAL`.
   - Quantity: Integer $> 0$.
   - Unit price: Decimal $\ge 0.00$. Free items ($0.00) permitted.
6. **Regional Taxation:**
   - `US_CA`: GOODS 7.25%, DIGITAL 0%, ESSENTIAL 0%.
   - `US_NY`: GOODS 8.875%, DIGITAL 8.875%, ESSENTIAL 0%.
   - `EU_DE`: GOODS 19%, DIGITAL 19%, ESSENTIAL 7%.
   - `UK`: GOODS 20%, DIGITAL 20%, ESSENTIAL 0%.
   - `EXPORT`: All categories 0%.
   - Zero subtotal short-circuits to $0.00 tax and empty breakdown `[]`.
7. **Shipping Thresholds (Pre-Discount Subtotal Basis):**
   - Evaluated on pre-discount subtotal, not post-discount subtotal.
   - `US_CA` & `US_NY`: Free ($\ge$ $150.00) vs $12.00 (< $150.00).
   - `EU_DE` & `UK`: Free ($\ge$ $250.00) vs $18.00 (< $250.00).
   - `EXPORT`: Flat $35.00 across all order amounts.
8. **Payment Methods & Service Fees:**
   - Supported: `CARD` (default), `BANK_TRANSFER`.
   - CARD Service Fee: 1.5% (`ROUND_HALF_UP`) on `discounted_subtotal` only when `discounted_subtotal` $\ge$ $1,500.00.
   - BANK_TRANSFER: Always $0.00 fee.
9. **Refund Lifecycle & Windows:**
   - 0-24 hours: `status: "APPROVED"`, fee: $0.00, refund_amount = grand_total.
   - 25-72 hours: `status: "APPROVED"`, fee: 5.0% (`ROUND_HALF_EVEN`), refund_amount = grand_total - fee.
   - $> 72$ hours: `status: "MANUAL_REVIEW"`, fee: $0.00, refund_amount: $0.00.
   - Approved refund transitions invoice to `"REFUNDED"`. Manual review leaves invoice `"OPEN"`.
10. **Persistence & Side Effects:**
    - Invoice Charge: Emits `DEBIT` ledger entry and `INVOICE_CREATED` audit event.
    - Approved Refund: Emits `CREDIT` ledger entry and `REFUND_APPROVED` audit event.
    - Manual Review: Emits `REFUND_MANUAL_REVIEW` audit event; NO ledger entry written.
11. **Idempotency Guarantees:**
    - Keyed by `create_invoice:<op_id>` and `refund_invoice:<op_id>`.
    - Duplicate submission returns identical cached dictionary with zero secondary side effects (no new ledger entries, no new audit events).
    - Failed requests are never cached.

---

## 4. Exact Boundaries & Thresholds Matrix

| Threshold Domain | Boundary Condition | Delta ($\Delta$) | Values Tested in Contract | Observed Behavior |
|---|---|---|---|---|
| **VIP Discount Low** | $500.00 | $0.01 | $499.99, $500.00, $500.01 | Rate changes from 0.0300 to 0.0700 at exactly $500.00 |
| **VIP Discount High** | $1,000.00 | $0.01 | $999.99, $1,000.00, $1,000.01 | Rate changes from 0.0700 to 0.1000 at exactly $1,000.00 |
| **Business Discount Low** | $1,000.00 | $0.01 | $999.99, $1,000.00, $1,000.01 | Rate changes from 0.0000 to 0.0400 at exactly $1,000.00 |
| **Business Discount High**| $2,000.00 | $0.01 | $1,999.99, $2,000.00, $2,000.01 | Rate changes from 0.0400 to 0.0600 at exactly $2,000.00 |
| **Coupon FIXED25** | $250.00 | $0.01 | $249.99, $250.00, $250.01 | Fixed discount: $0.00 below, $25.00 at and above |
| **Coupon WELCOME10 Cap**| 15% rate | - | 13%, 14%, 15% (uncapped/capped) | Rates above 15% (e.g. 17%, 20%) capped at 0.1500 |
| **US Shipping** | $150.00 | $0.01 | $149.99, $150.00, $150.01 | Shipping: $12.00 below, $0.00 at and above |
| **EU / UK Shipping** | $250.00 | $0.01 | $249.99, $250.00, $250.01 | Shipping: $18.00 below, $0.00 at and above |
| **CARD Service Fee** | $1,500.00 | $0.01 | $1,499.99, $1,500.00, $1,500.01 | Fee: $0.00 below, 1.5% ($22.50) at and above |
| **Refund Window 1 / 2** | 24 hours | 1 hour | 24, 25 | Hours $\le 24$: 0% fee; Hours $25-72$: 5% fee |
| **Refund Window 2 / 3** | 72 hours | 1 hour | 72, 73 | Hours $\le 72$: APPROVED; Hours $73+$: MANUAL_REVIEW |

---

## 5. Rounding & Numerical Analysis

### Rounding Mode Assignment
- Arithmetic Rounding (`ROUND_HALF_UP`):
  - Unit price input quantization (`_money()`)
  - Line total computation (`unit_price * qty`)
  - Accumulated subtotal
  - Discounted merchandise subtotal
  - Line taxable base calculation
  - Line tax and total tax quantization
  - Card payment service fee
  - Grand total
  - Approved refund net payout amount
- Banker's Rounding (`ROUND_HALF_EVEN`):
  - Customer tier percentage discount calculation
  - Combined discount calculation
  - Proportional multi-line discount shares (lines $0 \dots N-2$)
  - Final line discount residual calculation
  - Refund fee calculation (5%)

### Intermediate Precision
Intermediate arithmetic within the discount allocation pipeline maintains full Python `Decimal` context precision (28 decimal places). Quantization occurs explicitly at each pipeline boundary.

---

## 6. Coverage Gate & Baseline Results

Executing the Aegis verification suite yielded:
- **Baseline Invariant Failures:** 0
- **Baseline Evidence SHA-256:** `2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7`
- **Total Statements in Monolith:** 209
- **Covered Statements:** 209 (100.00%)
- **Total Branches in Monolith:** 96
- **Covered Branches:** 95 (98.96%)
- **Uncovered Branch:** Line 344 $\rightarrow$ 347 (`elif region == "EXPORT":`). This branch represents the defensive fallthrough of a categorical `elif` chain where prior validation (`monolith.py#L115`) strictly guarantees `region` must be one of the 5 enumerated regions. Hence, the `False` condition is mathematically unreachable.
- **Contract Readiness Gate:** `READY` (exceeds $\ge 95\%$ statement and $\ge 90\%$ branch coverage requirements).

---
*Report certified by Aegis Contract Archaeologist.*
