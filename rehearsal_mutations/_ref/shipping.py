from decimal import Decimal

class ShippingPolicy:
    def calculate(self, region: str, subtotal: Decimal) -> Decimal:
        if region in {"US_CA", "US_NY"}:
            return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")
        if region in {"EU_DE", "UK"}:
            return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("18.00")
        return Decimal("35.00")
