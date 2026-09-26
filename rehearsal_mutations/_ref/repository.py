from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, List, Optional

class Repository:
    def __init__(self) -> None:
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._refunds: Dict[str, Dict[str, Any]] = {}
        self._ledger: List[Dict[str, Any]] = []
        self._idempotency: Dict[str, Dict[str, Any]] = {}

    def save_invoice(self, invoice_id: str, invoice: Dict[str, Any]) -> None:
        self._invoices[invoice_id] = deepcopy(invoice)

    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        value = self._invoices.get(invoice_id)
        return deepcopy(value) if value is not None else None

    def all_invoices(self) -> List[Dict[str, Any]]:
        return [deepcopy(self._invoices[k]) for k in sorted(self._invoices)]

    def save_refund(self, refund_id: str, refund: Dict[str, Any]) -> None:
        self._refunds[refund_id] = deepcopy(refund)

    def all_refunds(self) -> List[Dict[str, Any]]:
        return [deepcopy(self._refunds[k]) for k in sorted(self._refunds)]

    def add_ledger(self, entry: Dict[str, Any]) -> None:
        self._ledger.append(deepcopy(entry))

    def ledger(self) -> List[Dict[str, Any]]:
        return deepcopy(self._ledger)

    def get_idempotency(self, key: str) -> Optional[Dict[str, Any]]:
        value = self._idempotency.get(key)
        return deepcopy(value) if value is not None else None

    def save_idempotency(self, key: str, value: Dict[str, Any]) -> None:
        self._idempotency[key] = deepcopy(value)
