# Security Policy & Repository Hygiene

## Overview

Aegis ContractLock is an automated modernization and behavioral-contract verification framework designed to guarantee zero semantic drift during legacy refactoring.

This document details repository security practices, secret handling, guidelines for AI pair-programming sessions with IBM Bob, and vulnerability disclosure procedures.

---

## 1. Secret Handling & Zero-Credential Baseline

The core Aegis verification suite runs deterministically and offline without requiring runtime secrets.

- **No Committed Credentials:** Under no circumstances should real credentials, API keys, private keys (`.pem`, `.key`, `.p12`, `.pfx`), passwords, personal access tokens, database connection URLs, or authentication certificates be committed to this repository.
- **Repository Exclusions:** Both `.gitignore` and `.bobignore` enforce exclusions for environment secret files (`.env`, `.env.*`), private keys, tokens, and credential payloads.
- **Preflight Verification:** Run `security_preflight.ps1` before submitting or sharing code to verify that no sensitive patterns or absolute local paths are present in tracked files.

---

## 2. Environment Variable Guidance

- **Core Self-Containment:** Core Aegis engine execution (`aegis.cli`, `pytest`) requires no active `.env` file or cloud secrets.
- **Template Tracking (`.env.example`):** The repository tracks `.env.example` as a template for non-sensitive configuration defaults.
- **Local Secret Isolation:** Any local `.env` or `.env.*` file created for custom development must remain uncommitted. Never place production or real API keys in local development files.

---

## 3. IBM Bob Session and Export Hygiene

Aegis was developed using IBM Bob for clean-room contract archaeology, modernization, and drift repair. When conducting AI pair-programming sessions:

- **No Secret Prompting:** Never paste credentials, API tokens, internal corporate infrastructure URLs, passwords, or personal data into IBM Bob prompts or LLM chat sessions.
- **Transcript and Artifact Review:** Before committing or publishing session logs, prompts, or evidence artifacts (`bob_sessions/`, `bob_prompts/`, `bob_evidence/`), ensure:
  - No secret tokens, authorization headers, or private keys are embedded in transcripts.
  - No absolute user directory paths or local file URI schemes (e.g., local home directories or absolute system paths) are present in judge-facing documentation or reports.
- **Screenshot Hygiene:** Review all exported screenshots in `bob_sessions/` to confirm they contain only intended IDE editor windows, and do not inadvertently display background tabs, desktop notifications, or sensitive personal data.

---

## 4. What to Do If a Credential Is Exposed

If a credential or secret is inadvertently committed to this repository or entered into an AI session:

1. **Immediate Revocation (Primary Defense):** Assume any exposed secret is compromised immediately. Revoke and rotate the credential at the issuing service or provider (e.g., identity provider, cloud host, database server). Do not rely solely on modifying git history.
2. **Git History Remediation:** Simply deleting the secret file in a new commit leaves the secret accessible in git commit history. Purge the sensitive commit using tools such as `git-filter-repo` or BFG Repo-Cleaner, or push a clean repository branch.
3. **Session Audit:** If the credential was input into an AI session or prompt file, revoke the credential immediately and cleanse the local prompt log or session file before export.

---

## 5. Execution Model and Sandbox Limitations

The Aegis ContractLock verifier executes Python candidate code directly within the runtime environment to evaluate return values, state mutations, invariants, exceptions, and audit events against legacy baselines.

- **Not a Hostile-Code Sandbox:** The verifier is an automated modernization and regression-detection tool, **not** a hardened, multi-tenant sandbox designed to contain intentionally malicious code.
- **Direct Python Execution:** Executing untrusted candidate modules invokes Python bytecode directly on the host machine. Untrusted code can invoke arbitrary Python standard library routines or OS primitives.
- **Isolated Evaluation:** Always execute unvetted or untrusted code in an isolated development environment, containerized sandbox, or ephemeral CI/CD worker with restricted filesystem and network privileges.

---

## 6. Responsible Disclosure

If you discover a security vulnerability or repository hygiene issue in Aegis ContractLock:

- Report the issue privately to the repository maintainers rather than opening a public GitHub issue.
- Contact the maintainers via private security advisory or project email.
- Include a clear description of the vulnerability, reproduction steps, and impact assessment.
- We will acknowledge receipt within 48 hours and work to investigate and resolve the issue.

---

## 7. Scope and Disclaimers

- **Independent Project:** Aegis ContractLock is an independent project developed for demonstration and modernization governance.
- **No Third-Party Endorsement:** This project, its security policies, and its verification reports are not officially certified, approved, endorsed, or guaranteed by IBM or any third-party auditing entity.
- **Contract Equivalence Scope:** Behavioral equivalence is demonstrated strictly across the defined contract and executed scenario corpus; it does not constitute formal mathematical proof of complete program equivalence or comprehensive security verification.
