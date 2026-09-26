# IBM Bob Session Evidence & Provenance

This directory contains visual and session evidence documenting the use of **IBM Bob** throughout the development and verification lifecycle of Aegis ContractLock.

---

## Directory Organization

```text
bob_sessions/
├── README.md
│
├── final/
│   ├── 01_contract_archaeologist.png
│   ├── 02_modernization_executor.png
│   └── 03_drift_critic_repair.png
│
└── archive/
    ├── original_task01_contract_archaeology.png
    └── original_task02_modernization_architecture.png
```

---

## 1. `archive/` — Initial Exploratory Bob Runs

The images in `archive/` capture genuine initial IBM Bob sessions executed during early project development:

- **`original_task01_contract_archaeology.png`**: Documents the early contract archaeology exploration in IBM Bob (exploring 97 scenarios and boundary sweeps).
- **`original_task02_modernization_architecture.png`**: Documents the initial 10-module / 4-tier modernization design proposal.

### Provenance & Retention Note
These historical screenshots are intentionally retained in `archive/` to demonstrate authentic, early-stage IBM Bob usage and token expenditure (Bobcoins). Because subsequent clean-room refactoring, branch analysis, and invariant pruning refined the contract into the final **86-scenario / 11-module** architecture, the historical metrics in these screenshots do not represent the final sealed production codebase. They are preserved purely for provenance integrity.

---

## 2. `final/` — Production Submission Alignment

The `final/` directory is reserved for the 3 targeted IBM Bob alignment sessions:

1. **`01_contract_archaeologist.png`** — Execution of `bob_prompts/01_contract_archaeologist.md`, extracting the finalized 86-scenario behavioral contract against `legacy_app/billing/monolith.py`.
2. **`02_modernization_executor.png`** — Execution of `bob_prompts/03_modernization_executor.md`, scaffolding and implementing the clean 11-module modernized architecture in `modern_app/billing/`.
3. **`03_drift_critic_repair.png`** — Execution of `bob_prompts/04_drift_critic_and_repair.md`, running the Aegis verifier to detect semantic drift, diagnose root causes, and apply surgical repairs.

These screenshots directly reflect the final production metrics reported across the repository and in `reports/readiness.md`.
