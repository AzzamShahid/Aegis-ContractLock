from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aegis.architecture import analyze_python_tree
from aegis.certificate import build_certificate
from aegis.comparator import compare_bundles
from aegis.contracts import ContractError, load_contract
from aegis.evidence import build_evidence_bundle
from aegis.gauntlet import run_gauntlet
from aegis.readiness import run_readiness
from aegis.report import render_markdown, render_text
from aegis.runner import run_case, run_suite
from aegis.util import canonical_json, fingerprint


# ==============================================================================
# Synthetic Harnesses & Dummy Services for Verifier Self-Validation
# ==============================================================================

class DummyService:
    """Deterministic in-memory service implementing Aegis required contract protocol."""

    def __init__(self):
        self.state = {"counter": 0, "history": [], "audit": []}

    def execute(self, operation: str, payload: dict):
        if operation == "inc":
            step_by = payload.get("by", 1)
            self.state["counter"] += step_by
            self.state["history"].append(step_by)
            self.state["audit"].append({
                "event": "counter_incremented",
                "data": {"counter": self.state["counter"]},
            })
            return {"counter": self.state["counter"]}
        elif operation == "fail":
            raise ValueError(payload.get("msg", "intentional execution failure"))
        elif operation == "shrink_audit":
            self.state["audit"] = []
            return {"status": "audit_cleared"}
        raise KeyError(f"Unsupported operation: {operation}")

    def snapshot_state(self):
        return copy.deepcopy(self.state)


def dummy_service_factory():
    return DummyService()


class DriftMutantService(DummyService):
    def execute(self, operation: str, payload: dict):
        res = super().execute(operation, payload)
        res["counter"] += 100  # Inject semantic discrepancy
        return res


def drift_mutant_factory():
    return DriftMutantService()


def survivor_mutant_factory():
    return DummyService()  # Equivalent to baseline; should survive


class MissingProtocolService:
    def execute(self, operation: str, payload: dict):
        return {"status": "ok"}
    # Intentionally missing snapshot_state()


def missing_protocol_factory():
    return MissingProtocolService()


def make_step(
    step_id="step_1",
    op="inc",
    inp=None,
    res=None,
    exc=None,
    state_before=None,
    state_after=None,
    events_delta=None,
):
    return {
        "id": step_id,
        "operation": op,
        "input": inp if inp is not None else {"by": 1},
        "result": res if res is not None else {"counter": 1},
        "exception": exc,
        "state_before": state_before if state_before is not None else {"counter": 0, "history": [], "audit": []},
        "state_after": state_after if state_after is not None else {
            "counter": 1,
            "history": [1],
            "audit": [{"event": "counter_incremented", "data": {"counter": 1}}],
        },
        "events_delta": events_delta if events_delta is not None else [
            {"event": "counter_incremented", "data": {"counter": 1}}
        ],
    }


def make_case(case_id="case_1", steps=None, inv_failures=None, final_state=None):
    st = steps if steps is not None else [make_step()]
    fs = final_state if final_state is not None else copy.deepcopy(st[-1]["state_after"])
    return {
        "case_id": case_id,
        "description": f"Verification scenario {case_id}",
        "steps": st,
        "invariant_failures": inv_failures if inv_failures is not None else [],
        "final_state": fs,
    }


def make_bundle(cases=None, kind="candidate"):
    cs = cases if cases is not None else [make_case()]
    return {
        "aegis_evidence_version": "1.0",
        "kind": kind,
        "contract_version": "1.0",
        "factory": "tests.test_verifier_self_validation:dummy_service_factory",
        "case_count": len(cs),
        "cases": cs,
        "evidence_sha256": "dummy_sha256_hash",
        "created_at_utc": "2026-09-27T00:00:00+00:00",
    }


# ==============================================================================
# Area A: Comparator Engine Self-Validation
# ==============================================================================

class TestComparatorEngine(unittest.TestCase):
    """Deeply challenges aegis.comparator: bundle comparison, drift classification, counterexamples."""

    def test_comparator_identical_semantic_evidence_accepted(self):
        b1 = make_bundle([make_case("case_alpha")])
        b2 = make_bundle([make_case("case_alpha")])

        res = compare_bundles(b1, b2)
        self.assertEqual(res["verdict"], "ACCEPTED")
        self.assertEqual(res["matched"], 1)
        self.assertEqual(res["drifted"], 0)
        self.assertIsNone(res["minimal_counterexample"])
        self.assertEqual(res["cases"][0]["status"], "MATCH")
        self.assertEqual(res["cases"][0]["diffs"], [])

    def test_comparator_detects_result_and_state_drifts(self):
        baseline = make_bundle([make_case("case_delta")])

        # 1. Changed business result
        cand_result = make_bundle([
            make_case("case_delta", steps=[make_step(res={"counter": 999})])
        ])
        res1 = compare_bundles(baseline, cand_result)
        self.assertEqual(res1["verdict"], "BLOCKED")
        self.assertEqual(res1["drifted"], 1)
        self.assertEqual(res1["cases"][0]["status"], "DRIFT")
        paths1 = [d["path"] for d in res1["cases"][0]["diffs"]]
        self.assertTrue(any(p.startswith("$.steps[0].result") for p in paths1))

        # 2. Changed intermediate and final state
        cand_state = make_bundle([
            make_case(
                "case_delta",
                steps=[make_step(state_after={"counter": 1, "history": [1], "audit": [], "corrupted": True})],
                final_state={"counter": 1, "history": [1], "audit": [], "corrupted": True},
            )
        ])
        res2 = compare_bundles(baseline, cand_state)
        self.assertEqual(res2["verdict"], "BLOCKED")
        self.assertEqual(res2["drifted"], 1)
        paths2 = [d["path"] for d in res2["cases"][0]["diffs"]]
        self.assertTrue(any("state_after" in p or "final_state" in p for p in paths2))

    def test_comparator_detects_event_and_exception_drifts(self):
        baseline = make_bundle([make_case("case_events")])

        # 1. Changed emitted event delta
        cand_events = make_bundle([
            make_case("case_events", steps=[make_step(events_delta=[])])
        ])
        res1 = compare_bundles(baseline, cand_events)
        self.assertEqual(res1["verdict"], "BLOCKED")
        self.assertEqual(res1["drifted"], 1)
        paths1 = [d["path"] for d in res1["cases"][0]["diffs"]]
        self.assertTrue(any("events_delta" in p for p in paths1))

        # 2. Changed exception (baseline None vs candidate exception)
        cand_exc = make_bundle([
            make_case("case_events", steps=[make_step(
                res=None,
                exc={"type": "RuntimeError", "code": "ERR_FAILED", "message": "unhandled error"},
            )])
        ])
        res2 = compare_bundles(baseline, cand_exc)
        self.assertEqual(res2["verdict"], "BLOCKED")
        self.assertEqual(res2["drifted"], 1)
        paths2 = [d["path"] for d in res2["cases"][0]["diffs"]]
        self.assertTrue(any("exception" in p for p in paths2))

    def test_comparator_missing_unexpected_cases_and_counterexample_selection(self):
        base = make_bundle([make_case("case_a"), make_case("case_b"), make_case("case_c")])

        # Candidate missing case_c and having an unexpected case_z
        cand = make_bundle([make_case("case_a"), make_case("case_b", steps=[make_step(res={"counter": -1})]), make_case("case_z")])

        res = compare_bundles(base, cand)
        self.assertEqual(res["verdict"], "BLOCKED")
        self.assertEqual(res["case_count"], 4)  # case_a, case_b, case_c, case_z
        self.assertEqual(res["matched"], 1)     # case_a matched
        self.assertEqual(res["drifted"], 3)     # case_b drifted, case_c missing, case_z unexpected

        case_map = {c["case_id"]: c for c in res["cases"]}
        self.assertEqual(case_map["case_c"]["diffs"], [{"path": "$", "kind": "missing_case"}])
        self.assertEqual(case_map["case_z"]["diffs"], [{"path": "$", "kind": "unexpected_case"}])

        # Counterexample selection must point to a drifted case in the set
        ce = res["minimal_counterexample"]
        self.assertIsNotNone(ce)
        self.assertEqual(ce["status"], "DRIFT")
        self.assertIn(ce["case_id"], {"case_b", "case_c", "case_z"})
        self.assertEqual(ce["case_id"], "case_b")  # first in alphabetical order of all_case_ids


# ==============================================================================
# Area B: Semantic Evidence Fingerprinting
# ==============================================================================

class TestEvidenceFingerprinting(unittest.TestCase):
    """Challenges evidence hashing: canonicalization, metadata exclusion, sensitivity."""

    def test_fingerprint_invariance_to_metadata_and_key_ordering(self):
        # 1. Serialization ordering: canonical_json sorts keys at all depths
        d1 = {"z": 100, "b": {"y": 2, "a": 1}, "list": [3, 2, 1]}
        d2 = {"b": {"a": 1, "y": 2}, "list": [3, 2, 1], "z": 100}
        self.assertEqual(canonical_json(d1), canonical_json(d2))
        self.assertEqual(fingerprint(d1), fingerprint(d2))

        # 2. Metadata exclusion in build_evidence_bundle
        contract = {"version": "1.0"}
        suite = {
            "factory": "tests.test_verifier_self_validation:dummy_service_factory",
            "case_count": 1,
            "cases": [make_case()],
        }
        b1 = build_evidence_bundle(contract, suite, kind="candidate")
        # Simulating a subsequent run with different generation timestamp
        b2 = copy.deepcopy(b1)
        b2["created_at_utc"] = "2099-12-31T23:59:59+00:00"
        # The payload that produced evidence_sha256 intentionally excluded created_at_utc
        self.assertEqual(b1["evidence_sha256"], b2["evidence_sha256"])

        # 3. Metadata exclusion in build_certificate
        base_bundle = make_bundle()
        cand_bundle = make_bundle()
        comp = compare_bundles(base_bundle, cand_bundle)
        cov = {"statement_coverage": 100.0, "branch_coverage": 100.0}
        gaunt = {"seeded_regressions": 1, "detected": 1, "escaped": 0, "verifier_validation": "PASS"}
        arch = {"checks": {"modern_has_no_legacy_imports": True, "modern_has_no_cycles": True}}

        contract_full = {"version": "1.0", "cases": [make_case()]}
        c1 = build_certificate(contract_full, base_bundle, cand_bundle, comp, cov, gaunt, arch)
        c2 = copy.deepcopy(c1)
        c2["generated_at_utc"] = "2099-01-01T00:00:00+00:00"
        hash_recomputed = fingerprint({k: v for k, v in c2.items() if k not in {"generated_at_utc", "certificate_sha256"}})
        self.assertEqual(c1["certificate_sha256"], hash_recomputed)

    def test_fingerprint_sensitivity_to_business_result_state_and_events(self):
        base_step = make_step(res={"counter": 10}, state_after={"counter": 10}, events_delta=[{"event": "e1"}])
        fp_base = fingerprint({
            "result": base_step["result"],
            "exception": base_step["exception"],
            "state_after": base_step["state_after"],
            "events_delta": base_step["events_delta"],
        })

        # Change result
        step_res = copy.deepcopy(base_step)
        step_res["result"] = {"counter": 11}
        fp_res = fingerprint({
            "result": step_res["result"],
            "exception": step_res["exception"],
            "state_after": step_res["state_after"],
            "events_delta": step_res["events_delta"],
        })
        self.assertNotEqual(fp_base, fp_res)

        # Change state
        step_st = copy.deepcopy(base_step)
        step_st["state_after"]["counter"] = 99
        fp_st = fingerprint({
            "result": step_st["result"],
            "exception": step_st["exception"],
            "state_after": step_st["state_after"],
            "events_delta": step_st["events_delta"],
        })
        self.assertNotEqual(fp_base, fp_st)

        # Change event delta
        step_ev = copy.deepcopy(base_step)
        step_ev["events_delta"] = [{"event": "e2"}]
        fp_ev = fingerprint({
            "result": step_ev["result"],
            "exception": step_ev["exception"],
            "state_after": step_ev["state_after"],
            "events_delta": step_ev["events_delta"],
        })
        self.assertNotEqual(fp_base, fp_ev)


# ==============================================================================
# Area C: Contract Loading and Schema Validation
# ==============================================================================

class TestContractValidation(unittest.TestCase):
    """Challenges aegis.contracts: malformed inputs, required sections, step schema."""

    def test_contract_validation_root_and_required_keys(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "contract.yaml"

            # 1. Malformed root: list instead of mapping
            p.write_text("- item1\n- item2\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Contract root must be a mapping", str(ctx.exception))

            # 2. Missing root keys (version, subject, cases)
            p.write_text("subject: {}\ncases: []\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Missing required contract key: version", str(ctx.exception))

            p.write_text("version: '1.0'\ncases: []\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Missing required contract key: subject", str(ctx.exception))

            p.write_text("version: '1.0'\nsubject: {}\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Missing required contract key: cases", str(ctx.exception))

    def test_contract_validation_subject_factories_and_empty_cases(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "contract.yaml"

            # Missing legacy_factory in subject
            p.write_text("version: '1.0'\nsubject:\n  candidate_factory: 'pkg:cand'\ncases:\n  - id: c1\n    steps: [{id: s1, operation: op, input: {}}]\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Missing subject.legacy_factory", str(ctx.exception))

            # Missing candidate_factory in subject
            p.write_text("version: '1.0'\nsubject:\n  legacy_factory: 'pkg:leg'\ncases:\n  - id: c1\n    steps: [{id: s1, operation: op, input: {}}]\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Missing subject.candidate_factory", str(ctx.exception))

            # Empty cases list
            p.write_text("version: '1.0'\nsubject:\n  legacy_factory: 'pkg:leg'\n  candidate_factory: 'pkg:cand'\ncases: []\n", encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Contract requires at least one case", str(ctx.exception))

    def test_contract_validation_case_ids_and_step_constraints(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "contract.yaml"
            header = "version: '1.0'\nsubject:\n  legacy_factory: 'pkg:leg'\n  candidate_factory: 'pkg:cand'\n"

            # Duplicate case IDs
            content_dup_case = header + "cases:\n  - id: c_dup\n    steps: [{id: s1, operation: o, input: {}}]\n  - id: c_dup\n    steps: [{id: s2, operation: o, input: {}}]\n"
            p.write_text(content_dup_case, encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("Invalid/duplicate case id", str(ctx.exception))

            # Case with empty steps
            content_empty_steps = header + "cases:\n  - id: c1\n    steps: []\n"
            p.write_text(content_empty_steps, encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("requires at least one step", str(ctx.exception))

            # Duplicate step ID in same case
            content_dup_step = header + "cases:\n  - id: c1\n    steps:\n      - id: s_dup\n        operation: o\n        input: {}\n      - id: s_dup\n        operation: o\n        input: {}\n"
            p.write_text(content_dup_step, encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("invalid/duplicate step id", str(ctx.exception))

            # Missing operation or input in step
            content_missing_op = header + "cases:\n  - id: c1\n    steps:\n      - id: s1\n        input: {}\n"
            p.write_text(content_missing_op, encoding="utf-8")
            with self.assertRaises(ContractError) as ctx:
                load_contract(p)
            self.assertIn("operation/input required", str(ctx.exception))


# ==============================================================================
# Area D: Runner Engine Self-Validation
# ==============================================================================

class TestRunnerEngine(unittest.TestCase):
    """Challenges aegis.runner: multi-step state continuity, exception handling, audit deltas."""

    def test_runner_normal_operations_multi_step_and_state_continuity(self):
        case_spec = {
            "id": "scenario_chain",
            "steps": [
                {"id": "s1", "operation": "inc", "input": {"by": 10}},
                {"id": "s2", "operation": "inc", "input": {"by": "$steps.s1.result.counter"}},
            ],
            "invariants": [
                {"id": "inv_s2", "type": "field_equals", "step": "s2", "path": "result.counter", "value": 20}
            ]
        }

        evidence = run_case("tests.test_verifier_self_validation:dummy_service_factory", case_spec)
        self.assertEqual(len(evidence["steps"]), 2)
        # Step 1 produced 10
        self.assertEqual(evidence["steps"][0]["result"], {"counter": 10})
        # Step 2 referenced step 1 result and incremented by 10 to 20
        self.assertEqual(evidence["steps"][1]["input"], {"by": 10})
        self.assertEqual(evidence["steps"][1]["result"], {"counter": 20})
        # Observable state continuity: s2 state_before matches s1 state_after
        self.assertEqual(evidence["steps"][1]["state_before"]["counter"], 10)
        self.assertEqual(evidence["steps"][1]["state_after"]["counter"], 20)
        self.assertEqual(evidence["final_state"]["counter"], 20)
        self.assertEqual(evidence["invariant_failures"], [])

    def test_runner_captured_exceptions_and_event_deltas(self):
        case_spec = {
            "id": "scenario_errors",
            "steps": [
                {"id": "s_normal", "operation": "inc", "input": {"by": 3}},
                {"id": "s_fail", "operation": "fail", "input": {"msg": "invalid authorization token"}},
                {"id": "s_shrink", "operation": "shrink_audit", "input": {}},
            ],
        }

        evidence = run_case("tests.test_verifier_self_validation:dummy_service_factory", case_spec)
        step_fail = evidence["steps_by_id"]["s_fail"]
        # Normalizes exception into structured record rather than unhandled abort
        self.assertIsNone(step_fail["result"])
        self.assertEqual(step_fail["exception"]["type"], "ValueError")
        self.assertEqual(step_fail["exception"]["message"], "invalid authorization token")

        # Event delta tracking
        step_normal = evidence["steps_by_id"]["s_normal"]
        self.assertEqual(len(step_normal["events_delta"]), 1)
        self.assertEqual(step_normal["events_delta"][0]["event"], "counter_incremented")

        # Detection of state corruption when audit event log shrinks
        step_shrink = evidence["steps_by_id"]["s_shrink"]
        self.assertEqual(step_shrink["events_delta"][0]["event"], "__AEGIS_STATE_ERROR__")
        self.assertEqual(step_shrink["events_delta"][0]["data"]["reason"], "audit shrank")

    def test_runner_failure_surfacing_and_invalid_services(self):
        case_spec = {
            "id": "scenario_contract_breach",
            "steps": [{"id": "s1", "operation": "inc", "input": {"by": 1}}],
            "invariants": [
                {"id": "inv_must_be_100", "type": "field_equals", "step": "s1", "path": "result.counter", "value": 100}
            ]
        }

        # 1. Invariant failures are faithfully collected and surfaced
        evidence = run_case("tests.test_verifier_self_validation:dummy_service_factory", case_spec)
        self.assertEqual(len(evidence["invariant_failures"]), 1)
        self.assertEqual(evidence["invariant_failures"][0]["invariant_id"], "inv_must_be_100")

        # 2. Service missing required protocol methods raises TypeError
        with self.assertRaises(TypeError) as ctx:
            run_case("tests.test_verifier_self_validation:missing_protocol_factory", case_spec)
        self.assertIn("must return an object implementing execute() and snapshot_state()", str(ctx.exception))

        # 3. Invalid import spec raises ValueError
        with self.assertRaises(ValueError) as ctx:
            run_case("invalid_import_spec_without_colon", case_spec)
        self.assertIn("Expected import spec 'module:symbol'", str(ctx.exception))


# ==============================================================================
# Area E: Gauntlet Engine Self-Validation
# ==============================================================================

class TestGauntletEngine(unittest.TestCase):
    """Challenges aegis.gauntlet: mutant execution, classification, survivor handling."""

    def setUp(self):
        self.synthetic_contract = {
            "version": "1.0",
            "subject": {
                "legacy_factory": "tests.test_verifier_self_validation:dummy_service_factory",
                "candidate_factory": "tests.test_verifier_self_validation:dummy_service_factory",
            },
            "cases": [
                {"id": "syn_1", "steps": [{"id": "s1", "operation": "inc", "input": {"by": 1}}]}
            ]
        }
        suite = run_suite("tests.test_verifier_self_validation:dummy_service_factory", self.synthetic_contract)
        self.synthetic_baseline = build_evidence_bundle(self.synthetic_contract, suite, kind="baseline")

    def test_gauntlet_detection_classification_and_survivor_handling(self):
        # 1. All mutants detected -> PASS
        mutants_detected = [
            ("mutant_drift_a", "tests.test_verifier_self_validation:drift_mutant_factory"),
        ]
        with mock.patch("rehearsal_mutations.MUTANTS", mutants_detected):
            res1 = run_gauntlet(self.synthetic_contract, self.synthetic_baseline)
            self.assertEqual(res1["verifier_validation"], "PASS")
            self.assertEqual(res1["seeded_regressions"], 1)
            self.assertEqual(res1["detected"], 1)
            self.assertEqual(res1["escaped"], 0)
            self.assertEqual(res1["detection_rate"], 100.0)

        # 2. Mutant survivor -> FAIL
        mutants_with_survivor = [
            ("mutant_drift_b", "tests.test_verifier_self_validation:drift_mutant_factory"),
            ("mutant_survivor", "tests.test_verifier_self_validation:survivor_mutant_factory"),
        ]
        with mock.patch("rehearsal_mutations.MUTANTS", mutants_with_survivor):
            res2 = run_gauntlet(self.synthetic_contract, self.synthetic_baseline)
            self.assertEqual(res2["verifier_validation"], "FAIL")
            self.assertEqual(res2["seeded_regressions"], 2)
            self.assertEqual(res2["detected"], 1)
            self.assertEqual(res2["escaped"], 1)
            self.assertEqual(res2["detection_rate"], 50.0)

            # Mathematical consistency checks
            self.assertEqual(res2["seeded_regressions"], res2["detected"] + res2["escaped"])
            self.assertLessEqual(res2["detected"], res2["seeded_regressions"])
            survivor_row = [r for r in res2["mutants"] if r["name"] == "mutant_survivor"][0]
            self.assertFalse(survivor_row["detected"])
            self.assertIsNone(survivor_row["counterexample"])

    def test_gauntlet_empty_and_invalid_configuration_behavior(self):
        # 1. Empty mutants configuration behavior
        with mock.patch("rehearsal_mutations.MUTANTS", []):
            res = run_gauntlet(self.synthetic_contract, self.synthetic_baseline)
            self.assertEqual(res["seeded_regressions"], 0)
            self.assertEqual(res["detected"], 0)
            self.assertEqual(res["escaped"], 0)
            self.assertEqual(res["detection_rate"], 0.0)
            # Documents current verifier behavior: 0 == 0 evaluates to 'PASS'
            self.assertEqual(res["verifier_validation"], "PASS")

        # 2. Missing rehearsal_mutations package raises RuntimeError
        with mock.patch.dict("sys.modules", {"rehearsal_mutations": None}):
            with self.assertRaises(RuntimeError) as ctx:
                run_gauntlet(self.synthetic_contract, self.synthetic_baseline)
            self.assertIn("rehearsal_mutations package is required", str(ctx.exception))


# ==============================================================================
# Area F: Architecture Analyzer Self-Validation
# ==============================================================================

class TestArchitectureAnalyzer(unittest.TestCase):
    """Challenges aegis.architecture: AST cycle detection, legacy imports, deterministic metrics."""

    def test_architecture_detects_legacy_imports_and_cycles(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            # 1. Legacy import detection
            pkg_leg = root / "leg_pkg"
            pkg_leg.mkdir()
            (pkg_leg / "__init__.py").write_text("", encoding="utf-8")
            (pkg_leg / "service.py").write_text(
                "import legacy_app.billing.monolith\nfrom legacy_app.billing import events\n",
                encoding="utf-8",
            )
            res_leg = analyze_python_tree(pkg_leg)
            imports = [item["import"] for item in res_leg["legacy_imports"]]
            self.assertIn("legacy_app.billing.monolith", imports)
            self.assertIn("legacy_app.billing", imports)

            # 2. Cyclic dependency detection (cycle_pkg.a <-> cycle_pkg.b)
            pkg_cyc = root / "cycle_pkg"
            pkg_cyc.mkdir()
            (pkg_cyc / "__init__.py").write_text("", encoding="utf-8")
            (pkg_cyc / "a.py").write_text("import cycle_pkg.b\n", encoding="utf-8")
            (pkg_cyc / "b.py").write_text("import cycle_pkg.a\n", encoding="utf-8")
            res_cyc = analyze_python_tree(pkg_cyc)
            self.assertGreaterEqual(len(res_cyc["circular_dependencies"]), 1)

            # 3. Acyclic graph passes (dag_pkg.m1 -> dag_pkg.m2)
            pkg_dag = root / "dag_pkg"
            pkg_dag.mkdir()
            (pkg_dag / "__init__.py").write_text("", encoding="utf-8")
            (pkg_dag / "m1.py").write_text("import dag_pkg.m2\n", encoding="utf-8")
            (pkg_dag / "m2.py").write_text("VALUE = 42\n", encoding="utf-8")
            res_dag = analyze_python_tree(pkg_dag)
            self.assertEqual(res_dag["circular_dependencies"], [])

    def test_architecture_metrics_are_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            metrics_dir = Path(td) / "metrics_test"
            metrics_dir.mkdir()
            code = (
                "# Header comment line\n"
                "\n"
                "def calculate_tax(amount):\n"
                "    # inner comment\n"
                "    return amount * 0.1\n"
                "\n"
                "class TaxCalculator:\n"
                "    def process(self):\n"
                "        return calculate_tax(100)\n"
            )
            (metrics_dir / "tax.py").write_text(code, encoding="utf-8")

            res1 = analyze_python_tree(metrics_dir)
            res2 = analyze_python_tree(metrics_dir)

            self.assertEqual(res1, res2)
            self.assertEqual(res1["module_count"], 1)
            self.assertEqual(res1["class_count"], 1)
            self.assertEqual(res1["function_count"], 2)  # calculate_tax and process
            self.assertEqual(res1["total_loc"], 5)        # non-empty, non-comment lines


# ==============================================================================
# Area G: Report Terminology Self-Validation
# ==============================================================================

class TestReportTerminology(unittest.TestCase):
    """Verifies that user-facing reports enforce BEHAVIORAL COUNTEREXAMPLE terminology."""

    def test_report_rendered_text_and_markdown_terminology(self):
        ce = {
            "case_id": "case_terminal_check",
            "diffs": [{"path": "$.steps[0].result", "kind": "value", "baseline": "legacy_val", "candidate": "modern_val"}],
        }
        comparison = {
            "verdict": "BLOCKED",
            "matched": 0,
            "drifted": 1,
            "case_count": 1,
            "cases": [{"case_id": "case_terminal_check", "status": "DRIFT", "diffs": ce["diffs"]}],
            "minimal_counterexample": ce,
        }
        baseline = make_bundle([make_case("case_terminal_check")])
        candidate = make_bundle([make_case("case_terminal_check")])

        # Rendered text verification
        text_report = render_text(comparison, baseline, candidate)
        self.assertIn("BEHAVIORAL COUNTEREXAMPLE", text_report)
        text_without_target = text_report.replace("BEHAVIORAL COUNTEREXAMPLE", "")
        self.assertNotIn("MINIMAL COUNTEREXAMPLE", text_without_target.upper())

        # Rendered markdown verification
        md_report = render_markdown(comparison, baseline, candidate)
        self.assertIn("## Behavioral Counterexample", md_report)
        self.assertNotIn("MINIMAL COUNTEREXAMPLE", md_report.upper())

    def test_report_preserves_internal_compatibility_key(self):
        baseline = make_bundle([make_case("case_drift")])
        candidate = make_bundle([make_case("case_drift", steps=[make_step(res={"counter": -99})])])
        cmp_result = compare_bundles(baseline, candidate)

        # Internal compatibility key minimal_counterexample must remain present
        self.assertIn("minimal_counterexample", cmp_result)
        self.assertIsNotNone(cmp_result["minimal_counterexample"])
        self.assertEqual(cmp_result["minimal_counterexample"]["case_id"], "case_drift")


# ==============================================================================
# Area H: Readiness Engine Self-Validation
# ==============================================================================

class TestReadinessEngine(unittest.TestCase):
    """Challenges aegis.readiness aggregation logic using hermetic synthetic results."""

    def _setup_paths(self, td: Path):
        return {
            "baseline": str(td / "baseline.json"),
            "candidate_evidence": str(td / "candidate-evidence.json"),
            "coverage_json": str(td / "coverage.json"),
            "coverage_md": str(td / "coverage.md"),
            "gauntlet_json": str(td / "gauntlet.json"),
            "gauntlet_md": str(td / "gauntlet.md"),
            "architecture_json": str(td / "architecture.json"),
            "architecture_md": str(td / "architecture.md"),
            "certificate_json": str(td / "certificate.json"),
            "certificate_md": str(td / "certificate.md"),
            "dashboard_html": str(td / "dashboard.html"),
        }

    def _base_mock_fixtures(self):
        cov = {
            "contract_readiness": "READY",
            "scenario_count": 1,
            "workflow_step_count": 1,
            "invariant_count": 0,
            "statement_coverage": 100.0,
            "branch_coverage": 100.0,
            "baseline_invariant_failures": 0,
            "tag_counts": {"core": 1},
        }
        comp = {
            "verdict": "ACCEPTED",
            "matched": 1,
            "drifted": 0,
            "case_count": 1,
            "cases": [],
            "minimal_counterexample": None,
        }
        gaunt = {
            "verifier_validation": "PASS",
            "seeded_regressions": 2,
            "detected": 2,
            "escaped": 0,
            "detection_rate": 100.0,
            "mutants": [],
        }
        arch = {
            "checks": {
                "modern_has_no_legacy_imports": True,
                "modern_has_no_cycles": True,
                "largest_module_reduced": True,
            },
            "before": {"module_count": 1, "largest_module_loc": 50, "total_loc": 50, "function_count": 2, "class_count": 1, "dependency_edges": 0, "circular_dependencies": []},
            "after": {"module_count": 1, "largest_module_loc": 25, "total_loc": 25, "function_count": 2, "class_count": 1, "dependency_edges": 0, "circular_dependencies": [], "legacy_imports": []},
        }
        cert = {
            "behavioral_verdict": "ACCEPTED",
            "cases_matched": 1,
            "scenario_count": 1,
            "workflow_step_count": 1,
            "invariant_count": 0,
            "candidate_invariant_failures": 0,
            "statement_coverage": 100.0,
            "branch_coverage": 100.0,
            "cases_drifted": 0,
            "baseline_evidence_sha256": "base_hash",
            "candidate_evidence_sha256": "cand_hash",
            "certificate_sha256": "cert_hash",
            "scope": "Verification scope",
            "architecture_checks": arch["checks"],
            "gauntlet": {"detected": 2, "seeded_regressions": 2},
        }
        proc = mock.Mock(returncode=0, stdout="OK", stderr="")
        return cov, comp, gaunt, arch, cert, proc

    def test_readiness_all_passing_yields_ready(self):
        contract = {
            "version": "1.0",
            "subject": {"candidate_factory": "dummy:cand"},
            "cases": [make_case()],
        }
        cov, comp, gaunt, arch, cert, proc = self._base_mock_fixtures()

        with tempfile.TemporaryDirectory() as td:
            paths = self._setup_paths(Path(td))

            with mock.patch("subprocess.run", return_value=proc), \
                 mock.patch("aegis.readiness.record_baseline", return_value=make_bundle()), \
                 mock.patch("aegis.readiness.measure_contract_coverage", return_value=cov), \
                 mock.patch("aegis.readiness.run_suite", return_value={"cases": []}), \
                 mock.patch("aegis.readiness.build_evidence_bundle", return_value=make_bundle()), \
                 mock.patch("aegis.readiness.compare_bundles", return_value=comp), \
                 mock.patch("aegis.readiness.run_gauntlet", return_value=gaunt), \
                 mock.patch("aegis.readiness.compare_architecture", return_value=arch), \
                 mock.patch("aegis.readiness.build_certificate", return_value=cert):

                res = run_readiness(contract, paths)

                self.assertEqual(res["readiness"], "READY")
                self.assertTrue(all(res["checks"].values()))
                # Filesystem isolation: all artifacts written to temporary directory
                self.assertTrue(Path(paths["certificate_md"]).exists())
                self.assertTrue(Path(paths["dashboard_html"]).exists())

    def test_readiness_any_failure_yields_not_ready(self):
        contract = {
            "version": "1.0",
            "subject": {"candidate_factory": "dummy:cand"},
            "cases": [make_case()],
        }
        cov, comp, gaunt, arch, cert, proc = self._base_mock_fixtures()

        # Inject single failure: behavioral drift present
        comp["verdict"] = "BLOCKED"
        cert["cases_drifted"] = 1

        with tempfile.TemporaryDirectory() as td:
            paths = self._setup_paths(Path(td))

            with mock.patch("subprocess.run", return_value=proc), \
                 mock.patch("aegis.readiness.record_baseline", return_value=make_bundle()), \
                 mock.patch("aegis.readiness.measure_contract_coverage", return_value=cov), \
                 mock.patch("aegis.readiness.run_suite", return_value={"cases": []}), \
                 mock.patch("aegis.readiness.build_evidence_bundle", return_value=make_bundle()), \
                 mock.patch("aegis.readiness.compare_bundles", return_value=comp), \
                 mock.patch("aegis.readiness.run_gauntlet", return_value=gaunt), \
                 mock.patch("aegis.readiness.compare_architecture", return_value=arch), \
                 mock.patch("aegis.readiness.build_certificate", return_value=cert):

                res = run_readiness(contract, paths)

                self.assertEqual(res["readiness"], "NOT_READY")
                self.assertFalse(res["checks"]["modernization_verify"])
                self.assertFalse(res["checks"]["certificate_no_drift"])


if __name__ == "__main__":
    unittest.main()
