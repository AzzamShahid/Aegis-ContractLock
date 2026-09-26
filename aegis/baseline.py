from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence import build_evidence_bundle, write_json
from .runner import run_suite


def record_baseline(
    contract: dict[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    suite = run_suite(contract["subject"]["legacy_factory"], contract)
    bundle = build_evidence_bundle(contract, suite, kind="baseline")
    write_json(output_path, bundle)
    return bundle
