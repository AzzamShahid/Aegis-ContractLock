# Aegis ContractLock — Task 6: Integrated System and Evidence Audit

Operate as a read-only senior auditor.

Your task is to inspect the entire Aegis ContractLock repository and determine whether the implementation, evidence, documentation, and claims are internally consistent.

Do not modify files.

## Audit Areas

1. Legacy reference
2. Behavioral contract
3. Sealed baseline
4. Modern candidate
5. Aegis verification engine
6. Architecture checks
7. Regression gauntlet
8. Verifier self-tests
9. Coverage reports
10. Evidence certificate
11. Readiness report
12. README claims
13. Bob evidence/screenshots
14. GitHub Actions workflow
15. Security / secret hygiene
16. Submission-facing language

## Check For

- stale metrics
- contradictory scenario counts
- mixed evidence corpora
- unsupported claims
- broken file references
- baseline regeneration
- accidental legacy imports
- dependency cycles
- vacuous tests
- empty mutation sets
- malformed contracts
- unsupported "formal proof" language
- unsupported "guaranteed zero drift" wording
- missing human-governance language
- secrets or credentials
- local absolute paths
- evidence that cannot be reproduced

## Corpus Separation

Never combine metrics from different evidence corpora.

For example:
- historical Bob clean-room corpus
- current hardened public corpus
- curated mutation gauntlet
- historical broad holdout
- PR-specific targeted mutation challenge

Each must retain its own denominator and scope.

## Output Findings by Severity

CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL

For each finding provide:
- evidence
- impact
- exact file/reference
- recommended remediation

Finish with a release-readiness conclusion, but do not merge or modify anything.

Use conservative language.
