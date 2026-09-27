# Aegis ContractLock — Task 2: Modernization Architecture

You are the Modernization Architect.

The legacy system has already undergone contract archaeology.

## Inputs

Legacy source:
`{{LEGACY_ROOT}}`

Behavior contract:
`{{CONTRACT_PATH}}`

Policy material:
`{{POLICY_PATHS}}`

Modern target:
`{{MODERN_ROOT}}`

Your task is to design a modular modernization architecture while preserving the behavioral contract as the external acceptance boundary.

Do not implement the full modernization yet.

## First Analyze the Legacy Structure

Report:
- current modules
- largest modules
- major responsibilities
- classes/types
- mutable stores
- business domains
- persistence boundaries
- cross-domain coupling
- external interfaces
- architectural cycles
- implicit global state
- legacy-specific dependencies

## Then Design the Modern Architecture

Prefer clear responsibility boundaries such as:
- domain models
- pricing / policy
- tax
- billing
- ledger
- refund
- persistence
- audit/events
- orchestration
- errors
- adapters

Use only domains justified by the actual system.

## Architectural Requirements

1. Preserve externally observable behavior represented by the contract.
2. Do not import the legacy package into the modern implementation.
3. Avoid dependency cycles.
4. Reduce monolithic responsibility concentration.
5. Prefer explicit interfaces and data flow.
6. Preserve deterministic financial calculations.
7. Preserve state and event semantics.
8. Preserve exception semantics where represented by the contract.
9. Do not simplify behavior merely because the legacy implementation looks awkward.
10. Do not rewrite the contract to fit the proposed architecture.

## Produce

- proposed module tree
- responsibility of each module
- dependency direction
- state ownership
- public API compatibility strategy
- migration sequence
- high-risk behavioral areas
- contract scenarios most likely to expose modernization drift
- expected structural improvements
- explicit list of prohibited legacy dependencies

Before implementation, perform a design review against the behavioral contract.

End with:

`MODERNIZATION ARCHITECTURE COMPLETE — IMPLEMENTATION REQUIRES INDEPENDENT CONTRACT VERIFICATION`
