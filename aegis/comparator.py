from __future__ import annotations

from typing import Any


def _diff(a: Any, b: Any, path: str = "$") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    if type(a) is not type(b):
        return [{"path": path, "kind": "type", "baseline": a, "candidate": b}]

    if isinstance(a, dict):
        keys = list(a.keys()) + [key for key in b.keys() if key not in a]
        for key in keys:
            p = f"{path}.{key}"
            if key not in a:
                out.append({"path": p, "kind": "added", "baseline": None, "candidate": b[key]})
            elif key not in b:
                out.append({"path": p, "kind": "removed", "baseline": a[key], "candidate": None})
            else:
                out.extend(_diff(a[key], b[key], p))
        return out

    if isinstance(a, list):
        if len(a) != len(b):
            out.append(
                {
                    "path": path,
                    "kind": "length",
                    "baseline": len(a),
                    "candidate": len(b),
                }
            )
        for idx, (left, right) in enumerate(zip(a, b)):
            out.extend(_diff(left, right, f"{path}[{idx}]"))
        return out

    if a != b:
        out.append({"path": path, "kind": "value", "baseline": a, "candidate": b})

    return out


def compare_bundles(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    baseline_cases = {c["case_id"]: c for c in baseline["cases"]}
    candidate_cases = {c["case_id"]: c for c in candidate["cases"]}

    case_results: list[dict[str, Any]] = []
    all_case_ids = sorted(set(baseline_cases) | set(candidate_cases))

    for case_id in all_case_ids:
        if case_id not in baseline_cases:
            case_results.append(
                {
                    "case_id": case_id,
                    "status": "DRIFT",
                    "diffs": [{"path": "$", "kind": "unexpected_case"}],
                }
            )
            continue
        if case_id not in candidate_cases:
            case_results.append(
                {
                    "case_id": case_id,
                    "status": "DRIFT",
                    "diffs": [{"path": "$", "kind": "missing_case"}],
                }
            )
            continue

        # Fingerprints/metadata are not compared. We compare the semantically
        # meaningful evidence fields directly.
        left = baseline_cases[case_id]
        right = candidate_cases[case_id]

        left_cmp = {
            "steps": [
                {
                    "id": s["id"],
                    "operation": s["operation"],
                    "input": s["input"],
                    "result": s["result"],
                    "exception": s["exception"],
                    "state_before": s["state_before"],
                    "state_after": s["state_after"],
                    "events_delta": s["events_delta"],
                }
                for s in left["steps"]
            ],
            "invariant_failures": left["invariant_failures"],
            "final_state": left["final_state"],
        }
        right_cmp = {
            "steps": [
                {
                    "id": s["id"],
                    "operation": s["operation"],
                    "input": s["input"],
                    "result": s["result"],
                    "exception": s["exception"],
                    "state_before": s["state_before"],
                    "state_after": s["state_after"],
                    "events_delta": s["events_delta"],
                }
                for s in right["steps"]
            ],
            "invariant_failures": right["invariant_failures"],
            "final_state": right["final_state"],
        }

        diffs = _diff(left_cmp, right_cmp)
        case_results.append(
            {
                "case_id": case_id,
                "status": "MATCH" if not diffs else "DRIFT",
                "diffs": diffs,
            }
        )

    drifted = [r for r in case_results if r["status"] == "DRIFT"]
    return {
        "verdict": "ACCEPTED" if not drifted else "BLOCKED",
        "case_count": len(case_results),
        "matched": len(case_results) - len(drifted),
        "drifted": len(drifted),
        "cases": case_results,
        "minimal_counterexample": drifted[0] if drifted else None,
    }
