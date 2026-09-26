# Task 4 — Repair Report

## Controlled Safety Rehearsal

The BLOCKED candidate contained an intentionally introduced semantic regression for gate validation. Specifically, the VIP tier discount boundary at 1000.00 was changed from an inclusive (`>=`) to a strict (`>`) comparison in `modern_app/billing/pricing.py`, causing the candidate to apply the wrong discount rate when the subtotal equals exactly 1000.00. This report documents the diagnosis, repair, and re-verification.

---

## Behavioral counterexample

**Case ID:** `vip_exact_1000_10pct`

**Description:** VIP stepped tier discount — subtotal exactly 1000.00 steps up to 10% (inclusive boundary).

**Input:**
- Customer tier: `VIP`
- Region: `US_CA`
- Items: 1× SKU-001, GOODS, qty=1, unit_price=1000.00
- Payment method: `CARD`
- No coupon

**Observed drift (24 field/state/event differences):**

| Field | Legacy (baseline) | Candidate (blocked) |
|---|---|---|
| `discount_rate` | `0.1000` | `0.0700` |
| `discount` | `100.00` | `70.00` |
| `tax` | `65.25` | `67.43` |
| `tax_breakdown[0].taxable_base` | `900.00` | `930.00` |
| `grand_total` | `965.25` | `997.43` |
| ledger / audit / event amounts | `965.25` | `997.43` |
| invariant failures | 0 | 2 |

---

## Root cause

| Attribute | Detail |
|---|---|
| **File** | `modern_app/billing/pricing.py` |
| **Function** | `_discount_rate` |
| **Line** | 26 |
| **Broken expression** | `if subtotal > Decimal("1000.00"):` |
| **Effect** | At `subtotal == 1000.00`, the strict `>` test is `False`; execution falls to the `>= 500` branch returning 7% instead of 10% |
| **Contract specification** | Case description and invariant `vip_1000-rate` both assert that 1000.00 is an **inclusive** upper boundary stepping to 10% |

---

## Repair

| Attribute | Detail |
|---|---|
| **File changed** | `modern_app/billing/pricing.py` |
| **Function changed** | `_discount_rate` |
| **Logical lines changed** | 1 |
| **Change** | `if subtotal > Decimal("1000.00"):` → `if subtotal >= Decimal("1000.00"):` |

**Before semantics:** The 10% VIP bracket was only applied when subtotal was strictly greater than 1000.00. At exactly 1000.00, the 7% bracket was applied.

**After semantics:** The 10% VIP bracket is applied when subtotal is greater than or equal to 1000.00. At exactly 1000.00, 10% is now correctly applied.

**Pre-repair SHA-256 of `modern_app/billing/pricing.py`:** `CEEF8FF03998EE548210F0F9894A8EF2768B5B6D5AC0F7BBFF036DCC132F929F`

**Post-repair SHA-256 of `modern_app/billing/pricing.py`:** `68D26081E4B96136C1C550BBBD082692E0FAF08CB00FB18F51F2517BA15EC487`

---

## Verification

| Metric | Before repair (BLOCKED) | After repair |
|---|---|---|
| Cases matched | 46 / 47 | 47 / 47 |
| Cases drifted | 1 | 0 |
| Verdict | `BLOCKED` | `ACCEPTED` |
| Baseline semantic evidence SHA-256 | `2d9d6ef6b3e1d972e0cf68c504083f239391e1becb939c6726fabdad6d906db5` | `2d9d6ef6b3e1d972e0cf68c504083f239391e1becb939c6726fabdad6d906db5` |
| Candidate semantic evidence SHA-256 | `d569d131fdbe2f23dd9943431f72c435138fa06f4cab4be5bf3959f43a5fd654` | `f6c79144ab8592e71b459be6729ff774740922c15207397c75950773a4e321cf` |

---

## Architecture

| Check | Result |
|---|---|
| Modern imports from legacy | **0** |
| Dependency cycles | **0** |

The repair did not compromise architectural separation.

---

## Protected evidence

| Artifact | Status |
|---|---|
| `legacy_app/` source | Unchanged |
| Policy documentation | Unchanged |
| `aegis_contract.yaml` | Unchanged — SHA-256: `F499A652E62A22B6D209D6B38A0BD904F9410C9B01CE2D4A358E097DB84F6084` |
| `baseline/baseline.json` | Unchanged — SHA-256: `27431FE044DE91B2C543D5CBFDB61BD8830118F8B83684A66E7DF80D6DF746BC` |
| Aegis verifier implementation (`aegis/`) | Unchanged |
| `reports/task4-blocked-verification.md` | Unchanged — SHA-256: `F4157E5C25D7DABFBA0C0EE4E8288B532338FE3658D47659A3ABAC5FBB1F31F3` |
| `reports/task4-blocked-verification.json` | Unchanged — SHA-256: `01E67641C44A9A29C3EEA3104D69D17E1DA681273863A5D869CBDAFA427B9E99` |
| `reports/task4-blocked-candidate-evidence.json` | Unchanged — SHA-256: `AEDFAD195D042C64C2C41649E3824FAAF513420DEA768B314F55965BCF59A213` |

SHA-256 values are integrity fingerprints, not proofs of correctness.

---

## Scope

Behavioral equivalence is demonstrated only across the sealed contract and executed scenario corpus. This is not a formal proof of complete program equivalence.
