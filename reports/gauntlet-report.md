# Aegis Verifier Regression Gauntlet

**Verifier validation:** `PASS`

- Seeded semantic regressions: **21**
- Detected: **21**
- Escaped: **0**
- Detection rate: **100.00%**

| Mutation | Detected | Drifted cases | First counterexample |
|---|---:|---:|---|
| `vip_1000_strict` | YES | 1 | `bnd_vip_subtotal_1000_00` |
| `vip_500_strict` | YES | 1 | `bnd_vip_subtotal_500_00` |
| `business_2000_strict` | YES | 1 | `bnd_bus_subtotal_2000_00` |
| `business_1000_strict` | YES | 1 | `bnd_bus_subtotal_1000_00` |
| `welcome_cap_20` | YES | 3 | `coupon_welcome10_bus_high_capped` |
| `fixed25_strict` | YES | 2 | `coupon_ceiling_subtotal` |
| `us_shipping_strict` | YES | 1 | `shipping_us_ca_at_150_00` |
| `eu_shipping_strict` | YES | 2 | `shipping_eu_de_at_250_00` |
| `eude_essential_standard_tax` | YES | 1 | `tax_eu_de_essential` |
| `uk_essential_taxed` | YES | 1 | `tax_uk_essential` |
| `export_taxed` | YES | 4 | `rounding_refund_fee_half_even` |
| `ny_digital_exempt` | YES | 1 | `tax_us_ny_digital` |
| `ca_goods_wrong_rate` | YES | 38 | `bnd_vip_subtotal_1000_00` |
| `card_fee_strict` | YES | 1 | `fee_card_at_1500_00` |
| `refund_24_strict` | YES | 1 | `refund_full_window_24h` |
| `refund_72_strict` | YES | 1 | `refund_fee_window_72h` |
| `refund_direction_debit` | YES | 8 | `idempotency_refund_exact_replay` |
| `omit_refund_ledger` | YES | 8 | `idempotency_refund_exact_replay` |
| `omit_invoice_audit` | YES | 68 | `bnd_bus_subtotal_1000_00` |
| `omit_refund_audit` | YES | 8 | `idempotency_refund_exact_replay` |
| `no_idempotency` | YES | 3 | `idempotency_invoice_exact_replay` |

These are synthetic fault-injection candidates used to stress-test the contract/verifier. They are not claims about naturally occurring AI error frequency.
