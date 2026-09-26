# Task 3 — Modernization Executor

Implement the approved modernization plan in `modern_app/` only. Preserve behavior represented by the Aegis contract, including subtle rounding, exact thresholds, exceptions, state transitions, ledger direction, audit events, and idempotency.

After implementation run:

```text
python -m aegis.cli baseline
python -m aegis.cli verify
python -m aegis.cli architecture
```

If verification is BLOCKED, stop. Do not modify the contract or verifier to make the candidate pass. Report the first counterexample for the Drift Critic task.
