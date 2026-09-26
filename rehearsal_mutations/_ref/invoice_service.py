from __future__ import annotations
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
from typing import Any, Dict
from .discounts import DiscountPolicy
from .events import AuditLog
from .models import AccountSuspendedError, ValidationError
from .money import money_round_up, money_str
from .repository import Repository
from .shipping import ShippingPolicy
from .taxes import TaxPolicy

class InvoiceService:
    def _service_fee(self, payment_method: str, discounted_subtotal: Decimal) -> Decimal:
        if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):
            return money_round_up(discounted_subtotal * Decimal("0.015"))
        return Decimal("0.00")

    def __init__(self, repo: Repository, audit: AuditLog, discounts: DiscountPolicy, shipping: ShippingPolicy, taxes: TaxPolicy) -> None:
        self.repo, self.audit = repo, audit
        self.discounts, self.shipping, self.taxes = discounts, shipping, taxes

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        operation_id = str(payload.get("operation_id", "")).strip()
        if not operation_id:
            raise ValidationError("operation_id is required")
        idem_key = f"create_invoice:{operation_id}"
        existing = self.repo.get_idempotency(idem_key)
        if existing is not None:
            return existing

        customer = deepcopy(payload.get("customer") or {})
        items = deepcopy(payload.get("items") or [])
        coupon = payload.get("coupon")
        customer_id = str(customer.get("id", "")).strip()
        tier = str(customer.get("tier", "RETAIL")).upper()
        region = str(customer.get("region", "")).upper()
        status = str(customer.get("status", "ACTIVE")).upper()
        if not customer_id:
            raise ValidationError("customer.id is required")
        if status == "SUSPENDED":
            raise AccountSuspendedError(f"Customer {customer_id} is suspended")
        if tier not in {"RETAIL", "BUSINESS", "VIP"}:
            raise ValidationError(f"Unknown customer tier: {tier}")
        if region not in {"US_CA", "US_NY", "EU_DE", "UK", "EXPORT"}:
            raise ValidationError(f"Unknown region: {region}")
        if not items:
            raise ValidationError("At least one invoice item is required")

        lines = []
        subtotal = Decimal("0.00")
        for raw in items:
            sku = str(raw.get("sku", "")).strip()
            category = str(raw.get("category", "GOODS")).upper()
            qty = int(raw.get("qty", 0))
            unit_price = money_round_up(raw.get("unit_price", "0"))
            if not sku:
                raise ValidationError("Each item requires sku")
            if category not in {"GOODS", "DIGITAL", "ESSENTIAL"}:
                raise ValidationError(f"Unknown category: {category}")
            if qty <= 0:
                raise ValidationError(f"Quantity for {sku} must be > 0")
            if unit_price < 0:
                raise ValidationError(f"Unit price for {sku} must be >= 0")
            line_total = money_round_up(unit_price * qty)
            subtotal += line_total
            lines.append({"sku": sku, "category": category, "qty": qty, "unit_price": money_str(unit_price), "line_total": money_str(line_total)})
        subtotal = money_round_up(subtotal)

        discount_rate, discount, discounted_subtotal = self.discounts.apply(tier, subtotal, coupon)
        shipping = self.shipping.calculate(region, subtotal)
        tax, tax_breakdown = self.taxes.calculate(region, lines, subtotal, discount)
        payment_method = str(payload.get("payment_method", "CARD")).upper()
        if payment_method not in {"CARD", "BANK_TRANSFER"}:
            raise ValidationError(f"Unknown payment_method: {payment_method}")
        service_fee = self._service_fee(payment_method, discounted_subtotal)
        grand_total = money_round_up(discounted_subtotal + shipping + tax + service_fee)
        invoice_id = "INV-" + sha256(operation_id.encode()).hexdigest()[:10].upper()
        invoice = {
            "invoice_id": invoice_id, "operation_id": operation_id, "customer_id": customer_id,
            "tier": tier, "region": region, "status": "OPEN", "payment_method": payment_method,
            "items": lines, "subtotal": money_str(subtotal), "discount_rate": f"{discount_rate:.4f}",
            "discount": money_str(discount), "shipping": money_str(shipping), "tax": money_str(tax),
            "tax_breakdown": tax_breakdown, "service_fee": money_str(service_fee), "grand_total": money_str(grand_total),
        }
        self.repo.save_invoice(invoice_id, invoice)
        self.repo.add_ledger({"type": "INVOICE_CHARGE", "invoice_id": invoice_id, "amount": money_str(grand_total), "direction": "DEBIT"})
        self.audit.emit("INVOICE_CREATED", {"invoice_id": invoice_id, "customer_id": customer_id, "amount": money_str(grand_total)})
        self.repo.save_idempotency(idem_key, invoice)
        return deepcopy(invoice)
