"""Centralized audit event logging with monotonic integer sequencing."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


class AuditLog:
    def __init__(self) -> None:
        self._audit: List[Dict[str, Any]] = []
        self._audit_seq = 0

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        self._audit_seq += 1
        self._audit.append(
            {
                "seq": self._audit_seq,
                "event": event_type,
                "data": deepcopy(data),
            }
        )

    def snapshot(self) -> List[Dict[str, Any]]:
        return deepcopy(self._audit)
