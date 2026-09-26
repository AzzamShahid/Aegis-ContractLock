# Aegis ContractLock — Task 4 Behavioral Drift Diagnosis

**System:** Aegis ContractLock Billing Modernization  
**Task:** Task 4 — Behavioral Drift Diagnosis & Surgical Repair  
**Governing Standard:** `.bobrules`  
**Status:** Pre-Repair Root Cause Analysis Completed  

---

## 1. Protected Evidence Baseline Hashes (Pre-Repair)

In accordance with Requirement R1 and `.bobrules`, baseline integrity hashes were recorded prior to diagnosis or any candidate file changes:

| Target File | Protected SHA-256 Hash | Integrity Status |
|---|---|---|
| `legacy_app/billing/monolith.py` | `8f18fdf91e5a970b25b0be053d9ae5c5df57435358122a73da10c87973dce19f` | Verified Protected |
| `aegis_contract.yaml` | `a3130dd7daa9828ec6951ab7c7ef4b17e8adb8b728524dd44c5ba0019567f993` | Verified Protected |
| `baseline/baseline.json` | `6ecdfb56129e3ca342ab76668b23768000db0e9e84e2b107ca353183e8eb9177` | Verified Protected |

Isolation constraints confirmed: No external reference implementations, previous accepted candidate copies, or unauthorized documentation were read.

---

## 2. Blocked Verification Summary

Evidence source: `reports/safety-rehearsal-blocked-verification.md` and `reports/safety-rehearsal-blocked-verification.json`.

- **Verdict:** `BLOCKED`
- **Total Cases Tested:** 86
- **Cases Matched:** 85
- **Cases Drifted:** 1
- **Failing Case ID:** `bnd_vip_subtotal_1000_00`
- **Total Divergent Diff Paths:** 24 differences

---

## 3. Case Analysis & Earliest Semantic Divergence

### 3.1 Failing Case Specification
- **Case ID:** `bnd_vip_subtotal_1000_00`
- **Contract Tags:** `critical_boundary`, `discount`, `vip`
- **Contract Description:** `VIP customer subtotal exactly at $1000.00 threshold receives 10% discount`
- **Operation:** `create_invoice`
- **Operation Input:**
  ```json
  {
    "operation_id": "op-vip-1000-00",
    "customer": {
      "id": "C-VIP-05",
      "tier": "VIP",
      "region": "US_CA"
    },
    "items": [
      {
        "sku": "SKU-1000",
        "qty": 1,
        "unit_price": "1000.00"
      }
    ],
    "payment_method": "BANK_TRANSFER"
  }
  ```

### 3.2 Earliest Semantic Divergence
The earliest point of semantic divergence between legacy baseline and modern candidate execution is:
- **Path:** `$.steps[0].result.discount_rate`
  - **Legacy Baseline:** `0.1000` (10.00%)
  - **Candidate Modern:** `0.0700` (7.00%)
  - **Delta:** Candidate under-calculated tier discount rate by 300 basis points (3.00%).

In `legacy_app/billing/monolith.py` line 250:
```python
if subtotal >= Decimal("1000.00"):
    return Decimal("0.10")
```
When `subtotal == Decimal("1000.00")`, the VIP discount bracket rule evaluates to `0.1000`.

In `modern_app/billing/pricing_policy.py` line 13:
```python
if subtotal > Decimal("1000.00"):
    return Decimal("0.10")
```
Because the candidate used strict inequality (`>`), `subtotal == Decimal("1000.00")` evaluated to `False`. The logic then fell through to `if subtotal >= Decimal("500.00"): return Decimal("0.07")`.

---

## 4. Causal Downstream Consequences

Because `discount_rate` diverged from `0.1000` to `0.0700`, a cascading ripple of 24 divergence diffs occurred across financial calculation, observable state, audit trails, and contract invariants:

1. **Discount Calculation (`result.discount`, `state_after.invoices[0].discount`, `final_state.invoices[0].discount`):**
   - Baseline: `1000.00 * 0.1000 = 100.00`
   - Candidate: `1000.00 * 0.0700 = 70.00`
   - *Impact:* Customer granted $30.00 less discount than legally required.

2. **Taxable Base (`result.tax_breakdown[0].taxable_base`, `state_after.invoices[0].tax_breakdown[0].taxable_base`, `final_state.invoices[0].tax_breakdown[0].taxable_base`):**
   - Baseline: `1000.00 - 100.00 = 900.00`
   - Candidate: `1000.00 - 70.00 = 930.00`
   - *Impact:* Taxable merchandise subtotal inflated by $30.00.

3. **Tax Computation (`result.tax`, `result.tax_breakdown[0].tax`, `state_after.invoices[0].tax`, `final_state.invoices[0].tax`):**
   - Region is `US_CA` with `GOODS` tax rate `7.25%` (`0.0725`):
     - Baseline: `900.00 * 0.0725 = 65.25`
     - Candidate: `930.00 * 0.0725 = 67.425 -> 67.43` (ROUND_HALF_UP)
   - *Impact:* Customer over-taxed by $2.18.

4. **Grand Total (`result.grand_total`, `state_after.invoices[0].grand_total`, `final_state.invoices[0].grand_total`):**
   - Free shipping applies (`$1000.00 >= $150.00` in `US_CA`), and payment method `BANK_TRANSFER` has zero card fee:
     - Baseline: `900.00 (subtotal) + 0.00 (shipping) + 65.25 (tax) = 965.25`
     - Candidate: `930.00 (subtotal) + 0.00 (shipping) + 67.43 (tax) = 997.43`
   - *Impact:* Total invoice charge over-billed by $32.18.

5. **Ledger & Audit Trail Records (`state_after.ledger[0].amount`, `state_after.audit[0].data.amount`, `final_state.ledger[0].amount`, `final_state.audit[0].data.amount`):**
   - Baseline persists transaction amounts of `965.25`.
   - Candidate persists transaction amounts of `997.43`.

6. **Outbound Event Notifications (`events_delta[0].data.amount`):**
   - Baseline emitted `invoice_created` event with amount `965.25`.
   - Candidate emitted `invoice_created` event with amount `997.43`.

7. **Contract Invariant Failures (`invariant_failures`):**
   - Invariant `bnd_vip_1000_00-rate` asserted `result.discount_rate == '0.1000'`.
   - Candidate failed this invariant (candidate invariant failures count = 1; baseline = 0).

---

## 5. Root Cause

- **File:** `modern_app/billing/pricing_policy.py`
- **Function:** `calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal`
- **Location:** Line 13
- **Defective Expression:**
  ```python
  if subtotal > Decimal("1000.00"):
  ```
- **Analysis:**
  The VIP tier discount policy requires that orders with subtotal *greater than or equal to* $1000.00 receive a 10% discount (`Decimal("0.10")`). Using a strict inequality (`>`) created an off-by-one boundary failure specifically at exact subtotal values of $1000.00.

---

## 6. Proposed Surgical Repair

Modify the boundary comparison in `modern_app/billing/pricing_policy.py` from strict greater-than (`>`) to greater-than-or-equal-to (`>=`):

```diff
--- a/modern_app/billing/pricing_policy.py
+++ b/modern_app/billing/pricing_policy.py
@@ -10,7 +10,7 @@
 def calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal:
     """Calculate tier discount rate based on customer tier and subtotal."""
     if tier == "VIP":
-        if subtotal > Decimal("1000.00"):
+        if subtotal >= Decimal("1000.00"):
             return Decimal("0.10")
         if subtotal >= Decimal("500.00"):
             return Decimal("0.07")
```

### Architectural & Compliance Evaluation
- **Files Modified:** Exactly 1 file (`modern_app/billing/pricing_policy.py`).
- **Diff Footprint:** 1 line modified (change `>` to `>=`).
- **Generality:** General business rule correction adhering to domain specification. No hardcoding of case IDs, customer IDs, or scenario outputs.
- **Architectural Constraints:**
  - Modern → legacy imports: 0 (unchanged)
  - Dependency cycles: 0 (unchanged)
  - Financial precision: Decimal maintained with exact quantize and rounding semantics.
