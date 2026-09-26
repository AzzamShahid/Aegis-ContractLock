# Task 1 — Contract Archaeologist

Analyze `@legacy_app/billing/monolith.py` together with `@legacy_app/docs/BILLING_POLICY.md`. Do not modernize code yet.

Use specialized subagents:

1. **Business Rule Miner** — extract customer-tier, coupon, tax, shipping, payment-fee, refund, idempotency, ledger, and audit rules from code and documentation. Flag code/document disagreements instead of silently reconciling them.
2. **Boundary & Failure Analyst** — identify every numeric threshold, rounding mode, invalid-input path, exception contract, and boundary values immediately below/at/above important thresholds.
3. **State & Side-Effect Analyst** — identify invoice/refund state transitions, ledger mutations, audit events, and retry/idempotency guarantees.

Synthesize an executable Aegis behavioral contract. Preserve externally observable legacy behavior. Do not modify `legacy_app/`. Do not claim complete program equivalence. Produce a concise report explaining the contract families and risks that require exact-boundary scenarios.
