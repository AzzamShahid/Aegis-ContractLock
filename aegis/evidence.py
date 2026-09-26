from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .util import ensure_parent, fingerprint


def build_evidence_bundle(
    contract: dict[str, Any],
    suite: dict[str, Any],
    *,
    kind: str,
) -> dict[str, Any]:
    payload = {
        "aegis_evidence_version": "1.0",
        "kind": kind,
        "contract_version": contract["version"],
        "factory": suite["factory"],
        "case_count": suite["case_count"],
        "cases": suite["cases"],
    }
    # created_at is metadata and deliberately excluded from the evidence hash.
    return {
        **payload,
        "evidence_sha256": fingerprint(payload),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def write_json(path: str | Path, value: Any) -> Path:
    path = Path(path)
    ensure_parent(path)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
