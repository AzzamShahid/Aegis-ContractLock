from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import coverage
from .runner import run_suite
from .util import ensure_parent


def measure_contract_coverage(contract: dict[str, Any], contract_path: str = "aegis_contract.yaml") -> dict[str, Any]:
    import subprocess, sys, tempfile
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "coverage-worker.json"
        proc = subprocess.run([sys.executable, "-m", "aegis.coverage_worker", contract_path, str(out)], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Coverage worker failed: {proc.stdout}\n{proc.stderr}")
        worker = json.loads(out.read_text(encoding="utf-8"))
    target = worker["target"]
    summary = target["summary"]
    tags: dict[str, int] = {}
    step_count = 0
    invariant_count = 0
    for case in contract["cases"]:
        step_count += len(case.get("steps", []))
        invariant_count += len(case.get("invariants", []))
        for tag in case.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    readiness = contract.get("readiness", {})
    statement_pct = float(summary.get("percent_statements_covered", 0.0))
    branch_pct = float(summary.get("percent_branches_covered", 0.0))
    statement_min = float(readiness.get("statement_coverage_min", 95.0))
    branch_min = float(readiness.get("branch_coverage_min", 90.0))
    required_tags = readiness.get("critical_tags", [])
    missing_tags = [t for t in required_tags if tags.get(t, 0) == 0]
    invariant_failures = int(worker.get("invariant_failures", 0))
    ready = statement_pct >= statement_min and branch_pct >= branch_min and not missing_tags and invariant_failures == 0
    return {
        "scenario_count": len(contract["cases"]),
        "workflow_step_count": step_count,
        "invariant_count": invariant_count,
        "statement_coverage": round(statement_pct, 2),
        "branch_coverage": round(branch_pct, 2),
        "covered_statements": summary.get("covered_lines", 0),
        "total_statements": summary.get("num_statements", 0),
        "covered_branches": summary.get("covered_branches", 0),
        "total_branches": summary.get("num_branches", 0),
        "missing_lines": target.get("missing_lines", []),
        "missing_branches": target.get("missing_branches", []),
        "tag_counts": dict(sorted(tags.items())),
        "required_tags_missing": missing_tags,
        "baseline_invariant_failures": invariant_failures,
        "thresholds": {"statement": statement_min, "branch": branch_min},
        "contract_readiness": "READY" if ready else "NOT_READY",
    }


def render_coverage_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Aegis Contract Coverage",
        "",
        f"**Contract readiness:** `{result['contract_readiness']}`",
        "",
        f"- Scenarios: **{result['scenario_count']}**",
        f"- Workflow steps: **{result['workflow_step_count']}**",
        f"- Invariants: **{result['invariant_count']}**",
        f"- Legacy statement coverage: **{result['statement_coverage']:.2f}%**",
        f"- Legacy branch coverage: **{result['branch_coverage']:.2f}%**",
        f"- Baseline invariant failures: **{result['baseline_invariant_failures']}**",
        "",
        "## Contract families",
        "",
        "| Tag | Scenarios |",
        "|---|---:|",
    ]
    for tag, count in result["tag_counts"].items():
        lines.append(f"| `{tag}` | {count} |")
    lines += [
        "",
        "## Scope",
        "",
        "Coverage measures execution of the legacy reference implementation by the defined behavioral contract. It does not establish complete program equivalence.",
        "",
    ]
    return "\n".join(lines)
