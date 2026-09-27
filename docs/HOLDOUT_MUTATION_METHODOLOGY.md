# Aegis ContractLock — Holdout Mutation Methodology

## 1. Overview & Provenance Boundary

This document defines the post-freeze adversarial mutation testing methodology for **Aegis ContractLock**.

### 1.1 Separation of Roles
- **Historical Clean-Room (IBM Bob)**: The clean-room modernization from legacy monolithic code to modern modular architecture was conducted independently by IBM Bob. All clean-room transcripts and artifacts (`bob_evidence/`, `bob_sessions/`) represent historical, unaugmented evidence and remain strictly separate.
- **Judge (Aegis Verifier & Contract)**: The frozen behavioral contract (`aegis_contract.yaml`), the sealed baseline (`baseline/baseline.json`), and the Aegis engine (`aegis/`) serve as the impartial judge.
- **Adversarial Challenger (Antigravity)**: Antigravity acts as the post-freeze adversarial challenger, generating semantic and generic mutations after the freeze boundary to test whether the frozen contract detects subtle regressions.

### 1.2 The Freeze Boundary
Before any generated mutation was created or evaluated, the candidate system, contract, baseline, and verifier were committed and tagged at:
- **Git Tag**: `aegis-holdout-freeze-20260927`
- **Manifest**: `reports/holdout-freeze-manifest.json`

The first gate of the holdout audit recomputes and verifies all frozen artifact SHA-256 digests and canonical directory tree fingerprints. If any value differs from the manifest, the audit aborts immediately.

---

## 2. Mutation Experiment Design

### 2.1 Temporary Copy Isolation
To prevent in-place pollution or accidental mutation of the accepted candidate codebase:
- All mutations operate exclusively on **temporary copies** of `modern_app`.
- A temporary directory is provisioned using `tempfile.TemporaryDirectory`.
- The `modern_app` package is copied into the temporary workspace.
- The mutation is applied to the temporary file.
- An isolated Python subprocess is executed with `PYTHONPATH` prepended to prioritize the mutated package.
- The temporary directory is unconditionally destroyed upon completion.
- `modern_app/` in the repository working tree is never modified.

### 2.2 Operator Taxonomy
Candidate mutations are divided into two primary families:

#### A. Generic Syntactic & Relational Operators
1. **Relational Boundary Shifts**:
   - `>=` to `>` (e.g. VIP $1,000 and $500 tiers, Business $2,000 and $1,000 tiers, card surcharge $1,500 threshold, shipping $150 and $250 boundaries, coupon qualification thresholds)
   - `<=` to `<` (e.g. refund 24h grace window, refund 72h window, item quantity <= 0 validation)
2. **Equality Inversions**:
   - `==` to `!=` (e.g. payment method `CARD`, tax category `GOODS`)
3. **Condition Negation**:
   - `in` to `not in` (e.g. US shipping regions)
4. **Branch & Guard Removals**:
   - Replacement of conditional checks with `if False:` (e.g. zero-subtotal tax short-circuit, customer suspension check)
5. **Arithmetic Inversions**:
   - Subtraction to addition (`subtotal - discount` to `subtotal + discount`)

#### B. Domain-Semantic Business Operators
1. **Tier & Discount Rates**:
   - Alteration of VIP tier discounts (3%, 7%, 10% shifted to 2%, 8%, 12%)
   - Alteration of Business tier discounts (4%, 6% shifted to 5%, 7%)
   - Alteration of Retail default rate (0% shifted to 1%)
2. **Coupon Mechanics**:
   - WELCOME10 ceiling cap alteration (15% raised to 20%)
   - WELCOME10 ceiling cap complete removal
   - WELCOME10 bonus rate alteration (10% shifted to 8%)
   - FIXED25 subtotal threshold shift ($250 to $300) and grant shift ($25 to $30)
3. **Shipping Policies**:
   - Regional flat rates ($12 to $15, $18 to $22, $35 to $40)
   - Free shipping thresholds ($150 to $200)
4. **Tax Calculation & Rounding**:
   - Regional tax rates (US_CA GOODS 7.25% to 8.0%, US_NY 8.875% to 8.5%, EU_DE ESSENTIAL 7% to 8%, EU_DE standard 19% to 20%, UK standard 20% to 21%, EXPORT 0% to 5%)
   - Line and total tax rounding modes (`ROUND_HALF_UP` to `ROUND_HALF_EVEN`)
5. **Refund Policies & Windows**:
   - Grace window drift (24h to 48h, 72h to 96h)
   - Late refund fee rate (5% to 10%)
   - Fee rounding mode (`ROUND_HALF_EVEN` to `ROUND_HALF_UP`)
6. **State & Event Guarantees**:
   - Ledger entry direction reversal (`DEBIT` to `CREDIT`, `CREDIT` to `DEBIT`)
   - Audit event emission omission (`INVOICE_CREATED`, `REFUND_APPROVED`)
   - Idempotency cache lookup bypass in `create_invoice` and `refund_invoice`
   - Persistent invoice status update omission upon refund approval
   - Duplicate refund prevention check removal

#### C. Deliberate Survivor Candidates
Deliberate survivor candidates include transformations that may expose unexercised behavioral regions, defensive or redundant logic, or behavior that is observationally indistinguishable within the currently exercised workflows:
- Redundant rounding mode changes on pre-quantized whole-cent values (`MUT-SURV-01`).
- Defensive zero-floor clamp removals where proportional allocation guarantees non-negative bases (`MUT-SURV-02`).
- Validation threshold shifts where single negative test inputs are too large to catch subtle negative values (`MUT-SURV-03`).
- Storage-layer defensive guards that are shadowed by service-layer pre-checks (`MUT-SURV-04`).
- Whitespace trimming omission when all input fixtures are pre-trimmed (`MUT-SURV-05`).
- Unexercised high-tier business rules in regions lacking large test transactions (`MUT-SURV-06`).

#### D. Invalid / Unrunnable Test Candidates
Deliberate syntax and import faults (`MUT-INV-01`, `MUT-INV-02`) injected to verify that non-functional candidates are properly categorized as `INVALID_OR_UNRUNNABLE` and excluded from detection metrics.

---

## 3. Run Classification State Machine

Every generated mutant is evaluated and transitions through a rigorous classification state machine:

```
                  +---------------+
                  |   GENERATED   |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  |    APPLIED    |
                  +-------+-------+
                          |
             +------------+------------+
             |                         |
             v                         v
     +---------------+         +---------------+
     |    RUNNABLE   |         |    INVALID    |
     +-------+-------+         +---------------+
             |
     +-------+-------+
     |               |
     v               v
+----------+ +---------------+
| DETECTED | |   SURVIVED    |
+----------+ +---------------+
```

1. **`GENERATED`**: The mutation candidate specification was generated.
2. **`APPLIED`**: The source transformation was successfully applied to the temporary copy.
3. **`RUNNABLE`**: The mutated candidate compiles and imports cleanly, allowing Aegis to execute the scenario corpus.
4. **`DETECTED`**: The frozen Aegis contract verifier detects behavioral drift or invariant violations against the sealed baseline (`verdict == 'BLOCKED'`).
5. **`SURVIVED_CONTRACT`**: The mutant compiles and runs, and the frozen contract returns `verdict == 'ACCEPTED'`.
6. **`INVALID_OR_UNRUNNABLE`**: Syntax, import, or runtime initialization errors prevent behavioral evaluation. These are **never** counted as detections.
7. **`TIMEOUT_OR_INFRA_ERROR`**: Evaluation failed due to infrastructure timeout or execution environment limits.

### Denominator Definition
To maintain scientific validity:
$$\text{Detection Rate} = \frac{\text{DETECTED}}{\text{RUNNABLE}} \times 100\% = \frac{\text{DETECTED}}{\text{DETECTED} + \text{SURVIVED\_CONTRACT}} \times 100\%$$

Invalid/unrunnable mutants and timeouts are excluded from the denominator.

---

## 4. Survivor Disclosure & The Anti-Backfitting Rule

> [!CAUTION]
> **Survivors are Scientific Evidence — Do Not Backfit**
> A common flaw in mutation testing is using surviving mutants to iteratively modify the contract until 100% detection is achieved. Doing so destroys the provenance boundary and turns a validation test into an overfitted feedback loop.

In this audit:
- The contract was sealed before mutations were generated.
- All surviving mutants are documented with:
  1. Mutant ID and target file/line.
  2. Exact original vs mutated code.
  3. Analysis of why the mutant survived (e.g. unexercised input domain, shadowed guard, pre-quantized precision).
  4. Explicit disclosure that the frozen contract did not distinguish the mutation.
- The contract was **not** edited after observing survivors.

---

## 5. Scope & Scientific Limitations

1. **Finite Mutation Testing**: This experiment measures empirical verifier sensitivity across 65 structured fault injections; it does not constitute a formal mathematical proof of program equivalence.
2. **Empirical Evidence vs Formal Proof**: Behavioral equivalence is established over the finite domain of the 86 contract scenarios. Unexercised combinations may exist outside this corpus.
3. **Reproducibility**: The evaluation pipeline is deterministic, network-free, subprocess-isolated, and rerunnable via `scripts/generated_mutation_audit.py`.

