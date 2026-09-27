from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ContractError(ValueError):
    pass


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a mapping")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def load_contract(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError("Contract root must be a mapping")

    for key in ("version", "subject", "cases"):
        if key not in data:
            raise ContractError(f"Missing required contract key: {key}")

    subject = _require_mapping(data["subject"], "subject")
    for key in ("legacy_factory", "candidate_factory"):
        if key not in subject:
            raise ContractError(f"Missing subject.{key}")
        _require_nonempty_string(subject[key], f"subject.{key}")

    cases = data["cases"]
    if not isinstance(cases, list) or not cases:
        raise ContractError("Contract requires at least one case")

    seen_cases: set[str] = set()
    for index, raw_case in enumerate(cases):
        case = _require_mapping(raw_case, f"cases[{index}]")
        case_id = _require_nonempty_string(case.get("id"), f"cases[{index}].id")
        if case_id in seen_cases:
            raise ContractError(f"Invalid/duplicate case id: {case_id!r}")
        seen_cases.add(case_id)

        steps = case.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ContractError(f"Case {case_id} requires at least one step")

        seen_steps: set[str] = set()
        for step_index, raw_step in enumerate(steps):
            step = _require_mapping(raw_step, f"Case {case_id} steps[{step_index}]")
            step_id = _require_nonempty_string(
                step.get("id"),
                f"Case {case_id} steps[{step_index}].id",
            )
            if step_id in seen_steps:
                raise ContractError(
                    f"Case {case_id}: invalid/duplicate step id {step_id!r}"
                )
            seen_steps.add(step_id)

            if "operation" not in step or "input" not in step:
                raise ContractError(
                    f"Case {case_id}, step {step_id}: operation/input required"
                )
            _require_nonempty_string(
                step["operation"],
                f"Case {case_id}, step {step_id}.operation",
            )
            if not isinstance(step["input"], dict):
                raise ContractError(
                    f"Case {case_id}, step {step_id}.input must be a mapping"
                )

    return data
