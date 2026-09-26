from __future__ import annotations
from decimal import Decimal
from typing import Any, Dict, List, Tuple
from .money import money_round_even, money_round_up, money_str

class TaxPolicy:
    def rate_for(self, region: str, category: str) -> Decimal:
        if region == "US_CA":
            return Decimal("0.0725") if category == "GOODS" else Decimal("0.00")
        if region == "US_NY":
            return Decimal("0.08875") if category in {"GOODS", "DIGITAL"} else Decimal("0.00")
        if region == "EU_DE":
            return Decimal("0.07") if category == "ESSENTIAL" else Decimal("0.19")
        if region == "UK":
            return Decimal("0.00") if category == "ESSENTIAL" else Decimal("0.20")
        return Decimal("0.00")

    def calculate(self, region: str, lines: List[Dict[str, Any]], subtotal: Decimal, total_discount: Decimal) -> Tuple[Decimal, List[Dict[str, str]]]:
        if subtotal == 0:
            return Decimal("0.00"), []
        allocations: List[Decimal] = []
        allocated = Decimal("0.00")
        for idx, line in enumerate(lines):
            line_total = Decimal(line["line_total"])
            if idx == len(lines) - 1:
                share = money_round_even(total_discount - allocated)
            else:
                share = money_round_even(total_discount * (line_total / subtotal))
                allocated += share
            allocations.append(share)

        total_tax = Decimal("0.00")
        breakdown: List[Dict[str, str]] = []
        for line, discount_share in zip(lines, allocations):
            line_total = Decimal(line["line_total"])
            taxable_base = max(Decimal("0.00"), money_round_up(line_total - discount_share))
            rate = self.rate_for(region, line["category"])
            line_tax = money_round_up(taxable_base * rate)
            total_tax += line_tax
            breakdown.append({
                "sku": line["sku"],
                "taxable_base": money_str(taxable_base),
                "rate": f"{rate:.5f}",
                "tax": money_str(line_tax),
            })
        return money_round_up(total_tax), breakdown
