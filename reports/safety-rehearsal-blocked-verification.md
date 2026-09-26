# Aegis ContractLock Verification Report

**Verdict:** `BLOCKED`

- Cases matched: **85 / 86**
- Cases drifted: **1**
- Baseline evidence SHA-256: `2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7`
- Candidate evidence SHA-256: `1ea9f7929341101d0d81b50a441e39df44bbd823ffa48176af93744ae67fd4ac`

| Case | Status | Drift count |
|---|---:|---:|
| `bnd_bus_subtotal_1000_00` | MATCH | 0 |
| `bnd_bus_subtotal_1000_01` | MATCH | 0 |
| `bnd_bus_subtotal_1999_99` | MATCH | 0 |
| `bnd_bus_subtotal_2000_00` | MATCH | 0 |
| `bnd_bus_subtotal_2000_01` | MATCH | 0 |
| `bnd_bus_subtotal_999_99` | MATCH | 0 |
| `bnd_vip_subtotal_1000_00` | DRIFT | 24 |
| `bnd_vip_subtotal_1000_01` | MATCH | 0 |
| `bnd_vip_subtotal_499_99` | MATCH | 0 |
| `bnd_vip_subtotal_500_00` | MATCH | 0 |
| `bnd_vip_subtotal_500_01` | MATCH | 0 |
| `bnd_vip_subtotal_999_99` | MATCH | 0 |
| `coupon_case_insensitivity` | MATCH | 0 |
| `coupon_ceiling_subtotal` | MATCH | 0 |
| `coupon_fixed25_above_250_01` | MATCH | 0 |
| `coupon_fixed25_at_250_00` | MATCH | 0 |
| `coupon_fixed25_below_249_99` | MATCH | 0 |
| `coupon_welcome10_bus_high_capped` | MATCH | 0 |
| `coupon_welcome10_bus_mid` | MATCH | 0 |
| `coupon_welcome10_retail` | MATCH | 0 |
| `coupon_welcome10_vip_high_capped` | MATCH | 0 |
| `coupon_welcome10_vip_low` | MATCH | 0 |
| `coupon_welcome10_vip_mid_capped` | MATCH | 0 |
| `default_values_customer_and_item` | MATCH | 0 |
| `fee_bank_transfer_high_value` | MATCH | 0 |
| `fee_card_above_1500_01` | MATCH | 0 |
| `fee_card_at_1500_00` | MATCH | 0 |
| `fee_card_below_1499_99` | MATCH | 0 |
| `idempotency_invoice_exact_replay` | MATCH | 0 |
| `idempotency_invoice_tampered_payload` | MATCH | 0 |
| `idempotency_refund_exact_replay` | MATCH | 0 |
| `refund_after_manual_review_allowed` | MATCH | 0 |
| `refund_duplicate_approved_rejected` | MATCH | 0 |
| `refund_fee_window_25h` | MATCH | 0 |
| `refund_fee_window_72h` | MATCH | 0 |
| `refund_full_window_0h` | MATCH | 0 |
| `refund_full_window_24h` | MATCH | 0 |
| `refund_manual_review_73h` | MATCH | 0 |
| `retail_high_value_order` | MATCH | 0 |
| `retail_standard_order` | MATCH | 0 |
| `rounding_bankers_half_even_discount` | MATCH | 0 |
| `rounding_multiline_proportional_residual` | MATCH | 0 |
| `rounding_refund_fee_half_even` | MATCH | 0 |
| `shipping_eu_de_at_250_00` | MATCH | 0 |
| `shipping_eu_de_below_249_99` | MATCH | 0 |
| `shipping_export_flat_high` | MATCH | 0 |
| `shipping_export_flat_low` | MATCH | 0 |
| `shipping_pre_discount_subtotal_trap` | MATCH | 0 |
| `shipping_uk_at_250_00` | MATCH | 0 |
| `shipping_uk_below_249_99` | MATCH | 0 |
| `shipping_us_ca_above_150_01` | MATCH | 0 |
| `shipping_us_ca_at_150_00` | MATCH | 0 |
| `shipping_us_ca_below_149_99` | MATCH | 0 |
| `shipping_us_ny_below_149_99` | MATCH | 0 |
| `tax_eu_de_digital` | MATCH | 0 |
| `tax_eu_de_essential` | MATCH | 0 |
| `tax_eu_de_goods` | MATCH | 0 |
| `tax_export_all_categories` | MATCH | 0 |
| `tax_uk_digital` | MATCH | 0 |
| `tax_uk_essential` | MATCH | 0 |
| `tax_uk_goods` | MATCH | 0 |
| `tax_us_ca_digital` | MATCH | 0 |
| `tax_us_ca_essential` | MATCH | 0 |
| `tax_us_ca_goods` | MATCH | 0 |
| `tax_us_ny_digital` | MATCH | 0 |
| `tax_us_ny_essential` | MATCH | 0 |
| `tax_us_ny_goods` | MATCH | 0 |
| `tax_zero_subtotal_short_circuit` | MATCH | 0 |
| `val_empty_items` | MATCH | 0 |
| `val_item_missing_sku` | MATCH | 0 |
| `val_item_negative_price` | MATCH | 0 |
| `val_item_negative_qty` | MATCH | 0 |
| `val_item_unknown_category` | MATCH | 0 |
| `val_item_zero_qty` | MATCH | 0 |
| `val_missing_customer_id` | MATCH | 0 |
| `val_missing_operation_id` | MATCH | 0 |
| `val_refund_invoice_not_found` | MATCH | 0 |
| `val_refund_missing_invoice_id` | MATCH | 0 |
| `val_refund_missing_op_id` | MATCH | 0 |
| `val_refund_negative_hours` | MATCH | 0 |
| `val_suspended_customer` | MATCH | 0 |
| `val_unknown_coupon` | MATCH | 0 |
| `val_unknown_customer_tier` | MATCH | 0 |
| `val_unknown_payment_method` | MATCH | 0 |
| `val_unknown_region` | MATCH | 0 |
| `val_unsupported_operation` | MATCH | 0 |

> **Scope:** This verdict establishes behavioral equivalence across the defined contract and executed scenario corpus. It is not a formal proof of complete program equivalence.

## Minimal Counterexample

**Case:** `bnd_vip_subtotal_1000_00`

```text
$.steps[0].result.discount_rate [value]
legacy    = '0.1000'
candidate = '0.0700'

$.steps[0].result.discount [value]
legacy    = '100.00'
candidate = '70.00'

$.steps[0].result.tax [value]
legacy    = '65.25'
candidate = '67.43'

$.steps[0].result.tax_breakdown[0].taxable_base [value]
legacy    = '900.00'
candidate = '930.00'

$.steps[0].result.tax_breakdown[0].tax [value]
legacy    = '65.25'
candidate = '67.43'

$.steps[0].result.grand_total [value]
legacy    = '965.25'
candidate = '997.43'

$.steps[0].state_after.invoices[0].discount_rate [value]
legacy    = '0.1000'
candidate = '0.0700'

$.steps[0].state_after.invoices[0].discount [value]
legacy    = '100.00'
candidate = '70.00'

$.steps[0].state_after.invoices[0].tax [value]
legacy    = '65.25'
candidate = '67.43'

$.steps[0].state_after.invoices[0].tax_breakdown[0].taxable_base [value]
legacy    = '900.00'
candidate = '930.00'

$.steps[0].state_after.invoices[0].tax_breakdown[0].tax [value]
legacy    = '65.25'
candidate = '67.43'

$.steps[0].state_after.invoices[0].grand_total [value]
legacy    = '965.25'
candidate = '997.43'

$.steps[0].state_after.ledger[0].amount [value]
legacy    = '965.25'
candidate = '997.43'

$.steps[0].state_after.audit[0].data.amount [value]
legacy    = '965.25'
candidate = '997.43'

$.steps[0].events_delta[0].data.amount [value]
legacy    = '965.25'
candidate = '997.43'

$.invariant_failures [length]
legacy    = 0
candidate = 1

$.final_state.invoices[0].discount_rate [value]
legacy    = '0.1000'
candidate = '0.0700'

$.final_state.invoices[0].discount [value]
legacy    = '100.00'
candidate = '70.00'

$.final_state.invoices[0].tax [value]
legacy    = '65.25'
candidate = '67.43'

$.final_state.invoices[0].tax_breakdown[0].taxable_base [value]
legacy    = '900.00'
candidate = '930.00'

```

