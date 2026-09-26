from __future__ import annotations
from typing import Any, Dict
from .discounts import DiscountPolicy
from .events import AuditLog
from .invoice_service import InvoiceService
from .models import ValidationError
from .refund_service import RefundService
from .repository import Repository
from .shipping import ShippingPolicy
from .taxes import TaxPolicy

class ModernBillingSystem:
    def __init__(self, *, discounts=None, shipping=None, taxes=None, repository=None, audit=None, invoice_service_cls=InvoiceService, refund_service_cls=RefundService) -> None:
        self.repo = repository or Repository()
        self.audit = audit or AuditLog()
        self.discounts = discounts or DiscountPolicy()
        self.shipping = shipping or ShippingPolicy()
        self.taxes = taxes or TaxPolicy()
        self.invoice = invoice_service_cls(self.repo, self.audit, self.discounts, self.shipping, self.taxes)
        self.refunds = refund_service_cls(self.repo, self.audit)

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "create_invoice":
            return self.invoice.create(payload)
        if operation == "refund_invoice":
            return self.refunds.refund(payload)
        raise ValidationError(f"Unsupported operation: {operation}")

    def snapshot_state(self) -> Dict[str, Any]:
        return {"invoices": self.repo.all_invoices(), "refunds": self.repo.all_refunds(), "ledger": self.repo.ledger(), "audit": self.audit.snapshot()}

def create_service() -> ModernBillingSystem:
    return ModernBillingSystem()
