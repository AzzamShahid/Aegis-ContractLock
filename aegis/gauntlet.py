from __future__ import annotations
from typing import Any
from .runner import run_suite
from .evidence import build_evidence_bundle
from .comparator import compare_bundles

def run_gauntlet(contract: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    try:
        from rehearsal_mutations import MUTANTS
    except ImportError:
        raise RuntimeError("rehearsal_mutations package is required to run the regression gauntlet.")
    rows=[]
    for name,spec in MUTANTS:
        suite=run_suite(spec,contract)
        bundle=build_evidence_bundle(contract,suite,kind='mutation')
        comparison=compare_bundles(baseline,bundle)
        detected=comparison['verdict']=='BLOCKED'
        ce=comparison.get('minimal_counterexample')
        rows.append({'name':name,'factory':spec,'detected':detected,'drifted_cases':comparison['drifted'],'counterexample':None if ce is None else ce['case_id']})
    detected=sum(1 for r in rows if r['detected'])
    total=len(rows)
    return {'seeded_regressions':total,'detected':detected,'escaped':total-detected,'detection_rate':round((detected/total*100.0) if total else 0.0,2),'verifier_validation':'NOT_VALIDATED' if total == 0 else ('PASS' if detected == total else 'FAIL'),'mutants':rows}


def render_gauntlet_markdown(result):
    lines=['# Aegis Verifier Regression Gauntlet','',f"**Verifier validation:** `{result['verifier_validation']}`",'',f"- Seeded semantic regressions: **{result['seeded_regressions']}**",f"- Detected: **{result['detected']}**",f"- Escaped: **{result['escaped']}**",f"- Detection rate: **{result['detection_rate']:.2f}%**",'', '| Mutation | Detected | Drifted cases | First counterexample |','|---|---:|---:|---|']
    for r in result['mutants']:
        lines.append(f"| `{r['name']}` | {'YES' if r['detected'] else 'NO'} | {r['drifted_cases']} | `{r['counterexample'] or '-'}` |")
    lines += ['', 'These are synthetic fault-injection candidates used to stress-test the contract/verifier. They are not claims about naturally occurring AI error frequency.', '']
    return '\n'.join(lines)
