from __future__ import annotations
import subprocess, sys
from pathlib import Path
from typing import Any
from .baseline import record_baseline
from .coverage_report import measure_contract_coverage
from .runner import run_suite
from .evidence import build_evidence_bundle, write_json
from .comparator import compare_bundles
from .gauntlet import run_gauntlet
from .architecture import compare_architecture
from .certificate import build_certificate, render_certificate_markdown
from .dashboard import render_dashboard
from .report import write_markdown


def run_readiness(contract: dict[str, Any], paths: dict[str,str]) -> dict[str,Any]:
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],capture_output=True,text=True)
    baseline=record_baseline(contract,paths['baseline'])
    coverage_result=measure_contract_coverage(contract)
    candidate=build_evidence_bundle(contract,run_suite(contract['subject']['candidate_factory'],contract),kind='candidate')
    write_json(paths['candidate_evidence'],candidate)
    comparison=compare_bundles(baseline,candidate)
    gauntlet=run_gauntlet(contract,baseline)
    architecture=compare_architecture()
    certificate=build_certificate(contract,baseline,candidate,comparison,coverage_result,gauntlet,architecture)
    write_json(paths['coverage_json'],coverage_result)
    write_json(paths['gauntlet_json'],gauntlet)
    write_json(paths['architecture_json'],architecture)
    write_json(paths['certificate_json'],certificate)
    from .coverage_report import render_coverage_markdown
    from .gauntlet import render_gauntlet_markdown
    from .architecture import render_architecture_markdown
    write_markdown(paths['coverage_md'],render_coverage_markdown(coverage_result))
    write_markdown(paths['gauntlet_md'],render_gauntlet_markdown(gauntlet))
    write_markdown(paths['architecture_md'],render_architecture_markdown(architecture))
    write_markdown(paths['certificate_md'],render_certificate_markdown(certificate))
    p=Path(paths['dashboard_html']); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(render_dashboard(certificate,architecture,gauntlet),encoding='utf-8')
    checks={
      'engine_tests':tests.returncode==0,
      'contract_coverage':coverage_result['contract_readiness']=='READY',
      'modernization_verify':comparison['verdict']=='ACCEPTED',
      'regression_gauntlet':gauntlet['verifier_validation']=='PASS',
      'architecture_no_legacy_imports':architecture['checks']['modern_has_no_legacy_imports'],
      'architecture_no_cycles':architecture['checks']['modern_has_no_cycles'],
      'certificate_no_drift':certificate['cases_drifted']==0,
    }
    return {'readiness':'READY' if all(checks.values()) else 'NOT_READY','checks':checks,'tests_stdout':tests.stdout,'tests_stderr':tests.stderr,'coverage':coverage_result,'comparison':comparison,'gauntlet':gauntlet,'architecture':architecture,'certificate':certificate}
