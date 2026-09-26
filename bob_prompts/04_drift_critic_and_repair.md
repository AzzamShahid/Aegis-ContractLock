# Task 4 — Drift Critic & Minimal Repair

Use `@reports/verification.md`, the relevant files under `@modern_app/billing/`, and `@aegis_contract.yaml`.

Diagnose the supplied behavioral counterexample. Explain:
- the exact input/boundary that diverged,
- legacy behavior,
- modern behavior,
- downstream financial/state/event impact,
- likely candidate-side root cause.

Make the smallest safe change in `modern_app/` that restores the defined behavior. Do not edit legacy code, Aegis, baseline evidence, or the contract. Re-run `python -m aegis.cli verify` and report the actual result.
