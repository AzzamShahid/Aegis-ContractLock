# Threat Model & Trust Assumptions

## Overview

This document defines the security boundaries, trust assumptions, and threat detection profile for Aegis ContractLock.

Aegis ContractLock separates **repository hygiene and operational security** (handled via `.gitignore`, `.bobignore`, and `SECURITY.MD`) from **technical verification trust assumptions** (the formal boundaries under which candidate modernizations are proven equivalent).

---

## 1. System Trust Boundaries

In this demonstration, trust is partitioned strictly between the verification harness and the candidate code under evaluation:

```
+------------------------------------------------------------------------+
|                            TRUSTED BOUNDARY                            |
|                                                                        |
|  +---------------------------+       +------------------------------+  |
|  | Sealed BehavioralContract |       |     Aegis Verifier Engine    |  |
|  |  (aegis_contract.yaml)    |       |           (aegis/)           |  |
|  +---------------------------+       +------------------------------+  |
|               |                                      |                 |
|               v                                      v                 |
|  +---------------------------+       +------------------------------+  |
|  |     Legacy Reference      | ----> |       Sealed Baseline        |  |
|  |       (legacy_app/)       |       |    (baseline/baseline.json)  |  |
|  +---------------------------+       +------------------------------+  |
+------------------------------------------------------------------------+
                                   |
                                   | Evaluates against
                                   v
+------------------------------------------------------------------------+
|                          EVALUATED / UNTRUSTED                         |
|                                                                        |
|                   AI-Generated Modern Candidate                        |
|                           (modern_app/)                                |
+------------------------------------------------------------------------+
```

### Trusted for This Demo

1. **Sealed Behavioral Contract (`aegis_contract.yaml`):** The immutable contract specification defining domain operations, schemas, pre/post-conditions, invariants, and scenario test vectors.
2. **Aegis Verifier Engine (`aegis/`):** The trusted test harness, execution runner, trace comparator, invariant evaluator, and report generator.
3. **Legacy Reference (`legacy_app/`):** The legacy monolith serving as the authoritative reference implementation for baseline behavior.
4. **Sealed Baseline (`baseline/baseline.json`):** The cryptographically hashed, recorded execution traces and outputs generated from executing the legacy implementation against the sealed contract.

### Evaluated / Untrusted

- **AI-Generated Modern Candidate (`modern_app/`):** The refactored or modernized code produced by AI agents (e.g., IBM Bob) or developers. Because AI-generated code is prone to subtle regressions, hallucinations, threshold misinterpretations, and architectural degradation, its behavior is treated as entirely unverified until validated by Aegis.

---

## 2. Threats the Current Contract Can Detect

The Aegis ContractLock contract suite is designed specifically to detect semantic and behavioral drift introduced during refactoring or modernization:

| Threat Category | Description & Impact |
| :--- | :--- |
| **Threshold Drift** | Off-by-one errors or boundary condition mutations (e.g., changing `>= 100` to `> 100` in bulk discounting, volume thresholds, or coupon qualifications). |
| **Monetary / Rounding Drift** | Incompatible financial arithmetic, floating-point precision loss, Banker's rounding vs. round-half-up discrepancies, or cent vs. dollar unit confusion. |
| **Return-Value Drift** | Structural schema divergence, altered dictionary keys, dropped return fields, or mismatched return types on service operations. |
| **Exception Drift** | Mismatched error codes, swallowed exceptions, failure to raise required domain errors on invalid inputs, or raising unexpected error types. |
| **State Drift** | Incomplete, mutated, or missing persistent state changes (e.g., invoice balances, customer credit, status flags) following an operation. |
| **Event / Audit Drift** | Dropped audit events, missing telemetry entries, modified event payload structures, or disordered event dispatch sequences. |
| **Ledger-Direction Drift** | Accounting sign inversions, swapped debit/credit entries, or incorrect sign conventions applied to adjustments and refunds. |
| **Idempotency Drift** | Replay failure, duplicate charges on retry, or inconsistent side-effect execution when operations are repeated. |

---

## 3. Out of Current Scope

Aegis ContractLock focuses on contract-driven semantic equivalence. The following threats and operational hazards are explicitly outside the current scope:

1. **Malicious Candidate Attacking Verifier Process:** The verifier runs Python candidate code in-process without sandboxing. It does not defend against adversarial code designed to monkey-patch Aegis internals, inspect memory, or manipulate the execution runner.
2. **Operating-System Compromise:** Process-level privilege escalation, arbitrary local file system access outside project scope, or malicious system calls executed by candidate code.
3. **Supply-Chain Compromise:** Vulnerabilities, backdoors, or malicious tampering in upstream third-party dependencies, virtual environment tooling, or the Python runtime.
4. **Incorrect or Incomplete Contract:** If a specific legacy behavior, boundary edge case, or implicit side-effect is unmodeled in `aegis_contract.yaml`, semantic drift in that unmodeled area cannot be detected.
5. **Behavior Outside the Executed Contract:** Unexercised code branches, undocumented legacy endpoints, or scenarios not covered by the executed contract corpus.
6. **Unmodeled Concurrency / External Nondeterminism:** Race conditions, thread interleaving, distributed locking failures, or nondeterminism arising from unseeded random generators or external network services.

---

## 4. Rigor and Honest Boundaries

To prevent overclaiming:

- **No Formal Mathematical Proof:** Aegis ContractLock does not claim mathematical proof, formal verification, or comprehensive program equivalence.
- **Accurate Assertion:** The correct statement of assurance is:
  > *"Behavioral equivalence demonstrated across the defined contract and executed scenario corpus."*
- **Defense in Depth:** Aegis contract verification should be combined with isolated CI runners, dependency vulnerability scanning, static security analysis (SAST), and human code review before production deployment.
