"""In-memory persistence for invoices, refunds, ledger, and idempotency caching."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from .errors import InvoiceNotFoundError, RefundAlreadyProcessedError


class BillingStorage:
    def __init__(self) -> None:
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._refunds: Dict[str, Dict[str, Any]] = {}
        self._ledger: List[Dict[str, Any]] = []
        self._idempotency: Dict[str, Dict[str, Any]] = {}

    def get_idempotent(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._idempotency:
            return deepcopy(self._idempotency[key])
        return None

    def save_idempotent(self, key: str, data: Dict[str, Any]) -> None:
        self._idempotency[key] = deepcopy(data)

    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        if invoice_id in self._invoices:
            return deepcopy(self._invoices[invoice_id])
        return None

    def save_invoice(self, invoice: Dict[str, Any]) -> None:
        self._invoices[invoice["invoice_id"]] = deepcopy(invoice)

    def update_invoice_status(self, invoice_id: str, status: str) -> None:
        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(invoice_id)
        self._invoices[invoice_id]["status"] = status

    def has_approved_refund(self, invoice_id: str) -> bool:
        return any(
            refund.get("invoice_id") == invoice_id and refund.get("status") == "APPROVED"
            for refund in self._refunds.values()
        )

    def save_refund(self, refund: Dict[str, Any]) -> None:
        self._refunds[refund["refund_id"]] = deepcopy(refund)

    def record_ledger_debit(self, invoice_id: str, amount_s: str) -> None:
        self._ledger.append(
            {
                "type": "INVOICE_CHARGE",
                "invoice_id": invoice_id,
                "amount": amount_s,
                "direction": "DEBIT",
            }
        )

    def record_ledger_credit(
        self, invoice_id: str, refund_id: str, amount_s: str
    ) -> None:
        self._ledger.append(
            {
                "type": "REFUND",
                "invoice_id": invoice_id,
                "refund_id": refund_id,
                "amount": amount_s,
                "direction": "CREDIT",
            }
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "invoices": [deepcopy(self._invoices[k]) for k in sorted(self._invoices)],
            "refunds": [deepcopy(self._refunds[k]) for k in sorted(self._refunds)],
            "ledger": deepcopy(self._ledger),
        }
