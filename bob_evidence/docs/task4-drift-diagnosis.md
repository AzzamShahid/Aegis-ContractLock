# Task 4 — Drift Diagnosis

## Failing behavioral case

- **Case ID:** `vip_exact_1000_10pct`
- **Relevant input / boundary:** VIP tier customer, subtotal = **1000.00** (1× SKU-001, GOODS, qty=1, unit_price=1000.00), region US_CA, payment CARD, no coupon.

## Legacy behavior

The baseline expects:

| Field | Value |
|---|---|
| `discount_rate` | `0.1000` (10%) |
| `discount` | `100.00` |
| `tax` | `65.25` |
| `tax_breakdown[0].taxable_base` | `900.00` |
| `grand_total` | `965.25` |

The legacy implementation treats subtotal ≥ 1000.00 as the **inclusive** upper tier for VIP customers, yielding a 10% discount at exactly 1000.00.

## Candidate behavior

The blocked candidate produced:

| Field | Value |
|---|---|
| `discount_rate` | `0.0700` (7%) |
| `discount` | `70.00` |
| `tax` | `67.43` |
| `tax_breakdown[0].taxable_base` | `930.00` |
| `grand_total` | `997.43` |

The candidate applied the 7% bracket instead of 10%, resulting in a higher taxable base, higher tax, and higher grand total. Two contract invariants were also violated (`vip_1000-rate`, `vip_1000-grand`).

## First semantic divergence

The **first and only semantic divergence** is the selection of the wrong VIP discount rate bracket:

- Legacy: subtotal = 1000.00 → 10% (inclusive boundary)
- Candidate: subtotal = 1000.00 → 7% (boundary treated as exclusive)

This is the sole behavioral root cause. All 24 reported field/state/event differences are downstream arithmetic consequences of this single wrong rate.

## Downstream effects

All remaining drifted fields are purely derived from the wrong `discount_rate`:

1. `discount` is wrong because `discount = subtotal × discount_rate`.
2. `taxable_base` is wrong because it is `subtotal − discount`.
3. `tax` is wrong because it is `taxable_base × tax_rate`.
4. `grand_total` is wrong because it is `subtotal − discount + tax + shipping + service_fee`.
5. `state_after.invoices[*]` mirrors the same values.
6. `state_after.ledger[0].amount` = grand_total → wrong.
7. `state_after.audit[0].data.amount` = grand_total → wrong.
8. `events_delta[0].data.amount` = grand_total → wrong.
9. `invariant_failures` count = 2 (both invariants reference the wrong rate and wrong grand_total).
10. `final_state.*` fields mirror the same wrong values.

No independent secondary defect was identified.

## Candidate-side root cause

| Attribute | Value |
|---|---|
| **File** | `modern_app/billing/pricing.py` |
| **Function** | `_discount_rate` |
| **Line** | 26 |
| **Expression** | `if subtotal > Decimal("1000.00"):` |

The condition uses strict greater-than (`>`). When `subtotal == Decimal("1000.00")`, the condition is `False`, so execution falls through to the `elif subtotal >= Decimal("500.00"):` branch and returns `Decimal("0.07")` (7%). The contract specifies that 1000.00 is an **inclusive** boundary for the 10% tier.

The 500.00 boundary on line 28 already uses `>=` (inclusive) and is correct — confirmed by the passing cases `vip_exact_500_7pct` and `vip_below_1000_7pct`.

## Proposed minimal repair

Change **one operator** on line 26 of `modern_app/billing/pricing.py`:

```diff
-        if subtotal > Decimal("1000.00"):
+        if subtotal >= Decimal("1000.00"):
```

This is the smallest candidate-side change that restores behavioral compatibility for the failing boundary. No other file, function, constant, or condition requires modification.

### Regression risk

| Case | Subtotal | After repair | Risk |
|---|---|---|---|
| `vip_below_500_3pct` | 499.99 | Still < 500 → 3% | None |
| `vip_exact_500_7pct` | 500.00 | Still ≥ 500 AND < 1000 → 7% | None |
| `vip_below_1000_7pct` | 999.99 | Still < 1000 → 7% | None |
| `vip_exact_1000_10pct` | 1000.00 | Now ≥ 1000 → **10%** ✓ | Repaired |
| BUSINESS tier | any | Unrelated branch, unaffected | None |

---

*This diagnosis was derived exclusively from the blocked verification evidence, the sealed contract definition, and direct inspection of the current candidate source code.*
