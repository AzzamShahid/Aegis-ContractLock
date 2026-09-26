from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .util import fingerprint

SCOPE = "Acceptance establishes behavioral equivalence across the defined contract and executed scenario corpus. It is not a formal proof of complete program equivalence."

def build_certificate(contract: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any], comparison: dict[str, Any], coverage_result: dict[str, Any], gauntlet_result: dict[str, Any], architecture_result: dict[str, Any]) -> dict[str, Any]:
    step_count=sum(len(c.get('steps',[])) for c in contract['cases'])
    inv_total=sum(len(c.get('invariants',[])) for c in contract['cases'])
    inv_fail=sum(len(c.get('invariant_failures',[])) for c in candidate['cases'])
    cert={
      'aegis_certificate_version':'2.0',
      'contract_version':contract['version'],
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'scenario_count':len(contract['cases']),
      'workflow_step_count':step_count,
      'invariant_count':inv_total,
      'candidate_invariant_failures':inv_fail,
      'statement_coverage':coverage_result['statement_coverage'],
      'branch_coverage':coverage_result['branch_coverage'],
      'cases_matched':comparison['matched'],
      'cases_drifted':comparison['drifted'],
      'behavioral_verdict':comparison['verdict'],
      'gauntlet':{'seeded_regressions':gauntlet_result['seeded_regressions'],'detected':gauntlet_result['detected'],'escaped':gauntlet_result['escaped'],'validation':gauntlet_result['verifier_validation']},
      'architecture_checks':architecture_result['checks'],
      'baseline_evidence_sha256':baseline['evidence_sha256'],
      'candidate_evidence_sha256':candidate['evidence_sha256'],
      'scope':SCOPE,
    }
    cert['certificate_sha256']=fingerprint({k:v for k,v in cert.items() if k not in {'generated_at_utc','certificate_sha256'}})
    return cert

def render_certificate_markdown(c: dict[str, Any]) -> str:
    a=c['architecture_checks']; g=c['gauntlet']
    return f"""# Aegis Modernization Evidence Certificate

**Behavioral verdict:** `{c['behavioral_verdict']}`

- Behavioral scenarios: **{c['cases_matched']} / {c['scenario_count']} matched**
- Workflow steps: **{c['workflow_step_count']}**
- Contract invariants: **{c['invariant_count']}**
- Candidate invariant failures: **{c['candidate_invariant_failures']}**
- Legacy statement coverage: **{c['statement_coverage']:.2f}%**
- Legacy branch coverage: **{c['branch_coverage']:.2f}%**
- Behavioral drift: **{c['cases_drifted']} cases**
- Regression gauntlet: **{g['detected']} / {g['seeded_regressions']} detected**
- Modern imports from legacy: **{'PASS' if a['modern_has_no_legacy_imports'] else 'FAIL'}**
- Modern dependency-cycle check: **{'PASS' if a['modern_has_no_cycles'] else 'FAIL'}**

## Evidence fingerprints

- Baseline SHA-256: `{c['baseline_evidence_sha256']}`
- Candidate SHA-256: `{c['candidate_evidence_sha256']}`
- Certificate SHA-256: `{c['certificate_sha256']}`

## Scope

{c['scope']}
"""
