from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from aegis.architecture import compare_architecture
from aegis.baseline import record_baseline
from aegis.comparator import compare_bundles
from aegis.contracts import load_contract
from aegis.coverage_report import measure_contract_coverage
from aegis.evidence import build_evidence_bundle
from aegis.gauntlet import run_gauntlet
from aegis.runner import run_suite

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / 'aegis_contract.yaml'

class AegisV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CONTRACT_PATH.exists():
            raise unittest.SkipTest("aegis_contract.yaml has not been generated yet.")
        cls.contract = load_contract(CONTRACT_PATH)
        with tempfile.TemporaryDirectory() as td:
            cls.baseline = record_baseline(cls.contract, Path(td) / 'baseline.json')

    def bundle(self, spec):
        return build_evidence_bundle(self.contract, run_suite(spec, self.contract), kind='candidate')

    def test_contract_is_deep_enough(self):
        self.assertGreaterEqual(len(self.contract['cases']), 60)
        self.assertGreaterEqual(sum(len(c['steps']) for c in self.contract['cases']), 70)

    def test_baseline_has_no_invariant_failures(self):
        self.assertEqual(sum(len(c['invariant_failures']) for c in self.baseline['cases']), 0)

    def test_equivalent_modern_candidate_is_accepted(self):
        cmp = compare_bundles(self.baseline, self.bundle('modern_app.billing.api:create_service'))
        self.assertEqual(cmp['verdict'], 'ACCEPTED')
        self.assertEqual(cmp['drifted'], 0)

    def test_boundary_regression_is_blocked(self):
        cmp = compare_bundles(self.baseline, self.bundle('rehearsal_mutations.mutants:vip_1000_strict'))
        self.assertEqual(cmp['verdict'], 'BLOCKED')
        self.assertEqual(cmp['minimal_counterexample']['case_id'], 'bnd_vip_subtotal_1000_00')

    def test_contract_coverage_gate(self):
        r = measure_contract_coverage(self.contract)
        self.assertEqual(r['contract_readiness'], 'READY')
        self.assertGreaterEqual(r['statement_coverage'], 95.0)
        self.assertGreaterEqual(r['branch_coverage'], 90.0)

    def test_gauntlet_detects_all_seeded_regressions(self):
        r = run_gauntlet(self.contract, self.baseline)
        self.assertEqual(r['escaped'], 0)
        self.assertEqual(r['verifier_validation'], 'PASS')
        self.assertGreaterEqual(r['seeded_regressions'], 15)

    def test_architecture_evidence(self):
        r = compare_architecture()
        self.assertTrue(r['checks']['modern_has_no_legacy_imports'])
        self.assertTrue(r['checks']['modern_has_no_cycles'])
        self.assertTrue(r['checks']['largest_module_reduced'])

if __name__ == '__main__':
    unittest.main()
