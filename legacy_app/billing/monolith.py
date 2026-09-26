"""
Deliberately legacy-shaped enterprise billing monolith for Aegis ContractLock.

IMPORTANT:
- The regional tax rules below are FICTIONAL DEMO RULES. They are not tax advice.
- The code is intentionally dense and mixed-responsibility so an AI modernizer has
  something realistic to refactor while Aegis protects observable behavior.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Tuple


MONEY = Decimal("0.01")


def _money(value: Any, rounding=ROUND_HALF_UP) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=rounding)


def _money_s(value: Decimal) -> str:
    return f"{value.quantize(MONEY, rounding=ROUND_HALF_UP):.2f}"


class LegacyBillingError(Exception):
    code = "LEGACY_BILLING_ERROR"


class ValidationError(LegacyBillingError):
    code = "VALIDATION_ERROR"


class AccountSuspendedError(LegacyBillingError):
    code = "ACCOUNT_SUSPENDED"


class InvoiceNotFoundError(LegacyBillingError):
    code = "INVOICE_NOT_FOUND"


class RefundAlreadyProcessedError(LegacyBillingError):
    code = "REFUND_ALREADY_PROCESSED"


class LegacyBillingSystem:
    """
    A deliberately tangled service that owns pricing, tax, persistence, audit,
    idempotency, and refund behavior in one class.

    A modernized implementation may use any internal architecture it wants, but
    it must preserve the public protocol:
      - execute(operation: str, payload: dict) -> dict
      - snapshot_state() -> dict
    """

    def __init__(self) -> None:
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._refunds: Dict[str, Dict[str, Any]] = {}
        self._ledger: List[Dict[str, Any]] = []
        self._audit: List[Dict[str, Any]] = []
        self._idempotency: Dict[str, Dict[str, Any]] = {}
        self._audit_seq = 0

    # ----------------------------- Public protocol -----------------------------

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "create_invoice":
            return self._create_invoice(payload)
        if operation == "refund_invoice":
            return self._refund_invoice(payload)
        raise ValidationError(f"Unsupported operation: {operation}")

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Observable business state only. Internal implementation details such as
        idempotency caches are intentionally excluded, allowing the modernized
        implementation to change architecture freely.
        """
        return {
            "invoices": [deepcopy(self._invoices[k]) for k in sorted(self._invoices)],
            "refunds": [deepcopy(self._refunds[k]) for k in sorted(self._refunds)],
            "ledger": deepcopy(self._ledger),
            "audit": deepcopy(self._audit),
        }

    # ------------------------- Invoice path: intentionally mixed -------------------------

    def _create_invoice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        operation_id = str(payload.get("operation_id", "")).strip()
        if not operation_id:
            raise ValidationError("operation_id is required")

        idem_key = f"create_invoice:{operation_id}"
        if idem_key in self._idempotency:
            return deepcopy(self._idempotency[idem_key])

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
            unit_price = _money(raw.get("unit_price", "0"), ROUND_HALF_UP)

            if not sku:
                raise ValidationError("Each item requires sku")
            if category not in {"GOODS", "DIGITAL", "ESSENTIAL"}:
                raise ValidationError(f"Unknown category: {category}")
            if qty <= 0:
                raise ValidationError(f"Quantity for {sku} must be > 0")
            if unit_price < 0:
                raise ValidationError(f"Unit price for {sku} must be >= 0")

            # Legacy quirk #1: each line is rounded HALF_UP before subtotaling.
            line_total = (unit_price * qty).quantize(MONEY, rounding=ROUND_HALF_UP)
            subtotal += line_total
            normalized_lines.append(
                {
                    "sku": sku,
                    "category": category,
                    "qty": qty,
                    "unit_price": _money_s(unit_price),
                    "line_total": _money_s(line_total),
                }
            )

        subtotal = subtotal.quantize(MONEY, rounding=ROUND_HALF_UP)

        # Legacy discount rules.
        discount_rate = self._discount_rate(tier, subtotal)

        # Coupon behavior is cumulative but total percentage is capped at 15%.
        fixed_coupon = Decimal("0.00")
        if coupon:
            code = str(coupon).upper()
            if code == "WELCOME10":
                discount_rate = min(discount_rate + Decimal("0.10"), Decimal("0.15"))
            elif code == "FIXED25":
                if subtotal >= Decimal("250.00"):
                    fixed_coupon = Decimal("25.00")
            else:
                raise ValidationError(f"Unknown coupon: {code}")

        # Legacy quirk #2: percentage discount uses banker's rounding.
        pct_discount = (subtotal * discount_rate).quantize(
            MONEY, rounding=ROUND_HALF_EVEN
        )
        discount = min(
            subtotal,
            (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN),
        )
        discounted_subtotal = (subtotal - discount).quantize(
            MONEY, rounding=ROUND_HALF_UP
        )

        shipping = self._shipping(region, subtotal)
        tax, tax_breakdown = self._calculate_tax(
            region=region,
            lines=normalized_lines,
            subtotal=subtotal,
            total_discount=discount,
        )

        # Legacy quirk #3: service fee applies only to CARD payments when the
        # discounted merchandise subtotal is >= 1500; shipping/tax are excluded.
        payment_method = str(payload.get("payment_method", "CARD")).upper()
        if payment_method not in {"CARD", "BANK_TRANSFER"}:
            raise ValidationError(f"Unknown payment_method: {payment_method}")

        service_fee = Decimal("0.00")
        if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):
            service_fee = (discounted_subtotal * Decimal("0.015")).quantize(
                MONEY, rounding=ROUND_HALF_UP
            )

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
            "subtotal": _money_s(subtotal),
            "discount_rate": f"{discount_rate:.4f}",
            "discount": _money_s(discount),
            "shipping": _money_s(shipping),
            "tax": _money_s(tax),
            "tax_breakdown": tax_breakdown,
            "service_fee": _money_s(service_fee),
            "grand_total": _money_s(grand_total),
        }

        self._invoices[invoice_id] = deepcopy(invoice)
        self._ledger.append(
            {
                "type": "INVOICE_CHARGE",
                "invoice_id": invoice_id,
                "amount": _money_s(grand_total),
                "direction": "DEBIT",
            }
        )
        self._emit(
            "INVOICE_CREATED",
            {
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "amount": _money_s(grand_total),
            },
        )

        result = deepcopy(invoice)
        self._idempotency[idem_key] = deepcopy(result)
        return result

    def _discount_rate(self, tier: str, subtotal: Decimal) -> Decimal:
        if tier == "VIP":
            # Important boundary for the rehearsal mutation.
            if subtotal >= Decimal("1000.00"):
                return Decimal("0.10")
            if subtotal >= Decimal("500.00"):
                return Decimal("0.07")
            return Decimal("0.03")

        if tier == "BUSINESS":
            if subtotal >= Decimal("2000.00"):
                return Decimal("0.06")
            if subtotal >= Decimal("1000.00"):
                return Decimal("0.04")
            return Decimal("0.00")

        return Decimal("0.00")

    def _shipping(self, region: str, subtotal: Decimal) -> Decimal:
        # Shipping is based on pre-discount subtotal: another easy refactor trap.
        if region in {"US_CA", "US_NY"}:
            return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")
        if region in {"EU_DE", "UK"}:
            return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("18.00")
        return Decimal("35.00")  # EXPORT

    def _calculate_tax(
        self,
        region: str,
        lines: List[Dict[str, Any]],
        subtotal: Decimal,
        total_discount: Decimal,
    ) -> Tuple[Decimal, List[Dict[str, str]]]:
        """
        Fictional demo tax rules:
          US_CA: GOODS 7.25%, DIGITAL/ESSENTIAL exempt
          US_NY: GOODS + DIGITAL 8.875%, ESSENTIAL exempt
          EU_DE: GOODS + DIGITAL 19%, ESSENTIAL 7%
          UK: GOODS + DIGITAL 20%, ESSENTIAL exempt
          EXPORT: 0%

        Legacy quirk #4:
        Discount is allocated proportionally by rounded line value. Every line
        except the final line receives a HALF_EVEN rounded allocation; the final
        line receives the residual. This makes boundary/rounding behavior easy to
        accidentally change during refactoring.
        """
        if subtotal == 0:
            return Decimal("0.00"), []

        allocations: List[Decimal] = []
        allocated = Decimal("0.00")
        for idx, line in enumerate(lines):
            line_total = Decimal(line["line_total"])
            if idx == len(lines) - 1:
                share = (total_discount - allocated).quantize(
                    MONEY, rounding=ROUND_HALF_EVEN
                )
            else:
                share = (
                    total_discount * (line_total / subtotal)
                ).quantize(MONEY, rounding=ROUND_HALF_EVEN)
                allocated += share
            allocations.append(share)

        total_tax = Decimal("0.00")
        breakdown: List[Dict[str, str]] = []

        for line, discount_share in zip(lines, allocations):
            category = line["category"]
            line_total = Decimal(line["line_total"])
            taxable_base = max(
                Decimal("0.00"),
                (line_total - discount_share).quantize(MONEY, rounding=ROUND_HALF_UP),
            )

            rate = Decimal("0.00")
            if region == "US_CA":
                rate = Decimal("0.0725") if category == "GOODS" else Decimal("0.00")
            elif region == "US_NY":
                rate = (
                    Decimal("0.08875")
                    if category in {"GOODS", "DIGITAL"}
                    else Decimal("0.00")
                )
            elif region == "EU_DE":
                rate = (
                    Decimal("0.07")
                    if category == "ESSENTIAL"
                    else Decimal("0.19")
                )
            elif region == "UK":
                rate = (
                    Decimal("0.00")
                    if category == "ESSENTIAL"
                    else Decimal("0.20")
                )
            elif region == "EXPORT":
                rate = Decimal("0.00")

            line_tax = (taxable_base * rate).quantize(MONEY, rounding=ROUND_HALF_UP)
            total_tax += line_tax
            breakdown.append(
                {
                    "sku": line["sku"],
                    "taxable_base": _money_s(taxable_base),
                    "rate": f"{rate:.5f}",
                    "tax": _money_s(line_tax),
                }
            )

        return (
            total_tax.quantize(MONEY, rounding=ROUND_HALF_UP),
            breakdown,
        )

    # ------------------------- Refund path: also mixed -------------------------

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
        if idem_key in self._idempotency:
            return deepcopy(self._idempotency[idem_key])

        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(invoice_id)

        for refund in self._refunds.values():
            if refund["invoice_id"] == invoice_id and refund["status"] == "APPROVED":
                raise RefundAlreadyProcessedError(invoice_id)

        invoice = self._invoices[invoice_id]
        original_total = Decimal(invoice["grand_total"])
        refund_id = "RFD-" + sha256(operation_id.encode()).hexdigest()[:10].upper()

        if hours_since_purchase <= 24:
            status = "APPROVED"
            fee_rate = Decimal("0.00")
        elif hours_since_purchase <= 72:
            status = "APPROVED"
            fee_rate = Decimal("0.05")
        else:
            status = "MANUAL_REVIEW"
            fee_rate = Decimal("0.00")

        # Legacy quirk #5: refund fee uses HALF_EVEN, unlike invoice service fee.
        fee = (original_total * fee_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)

        if status == "APPROVED":
            refund_amount = (original_total - fee).quantize(
                MONEY, rounding=ROUND_HALF_UP
            )
            invoice["status"] = "REFUNDED"
        else:
            refund_amount = Decimal("0.00")

        refund = {
            "refund_id": refund_id,
            "operation_id": operation_id,
            "invoice_id": invoice_id,
            "hours_since_purchase": hours_since_purchase,
            "status": status,
            "fee_rate": f"{fee_rate:.4f}",
            "fee": _money_s(fee),
            "refund_amount": _money_s(refund_amount),
        }
        self._refunds[refund_id] = deepcopy(refund)

        if status == "APPROVED":
            self._ledger.append(
                {
                    "type": "REFUND",
                    "invoice_id": invoice_id,
                    "refund_id": refund_id,
                    "amount": _money_s(refund_amount),
                    "direction": "CREDIT",
                }
            )
            self._emit(
                "REFUND_APPROVED",
                {
                    "invoice_id": invoice_id,
                    "refund_id": refund_id,
                    "amount": _money_s(refund_amount),
                },
            )
        else:
            self._emit(
                "REFUND_MANUAL_REVIEW",
                {
                    "invoice_id": invoice_id,
                    "refund_id": refund_id,
                    "amount": "0.00",
                },
            )

        self._idempotency[idem_key] = deepcopy(refund)
        return deepcopy(refund)

    def _emit(self, event_type: str, data: Dict[str, Any]) -> None:
        self._audit_seq += 1
        self._audit.append(
            {
                "seq": self._audit_seq,
                "event": event_type,
                "data": deepcopy(data),
            }
        )


def create_service() -> LegacyBillingSystem:
    return LegacyBillingSystem()
