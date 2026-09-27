# Aegis ContractLock — End-to-End Traceability Matrix

**System:** Aegis ContractLock Modernization Engine
**Evidence Baseline:** `aegis-holdout-freeze-20260927`
**Contract Version:** `2.0` (`aegis_contract.yaml`)
**Scope:** Hardened Public Validation Package (86 behavioral cases, 100 workflow steps, 231 contract invariants, 21 negative controls)

---

## 1. Traceability Architecture

The Aegis ContractLock verification model enforces strict, multi-hop bidirectional traceability from documented business requirements to executable verification fixtures:

$$\text{Business Policy} \longleftrightarrow \text{Legacy Monolith Source} \longleftrightarrow \text{Behavioral Contract Cases} \longleftrightarrow \text{Curated Mutation Controls}$$

Rules are mapped across the legacy baseline, policy documentation, and the modern candidate to provide transparent behavioral accounting. Where defensive boundaries exist in source logic but are not independently activated by the finite frozen scenario corpus (such as defensive clipping caps), these boundaries are explicitly identified as disclosed coverage limits.

---

## 2. Rule Family Traceability Catalog

### Family 1: VIP Tier Volume Discounts
*Business Policy:* Orders below \$500.00 receive 3%; from \$500.00 through \$999.99 receive 7%; \$1,000.00 and above receive 10%. Thresholds are inclusive.
- **Legacy Source:** `legacy_app/billing/monolith.py#L247-L253` (`_get_discount_rate`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §1 ("Customer tiers and discounts")
- **Hardened Contract Cases (6 cases):**
  - `bnd_vip_subtotal_499_99` (`['critical_boundary', 'discount', 'vip']`): \$499.99 subtotal receives 3.00% (`0.0300`)
  - `bnd_vip_subtotal_500_00` (`['critical_boundary', 'discount', 'vip']`): Exact \$500.00 threshold receives 7.00% (`0.0700`)
  - `bnd_vip_subtotal_500_01` (`['critical_boundary', 'discount', 'vip']`): \$500.01 subtotal receives 7.00% (`0.0700`)
  - `bnd_vip_subtotal_999_99` (`['critical_boundary', 'discount', 'vip']`): \$999.99 subtotal receives 7.00% (`0.0700`)
  - `bnd_vip_subtotal_1000_00` (`['critical_boundary', 'discount', 'vip']`): Exact \$1,000.00 threshold receives 10.00% (`0.1000`)
  - `bnd_vip_subtotal_1000_01` (`['critical_boundary', 'discount', 'vip']`): \$1,000.01 subtotal receives 10.00% (`0.1000`)
- **Curated Mutation Controls:**
  - `vip_1000_strict` (Fault category: Boundary Inclusivity) — Caught by `bnd_vip_subtotal_1000_00` (1 drifted)
  - `vip_500_strict` (Fault category: Boundary Inclusivity) — Caught by `bnd_vip_subtotal_500_00` (1 drifted)

---

### Family 2: Business Tier Volume Discounts
*Business Policy:* Orders below \$1,000.00 receive 0%; from \$1,000.00 through \$1,999.99 receive 4%; \$2,000.00 and above receive 6%. Thresholds are inclusive.
- **Legacy Source:** `legacy_app/billing/monolith.py#L254-L260` (`_get_discount_rate`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §1 ("Customer tiers and discounts")
- **Hardened Contract Cases (6 cases):**
  - `bnd_bus_subtotal_999_99` (`['business', 'critical_boundary', 'discount']`): \$999.99 subtotal receives 0.00% (`0.0000`)
  - `bnd_bus_subtotal_1000_00` (`['business', 'critical_boundary', 'discount']`): Exact \$1,000.00 threshold receives 4.00% (`0.0400`)
  - `bnd_bus_subtotal_1000_01` (`['business', 'critical_boundary', 'discount']`): \$1,000.01 subtotal receives 4.00% (`0.0400`)
  - `bnd_bus_subtotal_1999_99` (`['business', 'critical_boundary', 'discount']`): \$1,999.99 subtotal receives 4.00% (`0.0400`)
  - `bnd_bus_subtotal_2000_00` (`['business', 'critical_boundary', 'discount']`): Exact \$2,000.00 threshold receives 6.00% (`0.0600`)
  - `bnd_bus_subtotal_2000_01` (`['business', 'critical_boundary', 'discount']`): \$2,000.01 subtotal receives 6.00% (`0.0600`)
- **Curated Mutation Controls:**
  - `business_1000_strict` (Fault category: Boundary Inclusivity) — Caught by `bnd_bus_subtotal_1000_00` (1 drifted)
  - `business_2000_strict` (Fault category: Boundary Inclusivity) — Caught by `bnd_bus_subtotal_2000_00` (1 drifted)

---

### Family 3: Retail Tier Orders
*Business Policy:* Retail customers receive 0.00% automatic volume tier discount regardless of order value.
- **Legacy Source:** `legacy_app/billing/monolith.py#L261-L262` (`_get_discount_rate`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §1 ("Customer tiers and discounts")
- **Hardened Contract Cases (2 cases):**
  - `retail_standard_order` (`['discount', 'retail']`): Standard subtotal order receives 0.00% discount
  - `retail_high_value_order` (`['discount', 'retail']`): High subtotal order (\$3,000.00+) strictly receives 0.00% discount
- **Curated Mutation Controls:**
  - Evaluated under general tier validation and boundary isolation.

---

### Family 4: Coupons, Stacking & Ceiling Rules
*Business Policy:* `WELCOME10` adds 10% to tier rate, capped at 15% combined. `FIXED25` grants \$25.00 off if subtotal $\ge$ \$250.00, silently \$0.00 if below. Coupon code is case-insensitive. Total discount capped at merchandise subtotal.
- **Legacy Source:** `legacy_app/billing/monolith.py#L147-L177` (`_calculate_discounts`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §1 ("Customer tiers and discounts")
- **Hardened Contract Cases (11 cases):**
  - `coupon_welcome10_retail` (`['coupon', 'critical_boundary', 'discount']`): 0% + 10% = 10% rate
  - `coupon_welcome10_vip_low` (`['coupon', 'critical_boundary', 'discount', 'vip']`): 3% + 10% = 13% rate
  - `coupon_welcome10_vip_mid_capped` (`['coupon', 'critical_boundary', 'discount', 'vip']`): 7% + 10% = 17% $\to$ capped at 15%
  - `coupon_welcome10_vip_high_capped` (`['coupon', 'critical_boundary', 'discount', 'vip']`): 10% + 10% = 20% $\to$ capped at 15%
  - `coupon_welcome10_bus_mid` (`['business', 'coupon', 'critical_boundary', 'discount']`): 4% + 10% = 14% rate
  - `coupon_welcome10_bus_high_capped` (`['business', 'coupon', 'critical_boundary', 'discount']`): 6% + 10% = 16% $\to$ capped at 15%
  - `coupon_fixed25_below_249_99` (`['coupon', 'critical_boundary', 'discount']`): Subtotal \$249.99 silently receives \$0.00 coupon discount
  - `coupon_fixed25_at_250_00` (`['coupon', 'critical_boundary', 'discount']`): Subtotal \$250.00 receives \$25.00 coupon discount
  - `coupon_fixed25_above_250_01` (`['coupon', 'critical_boundary', 'discount']`): Subtotal \$250.01 receives \$25.00 coupon discount
  - `coupon_case_insensitivity` (`['coupon', 'discount']`): Lowercase coupon `welcome10` matches canonical `WELCOME10`
  - `coupon_ceiling_subtotal` (`['coupon', 'critical_boundary', 'discount']`): Subtotal \$250.00 with VIP tier (3% = \$7.50) and FIXED25 (\$25.00) evaluates combined discount (\$32.50) at the coupon qualification boundary
- **Curated Mutation Controls:**
  - `welcome_cap_20` (Fault category: Coupon Cap Logic) — Caught by `coupon_welcome10_bus_high_capped` (3 drifted)
  - `fixed25_strict` (Fault category: Boundary Inclusivity, `>=` to `>`) — Caught by `coupon_ceiling_subtotal` (at exact \$250.00 threshold) and `coupon_fixed25_at_250_00` (2 drifted)

> [!NOTE]
> **Disclosed Finite-Coverage Boundary (Defensive Total-Discount Cap):**
> `legacy_app/billing/monolith.py#L170` contains defensive logic capping total discount to subtotal: `min(subtotal, (pct_discount + fixed_coupon).quantize(ROUND_HALF_EVEN))`.
> The 86-case frozen contract does not include a scenario where combined percentage and fixed discounts exceed merchandise subtotal (since `FIXED25` requires subtotal $\ge$ \$250.00, yielding max combined discount of \$25.00 + 15% = \$62.50 $\ll$ \$250.00).
> Consequently, post-freeze Lane C holdout mutation `MUT-GEN-06` (which removed `min(subtotal, ...)`) survived verification against the frozen contract with 0 drift. The 86-case frozen contract does not independently distinguish activation of that defensive truncation cap. This is documented as a known, disclosed finite-coverage boundary.

---

### Family 5: Shipping Rates & Threshold Evaluation Basis
*Business Policy:* US orders free if subtotal $\ge$ \$150.00, else \$12.00. EU/UK free if subtotal $\ge$ \$250.00, else \$18.00. EXPORT flat \$35.00. Thresholds evaluated on pre-discount merchandise subtotal.
- **Legacy Source:** `legacy_app/billing/monolith.py#L179-L191` (`_calculate_shipping`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §4 ("Shipping and payment fees")
- **Hardened Contract Cases (11 cases):**
  - `shipping_us_ca_below_149_99` (`['critical_boundary', 'shipping']`): US_CA order \$149.99 charges \$12.00
  - `shipping_us_ca_at_150_00` (`['critical_boundary', 'shipping']`): US_CA order exact \$150.00 qualifies for free shipping (\$0.00)
  - `shipping_us_ca_above_150_01` (`['critical_boundary', 'shipping']`): US_CA order \$150.01 qualifies for free shipping (\$0.00)
  - `shipping_us_ny_below_149_99` (`['critical_boundary', 'shipping']`): US_NY order \$149.99 charges \$12.00
  - `shipping_eu_de_below_249_99` (`['critical_boundary', 'shipping']`): EU_DE order \$249.99 charges \$18.00
  - `shipping_eu_de_at_250_00` (`['critical_boundary', 'shipping']`): EU_DE order exact \$250.00 qualifies for free shipping (\$0.00)
  - `shipping_uk_below_249_99` (`['critical_boundary', 'shipping']`): UK order \$249.99 charges \$18.00
  - `shipping_uk_at_250_00` (`['critical_boundary', 'shipping']`): UK order exact \$250.00 qualifies for free shipping (\$0.00)
  - `shipping_export_flat_low` (`['export', 'shipping']`): Low-value EXPORT order charges flat \$35.00
  - `shipping_export_flat_high` (`['export', 'shipping']`): High-value EXPORT order charges flat \$35.00
  - `shipping_pre_discount_subtotal_trap` (`['critical_boundary', 'discount', 'shipping']`): Pre-discount \$160.00 qualifies for free shipping even when post-discount subtotal drops to \$144.00
- **Curated Mutation Controls:**
  - `us_shipping_strict` (Fault category: Boundary Inclusivity) — Caught by `shipping_us_ca_at_150_00` (1 drifted)
  - `eu_shipping_strict` (Fault category: Boundary Inclusivity) — Caught by `shipping_eu_de_at_250_00` (2 drifted)

---

### Family 6: Regional Tax Rates & Category Exemptions
*Business Policy:* US_CA (GOODS 7.25%, DIGITAL/ESSENTIAL 0%). US_NY (GOODS/DIGITAL 8.875%, ESSENTIAL 0%). EU_DE (GOODS/DIGITAL 19%, ESSENTIAL 7%). UK (GOODS/DIGITAL 20%, ESSENTIAL 0%). EXPORT (all 0%).
- **Legacy Source:** `legacy_app/billing/monolith.py#L210-L245` (`_calculate_taxes`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §3 ("Fictional regional tax treatment")
- **Hardened Contract Cases (14 cases):**
  - `tax_us_ca_goods` (`['tax', 'us_ca']`): US_CA GOODS taxed at 7.25%
  - `tax_us_ca_digital` (`['tax', 'us_ca']`): US_CA DIGITAL exempt (0%)
  - `tax_us_ca_essential` (`['tax', 'us_ca']`): US_CA ESSENTIAL exempt (0%)
  - `tax_us_ny_goods` (`['tax', 'us_ny']`): US_NY GOODS taxed at 8.875%
  - `tax_us_ny_digital` (`['tax', 'us_ny']`): US_NY DIGITAL taxed at 8.875%
  - `tax_us_ny_essential` (`['tax', 'us_ny']`): US_NY ESSENTIAL exempt (0%)
  - `tax_eu_de_goods` (`['eu_de', 'tax']`): EU_DE GOODS taxed at 19%
  - `tax_eu_de_digital` (`['eu_de', 'tax']`): EU_DE DIGITAL taxed at 19%
  - `tax_eu_de_essential` (`['eu_de', 'tax']`): EU_DE ESSENTIAL reduced rate at 7%
  - `tax_uk_goods` (`['tax', 'uk']`): UK GOODS taxed at 20%
  - `tax_uk_digital` (`['tax', 'uk']`): UK DIGITAL taxed at 20%
  - `tax_uk_essential` (`['tax', 'uk']`): UK ESSENTIAL exempt (0%)
  - `tax_export_all_categories` (`['export', 'tax']`): EXPORT destination has 0% tax across all categories
  - `tax_zero_subtotal_short_circuit` (`['tax', 'validation']`): Zero-subtotal invoice short-circuits to \$0.00 tax and empty breakdown list `[]`
- **Curated Mutation Controls:**
  - `ca_goods_wrong_rate` (Fault category: Regional Tax Matrix) — Caught by `bnd_vip_subtotal_1000_00` (38 drifted)
  - `ny_digital_exempt` (Fault category: Regional Tax Matrix) — Caught by `tax_us_ny_digital` (1 drifted)
  - `eude_essential_standard_tax` (Fault category: Regional Tax Matrix) — Caught by `tax_eu_de_essential` (1 drifted)
  - `uk_essential_taxed` (Fault category: Regional Tax Matrix) — Caught by `tax_uk_essential` (1 drifted)
  - `export_taxed` (Fault category: Regional Tax Matrix) — Caught by `rounding_refund_fee_half_even` (4 drifted)

---

### Family 7: Monetary Precision & Rounding Pipeline
*Business Policy:* Half-up rounding on line items and grand totals; Banker's rounding (`ROUND_HALF_EVEN`) on discounts; multi-line proportional tax allocation assigns residual discount to final line.
- **Legacy Source:** `legacy_app/billing/monolith.py#L136-L145`, `L166-L177`, `L220-L240`, `L403`
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §2 ("Monetary behavior")
- **Hardened Contract Cases (2 cases):**
  - `rounding_multiline_proportional_residual` (`['critical_boundary', 'discount', 'tax']`): Proportional discount allocation assigns residual to line N-1
  - `rounding_bankers_half_even_discount` (`['critical_boundary', 'discount']`): Banker's rounding on fractional discount cents
- **Curated Mutation Controls:**
  - Validated across multi-line tax matrix mutations and refund fee rounding controls.

---

### Family 8: Payment Methods & Service Fees
*Business Policy:* CARD payments incur a 1.5% fee (`ROUND_HALF_UP`) only when discounted merchandise subtotal $\ge$ \$1,500.00. BANK_TRANSFER incurs zero fee.
- **Legacy Source:** `legacy_app/billing/monolith.py#L193-L208` (`_calculate_service_fee`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §4 ("Shipping and payment fees")
- **Hardened Contract Cases (4 cases):**
  - `fee_card_below_1499_99` (`['critical_boundary', 'service_fee']`): CARD payment at \$1,499.99 discounted subtotal incurs \$0.00 fee
  - `fee_card_at_1500_00` (`['critical_boundary', 'service_fee']`): CARD payment at exact \$1,500.00 discounted subtotal incurs 1.5% fee (\$22.50)
  - `fee_card_above_1500_01` (`['critical_boundary', 'service_fee']`): CARD payment at \$1,500.01 discounted subtotal incurs 1.5% fee (\$22.50)
  - `fee_bank_transfer_high_value` (`['critical_boundary', 'service_fee']`): BANK_TRANSFER incurs \$0.00 fee regardless of amount (\$2,500.00+)
- **Curated Mutation Controls:**
  - `card_fee_strict` (Fault category: Payment Fee Boundary) — Caught by `fee_card_at_1500_00` (1 drifted)

---

### Family 9: Refund Windows, State Transitions & Fees
*Business Policy:* 0-24h refund approved in full (0% fee). 25-72h approved with 5% Banker's rounding fee. >72h routed to `MANUAL_REVIEW` (\$0.00 fee, \$0.00 payout, invoice stays `OPEN`). Approved refund sets invoice `REFUNDED` and writes CREDIT ledger.
- **Legacy Source:** `legacy_app/billing/monolith.py#L358-L417` (`refund_invoice`)
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §6 ("Refund policy")
- **Hardened Contract Cases (8 cases):**
  - `refund_full_window_0h` (`['critical_boundary', 'refund', 'state_transition']`): 0 hours after purchase approved with \$0.00 fee
  - `refund_full_window_24h` (`['critical_boundary', 'refund', 'state_transition']`): Exact 24h boundary approved with \$0.00 fee
  - `refund_fee_window_25h` (`['critical_boundary', 'refund', 'state_transition']`): 25h boundary approved with 5% fee
  - `refund_fee_window_72h` (`['critical_boundary', 'refund', 'state_transition']`): Exact 72h boundary approved with 5% fee
  - `refund_manual_review_73h` (`['critical_boundary', 'refund', 'state_transition']`): 73h boundary routed to `MANUAL_REVIEW`, \$0 payout
  - `rounding_refund_fee_half_even` (`['critical_boundary', 'refund']`): 5% fee on \$50.10 rounds to \$2.50 via Banker's rounding
  - `refund_duplicate_approved_rejected` (`['refund', 'state_transition', 'validation']`): Second refund on already-refunded invoice rejected
  - `refund_after_manual_review_allowed` (`['refund', 'state_transition']`): Subsequent refund approved after prior `MANUAL_REVIEW`
- **Curated Mutation Controls:**
  - `refund_24_strict` (Fault category: Refund Window Boundary) — Caught by `refund_full_window_24h` (1 drifted)
  - `refund_72_strict` (Fault category: Refund Window Boundary) — Caught by `refund_fee_window_72h` (1 drifted)
  - `refund_direction_debit` (Fault category: Accounting Ledger Direction) — Caught by `idempotency_refund_exact_replay` (8 drifted)
  - `omit_refund_ledger` (Fault category: State Persistence Omission) — Caught by `idempotency_refund_exact_replay` (8 drifted)

---

### Family 10: Idempotency Guarantees & Audit Trails
*Business Policy:* Operations keyed by `operation_id` must return identical responses on retry without duplicating ledger records or audit events. Failed operations must not be cached.
- **Legacy Source:** `legacy_app/billing/monolith.py#L82-L89`, `L360-L364`
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §5 ("Invoice state and audit requirements")
- **Hardened Contract Cases (3 cases):**
  - `idempotency_invoice_exact_replay` (`['idempotency']`): Replaying invoice creation returns cached payload with 0 additional side effects
  - `idempotency_invoice_tampered_payload` (`['idempotency']`): Tampered payload with duplicate `operation_id` returns original cached result
  - `idempotency_refund_exact_replay` (`['idempotency', 'refund']`): Replaying refund returns cached refund record without duplicate credit entries
- **Curated Mutation Controls:**
  - `no_idempotency` (Fault category: Idempotency / Cache Bypass) — Caught by `idempotency_invoice_exact_replay` (3 drifted)
  - `omit_invoice_audit` (Fault category: Audit Trail Omission) — Caught by `bnd_bus_subtotal_1000_00` (68 drifted)
  - `omit_refund_audit` (Fault category: Audit Trail Omission) — Caught by `idempotency_refund_exact_replay` (8 drifted)

---

### Family 11: Input Validation & Domain Error Codes
*Business Policy:* Rejection of malformed, suspended, or out-of-domain payloads without state mutation.
- **Legacy Source:** `legacy_app/billing/monolith.py#L69-L134`, `L366-L386`
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §7 ("Failure behavior")
- **Hardened Contract Cases (18 cases):**
  - `val_unsupported_operation`: Operation other than `create_invoice` or `refund_invoice`
  - `val_missing_operation_id`: Empty/missing operation identifier
  - `val_missing_customer_id`: Missing customer entity identifier
  - `val_suspended_customer`: Account with `SUSPENDED` status (`ACCOUNT_SUSPENDED`)
  - `val_unknown_customer_tier`: Invalid customer tier name
  - `val_unknown_region`: Unrecognized destination region code
  - `val_empty_items`: Invoice with zero line items
  - `val_item_missing_sku`: Item missing SKU code
  - `val_item_unknown_category`: Unsupported item category
  - `val_item_zero_qty`: Quantity equal to 0
  - `val_item_negative_qty`: Negative item quantity
  - `val_item_negative_price`: Negative unit price
  - `val_unknown_coupon`: Unrecognized coupon code
  - `val_unknown_payment_method`: Unsupported payment method
  - `val_refund_missing_op_id`: Refund request missing operation ID
  - `val_refund_missing_invoice_id`: Refund request missing target invoice ID
  - `val_refund_negative_hours`: Negative `hours_since_purchase` integer
  - `val_refund_invoice_not_found`: Non-existent target invoice ID
- **Curated Mutation Controls:**
  - Validated by engine test suite and negative validation assertions.

---

### Family 12: Defaults & Normalization
*Business Policy:* Default values applied when optional fields are omitted (e.g., active customer status, retail tier, default goods category, card payment).
- **Legacy Source:** `legacy_app/billing/monolith.py#L91-L105`
- **Document Source:** `legacy_app/docs/BILLING_POLICY.md` §1 & §7
- **Hardened Contract Cases (1 case):**
  - `default_values_customer_and_item` (`['default_values']`): Normalization of omitted fields to standard business defaults

---

## 3. Curated Negative Control Gauntlet Mapping

| # | Mutant Name | Fault Category Injected | Primary Drifted Case | Total Drifted |
|---|---|---|---|:---:|
| 1 | `vip_1000_strict` | Boundary Inclusivity (`>=` to `>`) | `bnd_vip_subtotal_1000_00` | 1 |
| 2 | `vip_500_strict` | Boundary Inclusivity (`>=` to `>`) | `bnd_vip_subtotal_500_00` | 1 |
| 3 | `business_2000_strict` | Boundary Inclusivity (`>=` to `>`) | `bnd_bus_subtotal_2000_00` | 1 |
| 4 | `business_1000_strict` | Boundary Inclusivity (`>=` to `>`) | `bnd_bus_subtotal_1000_00` | 1 |
| 5 | `welcome_cap_20` | Coupon Stacking Cap (15% to 20%) | `coupon_welcome10_bus_high_capped` | 3 |
| 6 | `fixed25_strict` | Coupon Threshold Inclusivity (`>=` to `>`) | `coupon_ceiling_subtotal` | 2 |
| 7 | `us_shipping_strict` | Shipping Threshold Inclusivity (`>=` to `>`) | `shipping_us_ca_at_150_00` | 1 |
| 8 | `eu_shipping_strict` | Shipping Threshold Inclusivity (`>=` to `>`) | `shipping_eu_de_at_250_00` | 2 |
| 9 | `eude_essential_standard_tax` | Regional Tax Rate Modification (7% to 19%) | `tax_eu_de_essential` | 1 |
| 10 | `uk_essential_taxed` | Regional Exemption Removal (0% to 20%) | `tax_uk_essential` | 1 |
| 11 | `export_taxed` | Regional Exemption Removal (0% to 10%) | `rounding_refund_fee_half_even` | 4 |
| 12 | `ny_digital_exempt` | Regional Tax Rate Modification (8.875% to 0%) | `tax_us_ny_digital` | 1 |
| 13 | `ca_goods_wrong_rate` | Regional Tax Rate Modification (7.25% to 8.25%) | `bnd_vip_subtotal_1000_00` | 38 |
| 14 | `card_fee_strict` | Payment Fee Threshold Inclusivity (`>=` to `>`) | `fee_card_at_1500_00` | 1 |
| 15 | `refund_24_strict` | Refund Window Boundary Inclusivity (`<=` to `<`) | `refund_full_window_24h` | 1 |
| 16 | `refund_72_strict` | Refund Window Boundary Inclusivity (`<=` to `<`) | `refund_fee_window_72h` | 1 |
| 17 | `refund_direction_debit` | Ledger Accounting Direction (CREDIT to DEBIT) | `idempotency_refund_exact_replay` | 8 |
| 18 | `omit_refund_ledger` | State Persistence Omission (Skipped Ledger Entry) | `idempotency_refund_exact_replay` | 8 |
| 19 | `omit_invoice_audit` | Audit Trail Omission (Skipped Event Emission) | `bnd_bus_subtotal_1000_00` | 68 |
| 20 | `omit_refund_audit` | Audit Trail Omission (Skipped Event Emission) | `idempotency_refund_exact_replay` | 8 |
| 21 | `no_idempotency` | State Bypass / Cache Bypass (Duplicate Execution) | `idempotency_invoice_exact_replay` | 3 |

**Gauntlet Detection Summary:**
$$\frac{\text{Detected Regressions}}{\text{Seeded Regressions}} = \frac{21}{21} = \mathbf{100.00\%} \quad (\text{Escaped: } 0)$$

---

## 4. Total Case Partition Accounting

| Rule Family | Unique Case Count |
|---|:---:|
| 1. VIP Tier Volume Discounts | 6 |
| 2. Business Tier Volume Discounts | 6 |
| 3. Retail Tier Orders | 2 |
| 4. Coupons, Stacking & Ceilings | 11 |
| 5. Regional Shipping Rates & Basis | 11 |
| 6. Regional Tax Rates & Categories | 14 |
| 7. Monetary Rounding & Allocation | 2 |
| 8. Payment Method Service Fees | 4 |
| 9. Refund Lifecycle & Transitions | 8 |
| 10. Idempotency Guarantees & Audit | 3 |
| 11. Input Validation & Errors | 18 |
| 12. Defaults & Normalization | 1 |
| **Total Sealed Behavioral Cases** | **86** |

Every case ID in this matrix corresponds to an executable definition in `aegis_contract.yaml` and is evaluated against both the legacy baseline and the modern candidate during verification.
