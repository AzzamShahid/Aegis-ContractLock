from __future__ import annotations
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from typing import Any

MONEY = Decimal("0.01")

def money_round_up(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)

def money_round_even(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_EVEN)

def money_str(value: Decimal) -> str:
    return f"{value.quantize(MONEY, rounding=ROUND_HALF_UP):.2f}"
