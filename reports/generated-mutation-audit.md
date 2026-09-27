# Aegis ContractLock - Generated Holdout Mutation Audit

## Executive Summary

- **Role**: Antigravity (Post-Freeze Adversarial Challenger)
- **Judge**: Aegis ContractLock Behavioral Verifier (`aegis_contract.yaml`)
- **Freeze Boundary**: Tag `aegis-holdout-freeze-20260927` (`reports/holdout-freeze-manifest.json`)
- **Freeze Verification Status**: `PASSED`
- **Total Generated**: **65**
- **Applied**: **65**
- **Runnable Candidates**: **63**
- **Detected (BLOCKED)**: **54**
- **Survived Contract (ACCEPTED)**: **9**
- **Invalid / Unrunnable**: **2**
- **Timeout / Infra Error**: **0**
- **Adversarial Detection Rate**: **85.71%** (over 63 runnable mutants)

> [!IMPORTANT]
> **Provenance and Anti-Backfitting Rule**
> The behavioral contract and accepted candidate were frozen **before** this mutation audit commenced.
> Antigravity acted as an independent post-freeze challenger. The historical IBM Bob clean-room run
> remains entirely separate. Surviving mutations are disclosed as empirical evidence of finite coverage boundaries
> rather than used to alter or backfit the frozen contract.

## Classification Taxonomy

| State | Count | Description |
|---|---:|---|
| `GENERATED` | 65 | Mutation candidates created by Antigravity post-freeze |
| `APPLIED` | 65 | Source AST/text transformations successfully applied to temporary copy |
| `RUNNABLE` | 63 | Mutated candidate compiles, imports, and executes against the Aegis gate |
| `DETECTED` | 54 | Frozen Aegis contract returned semantic drift (`BLOCKED`) |
| `SURVIVED_CONTRACT` | 9 | Mutated candidate executed all 86 cases and contract still returned `ACCEPTED` |
| `INVALID_OR_UNRUNNABLE` | 2 | Syntax/import error prevented meaningful behavioral comparison |
| `TIMEOUT_OR_INFRA_ERROR` | 0 | Execution failed for infrastructure/timeout reasons |

> **Denominator Definition**: Detection rate is calculated strictly over **RUNNABLE** mutants (`detected / runnable * 100.0`).
> Invalid/unrunnable mutants and timeout/infra errors are excluded from the denominator to avoid inflating or distorting verifier efficacy.

## Disclosed Contract Survivors (Evidence)

The following mutations executed completely across the entire 86-scenario behavioral suite without triggering any invariant failure or semantic drift against the sealed baseline.

### Mutant `MUT-GEN-06`: Remove min(subtotal, ...) ceiling cap on total discount calculation
- **File**: `modern_app/billing/pricing_policy.py:46`
- **Operator**: `boundary-cap-removal`
- **Original Source**:
```python
    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN))
```
- **Mutated Source**:
```python
    discount = (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN)
```
- **Why It May Be Important**: In all 86 contract scenarios, total discount never exceeds the merchandise subtotal (the maximum discount tested is $100.00 on a $1,000.00 subtotal, and $32.50 on $250.00 in coupon_ceiling_subtotal). The discount cap min(subtotal, ...) is defensive and is never triggered by the contract's inputs. In production, an aberrant stacking discount exceeding 100% would result in negative totals without this cap, but the frozen contract does not distinguish it.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-DOM-15`: Card surcharge rounding mode changed from ROUND_HALF_UP to ROUND_HALF_EVEN
- **File**: `modern_app/billing/pricing_policy.py:54`
- **Operator**: `rounding-mode-shift`
- **Original Source**:
```python
        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_UP)
```
- **Mutated Source**:
```python
        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_EVEN)
```
- **Why It May Be Important**: The card surcharge fee applies only to discounted merchandise subtotals >= $1,500.00. The contract tests $1,500.00 (fee = $22.500 exactly) and $1,500.01 (fee = $22.50015). Neither scenario generates an exact half-cent (.005) tie-break. Therefore, ROUND_HALF_UP and Banker's ROUND_HALF_EVEN produce identical dollar values for all tested card fee transactions.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-DOM-27`: Total tax sum quantization rounding changed from ROUND_HALF_UP to ROUND_HALF_EVEN
- **File**: `modern_app/billing/tax_policy.py:61`
- **Operator**: `rounding-mode-shift`
- **Original Source**:
```python
    return total_tax.quantize(MONEY, rounding=ROUND_HALF_UP), breakdown
```
- **Mutated Source**:
```python
    return total_tax.quantize(MONEY, rounding=ROUND_HALF_EVEN), breakdown
```
- **Why It May Be Important**: Total tax is computed by summing the individual line_tax values, each of which has already been quantized to cents (MONEY) using ROUND_HALF_UP on line 50. Because the sum of numbers with two decimal places never has fractional cents beyond the hundredths position, applying ROUND_HALF_EVEN versus ROUND_HALF_UP to the sum produces identical values across all 86 cases.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-01`: Change rounding on (pct_discount + fixed_coupon) from ROUND_HALF_EVEN to ROUND_HALF_UP
- **File**: `modern_app/billing/pricing_policy.py:46`
- **Operator**: `redundant-rounding-mode`
- **Original Source**:
```python
    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN))
```
- **Mutated Source**:
```python
    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_UP))
```
- **Why It May Be Important**: pct_discount is already quantized to exact cents (MONEY) and fixed_coupon has 2 decimal digits. Their sum never has fractional cents in any tested case, so ROUND_HALF_UP and ROUND_HALF_EVEN produce identical results. Survives because current test corpus only issues whole-cent coupons.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-02`: Remove max(Decimal('0.00'), ...) defensive floor clamp on line taxable base
- **File**: `modern_app/billing/tax_policy.py:33`
- **Operator**: `defensive-clamp-removal`
- **Original Source**:
```python
        taxable_base = max(
            Decimal("0.00"),
            (line_total - discount_share).quantize(MONEY, rounding=ROUND_HALF_UP),
        )
```
- **Mutated Source**:
```python
        taxable_base = (line_total - discount_share).quantize(MONEY, rounding=ROUND_HALF_UP)
```
- **Why It May Be Important**: In all 86 contract scenarios, the multi-line discount allocation ensures discount_share <= line_total, meaning line_total - discount_share is never negative. The defensive floor of 0.00 is never activated by the contract's inputs. A future scenario with an over-allocated coupon discount would drift, but the frozen contract does not distinguish it.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-03`: Alter negative unit_price validation threshold from < 0 to <= -1.00
- **File**: `modern_app/billing/service.py:101`
- **Operator**: `validation-boundary-gap`
- **Original Source**:
```python
            if unit_price < 0:
                raise ValidationError(f"Unit price for {sku} must be >= 0")
```
- **Mutated Source**:
```python
            if unit_price <= Decimal("-1.00"):
                raise ValidationError(f"Unit price for {sku} must be >= 0")
```
- **Why It May Be Important**: The frozen contract contains exactly one test case for negative price (val_item_negative_price), which passes unit_price: '-5.00'. Because -5.00 <= -1.00 evaluates to True, val_item_negative_price raises ValidationError and matches baseline. Subtle negative prices between -0.99 and -0.01 are untested, so this semantic mutation survives the contract.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-04`: Remove InvoiceNotFoundError check inside BillingStorage.update_invoice_status
- **File**: `modern_app/billing/storage.py:34`
- **Operator**: `redundant-defensive-guard-removal`
- **Original Source**:
```python
        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(invoice_id)
```
- **Mutated Source**:
```python
        # if invoice_id not in self._invoices:
        #     raise InvoiceNotFoundError(invoice_id)
```
- **Why It May Be Important**: BillingService._refund_invoice already queries get_invoice(invoice_id) and raises InvoiceNotFoundError prior to calling update_invoice_status. Therefore, update_invoice_status is never invoked with an invalid invoice ID in the existing workflow. The storage-layer guard is redundant in the workflow corpus and its omission survives.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-05`: Omit .strip() whitespace trimming on customer_id in create_invoice
- **File**: `modern_app/billing/service.py:70`
- **Operator**: `input-normalization-omission`
- **Original Source**:
```python
        customer_id = str(customer.get("id", "")).strip()
```
- **Mutated Source**:
```python
        customer_id = str(customer.get("id", ""))
```
- **Why It May Be Important**: All customer IDs throughout the 86 contract scenarios are pre-trimmed without leading or trailing whitespace (e.g. 'C-VIP-01'). Omitting the .strip() call leaves valid trimmed IDs unchanged. Dirty whitespace inputs are not included in the frozen contract suite.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

### Mutant `MUT-SURV-06`: Add free shipping for EXPORT orders exceeding $5,000.00 subtotal
- **File**: `modern_app/billing/shipping_policy.py:13`
- **Operator**: `unexercised-high-tier-rule`
- **Original Source**:
```python
    return Decimal("35.00")  # EXPORT
```
- **Mutated Source**:
```python
    return Decimal("0.00") if subtotal >= Decimal("5000.00") else Decimal("35.00")
```
- **Why It May Be Important**: The maximum subtotal tested for EXPORT orders across the frozen scenario suite is $1,000.00 (shipping_export_flat_high). Subtotals >= $5,000.00 are completely unexercised for the EXPORT region, so adding a high-tier free shipping rule alters the policy semantics while surviving the finite contract.
- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.

## Complete Mutant Evaluation Register

| Mutant ID | Category | Operator | Classification | Drifted | Counterexample |
|---|---|---|---|---:|---|
| `MUT-GEN-01` | GENERIC | `>= -> >` | `DETECTED` | 1 | `bnd_vip_subtotal_1000_00` |
| `MUT-GEN-02` | GENERIC | `>= -> >` | `DETECTED` | 1 | `bnd_vip_subtotal_500_00` |
| `MUT-GEN-03` | GENERIC | `>= -> >` | `DETECTED` | 1 | `bnd_bus_subtotal_2000_00` |
| `MUT-GEN-04` | GENERIC | `>= -> >` | `DETECTED` | 1 | `bnd_bus_subtotal_1000_00` |
| `MUT-GEN-05` | GENERIC | `>= -> >` | `DETECTED` | 2 | `coupon_ceiling_subtotal` |
| `MUT-GEN-06` | GENERIC | `boundary-cap-removal` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-GEN-07` | GENERIC | `arithmetic - -> +` | `DETECTED` | 24 | `bnd_bus_subtotal_1000_00` |
| `MUT-GEN-08` | GENERIC | `== -> !=` | `DETECTED` | 8 | `bnd_bus_subtotal_1999_99` |
| `MUT-GEN-09` | GENERIC | `>= -> >` | `DETECTED` | 1 | `fee_card_at_1500_00` |
| `MUT-GEN-10` | GENERIC | `boolean-negation` | `DETECTED` | 66 | `bnd_bus_subtotal_1000_00` |
| `MUT-GEN-11` | GENERIC | `>= -> >` | `DETECTED` | 1 | `shipping_us_ca_at_150_00` |
| `MUT-GEN-12` | GENERIC | `>= -> >` | `DETECTED` | 2 | `shipping_eu_de_at_250_00` |
| `MUT-GEN-13` | GENERIC | `branch-removal` | `DETECTED` | 1 | `tax_zero_subtotal_short_circuit` |
| `MUT-GEN-14` | GENERIC | `== -> !=` | `DETECTED` | 41 | `bnd_vip_subtotal_1000_00` |
| `MUT-GEN-15` | GENERIC | `<= -> <` | `DETECTED` | 1 | `refund_full_window_24h` |
| `MUT-GEN-16` | GENERIC | `<= -> <` | `DETECTED` | 1 | `refund_fee_window_72h` |
| `MUT-GEN-17` | GENERIC | `branch-removal` | `DETECTED` | 1 | `val_suspended_customer` |
| `MUT-GEN-18` | GENERIC | `<= -> <` | `DETECTED` | 1 | `val_item_zero_qty` |
| `MUT-DOM-01` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 2 | `bnd_vip_subtotal_1000_00` |
| `MUT-DOM-02` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 4 | `bnd_vip_subtotal_500_00` |
| `MUT-DOM-03` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 4 | `bnd_vip_subtotal_499_99` |
| `MUT-DOM-04` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 2 | `bnd_bus_subtotal_2000_00` |
| `MUT-DOM-05` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 4 | `bnd_bus_subtotal_1000_00` |
| `MUT-DOM-06` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 48 | `coupon_case_insensitivity` |
| `MUT-DOM-07` | DOMAIN-SEMANTIC | `coupon-cap-alteration` | `DETECTED` | 3 | `coupon_welcome10_bus_high_capped` |
| `MUT-DOM-08` | DOMAIN-SEMANTIC | `coupon-cap-removal` | `DETECTED` | 3 | `coupon_welcome10_bus_high_capped` |
| `MUT-DOM-09` | DOMAIN-SEMANTIC | `coupon-rate-shift` | `DETECTED` | 5 | `coupon_case_insensitivity` |
| `MUT-DOM-10` | DOMAIN-SEMANTIC | `threshold-shift` | `DETECTED` | 4 | `coupon_ceiling_subtotal` |
| `MUT-DOM-11` | DOMAIN-SEMANTIC | `value-shift` | `DETECTED` | 4 | `coupon_ceiling_subtotal` |
| `MUT-DOM-12` | DOMAIN-SEMANTIC | `rounding-mode-shift` | `DETECTED` | 1 | `rounding_bankers_half_even_discount` |
| `MUT-DOM-13` | DOMAIN-SEMANTIC | `threshold-shift` | `DETECTED` | 2 | `fee_card_above_1500_01` |
| `MUT-DOM-14` | DOMAIN-SEMANTIC | `rate-shift` | `DETECTED` | 2 | `fee_card_above_1500_01` |
| `MUT-DOM-15` | DOMAIN-SEMANTIC | `rounding-mode-shift` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-DOM-16` | DOMAIN-SEMANTIC | `fee-shift` | `DETECTED` | 22 | `coupon_case_insensitivity` |
| `MUT-DOM-17` | DOMAIN-SEMANTIC | `threshold-shift` | `DETECTED` | 2 | `shipping_us_ca_above_150_01` |
| `MUT-DOM-18` | DOMAIN-SEMANTIC | `fee-shift` | `DETECTED` | 8 | `shipping_eu_de_below_249_99` |
| `MUT-DOM-19` | DOMAIN-SEMANTIC | `fee-shift` | `DETECTED` | 4 | `rounding_refund_fee_half_even` |
| `MUT-DOM-20` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 38 | `bnd_vip_subtotal_1000_00` |
| `MUT-DOM-21` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 11 | `bnd_bus_subtotal_1000_00` |
| `MUT-DOM-22` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 1 | `tax_eu_de_essential` |
| `MUT-DOM-23` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 4 | `shipping_eu_de_at_250_00` |
| `MUT-DOM-24` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 4 | `shipping_uk_at_250_00` |
| `MUT-DOM-25` | DOMAIN-SEMANTIC | `tax-rate-shift` | `DETECTED` | 4 | `rounding_refund_fee_half_even` |
| `MUT-DOM-26` | DOMAIN-SEMANTIC | `rounding-mode-shift` | `DETECTED` | 3 | `coupon_case_insensitivity` |
| `MUT-DOM-27` | DOMAIN-SEMANTIC | `rounding-mode-shift` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-DOM-28` | DOMAIN-SEMANTIC | `window-drift` | `DETECTED` | 2 | `refund_fee_window_25h` |
| `MUT-DOM-29` | DOMAIN-SEMANTIC | `window-drift` | `DETECTED` | 2 | `refund_after_manual_review_allowed` |
| `MUT-DOM-30` | DOMAIN-SEMANTIC | `fee-rate-shift` | `DETECTED` | 3 | `refund_fee_window_25h` |
| `MUT-DOM-31` | DOMAIN-SEMANTIC | `rounding-mode-shift` | `DETECTED` | 1 | `rounding_refund_fee_half_even` |
| `MUT-DOM-32` | DOMAIN-SEMANTIC | `ledger-reversal` | `DETECTED` | 68 | `bnd_bus_subtotal_1000_00` |
| `MUT-DOM-33` | DOMAIN-SEMANTIC | `ledger-reversal` | `DETECTED` | 8 | `idempotency_refund_exact_replay` |
| `MUT-DOM-34` | DOMAIN-SEMANTIC | `idempotency-removal` | `DETECTED` | 2 | `idempotency_invoice_exact_replay` |
| `MUT-DOM-35` | DOMAIN-SEMANTIC | `idempotency-removal` | `DETECTED` | 1 | `idempotency_refund_exact_replay` |
| `MUT-DOM-36` | DOMAIN-SEMANTIC | `audit-event-omission` | `DETECTED` | 68 | `bnd_bus_subtotal_1000_00` |
| `MUT-DOM-37` | DOMAIN-SEMANTIC | `audit-event-omission` | `DETECTED` | 8 | `idempotency_refund_exact_replay` |
| `MUT-DOM-38` | DOMAIN-SEMANTIC | `state-write-omission` | `DETECTED` | 8 | `idempotency_refund_exact_replay` |
| `MUT-DOM-39` | DOMAIN-SEMANTIC | `guard-removal` | `DETECTED` | 1 | `refund_duplicate_approved_rejected` |
| `MUT-SURV-01` | SURVIVOR-CANDIDATE | `redundant-rounding-mode` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-SURV-02` | SURVIVOR-CANDIDATE | `defensive-clamp-removal` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-SURV-03` | SURVIVOR-CANDIDATE | `validation-boundary-gap` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-SURV-04` | SURVIVOR-CANDIDATE | `redundant-defensive-guard-removal` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-SURV-05` | SURVIVOR-CANDIDATE | `input-normalization-omission` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-SURV-06` | SURVIVOR-CANDIDATE | `unexercised-high-tier-rule` | `SURVIVED_CONTRACT` | 0 | `-` |
| `MUT-INV-01` | INVALID-TEST | `syntax-error-injection` | `INVALID_OR_UNRUNNABLE` | 0 | `-` |
| `MUT-INV-02` | INVALID-TEST | `import-error-injection` | `INVALID_OR_UNRUNNABLE` | 0 | `-` |

## Scientific Limitations

1. **Finite Mutation Testing**: This experiment measures empirical verifier sensitivity across 65 structured fault injections; it does not constitute a formal mathematical proof of program equivalence.
2. **Clean-Room Boundary**: IBM Bob's historical evidence is preserved untouched. This audit reflects post-freeze adversarial testing by Antigravity.
3. **No Contract Backfitting**: In accordance with the freeze rules, the disclosed survivors were not patched into `aegis_contract.yaml`.
