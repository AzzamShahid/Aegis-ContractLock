from __future__ import annotations
from decimal import Decimal
from .money import money_round_even, money_round_up
from .models import ValidationError

class DiscountPolicy:
    def rate(self, tier: str, subtotal: Decimal) -> Decimal:
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
        return Decimal("0.00")

    def apply(self, tier: str, subtotal: Decimal, coupon: str | None):
        discount_rate = self.rate(tier, subtotal)
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
        pct_discount = money_round_even(subtotal * discount_rate)
        discount = min(subtotal, money_round_even(pct_discount + fixed_coupon))
        discounted_subtotal = money_round_up(subtotal - discount)
        return discount_rate, discount, discounted_subtotal
