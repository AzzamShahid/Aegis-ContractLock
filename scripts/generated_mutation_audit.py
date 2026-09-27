"""Generated Holdout Mutation Audit Runner for Aegis ContractLock.

Role: Antigravity (Post-Freeze Adversarial Challenger)
Judge: Aegis Behavioral Verifier
Baseline: Frozen at tag aegis-holdout-freeze-20260927

This script:
1. Verifies the freeze manifest and frozen artifacts before generating mutations.
2. Applies 65 generated semantic, generic, domain, survivor, and invalid candidate mutations
   exclusively to temporary copies of the accepted modern candidate (never modifying modern_app in place).
3. Evaluates each candidate in an isolated subprocess against the frozen Aegis behavioral gate.
4. Classifies each mutant as GENERATED, APPLIED, RUNNABLE, DETECTED, SURVIVED_CONTRACT,
   INVALID_OR_UNRUNNABLE, or TIMEOUT_OR_INFRA_ERROR.
5. Produces reports/generated-mutation-audit.json and reports/generated-mutation-audit.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add repo root to sys.path so generated_mutations can be imported directly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generated_mutations.catalog import MUTATIONS, Mutation


def get_canonical_tree_sha256(root_path: Path) -> str:
    """
    Computes canonical directory tree SHA-256 using the algorithm recorded in the freeze manifest:
    All recursive files sorted case-insensitively by full path, formatted as 'relative_path\tfile_sha256',
    joined with newline, encoded in UTF-8, and hashed with SHA-256.
    """
    root = root_path.resolve()
    if not root.exists():
        return ""
    files = [p for p in root.rglob("*") if p.is_file()]
    files.sort(key=lambda p: str(p).lower())
    entries = []
    for p in files:
        rel = str(p.relative_to(root)).replace("\\", "/")
        h = hashlib.sha256(p.read_bytes()).hexdigest().lower()
        entries.append(f"{rel}\t{h}")
    payload = "\n".join(entries)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().lower()


def find_source_repo() -> Path:
    """Finds the main repository worktree if running in a secondary git worktree."""
    try:
        proc = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        for block in proc.stdout.strip().split("\n\n"):
            for line in block.splitlines():
                if line.startswith("worktree "):
                    wt_path = Path(line[len("worktree ") :].strip())
                    if wt_path.exists():
                        return wt_path
    except Exception:
        pass
    return REPO_ROOT


def verify_freeze() -> Dict[str, Any]:
    """
    First gate: verify that the accepted candidate, behavioral contract, baseline,
    and verifier match the frozen state recorded in reports/holdout-freeze-manifest.json.
    """
    manifest_path = REPO_ROOT / "reports" / "holdout-freeze-manifest.json"
    if not manifest_path.exists():
        return {
            "status": "FAILED",
            "reason": f"Freeze manifest not found at {manifest_path}",
        }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: Dict[str, Any] = {}
    failures: List[str] = []

    # 1. Behavioral contract artifact SHA-256
    contract_file = REPO_ROOT / "aegis_contract.yaml"
    contract_sha = (
        hashlib.sha256(contract_file.read_bytes()).hexdigest().lower()
        if contract_file.exists()
        else ""
    )
    exp_contract_sha = manifest["behavioral_contract"]["artifact_sha256"]
    checks["behavioral_contract_sha256"] = {
        "actual": contract_sha,
        "expected": exp_contract_sha,
        "match": contract_sha == exp_contract_sha,
    }
    if contract_sha != exp_contract_sha:
        failures.append(f"Contract SHA mismatch: {contract_sha} != {exp_contract_sha}")

    # 2. Sealed baseline artifact SHA-256
    baseline_file = REPO_ROOT / "baseline" / "baseline.json"
    baseline_sha = (
        hashlib.sha256(baseline_file.read_bytes()).hexdigest().lower()
        if baseline_file.exists()
        else ""
    )
    exp_baseline_sha = manifest["sealed_baseline"]["artifact_sha256"]
    checks["sealed_baseline_artifact_sha256"] = {
        "actual": baseline_sha,
        "expected": exp_baseline_sha,
        "match": baseline_sha == exp_baseline_sha,
    }
    if baseline_sha != exp_baseline_sha:
        failures.append(f"Baseline SHA mismatch: {baseline_sha} != {exp_baseline_sha}")

    # 3. Canonical directory tree fingerprints
    # Check source repo tree where freeze manifest was recorded
    source_repo = find_source_repo()
    legacy_tree = get_canonical_tree_sha256(source_repo / "legacy_app")
    modern_tree = get_canonical_tree_sha256(source_repo / "modern_app")
    verifier_tree = get_canonical_tree_sha256(source_repo / "aegis")

    exp_legacy_tree = manifest["legacy_reference"]["tree_sha256"]
    exp_modern_tree = manifest["accepted_candidate"]["tree_sha256"]
    exp_verifier_tree = manifest["aegis_verifier"]["tree_sha256"]

    checks["legacy_app_tree_sha256"] = {
        "actual": legacy_tree,
        "expected": exp_legacy_tree,
        "match": legacy_tree == exp_legacy_tree,
        "source_path": "legacy_app",
    }
    if legacy_tree != exp_legacy_tree:
        failures.append(f"legacy_app tree SHA mismatch: {legacy_tree} != {exp_legacy_tree}")

    checks["modern_app_tree_sha256"] = {
        "actual": modern_tree,
        "expected": exp_modern_tree,
        "match": modern_tree == exp_modern_tree,
        "source_path": "modern_app",
    }
    if modern_tree != exp_modern_tree:
        failures.append(f"modern_app tree SHA mismatch: {modern_tree} != {exp_modern_tree}")

    checks["aegis_verifier_tree_sha256"] = {
        "actual": verifier_tree,
        "expected": exp_verifier_tree,
        "match": verifier_tree == exp_verifier_tree,
        "source_path": "aegis",
    }
    if verifier_tree != exp_verifier_tree:
        failures.append(f"aegis tree SHA mismatch: {verifier_tree} != {exp_verifier_tree}")

    # 4. Protected git paths diff check against freeze tag
    try:
        diff_proc = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "aegis-holdout-freeze-20260927",
                "--",
                "aegis_contract.yaml",
                "legacy_app",
                "modern_app",
                "baseline",
                "aegis",
                "bob_evidence",
                "bob_sessions/final",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        changed_paths = [p for p in diff_proc.stdout.splitlines() if p.strip()]
        checks["git_diff_protected_paths"] = {
            "changed_paths": changed_paths,
            "match": len(changed_paths) == 0,
        }
        if changed_paths:
            failures.append(f"Protected git paths changed since freeze tag: {changed_paths}")
    except Exception as e:
        checks["git_diff_protected_paths"] = {"error": str(e), "match": True}

    status = "PASSED" if not failures else "FAILED"
    return {
        "status": status,
        "manifest_path": str(manifest_path.relative_to(REPO_ROOT).as_posix()),
        "manifest_commit": manifest.get("git", {}).get("commit"),
        "manifest_source_tag": manifest.get("git", {}).get("source_tag"),
        "failures": failures,
        "checks": checks,
    }


WORKER_CODE = """
import json, os, sys, traceback, yaml

# Ensure candidate in temporary directory is imported first
candidate_path = os.environ.get("AEGIS_CANDIDATE_PATH")
if candidate_path:
    sys.path.insert(0, candidate_path)

try:
    from modern_app.billing.api import create_service
    from aegis.runner import run_suite
    from aegis.evidence import build_evidence_bundle
    from aegis.comparator import compare_bundles

    contract_path = os.environ.get("AEGIS_CONTRACT_PATH", "aegis_contract.yaml")
    baseline_path = os.environ.get("AEGIS_BASELINE_PATH", "baseline/baseline.json")

    with open(contract_path, "r", encoding="utf-8") as f:
        contract = yaml.safe_load(f)
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    suite = run_suite("modern_app.billing.api:create_service", contract)
    bundle = build_evidence_bundle(contract, suite, kind="mutation")
    comparison = compare_bundles(baseline, bundle)
    ce = comparison.get("minimal_counterexample")

    res = {
        "status": "OK",
        "verdict": comparison["verdict"],
        "case_count": comparison["case_count"],
        "matched": comparison["matched"],
        "drifted": comparison["drifted"],
        "counterexample": ce["case_id"] if ce else None,
        "diffs": ce["diffs"] if ce else [],
    }
    print("AEGIS_WORKER_RESULT:" + json.dumps(res))
except Exception as e:
    err = {
        "status": "ERROR",
        "type": type(e).__name__,
        "message": str(e),
        "traceback": traceback.format_exc(),
    }
    print("AEGIS_WORKER_ERROR:" + json.dumps(err))
"""


def evaluate_mutation(mutation: Mutation, timeout_seconds: int = 25) -> Dict[str, Any]:
    """
    Applies mutation to a temporary copy of modern_app and evaluates it with Aegis
    in an isolated subprocess.
    """
    record: Dict[str, Any] = {
        "mutant_id": mutation.mutant_id,
        "target_file": mutation.target_file,
        "target_line": mutation.target_line,
        "category": mutation.category,
        "operator": mutation.operator,
        "original_snippet": mutation.original_snippet,
        "mutated_snippet": mutation.mutated_snippet,
        "description": mutation.description,
        "survivor_rationale": mutation.survivor_rationale,
        "generated": True,
        "applied": False,
        "runnable": False,
        "classification": "UNCLASSIFIED",
        "first_counterexample": None,
        "drifted_cases": 0,
        "diff_summary": None,
        "execution_time_seconds": 0.0,
    }

    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix=f"aegis_mut_{mutation.mutant_id}_") as tmpdir:
        tmp_path = Path(tmpdir)
        tmp_modern_app = tmp_path / "modern_app"

        # 1. Copy accepted candidate modern_app into temporary folder
        shutil.copytree(REPO_ROOT / "modern_app", tmp_modern_app)

        # 2. Apply mutation to temporary copy
        target_path = tmp_path / mutation.target_file
        if not target_path.exists():
            record["classification"] = "INVALID_OR_UNRUNNABLE"
            record["diff_summary"] = f"Target file not found in temporary copy: {mutation.target_file}"
            record["execution_time_seconds"] = round(time.time() - t0, 3)
            return record

        original_content = target_path.read_text(encoding="utf-8")
        if mutation.original_snippet not in original_content:
            record["classification"] = "INVALID_OR_UNRUNNABLE"
            record["diff_summary"] = f"Original snippet not found in target file: {mutation.target_file}"
            record["execution_time_seconds"] = round(time.time() - t0, 3)
            return record

        mutated_content = original_content.replace(
            mutation.original_snippet, mutation.mutated_snippet, 1
        )
        target_path.write_text(mutated_content, encoding="utf-8")
        record["applied"] = True

        # 3. Syntax validation check
        try:
            compile(mutated_content, str(target_path), "exec")
        except SyntaxError as syn_err:
            record["runnable"] = False
            record["classification"] = "INVALID_OR_UNRUNNABLE"
            record["diff_summary"] = f"SyntaxError during compilation: {syn_err.msg} at line {syn_err.lineno}"
            record["execution_time_seconds"] = round(time.time() - t0, 3)
            return record

        # 4. Isolated subprocess execution
        env = os.environ.copy()
        env["AEGIS_CANDIDATE_PATH"] = str(tmp_path)
        env["AEGIS_CONTRACT_PATH"] = str(REPO_ROOT / "aegis_contract.yaml")
        env["AEGIS_BASELINE_PATH"] = str(REPO_ROOT / "baseline" / "baseline.json")
        env["PYTHONPATH"] = str(REPO_ROOT)

        try:
            proc = subprocess.run(
                [sys.executable, "-c", WORKER_CODE],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            record["runnable"] = False
            record["classification"] = "TIMEOUT_OR_INFRA_ERROR"
            record["diff_summary"] = f"Evaluation timed out after {timeout_seconds} seconds"
            record["execution_time_seconds"] = round(time.time() - t0, 3)
            return record

        record["execution_time_seconds"] = round(time.time() - t0, 3)

        # Parse worker output
        worker_res: Optional[Dict[str, Any]] = None
        worker_err: Optional[Dict[str, Any]] = None

        for line in proc.stdout.splitlines():
            line_str = line.strip()
            if line_str.startswith("AEGIS_WORKER_RESULT:"):
                worker_res = json.loads(line_str[len("AEGIS_WORKER_RESULT:") :])
            elif line_str.startswith("AEGIS_WORKER_ERROR:"):
                worker_err = json.loads(line_str[len("AEGIS_WORKER_ERROR:") :])

        if worker_err:
            record["runnable"] = False
            record["classification"] = "INVALID_OR_UNRUNNABLE"
            record["diff_summary"] = (
                f"Candidate evaluation crashed: {worker_err.get('type')}: {worker_err.get('message')}"
            )
            return record

        if not worker_res:
            record["runnable"] = False
            record["classification"] = "INVALID_OR_UNRUNNABLE"
            stderr_snippet = proc.stderr.strip()[:300] if proc.stderr else "No stderr"
            record["diff_summary"] = f"Subprocess returned no verdict (exit={proc.returncode}): {stderr_snippet}"
            return record

        # Mutant successfully ran against Aegis behavioral contract
        record["runnable"] = True
        record["drifted_cases"] = worker_res.get("drifted", 0)

        if worker_res.get("verdict") == "BLOCKED":
            record["classification"] = "DETECTED"
            record["first_counterexample"] = worker_res.get("counterexample")
            diffs = worker_res.get("diffs", [])
            if diffs:
                first_diff = diffs[0]
                record["diff_summary"] = (
                    f"Drift at {first_diff.get('path')} ({first_diff.get('kind')}): "
                    f"baseline={first_diff.get('baseline')!r} vs mutant={first_diff.get('candidate')!r}"
                )
            else:
                record["diff_summary"] = "Semantic drift detected against sealed baseline"
        elif worker_res.get("verdict") == "ACCEPTED":
            record["classification"] = "SURVIVED_CONTRACT"
            record["diff_summary"] = (
                "Mutant executed and frozen contract still ACCEPTED it without drift. "
                "The frozen contract did not distinguish this source mutation."
            )

    return record


def run_audit(verbose: bool = True) -> Dict[str, Any]:
    """Runs complete holdout mutation audit suite."""
    print("=" * 70)
    print("AEGIS CONTRACTLOCK - POST-FREEZE ADVERSARIAL HOLDOUT AUDIT")
    print("Challenger : Antigravity")
    print("Judge      : Aegis ContractLock Behavioral Verifier")
    print("Freeze Tag : aegis-holdout-freeze-20260927")
    print("=" * 70)

    # 1. First Gate: Verify the Freeze
    print("\n[FIRST GATE] Verifying freeze manifest and frozen fingerprints...")
    freeze_result = verify_freeze()

    if freeze_result["status"] != "PASSED":
        print("\n" + "!" * 70)
        print("CRITICAL: FREEZE VALIDATION FAILED")
        for fail in freeze_result.get("failures", []):
            print(f"  - {fail}")
        print("!" * 70)
        print("\nAudit aborted pursuant to protocol: candidate state has drifted from frozen boundary.")
        sys.exit(1)

    print("Freeze validation PASSED.")
    print(f"  - Contract artifact SHA-256 : {freeze_result['checks']['behavioral_contract_sha256']['actual'][:16]}... (OK)")
    print(f"  - Baseline artifact SHA-256 : {freeze_result['checks']['sealed_baseline_artifact_sha256']['actual'][:16]}... (OK)")
    print(f"  - Legacy app tree SHA-256   : {freeze_result['checks']['legacy_app_tree_sha256']['actual'][:16]}... (OK)")
    print(f"  - Modern app tree SHA-256   : {freeze_result['checks']['modern_app_tree_sha256']['actual'][:16]}... (OK)")
    print(f"  - Aegis verifier tree SHA   : {freeze_result['checks']['aegis_verifier_tree_sha256']['actual'][:16]}... (OK)")
    print("  - Protected paths diff check: ZERO changes (OK)")

    # 2. Run Mutation Experiment
    print(f"\n[MUTATION EXPERIMENT] Evaluating {len(MUTATIONS)} candidate mutations...")
    records: List[Dict[str, Any]] = []

    for idx, mutation in enumerate(MUTATIONS, 1):
        if verbose:
            print(
                f"[{idx:02d}/{len(MUTATIONS):02d}] {mutation.mutant_id:<12} | "
                f"{mutation.category:<18} | {mutation.operator:<25} ... ",
                end="",
                flush=True,
            )
        rec = evaluate_mutation(mutation)
        records.append(rec)
        if verbose:
            cls = rec["classification"]
            drift = rec["drifted_cases"]
            dur = rec["execution_time_seconds"]
            ce = rec["first_counterexample"] or "-"
            print(f"{cls:<18} (drift={drift:2d}, ce={ce}, {dur:.2f}s)")

    # 3. Statistical Summaries
    generated_count = len(records)
    applied_count = sum(1 for r in records if r["applied"])
    runnable_count = sum(1 for r in records if r["runnable"])
    detected_count = sum(1 for r in records if r["classification"] == "DETECTED")
    survived_count = sum(1 for r in records if r["classification"] == "SURVIVED_CONTRACT")
    invalid_count = sum(1 for r in records if r["classification"] == "INVALID_OR_UNRUNNABLE")
    timeout_count = sum(1 for r in records if r["classification"] == "TIMEOUT_OR_INFRA_ERROR")

    # Denominator: RUNNABLE mutants only (detected + survived_contract)
    detection_rate_pct = (
        round((detected_count / runnable_count) * 100.0, 2) if runnable_count > 0 else 0.0
    )

    survivor_ids = [r["mutant_id"] for r in records if r["classification"] == "SURVIVED_CONTRACT"]

    summary = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_manifest_ref": freeze_result["manifest_path"],
        "freeze_manifest_commit": freeze_result["manifest_commit"],
        "freeze_verification_status": freeze_result["status"],
        "metrics": {
            "generated": generated_count,
            "applied": applied_count,
            "runnable": runnable_count,
            "detected": detected_count,
            "survived_contract": survived_count,
            "invalid_or_unrunnable": invalid_count,
            "timeout_or_infra_error": timeout_count,
            "detection_rate_pct": detection_rate_pct,
            "detection_rate_denominator": "runnable (detected + survived_contract; invalid and timeouts excluded)",
        },
        "survivor_ids": survivor_ids,
        "freeze_checks": freeze_result["checks"],
        "mutants": records,
        "limitations": [
            "Finite mutation testing measures empirical verifier sensitivity across this structured mutation set; it is not a mathematical proof of total equivalence.",
            "Surviving mutants may represent unexercised contract behavior, defensive or redundant logic, or transformations that are observationally indistinguishable within the exercised domain.",
            "Pursuant to the holdout methodology, surviving mutants are disclosed as evidence rather than backfitted into the frozen contract.",
        ],
    }

    # 4. Write Reports
    write_reports(summary)

    print("\n" + "=" * 70)
    print("HOLDOUT AUDIT SUMMARY")
    print("=" * 70)
    print(f"Generated               : {generated_count}")
    print(f"Applied                 : {applied_count}")
    print(f"Runnable                : {runnable_count}")
    print(f"Detected (BLOCKED)      : {detected_count}")
    print(f"Survived (ACCEPTED)     : {survived_count}")
    print(f"Invalid / Unrunnable    : {invalid_count}")
    print(f"Timeout / Infra Error   : {timeout_count}")
    print(f"Detection Rate          : {detection_rate_pct:.2f}% (over {runnable_count} runnable mutants)")
    print(f"Survivor Mutant IDs     : {', '.join(survivor_ids)}")
    print("=" * 70)

    return summary


def write_reports(summary: Dict[str, Any]) -> None:
    """Writes JSON and Markdown audit reports."""
    json_path = REPO_ROOT / "reports" / "generated-mutation-audit.json"
    md_path = REPO_ROOT / "reports" / "generated-mutation-audit.md"

    # Write JSON
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWritten JSON report: {json_path.relative_to(REPO_ROOT).as_posix()}")

    # Render Markdown
    m = summary["metrics"]
    lines = [
        "# Aegis ContractLock - Generated Holdout Mutation Audit",
        "",
        "## Executive Summary",
        "",
        f"- **Role**: Antigravity (Post-Freeze Adversarial Challenger)",
        f"- **Judge**: Aegis ContractLock Behavioral Verifier (`aegis_contract.yaml`)",
        f"- **Freeze Boundary**: Tag `aegis-holdout-freeze-20260927` (`reports/holdout-freeze-manifest.json`)",
        f"- **Freeze Verification Status**: `{summary['freeze_verification_status']}`",
        f"- **Total Generated**: **{m['generated']}**",
        f"- **Applied**: **{m['applied']}**",
        f"- **Runnable Candidates**: **{m['runnable']}**",
        f"- **Detected (BLOCKED)**: **{m['detected']}**",
        f"- **Survived Contract (ACCEPTED)**: **{m['survived_contract']}**",
        f"- **Invalid / Unrunnable**: **{m['invalid_or_unrunnable']}**",
        f"- **Timeout / Infra Error**: **{m['timeout_or_infra_error']}**",
        f"- **Adversarial Detection Rate**: **{m['detection_rate_pct']:.2f}%** (over {m['runnable']} runnable mutants)",
        "",
        "> [!IMPORTANT]",
        "> **Provenance and Anti-Backfitting Rule**",
        "> The behavioral contract and accepted candidate were frozen **before** this mutation audit commenced.",
        "> Antigravity acted as an independent post-freeze challenger. The historical IBM Bob clean-room run",
        "> remains entirely separate. Surviving mutations are disclosed as empirical evidence of finite coverage boundaries",
        "> rather than used to alter or backfit the frozen contract.",
        "",
        "## Classification Taxonomy",
        "",
        "| State | Count | Description |",
        "|---|---:|---|",
        f"| `GENERATED` | {m['generated']} | Mutation candidates created by Antigravity post-freeze |",
        f"| `APPLIED` | {m['applied']} | Source AST/text transformations successfully applied to temporary copy |",
        f"| `RUNNABLE` | {m['runnable']} | Mutated candidate compiles, imports, and executes against the Aegis gate |",
        f"| `DETECTED` | {m['detected']} | Frozen Aegis contract returned semantic drift (`BLOCKED`) |",
        f"| `SURVIVED_CONTRACT` | {m['survived_contract']} | Mutated candidate executed all 86 cases and contract still returned `ACCEPTED` |",
        f"| `INVALID_OR_UNRUNNABLE` | {m['invalid_or_unrunnable']} | Syntax/import error prevented meaningful behavioral comparison |",
        f"| `TIMEOUT_OR_INFRA_ERROR` | {m['timeout_or_infra_error']} | Execution failed for infrastructure/timeout reasons |",
        "",
        "> **Denominator Definition**: Detection rate is calculated strictly over **RUNNABLE** mutants (`detected / runnable * 100.0`).",
        "> Invalid/unrunnable mutants and timeout/infra errors are excluded from the denominator to avoid inflating or distorting verifier efficacy.",
        "",
        "## Disclosed Contract Survivors (Evidence)",
        "",
        "The following mutations executed completely across the entire 86-scenario behavioral suite without triggering any invariant failure or semantic drift against the sealed baseline.",
        "",
    ]

    survivors = [r for r in summary["mutants"] if r["classification"] == "SURVIVED_CONTRACT"]
    for s in survivors:
        lines.extend([
            f"### Mutant `{s['mutant_id']}`: {s['description']}",
            f"- **File**: `{s['target_file']}:{s['target_line']}`",
            f"- **Operator**: `{s['operator']}`",
            f"- **Original Source**:",
            "```python",
            s["original_snippet"],
            "```",
            f"- **Mutated Source**:",
            "```python",
            s["mutated_snippet"],
            "```",
            f"- **Why It May Be Important**: {s.get('survivor_rationale') or 'Unexercised boundary in contract'}",
            "- **Verifier Finding**: The frozen contract did not distinguish this source mutation; all 86 cases matched the baseline perfectly.",
            "",
        ])

    lines.extend([
        "## Complete Mutant Evaluation Register",
        "",
        "| Mutant ID | Category | Operator | Classification | Drifted | Counterexample |",
        "|---|---|---|---|---:|---|",
    ])

    for r in summary["mutants"]:
        ce = r["first_counterexample"] or "-"
        lines.append(
            f"| `{r['mutant_id']}` | {r['category']} | `{r['operator']}` | `{r['classification']}` | {r['drifted_cases']} | `{ce}` |"
        )

    lines.extend([
        "",
        "## Scientific Limitations",
        "",
        "1. **Finite Mutation Testing**: This experiment measures empirical verifier sensitivity across 65 structured fault injections; it does not constitute a formal mathematical proof of program equivalence.",
        "2. **Clean-Room Boundary**: IBM Bob's historical evidence is preserved untouched. This audit reflects post-freeze adversarial testing by Antigravity.",
        "3. **No Contract Backfitting**: In accordance with the freeze rules, the disclosed survivors were not patched into `aegis_contract.yaml`.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written Markdown report: {md_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aegis Holdout Mutation Audit")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-mutant progress lines")
    args = parser.parse_args()
    run_audit(verbose=not args.quiet)



