"""Core billing application workflow service."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from typing import Any, Dict, List, Optional

from .errors import (
    AccountSuspendedError,
    InvoiceNotFoundError,
    RefundAlreadyProcessedError,
    ValidationError,
)
from .events import AuditLog
from .money import MONEY, format_money, format_rate_4, quantize_money
from .pricing_policy import (
    apply_coupon,
    calculate_card_fee,
    calculate_discount,
    calculate_tier_discount,
)
from .refund_policy import evaluate_refund
from .shipping_policy import calculate_shipping
from .storage import BillingStorage
from .tax_policy import calculate_tax


class BillingService:
    """Modern billing service coordinating pure policy modules and persistence."""

    def __init__(
        self,
        storage: Optional[BillingStorage] = None,
        events: Optional[AuditLog] = None,
    ) -> None:
        self._storage = storage if storage is not None else BillingStorage()
        self._events = events if events is not None else AuditLog()

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "create_invoice":
            return self._create_invoice(payload)
        if operation == "refund_invoice":
            return self._refund_invoice(payload)
        raise ValidationError(f"Unsupported operation: {operation}")

    def snapshot_state(self) -> Dict[str, Any]:
        storage_snap = self._storage.snapshot()
        return {
            "invoices": storage_snap["invoices"],
            "refunds": storage_snap["refunds"],
            "ledger": storage_snap["ledger"],
            "audit": self._events.snapshot(),
        }

    def _create_invoice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        operation_id = str(payload.get("operation_id", "")).strip()
        if not operation_id:
            raise ValidationError("operation_id is required")

        idem_key = f"create_invoice:{operation_id}"
        cached = self._storage.get_idempotent(idem_key)
        if cached is not None:
            return cached

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

        normalized_lines: List[Dict[str, Any]] = []
        subtotal = Decimal("0.00")

        for raw in items:
            sku = str(raw.get("sku", "")).strip()
            category = str(raw.get("category", "GOODS")).upper()
            qty = int(raw.get("qty", 0))
            unit_price = quantize_money(raw.get("unit_price", "0"), ROUND_HALF_UP)

            if not sku:
                raise ValidationError("Each item requires sku")
            if category not in {"GOODS", "DIGITAL", "ESSENTIAL"}:
                raise ValidationError(f"Unknown category: {category}")
            if qty <= 0:
                raise ValidationError(f"Quantity for {sku} must be > 0")
            if unit_price < 0:
                raise ValidationError(f"Unit price for {sku} must be >= 0")

            line_total = (unit_price * qty).quantize(MONEY, rounding=ROUND_HALF_UP)
            subtotal += line_total
            normalized_lines.append(
                {
                    "sku": sku,
                    "category": category,
                    "qty": qty,
                    "unit_price": format_money(unit_price),
                    "line_total": format_money(line_total),
                }
            )

        subtotal = subtotal.quantize(MONEY, rounding=ROUND_HALF_UP)

        discount_rate = calculate_tier_discount(tier, subtotal)
        discount_rate, fixed_coupon = apply_coupon(coupon, discount_rate, subtotal)
        discount, discounted_subtotal = calculate_discount(
            subtotal, discount_rate, fixed_coupon
        )

        shipping = calculate_shipping(region, subtotal)
        tax, tax_breakdown = calculate_tax(region, normalized_lines, subtotal, discount)

        payment_method = str(payload.get("payment_method", "CARD")).upper()
        if payment_method not in {"CARD", "BANK_TRANSFER"}:
            raise ValidationError(f"Unknown payment_method: {payment_method}")

        service_fee = calculate_card_fee(payment_method, discounted_subtotal)

        grand_total = (
            discounted_subtotal + shipping + tax + service_fee
        ).quantize(MONEY, rounding=ROUND_HALF_UP)

        invoice_id = "INV-" + sha256(operation_id.encode()).hexdigest()[:10].upper()

        invoice = {
            "invoice_id": invoice_id,
            "operation_id": operation_id,
            "customer_id": customer_id,
            "tier": tier,
            "region": region,
            "status": "OPEN",
            "payment_method": payment_method,
            "items": normalized_lines,
            "subtotal": format_money(subtotal),
            "discount_rate": format_rate_4(discount_rate),
            "discount": format_money(discount),
            "shipping": format_money(shipping),
            "tax": format_money(tax),
            "tax_breakdown": tax_breakdown,
            "service_fee": format_money(service_fee),
            "grand_total": format_money(grand_total),
        }

        self._storage.save_invoice(invoice)
        self._storage.record_ledger_debit(invoice_id, format_money(grand_total))
        self._events.emit(
            "INVOICE_CREATED",
            {
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "amount": format_money(grand_total),
            },
        )

        result = deepcopy(invoice)
        self._storage.save_idempotent(idem_key, result)
        return result

    def _refund_invoice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        operation_id = str(payload.get("operation_id", "")).strip()
        invoice_id = str(payload.get("invoice_id", "")).strip()
        hours_since_purchase = int(payload.get("hours_since_purchase", -1))

        if not operation_id:
            raise ValidationError("operation_id is required")
        if not invoice_id:
            raise ValidationError("invoice_id is required")
        if hours_since_purchase < 0:
            raise ValidationError("hours_since_purchase must be >= 0")

        idem_key = f"refund_invoice:{operation_id}"
        cached = self._storage.get_idempotent(idem_key)
        if cached is not None:
            return cached

        invoice = self._storage.get_invoice(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(invoice_id)

        if self._storage.has_approved_refund(invoice_id):
            raise RefundAlreadyProcessedError(invoice_id)

        original_total = Decimal(invoice["grand_total"])
        refund_id = "RFD-" + sha256(operation_id.encode()).hexdigest()[:10].upper()

        status, fee_rate, fee, refund_amount = evaluate_refund(
            original_total, hours_since_purchase
        )

        if status == "APPROVED":
            self._storage.update_invoice_status(invoice_id, "REFUNDED")

        refund = {
            "refund_id": refund_id,
            "operation_id": operation_id,
            "invoice_id": invoice_id,
            "hours_since_purchase": hours_since_purchase,
            "status": status,
            "fee_rate": format_rate_4(fee_rate),
            "fee": format_money(fee),
            "refund_amount": format_money(refund_amount),
        }
        self._storage.save_refund(refund)

        if status == "APPROVED":
            self._storage.record_ledger_credit(
                invoice_id, refund_id, format_money(refund_amount)
            )
            self._events.emit(
                "REFUND_APPROVED",
                {
                    "invoice_id": invoice_id,
                    "refund_id": refund_id,
                    "amount": format_money(refund_amount),
                },
            )
        else:
            self._events.emit(
                "REFUND_MANUAL_REVIEW",
                {
                    "invoice_id": invoice_id,
                    "refund_id": refund_id,
                    "amount": "0.00",
                },
            )

        self._storage.save_idempotent(idem_key, refund)
        return deepcopy(refund)
