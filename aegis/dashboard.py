from __future__ import annotations
import html
from typing import Any

def render_dashboard(certificate: dict[str, Any], architecture: dict[str, Any], gauntlet: dict[str, Any]) -> str:
    ok=certificate['behavioral_verdict']=='ACCEPTED'
    status='ACCEPTED' if ok else 'BLOCKED'
    b,a=architecture['before'],architecture['after']
    esc=html.escape
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Aegis ContractLock Evidence</title><style>
    body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#0b1020;color:#e8edf7;margin:0;padding:32px}} .wrap{{max-width:1100px;margin:auto}}
    .hero,.card{{background:#121a2c;border:1px solid #28344f;border-radius:18px;padding:24px;margin-bottom:18px;box-shadow:0 12px 40px #0004}}
    .hero h1{{margin:0 0 6px;font-size:36px}} .status{{font-size:28px;font-weight:800}} .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
    .metric{{background:#0e1628;border-radius:14px;padding:16px}} .n{{font-size:25px;font-weight:800}} .label{{opacity:.72;font-size:13px;margin-top:5px}}
    table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #26324a;text-align:left}} code{{word-break:break-all}} .scope{{opacity:.72;line-height:1.5}}
    @media(max-width:800px){{.grid{{grid-template-columns:1fr 1fr}}}}
    </style></head><body><div class="wrap">
    <div class="hero"><h1>AEGIS CONTRACTLOCK</h1><div>Evidence-Gated Legacy Modernization</div><p class="status">{status}</p></div>
    <div class="grid">
      <div class="metric"><div class="n">{certificate['cases_matched']}/{certificate['scenario_count']}</div><div class="label">Behavioral scenarios matched</div></div>
      <div class="metric"><div class="n">{certificate['statement_coverage']:.1f}%</div><div class="label">Legacy statement coverage</div></div>
      <div class="metric"><div class="n">{certificate['branch_coverage']:.1f}%</div><div class="label">Legacy branch coverage</div></div>
      <div class="metric"><div class="n">{gauntlet['detected']}/{gauntlet['seeded_regressions']}</div><div class="label">Seeded regressions detected</div></div>
    </div>
    <div class="card"><h2>Structural modernization</h2><table><tr><th>Metric</th><th>Legacy</th><th>Modern</th></tr>
      <tr><td>Python modules</td><td>{b['module_count']}</td><td>{a['module_count']}</td></tr>
      <tr><td>Largest module LOC</td><td>{b['largest_module_loc']}</td><td>{a['largest_module_loc']}</td></tr>
      <tr><td>Classes</td><td>{b['class_count']}</td><td>{a['class_count']}</td></tr>
      <tr><td>Dependency cycles</td><td>{len(b['circular_dependencies'])}</td><td>{len(a['circular_dependencies'])}</td></tr>
      <tr><td>Imports from legacy</td><td>—</td><td>{len(a['legacy_imports'])}</td></tr></table></div>
    <div class="card"><h2>Evidence fingerprints</h2><p>Baseline: <code>{esc(certificate['baseline_evidence_sha256'])}</code></p><p>Candidate: <code>{esc(certificate['candidate_evidence_sha256'])}</code></p><p>Certificate: <code>{esc(certificate['certificate_sha256'])}</code></p></div>
    <div class="card scope"><strong>Scope</strong><p>{esc(certificate['scope'])}</p></div>
    </div></body></html>'''
