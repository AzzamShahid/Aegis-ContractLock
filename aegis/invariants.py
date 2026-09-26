from __future__ import annotations

from decimal import Decimal
from typing import Any

from .util import deep_get


class InvariantFailure:
    def __init__(self, invariant_id: str, message: str):
        self.invariant_id = invariant_id
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"invariant_id": self.invariant_id, "message": self.message}


def _step(case_evidence: dict[str, Any], step_id: str) -> dict[str, Any]:
    return case_evidence["steps_by_id"][step_id]


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def check_invariants(
    case_spec: dict[str, Any],
    case_evidence: dict[str, Any],
) -> list[dict[str, str]]:
    failures: list[InvariantFailure] = []

    for inv in case_spec.get("invariants", []):
        iid = inv["id"]
        kind = inv["type"]
        step = _step(case_evidence, inv["step"]) if "step" in inv else None

        try:
            if kind == "field_equals":
                actual = deep_get(step, inv["path"])
                expected = inv["value"]
                if actual != expected:
                    failures.append(
                        InvariantFailure(iid, f"{inv['path']} expected {expected!r}, got {actual!r}")
                    )

            elif kind == "field_decimal_gte":
                actual = _decimal(deep_get(step, inv["path"]))
                expected = _decimal(inv["value"])
                if actual < expected:
                    failures.append(
                        InvariantFailure(iid, f"{inv['path']} expected >= {expected}, got {actual}")
                    )

            elif kind == "invoice_total_equation":
                result = step["result"]
                if result is None:
                    raise ValueError("step has no result")
                lhs = _decimal(result["grand_total"])
                rhs = (
                    _decimal(result["subtotal"])
                    - _decimal(result["discount"])
                    + _decimal(result["shipping"])
                    + _decimal(result["tax"])
                    + _decimal(result["service_fee"])
                )
                if lhs != rhs:
                    failures.append(
                        InvariantFailure(iid, f"grand_total {lhs} != component sum {rhs}")
                    )

            elif kind == "event_present":
                event_name = inv["event"]
                events = step["events_delta"]
                if not any(e.get("event") == event_name for e in events):
                    failures.append(
                        InvariantFailure(iid, f"Missing event {event_name}")
                    )

            elif kind == "state_table_delta":
                table = inv["table"]
                expected = int(inv["delta"])
                before_n = len(step["state_before"].get(table, []))
                after_n = len(step["state_after"].get(table, []))
                actual = after_n - before_n
                if actual != expected:
                    failures.append(
                        InvariantFailure(
                            iid,
                            f"state table {table} delta expected {expected}, got {actual}",
                        )
                    )

            elif kind == "no_exception":
                if step["exception"] is not None:
                    failures.append(
                        InvariantFailure(
                            iid, f"Unexpected exception: {step['exception']}"
                        )
                    )

            elif kind == "exception_code":
                exc = step["exception"]
                expected = inv["code"]
                actual = None if exc is None else exc.get("code")
                if actual != expected:
                    failures.append(
                        InvariantFailure(
                            iid, f"exception code expected {expected!r}, got {actual!r}"
                        )
                    )

            elif kind == "refund_not_above_invoice":
                refund_step = _step(case_evidence, inv["step"])
                invoice_step = _step(case_evidence, inv["invoice_step"])
                refund = _decimal(refund_step["result"]["refund_amount"])
                invoice = _decimal(invoice_step["result"]["grand_total"])
                if refund > invoice:
                    failures.append(
                        InvariantFailure(
                            iid, f"refund {refund} exceeds invoice total {invoice}"
                        )
                    )

            elif kind == "same_result":
                a = _step(case_evidence, inv["step"])
                b = _step(case_evidence, inv["other_step"])
                if a["result"] != b["result"]:
                    failures.append(
                        InvariantFailure(iid, "Repeated operation returned a different result")
                    )

            elif kind == "state_unchanged_between_steps":
                a = _step(case_evidence, inv["step"])
                b = _step(case_evidence, inv["other_step"])
                if a["state_after"] != b["state_after"]:
                    failures.append(
                        InvariantFailure(iid, "Observable state changed on idempotent retry")
                    )

            elif kind == "no_new_events":
                if len(step["events_delta"]) != 0:
                    failures.append(
                        InvariantFailure(
                            iid,
                            f"Expected no new events, got {len(step['events_delta'])}",
                        )
                    )

            else:
                failures.append(InvariantFailure(iid, f"Unknown invariant type: {kind}"))

        except Exception as exc:
            failures.append(
                InvariantFailure(iid, f"Invariant evaluation error: {type(exc).__name__}: {exc}")
            )

    return [f.to_dict() for f in failures]
