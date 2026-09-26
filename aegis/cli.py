from __future__ import annotations

import argparse
from pathlib import Path

from .architecture import compare_architecture, render_architecture_markdown
from .baseline import record_baseline
from .certificate import build_certificate, render_certificate_markdown
from .comparator import compare_bundles
from .contracts import load_contract
from .coverage_report import measure_contract_coverage, render_coverage_markdown
from .dashboard import render_dashboard
from .evidence import build_evidence_bundle, read_json, write_json
from .gauntlet import render_gauntlet_markdown, run_gauntlet
from .readiness import run_readiness
from .report import render_markdown, render_text, write_markdown
from .runner import run_suite


def _paths(contract: dict):
    outputs = contract.get("outputs", {})
    defaults = {
        "baseline": "baseline/baseline.json",
        "verification_json": "reports/verification.json",
        "verification_md": "reports/verification.md",
        "candidate_evidence": "reports/candidate-evidence.json",
        "coverage_json": "reports/contract-coverage.json",
        "coverage_md": "reports/contract-coverage.md",
        "gauntlet_json": "reports/gauntlet-report.json",
        "gauntlet_md": "reports/gauntlet-report.md",
        "architecture_json": "reports/architecture-comparison.json",
        "architecture_md": "reports/architecture-comparison.md",
        "certificate_json": "reports/evidence-certificate.json",
        "certificate_md": "reports/evidence-certificate.md",
        "dashboard_html": "reports/dashboard.html",
        "readiness_json": "reports/readiness.json",
        "readiness_md": "reports/readiness.md",
    }
    return {k: outputs.get(k, v) for k, v in defaults.items()}


def cmd_baseline(args) -> int:
    contract = load_contract(args.contract); paths = _paths(contract)
    output = args.output or paths["baseline"]
    bundle = record_baseline(contract, output)
    invariant_failures = sum(len(c["invariant_failures"]) for c in bundle["cases"])
    print("AEGIS BASELINE SEALED")
    print(f"Cases              : {bundle['case_count']}")
    print(f"Invariant failures : {invariant_failures}")
    print(f"Evidence SHA-256   : {bundle['evidence_sha256']}")
    print(f"Written to         : {output}")
    return 2 if invariant_failures else 0


def _verify(contract, paths, candidate_factory=None):
    baseline = read_json(paths["baseline"])
    candidate_factory = candidate_factory or contract["subject"]["candidate_factory"]
    suite = run_suite(candidate_factory, contract)
    candidate = build_evidence_bundle(contract, suite, kind="candidate")
    write_json(paths["candidate_evidence"], candidate)
    comparison = compare_bundles(baseline, candidate)
    write_json(paths["verification_json"], {"comparison": comparison,"baseline_evidence_sha256": baseline["evidence_sha256"],"candidate_evidence_sha256": candidate["evidence_sha256"],"candidate_factory": candidate_factory})
    write_markdown(paths["verification_md"], render_markdown(comparison, baseline, candidate))
    return baseline, candidate, comparison


def cmd_verify(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    if args.baseline: paths['baseline']=args.baseline
    if args.candidate_evidence: paths['candidate_evidence']=args.candidate_evidence
    if args.report_json: paths['verification_json']=args.report_json
    if args.report_md: paths['verification_md']=args.report_md
    baseline,candidate,comparison=_verify(contract,paths,args.candidate)
    print(render_text(comparison,baseline,candidate))
    print(f"JSON report: {paths['verification_json']}")
    print(f"MD report  : {paths['verification_md']}")
    return 0 if comparison['verdict']=='ACCEPTED' else 1


def cmd_coverage(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    result=measure_contract_coverage(contract)
    write_json(paths['coverage_json'],result); write_markdown(paths['coverage_md'],render_coverage_markdown(result))
    print("AEGIS CONTRACT COVERAGE")
    print(f"Scenarios                  : {result['scenario_count']}")
    print(f"Workflow steps             : {result['workflow_step_count']}")
    print(f"Legacy statement coverage  : {result['statement_coverage']:.2f}%")
    print(f"Legacy branch coverage     : {result['branch_coverage']:.2f}%")
    print(f"Contract readiness         : {result['contract_readiness']}")
    return 0 if result['contract_readiness']=='READY' else 1


def cmd_gauntlet(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    if not Path(paths['baseline']).exists(): record_baseline(contract,paths['baseline'])
    result=run_gauntlet(contract,read_json(paths['baseline']))
    write_json(paths['gauntlet_json'],result); write_markdown(paths['gauntlet_md'],render_gauntlet_markdown(result))
    print("AEGIS VERIFIER GAUNTLET")
    print(f"Seeded regressions : {result['seeded_regressions']}")
    print(f"Detected           : {result['detected']}")
    print(f"Escaped            : {result['escaped']}")
    print(f"Detection rate     : {result['detection_rate']:.2f}%")
    print(f"Verifier validation: {result['verifier_validation']}")
    return 0 if result['verifier_validation']=='PASS' else 1


def cmd_architecture(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    result=compare_architecture(); write_json(paths['architecture_json'],result); write_markdown(paths['architecture_md'],render_architecture_markdown(result))
    print("AEGIS STRUCTURAL MODERNIZATION")
    print(f"Largest module LOC: {result['before']['largest_module_loc']} -> {result['after']['largest_module_loc']}")
    print(f"Python modules    : {result['before']['module_count']} -> {result['after']['module_count']}")
    print(f"Modern legacy imports: {len(result['after']['legacy_imports'])}")
    print(f"Modern cycles        : {len(result['after']['circular_dependencies'])}")
    return 0 if result['checks']['modern_has_no_legacy_imports'] and result['checks']['modern_has_no_cycles'] else 1


def cmd_certificate(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    if not Path(paths['baseline']).exists(): record_baseline(contract,paths['baseline'])
    baseline,candidate,comparison=_verify(contract,paths,args.candidate)
    coverage_result=measure_contract_coverage(contract)
    gauntlet=run_gauntlet(contract,baseline)
    architecture=compare_architecture()
    cert=build_certificate(contract,baseline,candidate,comparison,coverage_result,gauntlet,architecture)
    write_json(paths['certificate_json'],cert); write_markdown(paths['certificate_md'],render_certificate_markdown(cert))
    print(render_certificate_markdown(cert))
    return 0 if comparison['verdict']=='ACCEPTED' and gauntlet['verifier_validation']=='PASS' else 1


def cmd_dashboard(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    cert=read_json(paths['certificate_json']); architecture=read_json(paths['architecture_json']); gauntlet=read_json(paths['gauntlet_json'])
    p=Path(paths['dashboard_html']); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(render_dashboard(cert,architecture,gauntlet),encoding='utf-8')
    print(f"Dashboard written: {p}")
    return 0


def cmd_readiness(args) -> int:
    contract=load_contract(args.contract); paths=_paths(contract)
    result=run_readiness(contract,paths)
    summary={
      "readiness": result["readiness"],
      "checks": result["checks"],
      "scenario_count": result["coverage"]["scenario_count"],
      "workflow_step_count": result["coverage"]["workflow_step_count"],
      "statement_coverage": result["coverage"]["statement_coverage"],
      "branch_coverage": result["coverage"]["branch_coverage"],
      "gauntlet_detected": result["gauntlet"]["detected"],
      "gauntlet_seeded": result["gauntlet"]["seeded_regressions"],
      "behavioral_verdict": result["comparison"]["verdict"],
    }
    write_json(paths["readiness_json"], summary)
    md=["# Aegis Submission Readiness","",f"**Status:** `{summary['readiness']}`","", "| Gate | Status |","|---|---:|"]
    for name,ok in summary["checks"].items(): md.append(f"| `{name}` | {'PASS' if ok else 'FAIL'} |")
    md += ["",f"- Scenarios: **{summary['scenario_count']}**",f"- Workflow steps: **{summary['workflow_step_count']}**",f"- Statement coverage: **{summary['statement_coverage']:.2f}%**",f"- Branch coverage: **{summary['branch_coverage']:.2f}%**",f"- Regression gauntlet: **{summary['gauntlet_detected']} / {summary['gauntlet_seeded']}**",f"- Behavioral verdict: **{summary['behavioral_verdict']}**","","> READY means the local technical gates pass. The real IBM Bob run, Bob task screenshots, demo rehearsal, and hackathon submission assets remain separate required work.",""]
    write_markdown(paths["readiness_md"], "\n".join(md))
    print("AEGIS SUBMISSION READINESS")
    print("-"*44)
    for name,ok in result['checks'].items(): print(f"{name:34} {'PASS' if ok else 'FAIL'}")
    print(f"Scenarios                          {result['coverage']['scenario_count']}")
    print(f"Statement coverage                 {result['coverage']['statement_coverage']:.2f}%")
    print(f"Branch coverage                    {result['coverage']['branch_coverage']:.2f}%")
    print(f"Regression gauntlet                {result['gauntlet']['detected']}/{result['gauntlet']['seeded_regressions']}")
    print("-"*44)
    print(f"SUBMISSION READINESS: {result['readiness']}")
    if result['readiness']!='READY':
        print("\nUnit test output:\n",result['tests_stdout'],result['tests_stderr'])
    return 0 if result['readiness']=='READY' else 1


def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(prog='aegis',description='Evidence-gated legacy modernization verifier')
    parser.add_argument('--contract',default='aegis_contract.yaml')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('baseline'); p.add_argument('--output'); p.set_defaults(func=cmd_baseline)
    p=sub.add_parser('verify'); p.add_argument('--candidate'); p.add_argument('--baseline'); p.add_argument('--candidate-evidence'); p.add_argument('--report-json'); p.add_argument('--report-md'); p.set_defaults(func=cmd_verify)
    p=sub.add_parser('coverage'); p.set_defaults(func=cmd_coverage)
    p=sub.add_parser('gauntlet'); p.set_defaults(func=cmd_gauntlet)
    p=sub.add_parser('architecture'); p.set_defaults(func=cmd_architecture)
    p=sub.add_parser('certificate'); p.add_argument('--candidate'); p.set_defaults(func=cmd_certificate)
    p=sub.add_parser('dashboard'); p.set_defaults(func=cmd_dashboard)
    p=sub.add_parser('readiness'); p.set_defaults(func=cmd_readiness)
    return parser


def main(argv=None)->int:
    args=build_parser().parse_args(argv); return args.func(args)

if __name__=='__main__': raise SystemExit(main())
