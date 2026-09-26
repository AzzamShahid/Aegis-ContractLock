# INTENTIONALLY INJECTED SAFETY REHEARSAL
## Pre-Task-4 Adversarial Gate Check

> **CRITICAL NOTICE:** This mutation is an **INTENTIONALLY INJECTED SAFETY REHEARSAL**.
> It is NOT an accidental mistake, bug, or oversight by the modernization agent (Bob / Antigravity).
> The purpose of this rehearsal is to independently prove and demonstrate that the Aegis ContractLock framework detects subtle semantic regressions and successfully blocks candidate acceptance when business boundaries are breached.

---

## 1. Mutation Metadata

- **Rehearsal Phase:** Pre-Task-4 Adversarial Gate Check
- **Mutation Type:** Boundary inclusion regression (relational operator boundary mutation: `>=` to `>`)
- **Affected Modern File:** `modern_app/billing/pricing_policy.py`
- **Affected Function:** `calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal`
- **Affected Lines:** Line 13

---

## 2. Semantic Conditions

### Original Semantic Condition
```python
    if tier == "VIP":
        if subtotal >= Decimal("1000.00"):
            return Decimal("0.10")
        if subtotal >= Decimal("500.00"):
            return Decimal("0.07")
        return Decimal("0.03")
```

### Mutated Semantic Condition
```python
    if tier == "VIP":
        if subtotal > Decimal("1000.00"):
            return Decimal("0.10")
        if subtotal >= Decimal("500.00"):
            return Decimal("0.07")
        return Decimal("0.03")
```

---

## 3. Rationale and Realism

### Why this mutation is realistic:
Off-by-one and boundary inclusivity errors (`>` vs `>=`) are among the most pervasive semantic regressions encountered during legacy software rewrites. Requirements specifications frequently state phrases such as "orders over $1,000 receive 10%", leading developers to inadvertently implement strict inequality (`>`) rather than inclusive inequality (`>=`). Without rigorous contract-backed scenario testing at exact threshold points ($999.99, $1000.00, $1000.01), such regressions silently pass coarse-grained smoke tests and slip into production billing systems.

### Expected Affected Business Behavior:
- For VIP customers whose order subtotal is **strictly greater than $1,000.00** (e.g., $1000.01), behavior remains unchanged (receives 10% discount).
- For VIP customers whose order subtotal is **strictly less than $1,000.00 down to $500.00** (e.g., $999.99), behavior remains unchanged (receives 7% discount).
- For VIP customers whose order subtotal is **exactly $1,000.00** (covered by scenario `bnd_vip_subtotal_1000_00`), the candidate will erroneously award a 7% discount rate (`0.07`) instead of the required 10% discount rate (`0.10`).
- This root discrepancy will cascade down the billing calculation pipeline:
  - Discount rate: `0.07` vs `0.10`
  - Discount amount: `$70.00` vs `$100.00`
  - Taxable base: `$930.00` vs `$900.00`
  - Tax amount and grand total will diverge accordingly.
- Aegis ContractLock verification is expected to flag `bnd_vip_subtotal_1000_00` as drifted and return a `BLOCKED` verdict.

---

## 4. Empirical Verification Results

- **Verification Command:** `python -m aegis.cli verify`
- **Verdict:** `BLOCKED`
- **Total Contract Cases:** 86
- **Matched Cases:** 85
- **Drifted Cases:** 1
- **First (and only) Failing Case ID:** `bnd_vip_subtotal_1000_00`
- **Baseline Evidence SHA-256:** `2fd2c2f96614e5bcf8fa807b5c1b777fc702f53707be047ddf01c5a852680da7`
- **Mutated Candidate Evidence SHA-256:** `1ea9f7929341101d0d81b50a441e39df44bbd823ffa48176af93744ae67fd4ac`

### Observed Differences for `bnd_vip_subtotal_1000_00` (24 field diffs across pipeline):
1. `$.steps[0].result.discount_rate`: legacy `0.1000` vs candidate `0.0700`
2. `$.steps[0].result.discount`: legacy `100.00` vs candidate `70.00`
3. `$.steps[0].result.tax`: legacy `65.25` vs candidate `67.43`
4. `$.steps[0].result.tax_breakdown[0].taxable_base`: legacy `900.00` vs candidate `930.00`
5. `$.steps[0].result.tax_breakdown[0].tax`: legacy `65.25` vs candidate `67.43`
6. `$.steps[0].result.grand_total`: legacy `965.25` vs candidate `997.43`
7. `$.steps[0].state_after.invoices[0].discount_rate`: legacy `0.1000` vs candidate `0.0700`
8. `$.steps[0].state_after.invoices[0].discount`: legacy `100.00` vs candidate `70.00`
9. `$.steps[0].state_after.invoices[0].tax`: legacy `65.25` vs candidate `67.43`
10. `$.steps[0].state_after.invoices[0].tax_breakdown[0].taxable_base`: legacy `900.00` vs candidate `930.00`
11. `$.steps[0].state_after.invoices[0].tax_breakdown[0].tax`: legacy `65.25` vs candidate `67.43`
12. `$.steps[0].state_after.invoices[0].grand_total`: legacy `965.25` vs candidate `997.43`
13. `$.steps[0].state_after.ledger[0].amount`: legacy `965.25` vs candidate `997.43`
14. `$.steps[0].state_after.audit[0].data.amount`: legacy `965.25` vs candidate `997.43`
15. `$.steps[0].events_delta[0].data.amount`: legacy `965.25` vs candidate `997.43`
16. `$.invariant_failures`: legacy `0` vs candidate `1`
17. `$.final_state.invoices[0].discount_rate`: legacy `0.1000` vs candidate `0.0700`
18. `$.final_state.invoices[0].discount`: legacy `100.00` vs candidate `70.00`
19. `$.final_state.invoices[0].tax`: legacy `65.25` vs candidate `67.43`
20. `$.final_state.invoices[0].tax_breakdown[0].taxable_base`: legacy `900.00` vs candidate `930.00`
21. `$.final_state.invoices[0].tax_breakdown[0].tax`: legacy `65.25` vs candidate `67.43`
22. `$.final_state.invoices[0].grand_total`: legacy `965.25` vs candidate `997.43`
23. `$.final_state.ledger[0].amount`: legacy `965.25` vs candidate `997.43`
24. `$.final_state.audit[0].data.amount`: legacy `965.25` vs candidate `997.43`

---

## 5. Protected Artifacts Integrity

- `legacy_app/billing/monolith.py`: `8f18fdf91e5a970b25b0be053d9ae5c5df57435358122a73da10c87973dce19f` (UNCHANGED)
- `aegis_contract.yaml`: `a3130dd7daa9828ec6951ab7c7ef4b17e8adb8b728524dd44c5ba0019567f993` (UNCHANGED)
- `baseline/baseline.json`: `286320acaa99a09f3a90182857eef2f63ca686d8906da63e5875090d37dbf4a1` (UNCHANGED)

