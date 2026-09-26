from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from .util import ensure_parent


def render_text(
    comparison: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    width = 68
    lines = []
    lines.append("=" * width)
    lines.append("AEGIS CONTRACTLOCK — MODERNIZATION VERDICT")
    lines.append("=" * width)
    lines.append(f"Cases matched : {comparison['matched']} / {comparison['case_count']}")
    lines.append(f"Cases drifted : {comparison['drifted']}")
    lines.append(f"Baseline hash : {baseline['evidence_sha256']}")
    lines.append(f"Candidate hash: {candidate['evidence_sha256']}")
    lines.append("")
    lines.append(f"VERDICT: {comparison['verdict']}")

    if comparison["minimal_counterexample"]:
        ce = comparison["minimal_counterexample"]
        lines.append("")
        lines.append("-" * width)
        lines.append("MINIMAL COUNTEREXAMPLE")
        lines.append("-" * width)
        lines.append(f"Case: {ce['case_id']}")
        for diff in ce["diffs"][:12]:
            lines.append(f"* {diff.get('path')} [{diff.get('kind')}]")
            if "baseline" in diff:
                lines.append(f"  legacy   = {diff.get('baseline')!r}")
                lines.append(f"  candidate= {diff.get('candidate')!r}")
        if len(ce["diffs"]) > 12:
            lines.append(f"... {len(ce['diffs']) - 12} additional diff(s)")
    lines.append("")
    lines.append("Scope: equivalence across the defined contract and executed scenario corpus; not formal proof of complete program equivalence.")
    lines.append("=" * width)
    return "\n".join(lines)


def render_markdown(
    comparison: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    rows = ["| Case | Status | Drift count |", "|---|---:|---:|"]
    for case in comparison["cases"]:
        rows.append(
            f"| `{case['case_id']}` | {case['status']} | {len(case['diffs'])} |"
        )

    out = [
        "# Aegis ContractLock Verification Report",
        "",
        f"**Verdict:** `{comparison['verdict']}`",
        "",
        f"- Cases matched: **{comparison['matched']} / {comparison['case_count']}**",
        f"- Cases drifted: **{comparison['drifted']}**",
        f"- Baseline evidence SHA-256: `{baseline['evidence_sha256']}`",
        f"- Candidate evidence SHA-256: `{candidate['evidence_sha256']}`",
        "",
        *rows,
        "",
        "> **Scope:** This verdict establishes behavioral equivalence across the defined contract and executed scenario corpus. It is not a formal proof of complete program equivalence.",
    ]

    if comparison["minimal_counterexample"]:
        ce = comparison["minimal_counterexample"]
        out += [
            "",
            "## Minimal Counterexample",
            "",
            f"**Case:** `{ce['case_id']}`",
            "",
            "```text",
        ]
        for diff in ce["diffs"][:20]:
            out.append(f"{diff.get('path')} [{diff.get('kind')}]")
            if "baseline" in diff:
                out.append(f"legacy    = {diff.get('baseline')!r}")
                out.append(f"candidate = {diff.get('candidate')!r}")
                out.append("")
        out += ["```", ""]
    return "\n".join(out) + "\n"


def write_markdown(path: str | Path, content: str) -> Path:
    path = Path(path)
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    return path
