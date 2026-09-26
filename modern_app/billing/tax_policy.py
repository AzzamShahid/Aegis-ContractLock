from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from typing import Any, Dict, List, Tuple

from .money import MONEY, format_money


def calculate_tax(
    region: str, lines: List[Dict[str, Any]], subtotal: Decimal, total_discount: Decimal
) -> Tuple[Decimal, List[Dict[str, str]]]:
    """Calculate tax for regional lines with discount allocation."""
    if subtotal == 0:
        return Decimal("0.00"), []

    allocations: List[Decimal] = []
    allocated = Decimal("0.00")
    for idx, line in enumerate(lines):
        line_total = Decimal(line["line_total"])
        if idx == len(lines) - 1:
            share = (total_discount - allocated).quantize(MONEY, rounding=ROUND_HALF_EVEN)
        else:
            share = (total_discount * (line_total / subtotal)).quantize(MONEY, rounding=ROUND_HALF_EVEN)
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
            rate = Decimal("0.08875") if category in {"GOODS", "DIGITAL"} else Decimal("0.00")
        elif region == "EU_DE":
            rate = Decimal("0.07") if category == "ESSENTIAL" else Decimal("0.19")
        elif region == "UK":
            rate = Decimal("0.00") if category == "ESSENTIAL" else Decimal("0.20")
        elif region == "EXPORT":
            rate = Decimal("0.00")

        line_tax = (taxable_base * rate).quantize(MONEY, rounding=ROUND_HALF_UP)
        total_tax += line_tax
        breakdown.append(
            {
                "sku": line["sku"],
                "taxable_base": format_money(taxable_base),
                "rate": f"{rate:.5f}",
                "tax": format_money(line_tax),
            }
        )

    return total_tax.quantize(MONEY, rounding=ROUND_HALF_UP), breakdown
