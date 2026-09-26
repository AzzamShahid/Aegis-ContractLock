# Aegis ContractLock Verification Report

**Verdict:** `ACCEPTED`

- Cases matched: **47 / 47**
- Cases drifted: **0**
- Baseline evidence SHA-256: `2d9d6ef6b3e1d972e0cf68c504083f239391e1becb939c6726fabdad6d906db5`
- Candidate evidence SHA-256: `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf`

| Case | Status | Drift count |
|---|---:|---:|
| `business_below_1000_0pct` | MATCH | 0 |
| `business_below_2000_4pct` | MATCH | 0 |
| `business_exact_1000_4pct` | MATCH | 0 |
| `business_exact_2000_6pct` | MATCH | 0 |
| `coupon_fixed25_above_threshold` | MATCH | 0 |
| `coupon_fixed25_below_threshold` | MATCH | 0 |
| `coupon_welcome10_at_cap` | MATCH | 0 |
| `coupon_welcome10_below_cap` | MATCH | 0 |
| `idempotency_create_invoice` | MATCH | 0 |
| `idempotency_refund_invoice` | MATCH | 0 |
| `multiline_vip_usny_mixed_categories` | MATCH | 0 |
| `refund_at_24h_full_no_fee` | MATCH | 0 |
| `refund_at_25h_5pct_fee` | MATCH | 0 |
| `refund_at_72h_5pct_fee` | MATCH | 0 |
| `refund_at_73h_manual_review` | MATCH | 0 |
| `refund_duplicate_approved_blocked` | MATCH | 0 |
| `refund_manual_review_then_approved` | MATCH | 0 |
| `retail_basic_usca_goods` | MATCH | 0 |
| `service_fee_bank_transfer_never` | MATCH | 0 |
| `service_fee_card_below_threshold` | MATCH | 0 |
| `service_fee_card_exact_threshold` | MATCH | 0 |
| `shipping_eu_free_exact_threshold` | MATCH | 0 |
| `shipping_export_always_35` | MATCH | 0 |
| `shipping_us_free_exact_threshold` | MATCH | 0 |
| `shipping_us_paid_below_threshold` | MATCH | 0 |
| `tax_eude_essential_reduced_rate` | MATCH | 0 |
| `tax_export_zero` | MATCH | 0 |
| `tax_uk_goods_20pct` | MATCH | 0 |
| `tax_usca_essential_exempt` | MATCH | 0 |
| `tax_usca_goods_taxed_digital_exempt` | MATCH | 0 |
| `tax_usny_digital_taxed` | MATCH | 0 |
| `validation_empty_items` | MATCH | 0 |
| `validation_invalid_payment_method` | MATCH | 0 |
| `validation_invalid_region` | MATCH | 0 |
| `validation_invalid_tier` | MATCH | 0 |
| `validation_missing_operation_id` | MATCH | 0 |
| `validation_negative_unit_price` | MATCH | 0 |
| `validation_refund_invoice_not_found` | MATCH | 0 |
| `validation_refund_negative_hours` | MATCH | 0 |
| `validation_suspended_customer` | MATCH | 0 |
| `validation_unknown_coupon` | MATCH | 0 |
| `validation_zero_qty` | MATCH | 0 |
| `vip_below_1000_7pct` | MATCH | 0 |
| `vip_below_500_3pct` | MATCH | 0 |
| `vip_exact_1000_10pct` | MATCH | 0 |
| `vip_exact_500_7pct` | MATCH | 0 |
| `workflow_invoice_then_full_refund` | MATCH | 0 |

> **Scope:** This verdict establishes behavioral equivalence across the defined contract and executed scenario corpus. It is not a formal proof of complete program equivalence.
