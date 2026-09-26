from __future__ import annotations

import importlib
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def import_symbol(spec: str):
    if ":" not in spec:
        raise ValueError(f"Expected import spec 'module:symbol', got {spec!r}")
    module_name, symbol_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)


def deep_get(value: Any, path: str) -> Any:
    if path in {"", "."}:
        return value
    current = value
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def deep_set(value: Any, path: str, new_value: Any) -> Any:
    parts = path.split(".")
    target = value
    for part in parts[:-1]:
        if isinstance(target, list):
            target = target[int(part)]
        else:
            target = target[part]
    last = parts[-1]
    if isinstance(target, list):
        target[int(last)] = new_value
    else:
        target[last] = new_value
    return value


def resolve_refs(value: Any, context: dict[str, Any]) -> Any:
    """
    Resolve strings such as:
      $steps.invoice.result.invoice_id
    against the current case context.
    """
    if isinstance(value, str) and value.startswith("$"):
        return deepcopy(deep_get(context, value[1:]))
    if isinstance(value, list):
        return [resolve_refs(v, context) for v in value]
    if isinstance(value, dict):
        return {k: resolve_refs(v, context) for k, v in value.items()}
    return deepcopy(value)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
