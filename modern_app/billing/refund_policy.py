from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from typing import Tuple

from .money import MONEY


def evaluate_refund(
    original_total: Decimal, hours_since_purchase: int
) -> Tuple[str, Decimal, Decimal, Decimal]:
    """Evaluate refund request and return (status, fee_rate, fee, refund_amount)."""
    if hours_since_purchase <= 24:
        status = "APPROVED"
        fee_rate = Decimal("0.00")
    elif hours_since_purchase <= 72:
        status = "APPROVED"
        fee_rate = Decimal("0.05")
    else:
        status = "MANUAL_REVIEW"
        fee_rate = Decimal("0.00")

    # Refund fee uses ROUND_HALF_EVEN (Banker's rounding)
    fee = (original_total * fee_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)

    if status == "APPROVED":
        refund_amount = (original_total - fee).quantize(MONEY, rounding=ROUND_HALF_UP)
    else:
        refund_amount = Decimal("0.00")

    return status, fee_rate, fee, refund_amount
