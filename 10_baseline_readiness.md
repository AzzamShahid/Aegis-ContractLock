# Aegis ContractLock — Baseline Seal Readiness Review

You are preparing the legacy system for baseline sealing.

Do not create or modify the modern candidate.

Review:

`{{LEGACY_ROOT}}`

`{{CONTRACT_PATH}}`

`{{POLICY_PATHS}}`

Confirm that:
- all contract scenarios are executable against legacy
- scenario IDs are unique
- workflows are deterministic where expected
- monetary serialization is normalized
- exceptions are normalized
- state snapshots are deterministic
- ledger/audit output has stable ordering or normalization
- invariants are explicit
- policy ambiguities are documented
- external nondeterminism is controlled
- baseline output location is clearly defined

Do not seal or regenerate an existing baseline unless explicitly instructed by the human.

Report either:

`BASELINE READY TO SEAL`

or

`BASELINE NOT READY`

with exact blockers.
