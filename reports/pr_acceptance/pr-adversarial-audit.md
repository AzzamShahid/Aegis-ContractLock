# Aegis ContractLock — PR-Specific Post-Repair Adversarial Challenge

- Frozen repaired PR: `aegis-pr-repair-freeze-20260927`
- Commit: `fabc7b7a3a960fd1df7b7c6e51c44a27f797f95a`
- Generated targeted mutations: **24**
- Runnable mutations: **24**
- Detected / BLOCKED: **24**
- Survived contract: **0**
- Invalid / unrunnable: **0**
- Timeout / infrastructure errors: **0**
- Detection rate over runnable mutants: **100.00%**

## Results

| ID | Mutation | State | Verdict | Counterexample |
|---|---|---|---|---|
| `PR-BND-01` | VIP premium >= to > | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_1000_00` |
| `PR-BND-02` | VIP standard >= to > | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_500_00` |
| `PR-BND-03` | BUSINESS premium >= to > | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_2000_00` |
| `PR-BND-04` | BUSINESS standard >= to > | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1000_00` |
| `PR-VAL-01` | VIP premium threshold +0.01 | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_1000_00` |
| `PR-VAL-02` | VIP premium threshold -0.01 | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_999_99` |
| `PR-VAL-03` | VIP standard threshold +0.01 | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_500_00` |
| `PR-VAL-04` | VIP standard threshold -0.01 | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_499_99` |
| `PR-VAL-05` | BUSINESS premium threshold +0.01 | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_2000_00` |
| `PR-VAL-06` | BUSINESS premium threshold -0.01 | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1999_99` |
| `PR-VAL-07` | BUSINESS standard threshold +0.01 | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1000_00` |
| `PR-VAL-08` | BUSINESS standard threshold -0.01 | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_999_99` |
| `PR-RATE-01` | VIP premium 10% to 9% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_1000_00` |
| `PR-RATE-02` | VIP premium 10% to 11% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_1000_00` |
| `PR-RATE-03` | VIP standard 7% to 6% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_500_00` |
| `PR-RATE-04` | VIP standard 7% to 8% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_500_00` |
| `PR-RATE-05` | VIP base 3% to 2% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_499_99` |
| `PR-RATE-06` | VIP base 3% to 4% | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_499_99` |
| `PR-RATE-07` | BUSINESS premium 6% to 5% | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_2000_00` |
| `PR-RATE-08` | BUSINESS premium 6% to 7% | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_2000_00` |
| `PR-RATE-09` | BUSINESS standard 4% to 3% | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1000_00` |
| `PR-RATE-10` | BUSINESS standard 4% to 5% | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1000_00` |
| `PR-ROUTE-01` | VIP tier routing corruption | `DETECTED` | `BLOCKED` | `bnd_vip_subtotal_1000_00` |
| `PR-ROUTE-02` | BUSINESS tier routing corruption | `DETECTED` | `BLOCKED` | `bnd_bus_subtotal_1000_00` |

## Survivors

- None in this finite targeted mutation set.

## Scope

This is a finite PR-specific adversarial challenge created after the repaired PR candidate was frozen. It targets the pricing-policy surface changed by the pull request.

It does not replace the historical 65-mutation post-freeze challenge and does not constitute formal proof of complete program equivalence.

Surviving mutations, if any, are disclosed rather than used to alter or backfit the behavioral contract.
