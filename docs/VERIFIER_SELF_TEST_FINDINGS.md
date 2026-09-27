# Aegis ContractLock — Verifier Self-Validation Findings

## 1. Executive Summary: "Who Verifies Aegis?"

In high-stakes financial and transactional migrations, an automated verification engine cannot be accepted on faith. If the verifier itself harbors false positives, false negatives, vacuous passes, or silent error suppression, its acceptance certificates are structurally unsound.

The **VERIFIER SELF-VALIDATION** lane (`ag/verifier-tests`) answers the fundamental question: **"Who verifies Aegis?"**

Prior to this work, the Aegis engine test suite consisted of 7 high-level rehearsal tests in [`tests/test_rehearsal.py`](tests/test_rehearsal.py). While these validated that the specific billing application baseline and candidate passed known integration gates, they did not rigorously challenge the verification engine against adversarial inputs, malformed contracts, surviving mutants, state corruption, serialization permutations, or architectural false invariants.

This lane established **20 new comprehensive self-validation tests** in [`tests/test_verifier_self_validation.py`](tests/test_verifier_self_validation.py), expanding the engine test suite to **27 deterministic tests** without altering any sealed application or verifier core files.

---

## 2. Test Suite Expansion & Execution Metrics

| Metric | Baseline | Post-Expansion | Delta |
|---|---:|---:|---:|
| **Engine Test Count** | 7 | **27** | +20 (+285.7%) |
| **Pass Count** | 7 | **27** | +20 |
| **Fail Count** | 0 | **0** | 0 |
| **XFail / Skip Count** | 0 | **0** | 0 |
| **Verifier Areas Exercised** | High-level rehearsal | **8 targeted subsystems (A-H)** | Expanded adversarial coverage |

### Test Breakdown by Subsystem

1. **Area A: Comparator Engine** (4 tests):
   - `test_comparator_identical_semantic_evidence_accepted`
   - `test_comparator_detects_result_and_state_drifts`
   - `test_comparator_detects_event_and_exception_drifts`
   - `test_comparator_missing_unexpected_cases_and_counterexample_selection`
2. **Area B: Semantic Evidence Fingerprinting** (2 tests):
   - `test_fingerprint_invariance_to_metadata_and_key_ordering`
   - `test_fingerprint_sensitivity_to_business_result_state_and_events`
3. **Area C: Contract Loading and Schema Validation** (3 tests):
   - `test_contract_validation_root_and_required_keys`
   - `test_contract_validation_subject_factories_and_empty_cases`
   - `test_contract_validation_case_ids_and_step_constraints`
4. **Area D: Runner Engine & Execution Protocol** (3 tests):
   - `test_runner_normal_operations_multi_step_and_state_continuity`
   - `test_runner_captured_exceptions_and_event_deltas`
   - `test_runner_failure_surfacing_and_invalid_services`
5. **Area E: Mutation Regression Gauntlet** (2 tests):
   - `test_gauntlet_detection_classification_and_survivor_handling`
   - `test_gauntlet_empty_and_invalid_configuration_behavior`
6. **Area F: Architecture Analyzer** (2 tests):
   - `test_architecture_detects_legacy_imports_and_cycles`
   - `test_architecture_metrics_are_deterministic`
7. **Area G: Report Terminology Guard** (2 tests):
   - `test_report_rendered_text_and_markdown_terminology`
   - `test_report_preserves_internal_compatibility_key`
8. **Area H: Submission Readiness Aggregator** (2 tests):
   - `test_readiness_all_passing_yields_ready`
   - `test_readiness_any_failure_yields_not_ready`

---

## 3. Components Challenged

### A. Comparator Engine (`aegis.comparator`)
- **Identical evidence**: Verified that two bundles containing identical operations, results, states, and event deltas evaluate to `verdict: ACCEPTED` with `drifted: 0` and `minimal_counterexample: None`.
- **Result & State Drifts**: Verified that alterations in business payload results or intermediate/final snapshot states immediately flip the verdict to `BLOCKED` and accurately locate the diff path (e.g. `$.steps[0].result.counter` or `$.steps[0].state_after`).
- **Events & Exceptions**: Verified that omitted or modified audit events in `events_delta` and unexpected exception occurrences (or mismatched error codes) trigger `BLOCKED` with detailed type/value diff records.
- **Topology Mismatches**: Verified that missing baseline cases (candidate dropped a scenario) and unexpected candidate cases (candidate generated uncontracted scenarios) are both flagged as `DRIFT` with explicit `missing_case` and `unexpected_case` kinds.
- **Counterexample Selection**: Verified that the behavioral counterexample chosen corresponds to an actual drifted case in the evaluated set.

### B. Evidence Fingerprinting (`aegis.evidence`, `aegis.util`)
- **Metadata Exclusion**: Verified that non-semantic metadata (`created_at_utc` in evidence bundles and `generated_at_utc` in evidence certificates) is strictly excluded from `evidence_sha256` and `certificate_sha256`. Timestamps can change without altering cryptographic verification validity.
- **Canonical Serialization**: Verified that dictionary key insertion order, whitespace, and formatting permutations yield identical canonical JSON (`sort_keys=True`, compact separators) and identical SHA-256 fingerprints.
- **Semantic Sensitivity**: Verified that single-digit changes in business results, state properties, or event stream names produce completely different SHA-256 digests.

### C. Contract Loading & Validation (`aegis.contracts`)
- **Root-level schema**: Verified that non-mapping YAML roots (e.g. sequences, scalars) raise `ContractError("Contract root must be a mapping")`.
- **Mandatory top-level keys**: Verified enforcement of required keys (`version`, `subject`, `cases`).
- **Factory specifications**: Verified enforcement of `subject.legacy_factory` and `subject.candidate_factory`.
- **Case integrity**: Verified rejection of empty case collections, empty case IDs, and duplicate case IDs.
- **Step integrity**: Verified rejection of cases lacking steps, duplicate step IDs within a case, and steps missing `operation` or `input`.

### D. Runner Engine (`aegis.runner`)
- **Multi-Step Workflows & Continuity**: Verified that context references (`$steps.<id>.result.<field>`) resolve dynamically across sequential steps and that state changes persist on the service instance across steps.
- **Exception Normalization**: Verified that runtime service exceptions are captured into normalized structures (`type`, `code`, `message`) without terminating the runner.
- **State Auditing**: Verified that step-level event deltas are computed from snapshot state. Verified that an unexpected reduction in the audit log triggers the synthetic event `__AEGIS_STATE_ERROR__` with reason `"audit shrank"`.
- **Failure Surfacing**: Verified that services lacking `execute()` or `snapshot_state()` raise explicit `TypeError`s and invariant failures are recorded in `invariant_failures` without suppression.

### E. Mutation Regression Gauntlet (`aegis.gauntlet`)
- **Fault Detection & Classification**: Verified that when all seeded mutants drift, the gauntlet returns `verifier_validation: PASS` with `100.0%` detection rate.
- **Survivor Detection**: Verified that when a mutant behaves identically to baseline (survivor), the gauntlet returns `verifier_validation: FAIL`, registers `escaped > 0`, and classifies the survivor without a counterexample.
- **Invariant Consistency**: Verified that `seeded_regressions == detected + escaped` and `detected <= seeded_regressions` hold universally.

### F. Architecture Analyzer (`aegis.architecture`)
- **Legacy Import Detection**: Verified that static AST inspection flags direct imports and from-imports referencing `legacy_app` modules.
- **Cycle Detection**: Verified that circular dependencies between modules (e.g. `cycle_pkg.a <-> cycle_pkg.b`) are detected and surfaced in `circular_dependencies`.
- **Acyclic Graphs**: Verified that standard directed acyclic graphs (DAGs) pass with zero circular dependencies.
- **Metric Determinism**: Verified that non-comment line counts (LOC), function counts, and class counts are 100% deterministic across repeated runs.

### G. Report Terminology Guard (`aegis.report`)
- **Public Terminology**: Verified that both terminal text (`render_text`) and markdown (`render_markdown`) explicitly use the title **`BEHAVIORAL COUNTEREXAMPLE`** / **`## Behavioral Counterexample`** when presenting drifted scenarios.
- **Prohibition of "Minimal Counterexample" in Rendered Text**: Verified that the rendered text does not present the misleading phrase `"MINIMAL COUNTEREXAMPLE"` (since Aegis selects the first drifted case in lexicographical order rather than performing formal minimization).
- **Internal Compatibility**: Verified that the dictionary key `minimal_counterexample` remains intact for programmatic consumers.

### H. Submission Readiness Aggregator (`aegis.readiness`)
- **All-Passing Invariant**: Verified that when all 7 checks (engine tests, coverage, verification, gauntlet, 2 architecture checks, certificate zero drift) pass, `readiness` returns `READY`.
- **Failure Gating**: Verified that a failure in any individual gate (drift > 0, coverage not ready, cycle detected, legacy import, gauntlet failure, test error) forces `readiness: NOT_READY`.
- **Write Isolation**: Verified that passing synthetic paths to `run_readiness` isolates all report and evidence artifacts to temporary directories without dirtying the repository.

---

## 4. Genuine Engine Defects & Design Inconsistencies Discovered

During rigorous self-validation testing, the following genuine defects and design inconsistencies in the Aegis engine were identified. Per the lane guidelines, **no code in `aegis/` was modified**, preserving the integrity of the sealed core.

### Finding 1: Vacuous Gauntlet PASS on Empty Seeded Mutants
- **Location**: [`aegis/gauntlet.py:22`](aegis/gauntlet.py#L22)
- **Defect Description**:
  ```python
  detected = sum(1 for r in rows if r['detected'])
  total = len(rows)
  return {
      'seeded_regressions': total,
      'detected': detected,
      'escaped': total - detected,
      'detection_rate': round((detected / total * 100.0) if total else 0.0, 2),
      'verifier_validation': 'PASS' if detected == total else 'FAIL',
      'mutants': rows
  }
  ```
  When `MUTANTS` is empty (`total == 0` and `detected == 0`), the condition `detected == total` evaluates to `0 == 0`, which is `True`.
- **Actual Behavior**: The gauntlet reports `verifier_validation: 'PASS'`, `detection_rate: 0.0%`, `seeded_regressions: 0`, and `escaped: 0`.
- **Expected Behavior**: A mutation gauntlet with zero seeded regressions has tested nothing and cannot validate the verifier. It should require at least one valid mutant (`total > 0 and detected == total`) or return `'NOT_VALIDATED'` / `'FAIL'`.
- **Deterministic Reproduction**: `TestGauntletEngine.test_gauntlet_empty_and_invalid_configuration_behavior` in [`tests/test_verifier_self_validation.py`](tests/test_verifier_self_validation.py).

### Finding 2: Unhandled `TypeError` and `AttributeError` on Non-Dict Contract Nodes
- **Location**: [`aegis/contracts.py:23-38`](aegis/contracts.py#L23-L38)
- **Defect Description**:
  The loader checks whether `subject` and `cases` exist in `data`, but does not verify their types before indexing:
  ```python
  subject = data["subject"]
  for key in ("legacy_factory", "candidate_factory"):
      if key not in subject:  # Crashes with TypeError if subject is None or an integer
          raise ContractError(f"Missing subject.{key}")
  ```
  Similarly, if an item in `cases` is a string or list:
  ```python
  for case in cases:
      case_id = case.get("id")  # Crashes with AttributeError if case is not a dict
  ```
- **Actual Behavior**: Unhandled `TypeError: argument of type 'NoneType' is not iterable` or `AttributeError: 'str' object has no attribute 'get'` leaks to the caller.
- **Expected Behavior**: Contract syntax errors should consistently raise `ContractError` with a human-readable diagnosis.
- **Deterministic Reproduction**: Passing `subject: null` or `cases: ["invalid"]` in YAML.

### Finding 3: Relative From-Imports Without Module Omitted by Architecture AST Analyzer
- **Location**: [`aegis/architecture.py:36-37`](aegis/architecture.py#L36-L37)
- **Defect Description**:
  ```python
  elif isinstance(n, ast.ImportFrom):
      if n.module:
          names = [n.module]
  ```
  In Python packages, intra-package relative imports frequently use the syntax:
  ```python
  from . import discounts, taxes
  ```
  For this node, `n.module` is `None` (and `n.level == 1`). Because `if n.module:` evaluates to `False`, `names` remains empty.
- **Actual Behavior**: Imports of the form `from . import <module>` are completely invisible to the architecture dependency graph and cycle detector.
- **Expected Behavior**: The analyzer should resolve relative imports against the current module name (`module.rsplit('.', n.level)[0]`) and inspect the imported aliases (`[a.name for a in n.names]`).

### Finding 4: Overly Broad Prefix Matching for Legacy Imports in Architecture Analyzer
- **Location**: [`aegis/architecture.py:39-40`](aegis/architecture.py#L39-L40)
- **Defect Description**:
  ```python
  for name in names:
      if name.startswith("legacy_app"):
          legacy_imports.append({"module": module, "import": name})
  ```
- **Actual Behavior**: Any module name that begins with the string `"legacy_app"` (such as `legacy_app_shim`, `legacy_application_helpers`, or a third-party package `legacy_app_sdk`) will be flagged as an illegal legacy import.
- **Expected Behavior**: The condition should check for package boundary: `name == "legacy_app" or name.startswith("legacy_app.")`.

### Finding 5: Lexicographical Ordering vs. True Counterexample Minimization
- **Location**: [`aegis/comparator.py:130`](aegis/comparator.py#L130)
- **Defect Description**:
  ```python
  "minimal_counterexample": drifted[0] if drifted else None
  ```
  Because `all_case_ids` is sorted alphabetically (`sorted(set(baseline_cases) | set(candidate_cases))`), `drifted[0]` simply returns the first drifted case in alphabetical order. No delta debugging, input reduction, or step minimization is performed.
- **Impact & Mitigation**: While [`aegis/report.py`](aegis/report.py) correctly renders the user-facing title as `BEHAVIORAL COUNTEREXAMPLE`, consumers relying on the programmatic dictionary key `minimal_counterexample` must be aware that the counterexample is lexicographically first, not algorithmically minimal.

---

## 5. Architectural Boundaries & Methodological Limitations

When designing tests to challenge Aegis without modifying its core, several structural boundaries were cataloged:

1. **Context Reference Syntax**:
   In [`aegis/util.py:61`](aegis/util.py#L61), `resolve_refs` treats any string starting with `$` as a context path (e.g. `"$steps.invoice.result.invoice_id"`). If a domain scenario requires a literal string starting with `$` (e.g. currency input `"$100"`), `deep_get` will attempt to parse `"100"` as a context key and raise `KeyError`.
2. **Append-Only Assumption in Audit Event Deltas**:
   [`aegis/runner.py:23`](aegis/runner.py#L23) calculates new events by slicing `after_audit[len(before_audit):]`. If an in-place mutation alters prior audit events without changing the list length, `_audit_delta` will report an empty delta. However, because `comparator.py` also checks `state_after` in full, this drift is caught by the state comparator.
3. **Behavioral Scope vs. Formal Proof**:
   As emphasized across all Aegis certificates and reports, verification demonstrates equivalence across the defined contract and executed scenario corpus; it is not a formal mathematical proof of whole-program equivalence.

---

## 6. Sealed Path Integrity Audit

All work was performed strictly within the allowed lanes:
- **Files Created**:
  - `tests/test_verifier_self_validation.py`
  - `docs/VERIFIER_SELF_TEST_FINDINGS.md`
- **Sealed Paths Untouched**:
  - `README.md` (unmodified)
  - `requirements.txt` (unmodified)
  - `verify_submission.ps1` (unmodified)
  - `aegis/**` (unmodified)
  - `aegis_contract.yaml` (unmodified)
  - `legacy_app/**` (unmodified)
  - `modern_app/**` (unmodified)
  - `baseline/**` (unmodified)
  - `bob_evidence/**` (unmodified)
  - `bob_sessions/**` (unmodified)
  - `rehearsal_mutations/**` (unmodified)
  - `reports/**` (unmodified)

The verifier self-validation lane completed its defined targeted test scope.



