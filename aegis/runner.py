from __future__ import annotations

from copy import deepcopy
from typing import Any

from .invariants import check_invariants
from .util import fingerprint, import_symbol, resolve_refs


def _normalize_exception(exc: Exception) -> dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "code": getattr(exc, "code", type(exc).__name__),
        "message": str(exc),
    }


def _audit_delta(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    before_audit = before.get("audit", [])
    after_audit = after.get("audit", [])
    if len(after_audit) < len(before_audit):
        return [{"event": "__AEGIS_STATE_ERROR__", "data": {"reason": "audit shrank"}}]
    return deepcopy(after_audit[len(before_audit):])


def run_case(factory_spec: str, case_spec: dict[str, Any]) -> dict[str, Any]:
    factory = import_symbol(factory_spec)
    service = factory()

    if not hasattr(service, "execute") or not hasattr(service, "snapshot_state"):
        raise TypeError(
            f"{factory_spec} must return an object implementing execute() and snapshot_state()"
        )

    evidence: dict[str, Any] = {
        "case_id": case_spec["id"],
        "description": case_spec.get("description", ""),
        "steps": [],
        "steps_by_id": {},
    }

    context: dict[str, Any] = {"steps": {}}

    for step_spec in case_spec["steps"]:
        step_id = step_spec["id"]
        operation = step_spec["operation"]
        resolved_input = resolve_refs(step_spec["input"], context)

        state_before = service.snapshot_state()
        result = None
        exception = None

        try:
            result = service.execute(operation, deepcopy(resolved_input))
        except Exception as exc:
            exception = _normalize_exception(exc)

        state_after = service.snapshot_state()
        events_delta = _audit_delta(state_before, state_after)

        step_evidence = {
            "id": step_id,
            "operation": operation,
            "input": resolved_input,
            "result": deepcopy(result),
            "exception": exception,
            "state_before": state_before,
            "state_after": state_after,
            "events_delta": events_delta,
        }
        step_evidence["fingerprint"] = fingerprint(
            {
                "result": step_evidence["result"],
                "exception": step_evidence["exception"],
                "state_after": step_evidence["state_after"],
                "events_delta": step_evidence["events_delta"],
            }
        )

        evidence["steps"].append(step_evidence)
        evidence["steps_by_id"][step_id] = step_evidence
        context["steps"][step_id] = step_evidence

    evidence["invariant_failures"] = check_invariants(case_spec, evidence)
    evidence["final_state"] = service.snapshot_state()
    evidence["case_fingerprint"] = fingerprint(
        {
            "steps": evidence["steps"],
            "final_state": evidence["final_state"],
            "invariant_failures": evidence["invariant_failures"],
        }
    )
    return evidence


def run_suite(factory_spec: str, contract: dict[str, Any]) -> dict[str, Any]:
    cases = [run_case(factory_spec, case) for case in contract["cases"]]
    return {
        "factory": factory_spec,
        "case_count": len(cases),
        "cases": cases,
    }
