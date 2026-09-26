from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from typing import Optional, Tuple

from .errors import ValidationError
from .money import MONEY


def calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal:
    """Calculate tier discount rate based on customer tier and subtotal."""
    if tier == "VIP":
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
    return Decimal("0.00")  # RETAIL or default


def apply_coupon(coupon_code: Optional[str], tier_rate: Decimal, subtotal: Decimal) -> Tuple[Decimal, Decimal]:
    """Apply coupon code, returning (discount_rate, fixed_coupon)."""
    fixed_coupon = Decimal("0.00")
    discount_rate = tier_rate
    if coupon_code:
        code = str(coupon_code).upper()
        if code == "WELCOME10":
            discount_rate = min(tier_rate + Decimal("0.10"), Decimal("0.15"))
        elif code == "FIXED25":
            if subtotal >= Decimal("250.00"):
                fixed_coupon = Decimal("25.00")
        else:
            raise ValidationError(f"Unknown coupon: {code}")
    return discount_rate, fixed_coupon


def calculate_discount(subtotal: Decimal, discount_rate: Decimal, fixed_coupon: Decimal) -> Tuple[Decimal, Decimal]:
    """Calculate discount and discounted subtotal."""
    pct_discount = (subtotal * discount_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)
    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN))
    discounted_subtotal = (subtotal - discount).quantize(MONEY, rounding=ROUND_HALF_UP)
    return discount, discounted_subtotal


def calculate_card_fee(payment_method: str, discounted_subtotal: Decimal) -> Decimal:
    """Calculate card fee. Applies only to CARD payments when discounted merchandise subtotal >= 1500; uses ROUND_HALF_UP."""
    if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):
        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_UP)
    return Decimal("0.00")
