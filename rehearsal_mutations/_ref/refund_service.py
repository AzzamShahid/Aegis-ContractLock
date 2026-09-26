from __future__ import annotations
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
from typing import Any, Dict
from .events import AuditLog
from .models import InvoiceNotFoundError, RefundAlreadyProcessedError, ValidationError
from .money import money_round_even, money_round_up, money_str
from .repository import Repository

class RefundService:
    def _classify(self, hours: int):
        if hours <= 24:
            return "APPROVED", Decimal("0.00")
        if hours <= 72:
            return "APPROVED", Decimal("0.05")
        return "MANUAL_REVIEW", Decimal("0.00")

    def _write_approved_ledger(self, invoice_id: str, refund_id: str, refund_amount: Decimal) -> None:
        self.repo.add_ledger({"type": "REFUND", "invoice_id": invoice_id, "refund_id": refund_id, "amount": money_str(refund_amount), "direction": "CREDIT"})

    def _emit_approved(self, invoice_id: str, refund_id: str, refund_amount: Decimal) -> None:
        self.audit.emit("REFUND_APPROVED", {"invoice_id": invoice_id, "refund_id": refund_id, "amount": money_str(refund_amount)})

    def __init__(self, repo: Repository, audit: AuditLog) -> None:
        self.repo, self.audit = repo, audit

    def refund(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        operation_id = str(payload.get("operation_id", "")).strip()
        invoice_id = str(payload.get("invoice_id", "")).strip()
        hours = int(payload.get("hours_since_purchase", -1))
        if not operation_id:
            raise ValidationError("operation_id is required")
        if not invoice_id:
            raise ValidationError("invoice_id is required")
        if hours < 0:
            raise ValidationError("hours_since_purchase must be >= 0")
        idem_key = f"refund_invoice:{operation_id}"
        existing = self.repo.get_idempotency(idem_key)
        if existing is not None:
            return existing
        invoice = self.repo.get_invoice(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(invoice_id)
        for prior in self.repo.all_refunds():
            if prior["invoice_id"] == invoice_id and prior["status"] == "APPROVED":
                raise RefundAlreadyProcessedError(invoice_id)
        original_total = Decimal(invoice["grand_total"])
        refund_id = "RFD-" + sha256(operation_id.encode()).hexdigest()[:10].upper()
        status, fee_rate = self._classify(hours)
        fee = money_round_even(original_total * fee_rate)
        if status == "APPROVED":
            refund_amount = money_round_up(original_total - fee)
            invoice["status"] = "REFUNDED"
            self.repo.save_invoice(invoice_id, invoice)
        else:
            refund_amount = Decimal("0.00")
        refund = {"refund_id": refund_id, "operation_id": operation_id, "invoice_id": invoice_id,
                  "hours_since_purchase": hours, "status": status, "fee_rate": f"{fee_rate:.4f}",
                  "fee": money_str(fee), "refund_amount": money_str(refund_amount)}
        self.repo.save_refund(refund_id, refund)
        if status == "APPROVED":
            self._write_approved_ledger(invoice_id, refund_id, refund_amount)
            self._emit_approved(invoice_id, refund_id, refund_amount)
        else:
            self.audit.emit("REFUND_MANUAL_REVIEW", {"invoice_id": invoice_id, "refund_id": refund_id, "amount": "0.00"})
        self.repo.save_idempotency(idem_key, refund)
        return deepcopy(refund)
