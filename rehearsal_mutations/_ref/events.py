from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, List

class AuditLog:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._seq = 0

    def emit(self, event: str, data: Dict[str, Any]) -> None:
        self._seq += 1
        self._events.append({"seq": self._seq, "event": event, "data": deepcopy(data)})

    def snapshot(self) -> List[Dict[str, Any]]:
        return deepcopy(self._events)
