from __future__ import annotations
import json, sys
from pathlib import Path
import coverage
from .contracts import load_contract
from .runner import run_suite


def main(argv=None):
    argv=argv or sys.argv[1:]
    contract_path=argv[0]; output=Path(argv[1])
    contract=load_contract(contract_path)
    cov=coverage.Coverage(branch=True,source=['legacy_app'],data_file=None)
    cov.start(); suite=run_suite(contract['subject']['legacy_factory'],contract); cov.stop()
    raw=output.with_suffix('.raw.json')
    cov.json_report(outfile=str(raw))
    data=json.loads(raw.read_text(encoding='utf-8')); raw.unlink(missing_ok=True)
    target=None
    for name,info in data.get('files',{}).items():
        if name.replace('\\','/').endswith('legacy_app/billing/monolith.py'): target=info; break
    if target is None: raise RuntimeError('monolith coverage missing')
    output.write_text(json.dumps({'target':target,'invariant_failures':sum(len(c['invariant_failures']) for c in suite['cases'])}),encoding='utf-8')
    return 0

if __name__=='__main__': raise SystemExit(main())
