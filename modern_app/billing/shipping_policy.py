from __future__ import annotations

from decimal import Decimal
from .money import MONEY


def calculate_shipping(region: str, subtotal: Decimal) -> Decimal:
    """Calculate shipping cost based on destination region and pre-discount subtotal."""
    if region in {"US_CA", "US_NY"}:
        return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")
    if region in {"EU_DE", "UK"}:
        return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("18.00")
    return Decimal("35.00")  # EXPORT
