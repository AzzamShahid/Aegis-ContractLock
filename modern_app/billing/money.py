"""Monetary precision and rounding utilities."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from typing import Any

MONEY = Decimal("0.01")


def quantize_money(value: Any, rounding=ROUND_HALF_UP) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=rounding)


def quantize_even(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_EVEN)


def format_money(value: Decimal) -> str:
    return f"{value.quantize(MONEY, rounding=ROUND_HALF_UP):.2f}"


def format_rate_4(value: Decimal) -> str:
    return f"{value:.4f}"


def format_rate_5(value: Decimal) -> str:
    return f"{value:.5f}"
