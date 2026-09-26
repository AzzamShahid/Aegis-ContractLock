from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ContractError(ValueError):
    pass


def load_contract(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError("Contract root must be a mapping")

    for key in ("version", "subject", "cases"):
        if key not in data:
            raise ContractError(f"Missing required contract key: {key}")

    subject = data["subject"]
    for key in ("legacy_factory", "candidate_factory"):
        if key not in subject:
            raise ContractError(f"Missing subject.{key}")

    cases = data["cases"]
    if not isinstance(cases, list) or not cases:
        raise ContractError("Contract requires at least one case")

    seen_cases: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_cases:
            raise ContractError(f"Invalid/duplicate case id: {case_id!r}")
        seen_cases.add(case_id)
        steps = case.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ContractError(f"Case {case_id} requires at least one step")
        seen_steps: set[str] = set()
        for step in steps:
            step_id = step.get("id")
            if not step_id or step_id in seen_steps:
                raise ContractError(
                    f"Case {case_id}: invalid/duplicate step id {step_id!r}"
                )
            seen_steps.add(step_id)
            if "operation" not in step or "input" not in step:
                raise ContractError(
                    f"Case {case_id}, step {step_id}: operation/input required"
                )

    return data
