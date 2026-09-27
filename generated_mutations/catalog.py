"""Mutation Catalog for Holdout Audit.

Defines 65 semantic, generic, domain, survivor, and invalid candidate mutations.
All mutations operate only on temporary copies of the accepted candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Mutation:
    mutant_id: str
    target_file: str  # relative path within repo, e.g. 'modern_app/billing/pricing_policy.py'
    target_line: int
    category: str     # 'GENERIC', 'DOMAIN-SEMANTIC', 'SURVIVOR-CANDIDATE', 'INVALID-TEST'
    operator: str
    original_snippet: str
    mutated_snippet: str
    description: str
    survivor_rationale: Optional[str] = None


MUTATIONS: list[Mutation] = [
    # -------------------------------------------------------------------------
    # GENERIC OPERATORS (18 mutants)
    # -------------------------------------------------------------------------
    Mutation(
        mutant_id="MUT-GEN-01",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=13,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='    if tier == "VIP":\n        if subtotal >= Decimal("1000.00"):',
        mutated_snippet='    if tier == "VIP":\n        if subtotal > Decimal("1000.00"):',
        description="VIP tier $1000.00 boundary relational shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-02",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=15,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='        if subtotal >= Decimal("500.00"):',
        mutated_snippet='        if subtotal > Decimal("500.00"):',
        description="VIP tier $500.00 boundary relational shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-03",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=19,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='        if subtotal >= Decimal("2000.00"):',
        mutated_snippet='        if subtotal > Decimal("2000.00"):',
        description="Business tier $2000.00 boundary relational shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-04",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=21,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='    if tier == "BUSINESS":\n        if subtotal >= Decimal("2000.00"):\n            return Decimal("0.06")\n        if subtotal >= Decimal("1000.00"):',
        mutated_snippet='    if tier == "BUSINESS":\n        if subtotal >= Decimal("2000.00"):\n            return Decimal("0.06")\n        if subtotal > Decimal("1000.00"):',
        description="Business tier $1000.00 boundary relational shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-05",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=36,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='            if subtotal >= Decimal("250.00"):',
        mutated_snippet='            if subtotal > Decimal("250.00"):',
        description="FIXED25 coupon subtotal qualification boundary from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-06",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=46,
        category="GENERIC",
        operator="boundary-cap-removal",
        original_snippet='    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN))',
        mutated_snippet='    discount = (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN)',
        description="Remove min(subtotal, ...) ceiling cap on total discount calculation",
        survivor_rationale=(
            "In all 86 contract scenarios, total discount never exceeds the merchandise subtotal (the maximum discount "
            "tested is $100.00 on a $1,000.00 subtotal, and $32.50 on $250.00 in coupon_ceiling_subtotal). The discount "
            "cap min(subtotal, ...) is defensive and is never triggered by the contract's inputs. In production, an "
            "aberrant stacking discount exceeding 100% would result in negative totals without this cap, but the frozen "
            "contract does not distinguish it."
        ),
    ),
    Mutation(
        mutant_id="MUT-GEN-07",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=47,
        category="GENERIC",
        operator="arithmetic - -> +",
        original_snippet='    discounted_subtotal = (subtotal - discount).quantize(MONEY, rounding=ROUND_HALF_UP)',
        mutated_snippet='    discounted_subtotal = (subtotal + discount).quantize(MONEY, rounding=ROUND_HALF_UP)',
        description="Invert arithmetic operator in discounted subtotal calculation (- to +)",
    ),
    Mutation(
        mutant_id="MUT-GEN-08",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=53,
        category="GENERIC",
        operator="== -> !=",
        original_snippet='    if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):',
        mutated_snippet='    if payment_method != "CARD" and discounted_subtotal >= Decimal("1500.00"):',
        description="Invert payment method check for card surcharge fee from == to !=",
    ),
    Mutation(
        mutant_id="MUT-GEN-09",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=53,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='    if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):',
        mutated_snippet='    if payment_method == "CARD" and discounted_subtotal > Decimal("1500.00"):',
        description="Card surcharge fee boundary threshold shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-10",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=9,
        category="GENERIC",
        operator="boolean-negation",
        original_snippet='    if region in {"US_CA", "US_NY"}:',
        mutated_snippet='    if region not in {"US_CA", "US_NY"}:',
        description="Negate US shipping region membership condition (in to not in)",
    ),
    Mutation(
        mutant_id="MUT-GEN-11",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=10,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='        return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")',
        mutated_snippet='        return Decimal("0.00") if subtotal > Decimal("150.00") else Decimal("12.00")',
        description="US free shipping threshold comparison shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-12",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=12,
        category="GENERIC",
        operator=">= -> >",
        original_snippet='        return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("18.00")',
        mutated_snippet='        return Decimal("0.00") if subtotal > Decimal("250.00") else Decimal("18.00")',
        description="EU/UK free shipping threshold comparison shift from >= to >",
    ),
    Mutation(
        mutant_id="MUT-GEN-13",
        target_file="modern_app/billing/tax_policy.py",
        target_line=13,
        category="GENERIC",
        operator="branch-removal",
        original_snippet='    if subtotal == 0:\n        return Decimal("0.00"), []',
        mutated_snippet='    if False:\n        return Decimal("0.00"), []',
        description="Remove zero-subtotal short-circuit branch in tax calculation",
    ),
    Mutation(
        mutant_id="MUT-GEN-14",
        target_file="modern_app/billing/tax_policy.py",
        target_line=40,
        category="GENERIC",
        operator="== -> !=",
        original_snippet='            rate = Decimal("0.0725") if category == "GOODS" else Decimal("0.00")',
        mutated_snippet='            rate = Decimal("0.0725") if category != "GOODS" else Decimal("0.00")',
        description="Invert US_CA tax category match from category == 'GOODS' to !=",
    ),
    Mutation(
        mutant_id="MUT-GEN-15",
        target_file="modern_app/billing/refund_policy.py",
        target_line=13,
        category="GENERIC",
        operator="<= -> <",
        original_snippet='    if hours_since_purchase <= 24:',
        mutated_snippet='    if hours_since_purchase < 24:',
        description="Refund 24h grace window boundary relational shift from <= to <",
    ),
    Mutation(
        mutant_id="MUT-GEN-16",
        target_file="modern_app/billing/refund_policy.py",
        target_line=16,
        category="GENERIC",
        operator="<= -> <",
        original_snippet='    elif hours_since_purchase <= 72:',
        mutated_snippet='    elif hours_since_purchase < 72:',
        description="Refund 72h window boundary relational shift from <= to <",
    ),
    Mutation(
        mutant_id="MUT-GEN-17",
        target_file="modern_app/billing/service.py",
        target_line=77,
        category="GENERIC",
        operator="branch-removal",
        original_snippet='        if status == "SUSPENDED":\n            raise AccountSuspendedError(f"Customer {customer_id} is suspended")',
        mutated_snippet='        if False:\n            raise AccountSuspendedError(f"Customer {customer_id} is suspended")',
        description="Remove suspended customer status validation check branch",
    ),
    Mutation(
        mutant_id="MUT-GEN-18",
        target_file="modern_app/billing/service.py",
        target_line=99,
        category="GENERIC",
        operator="<= -> <",
        original_snippet='            if qty <= 0:\n                raise ValidationError(f"Quantity for {sku} must be > 0")',
        mutated_snippet='            if qty < 0:\n                raise ValidationError(f"Quantity for {sku} must be > 0")',
        description="Item quantity validation comparison shift from <= 0 to < 0 (allowing qty 0)",
    ),

    # -------------------------------------------------------------------------
    # DOMAIN-SEMANTIC OPERATORS (39 mutants)
    # -------------------------------------------------------------------------
    Mutation(
        mutant_id="MUT-DOM-01",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=14,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='            return Decimal("0.10")',
        mutated_snippet='            return Decimal("0.12")',
        description="VIP high bracket discount rate increased from 10% to 12%",
    ),
    Mutation(
        mutant_id="MUT-DOM-02",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=16,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='            return Decimal("0.07")',
        mutated_snippet='            return Decimal("0.08")',
        description="VIP mid bracket discount rate increased from 7% to 8%",
    ),
    Mutation(
        mutant_id="MUT-DOM-03",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=17,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='        return Decimal("0.03")',
        mutated_snippet='        return Decimal("0.02")',
        description="VIP baseline discount rate decreased from 3% to 2%",
    ),
    Mutation(
        mutant_id="MUT-DOM-04",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=20,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='            return Decimal("0.06")',
        mutated_snippet='            return Decimal("0.07")',
        description="Business high bracket discount rate increased from 6% to 7%",
    ),
    Mutation(
        mutant_id="MUT-DOM-05",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=22,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='            return Decimal("0.04")',
        mutated_snippet='            return Decimal("0.05")',
        description="Business mid bracket discount rate increased from 4% to 5%",
    ),
    Mutation(
        mutant_id="MUT-DOM-06",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=24,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='    return Decimal("0.00")  # RETAIL or default',
        mutated_snippet='    return Decimal("0.01")  # RETAIL or default',
        description="Retail default discount rate changed from 0% to 1%",
    ),
    Mutation(
        mutant_id="MUT-DOM-07",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=34,
        category="DOMAIN-SEMANTIC",
        operator="coupon-cap-alteration",
        original_snippet='            discount_rate = min(tier_rate + Decimal("0.10"), Decimal("0.15"))',
        mutated_snippet='            discount_rate = min(tier_rate + Decimal("0.10"), Decimal("0.20"))',
        description="WELCOME10 cumulative discount ceiling cap raised from 15% to 20%",
    ),
    Mutation(
        mutant_id="MUT-DOM-08",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=34,
        category="DOMAIN-SEMANTIC",
        operator="coupon-cap-removal",
        original_snippet='            discount_rate = min(tier_rate + Decimal("0.10"), Decimal("0.15"))',
        mutated_snippet='            discount_rate = tier_rate + Decimal("0.10")',
        description="WELCOME10 cumulative discount ceiling cap completely removed",
    ),
    Mutation(
        mutant_id="MUT-DOM-09",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=34,
        category="DOMAIN-SEMANTIC",
        operator="coupon-rate-shift",
        original_snippet='            discount_rate = min(tier_rate + Decimal("0.10"), Decimal("0.15"))',
        mutated_snippet='            discount_rate = min(tier_rate + Decimal("0.08"), Decimal("0.15"))',
        description="WELCOME10 bonus rate altered from 10% to 8%",
    ),
    Mutation(
        mutant_id="MUT-DOM-10",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=36,
        category="DOMAIN-SEMANTIC",
        operator="threshold-shift",
        original_snippet='            if subtotal >= Decimal("250.00"):',
        mutated_snippet='            if subtotal >= Decimal("300.00"):',
        description="FIXED25 subtotal threshold shifted upward from $250.00 to $300.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-11",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=37,
        category="DOMAIN-SEMANTIC",
        operator="value-shift",
        original_snippet='                fixed_coupon = Decimal("25.00")',
        mutated_snippet='                fixed_coupon = Decimal("30.00")',
        description="FIXED25 coupon cash grant altered from $25.00 to $30.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-12",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=45,
        category="DOMAIN-SEMANTIC",
        operator="rounding-mode-shift",
        original_snippet='    pct_discount = (subtotal * discount_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)',
        mutated_snippet='    pct_discount = (subtotal * discount_rate).quantize(MONEY, rounding=ROUND_HALF_UP)',
        description="Percentage discount rounding changed from Banker's ROUND_HALF_EVEN to ROUND_HALF_UP",
    ),
    Mutation(
        mutant_id="MUT-DOM-13",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=53,
        category="DOMAIN-SEMANTIC",
        operator="threshold-shift",
        original_snippet='    if payment_method == "CARD" and discounted_subtotal >= Decimal("1500.00"):',
        mutated_snippet='    if payment_method == "CARD" and discounted_subtotal >= Decimal("2000.00"):',
        description="Card surcharge threshold shifted from $1500.00 to $2000.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-14",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=54,
        category="DOMAIN-SEMANTIC",
        operator="rate-shift",
        original_snippet='        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_UP)',
        mutated_snippet='        return (discounted_subtotal * Decimal("0.020")).quantize(MONEY, rounding=ROUND_HALF_UP)',
        description="Card surcharge fee rate shifted from 1.5% to 2.0%",
    ),
    Mutation(
        mutant_id="MUT-DOM-15",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=54,
        category="DOMAIN-SEMANTIC",
        operator="rounding-mode-shift",
        original_snippet='        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_UP)',
        mutated_snippet='        return (discounted_subtotal * Decimal("0.015")).quantize(MONEY, rounding=ROUND_HALF_EVEN)',
        description="Card surcharge rounding mode changed from ROUND_HALF_UP to ROUND_HALF_EVEN",
        survivor_rationale=(
            "The card surcharge fee applies only to discounted merchandise subtotals >= $1,500.00. The contract tests "
            "$1,500.00 (fee = $22.500 exactly) and $1,500.01 (fee = $22.50015). Neither scenario generates an exact "
            "half-cent (.005) tie-break. Therefore, ROUND_HALF_UP and Banker's ROUND_HALF_EVEN produce identical dollar "
            "values for all tested card fee transactions."
        ),
    ),
    Mutation(
        mutant_id="MUT-DOM-16",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=10,
        category="DOMAIN-SEMANTIC",
        operator="fee-shift",
        original_snippet='        return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")',
        mutated_snippet='        return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("15.00")',
        description="US standard shipping charge altered from $12.00 to $15.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-17",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=10,
        category="DOMAIN-SEMANTIC",
        operator="threshold-shift",
        original_snippet='        return Decimal("0.00") if subtotal >= Decimal("150.00") else Decimal("12.00")',
        mutated_snippet='        return Decimal("0.00") if subtotal >= Decimal("200.00") else Decimal("12.00")',
        description="US free shipping subtotal threshold shifted from $150.00 to $200.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-18",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=12,
        category="DOMAIN-SEMANTIC",
        operator="fee-shift",
        original_snippet='        return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("18.00")',
        mutated_snippet='        return Decimal("0.00") if subtotal >= Decimal("250.00") else Decimal("22.00")',
        description="EU/UK standard shipping fee altered from $18.00 to $22.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-19",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=13,
        category="DOMAIN-SEMANTIC",
        operator="fee-shift",
        original_snippet='    return Decimal("35.00")  # EXPORT',
        mutated_snippet='    return Decimal("40.00")  # EXPORT',
        description="EXPORT flat shipping charge altered from $35.00 to $40.00",
    ),
    Mutation(
        mutant_id="MUT-DOM-20",
        target_file="modern_app/billing/tax_policy.py",
        target_line=40,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='            rate = Decimal("0.0725") if category == "GOODS" else Decimal("0.00")',
        mutated_snippet='            rate = Decimal("0.0800") if category == "GOODS" else Decimal("0.00")',
        description="US_CA GOODS tax rate shifted from 7.25% to 8.00%",
    ),
    Mutation(
        mutant_id="MUT-DOM-21",
        target_file="modern_app/billing/tax_policy.py",
        target_line=42,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='            rate = Decimal("0.08875") if category in {"GOODS", "DIGITAL"} else Decimal("0.00")',
        mutated_snippet='            rate = Decimal("0.08500") if category in {"GOODS", "DIGITAL"} else Decimal("0.00")',
        description="US_NY GOODS/DIGITAL tax rate shifted from 8.875% to 8.500%",
    ),
    Mutation(
        mutant_id="MUT-DOM-22",
        target_file="modern_app/billing/tax_policy.py",
        target_line=44,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='            rate = Decimal("0.07") if category == "ESSENTIAL" else Decimal("0.19")',
        mutated_snippet='            rate = Decimal("0.08") if category == "ESSENTIAL" else Decimal("0.19")',
        description="EU_DE ESSENTIAL reduced tax rate shifted from 7% to 8%",
    ),
    Mutation(
        mutant_id="MUT-DOM-23",
        target_file="modern_app/billing/tax_policy.py",
        target_line=44,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='            rate = Decimal("0.07") if category == "ESSENTIAL" else Decimal("0.19")',
        mutated_snippet='            rate = Decimal("0.07") if category == "ESSENTIAL" else Decimal("0.20")',
        description="EU_DE standard VAT rate shifted from 19% to 20%",
    ),
    Mutation(
        mutant_id="MUT-DOM-24",
        target_file="modern_app/billing/tax_policy.py",
        target_line=46,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='            rate = Decimal("0.00") if category == "ESSENTIAL" else Decimal("0.20")',
        mutated_snippet='            rate = Decimal("0.00") if category == "ESSENTIAL" else Decimal("0.21")',
        description="UK standard VAT rate shifted from 20% to 21%",
    ),
    Mutation(
        mutant_id="MUT-DOM-25",
        target_file="modern_app/billing/tax_policy.py",
        target_line=48,
        category="DOMAIN-SEMANTIC",
        operator="tax-rate-shift",
        original_snippet='        elif region == "EXPORT":\n            rate = Decimal("0.00")',
        mutated_snippet='        elif region == "EXPORT":\n            rate = Decimal("0.05")',
        description="EXPORT tax rate changed from exempt (0%) to 5%",
    ),
    Mutation(
        mutant_id="MUT-DOM-26",
        target_file="modern_app/billing/tax_policy.py",
        target_line=50,
        category="DOMAIN-SEMANTIC",
        operator="rounding-mode-shift",
        original_snippet='        line_tax = (taxable_base * rate).quantize(MONEY, rounding=ROUND_HALF_UP)',
        mutated_snippet='        line_tax = (taxable_base * rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)',
        description="Line-item tax calculation rounding changed from ROUND_HALF_UP to ROUND_HALF_EVEN",
    ),
    Mutation(
        mutant_id="MUT-DOM-27",
        target_file="modern_app/billing/tax_policy.py",
        target_line=61,
        category="DOMAIN-SEMANTIC",
        operator="rounding-mode-shift",
        original_snippet='    return total_tax.quantize(MONEY, rounding=ROUND_HALF_UP), breakdown',
        mutated_snippet='    return total_tax.quantize(MONEY, rounding=ROUND_HALF_EVEN), breakdown',
        description="Total tax sum quantization rounding changed from ROUND_HALF_UP to ROUND_HALF_EVEN",
        survivor_rationale=(
            "Total tax is computed by summing the individual line_tax values, each of which has already been quantized "
            "to cents (MONEY) using ROUND_HALF_UP on line 50. Because the sum of numbers with two decimal places never "
            "has fractional cents beyond the hundredths position, applying ROUND_HALF_EVEN versus ROUND_HALF_UP to the "
            "sum produces identical values across all 86 cases."
        ),
    ),
    Mutation(
        mutant_id="MUT-DOM-28",
        target_file="modern_app/billing/refund_policy.py",
        target_line=13,
        category="DOMAIN-SEMANTIC",
        operator="window-drift",
        original_snippet='    if hours_since_purchase <= 24:',
        mutated_snippet='    if hours_since_purchase <= 48:',
        description="Refund zero-fee grace window expanded from 24h to 48h",
    ),
    Mutation(
        mutant_id="MUT-DOM-29",
        target_file="modern_app/billing/refund_policy.py",
        target_line=16,
        category="DOMAIN-SEMANTIC",
        operator="window-drift",
        original_snippet='    elif hours_since_purchase <= 72:',
        mutated_snippet='    elif hours_since_purchase <= 96:',
        description="Refund fee-approved window boundary drifted from 72h to 96h",
    ),
    Mutation(
        mutant_id="MUT-DOM-30",
        target_file="modern_app/billing/refund_policy.py",
        target_line=18,
        category="DOMAIN-SEMANTIC",
        operator="fee-rate-shift",
        original_snippet='        fee_rate = Decimal("0.05")',
        mutated_snippet='        fee_rate = Decimal("0.10")',
        description="Late refund restocking fee rate shifted from 5% to 10%",
    ),
    Mutation(
        mutant_id="MUT-DOM-31",
        target_file="modern_app/billing/refund_policy.py",
        target_line=24,
        category="DOMAIN-SEMANTIC",
        operator="rounding-mode-shift",
        original_snippet='    fee = (original_total * fee_rate).quantize(MONEY, rounding=ROUND_HALF_EVEN)',
        mutated_snippet='    fee = (original_total * fee_rate).quantize(MONEY, rounding=ROUND_HALF_UP)',
        description="Refund fee calculation rounding mode changed from Banker's ROUND_HALF_EVEN to ROUND_HALF_UP",
    ),
    Mutation(
        mutant_id="MUT-DOM-32",
        target_file="modern_app/billing/storage.py",
        target_line=53,
        category="DOMAIN-SEMANTIC",
        operator="ledger-reversal",
        original_snippet='                "direction": "DEBIT",',
        mutated_snippet='                "direction": "CREDIT",',
        description="Invoice ledger entry direction inverted from DEBIT to CREDIT",
    ),
    Mutation(
        mutant_id="MUT-DOM-33",
        target_file="modern_app/billing/storage.py",
        target_line=66,
        category="DOMAIN-SEMANTIC",
        operator="ledger-reversal",
        original_snippet='                "direction": "CREDIT",',
        mutated_snippet='                "direction": "DEBIT",',
        description="Refund ledger entry direction inverted from CREDIT to DEBIT",
    ),
    Mutation(
        mutant_id="MUT-DOM-34",
        target_file="modern_app/billing/service.py",
        target_line=63,
        category="DOMAIN-SEMANTIC",
        operator="idempotency-removal",
        original_snippet='        idem_key = f"create_invoice:{operation_id}"\n        cached = self._storage.get_idempotent(idem_key)\n        if cached is not None:\n            return cached',
        mutated_snippet='        idem_key = f"create_invoice:{operation_id}"\n        cached = self._storage.get_idempotent(idem_key)\n        if False:\n            return cached',
        description="Disable idempotency cache retrieval in create_invoice",
    ),
    Mutation(
        mutant_id="MUT-DOM-35",
        target_file="modern_app/billing/service.py",
        target_line=187,
        category="DOMAIN-SEMANTIC",
        operator="idempotency-removal",
        original_snippet='        idem_key = f"refund_invoice:{operation_id}"\n        cached = self._storage.get_idempotent(idem_key)\n        if cached is not None:\n            return cached',
        mutated_snippet='        idem_key = f"refund_invoice:{operation_id}"\n        cached = self._storage.get_idempotent(idem_key)\n        if False:\n            return cached',
        description="Disable idempotency cache retrieval in refund_invoice",
    ),
    Mutation(
        mutant_id="MUT-DOM-36",
        target_file="modern_app/billing/service.py",
        target_line=160,
        category="DOMAIN-SEMANTIC",
        operator="audit-event-omission",
        original_snippet='        self._events.emit(\n            "INVOICE_CREATED",',
        mutated_snippet='        # OMITTED:\n        # self._events.emit(\n        if False: self._events.emit(\n            "INVOICE_CREATED",',
        description="Omit INVOICE_CREATED audit event emission during invoice creation",
    ),
    Mutation(
        mutant_id="MUT-DOM-37",
        target_file="modern_app/billing/service.py",
        target_line=223,
        category="DOMAIN-SEMANTIC",
        operator="audit-event-omission",
        original_snippet='            self._events.emit(\n                "REFUND_APPROVED",',
        mutated_snippet='            # OMITTED:\n            if False: self._events.emit(\n                "REFUND_APPROVED",',
        description="Omit REFUND_APPROVED audit event emission upon refund approval",
    ),
    Mutation(
        mutant_id="MUT-DOM-38",
        target_file="modern_app/billing/service.py",
        target_line=205,
        category="DOMAIN-SEMANTIC",
        operator="state-write-omission",
        original_snippet='        if status == "APPROVED":\n            self._storage.update_invoice_status(invoice_id, "REFUNDED")',
        mutated_snippet='        if False:\n            self._storage.update_invoice_status(invoice_id, "REFUNDED")',
        description="Omit updating invoice status to REFUNDED in persistent storage upon approval",
    ),
    Mutation(
        mutant_id="MUT-DOM-39",
        target_file="modern_app/billing/service.py",
        target_line=194,
        category="DOMAIN-SEMANTIC",
        operator="guard-removal",
        original_snippet='        if self._storage.has_approved_refund(invoice_id):\n            raise RefundAlreadyProcessedError(invoice_id)',
        mutated_snippet='        if False:\n            raise RefundAlreadyProcessedError(invoice_id)',
        description="Remove duplicate approved refund guard check in refund_invoice",
    ),

    # -------------------------------------------------------------------------
    # SURVIVOR CANDIDATES (6 mutants)
    # Realistic domain-semantic mutations where the behavior changes, but
    # survives the frozen contract's 86 test cases.
    # -------------------------------------------------------------------------
    Mutation(
        mutant_id="MUT-SURV-01",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=46,
        category="SURVIVOR-CANDIDATE",
        operator="redundant-rounding-mode",
        original_snippet='    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_EVEN))',
        mutated_snippet='    discount = min(subtotal, (pct_discount + fixed_coupon).quantize(MONEY, rounding=ROUND_HALF_UP))',
        description="Change rounding on (pct_discount + fixed_coupon) from ROUND_HALF_EVEN to ROUND_HALF_UP",
        survivor_rationale=(
            "pct_discount is already quantized to exact cents (MONEY) and fixed_coupon has 2 decimal digits. "
            "Their sum never has fractional cents in any tested case, so ROUND_HALF_UP and ROUND_HALF_EVEN produce "
            "identical results. Survives because current test corpus only issues whole-cent coupons."
        ),
    ),
    Mutation(
        mutant_id="MUT-SURV-02",
        target_file="modern_app/billing/tax_policy.py",
        target_line=33,
        category="SURVIVOR-CANDIDATE",
        operator="defensive-clamp-removal",
        original_snippet='        taxable_base = max(\n            Decimal("0.00"),\n            (line_total - discount_share).quantize(MONEY, rounding=ROUND_HALF_UP),\n        )',
        mutated_snippet='        taxable_base = (line_total - discount_share).quantize(MONEY, rounding=ROUND_HALF_UP)',
        description="Remove max(Decimal('0.00'), ...) defensive floor clamp on line taxable base",
        survivor_rationale=(
            "In all 86 contract scenarios, the multi-line discount allocation ensures discount_share <= line_total, "
            "meaning line_total - discount_share is never negative. The defensive floor of 0.00 is never activated "
            "by the contract's inputs. A future scenario with an over-allocated coupon discount would drift, but "
            "the frozen contract does not distinguish it."
        ),
    ),
    Mutation(
        mutant_id="MUT-SURV-03",
        target_file="modern_app/billing/service.py",
        target_line=101,
        category="SURVIVOR-CANDIDATE",
        operator="validation-boundary-gap",
        original_snippet='            if unit_price < 0:\n                raise ValidationError(f"Unit price for {sku} must be >= 0")',
        mutated_snippet='            if unit_price <= Decimal("-1.00"):\n                raise ValidationError(f"Unit price for {sku} must be >= 0")',
        description="Alter negative unit_price validation threshold from < 0 to <= -1.00",
        survivor_rationale=(
            "The frozen contract contains exactly one test case for negative price (val_item_negative_price), "
            "which passes unit_price: '-5.00'. Because -5.00 <= -1.00 evaluates to True, val_item_negative_price "
            "raises ValidationError and matches baseline. Subtle negative prices between -0.99 and -0.01 are untested, "
            "so this semantic mutation survives the contract."
        ),
    ),
    Mutation(
        mutant_id="MUT-SURV-04",
        target_file="modern_app/billing/storage.py",
        target_line=34,
        category="SURVIVOR-CANDIDATE",
        operator="redundant-defensive-guard-removal",
        original_snippet='        if invoice_id not in self._invoices:\n            raise InvoiceNotFoundError(invoice_id)',
        mutated_snippet='        # if invoice_id not in self._invoices:\n        #     raise InvoiceNotFoundError(invoice_id)',
        description="Remove InvoiceNotFoundError check inside BillingStorage.update_invoice_status",
        survivor_rationale=(
            "BillingService._refund_invoice already queries get_invoice(invoice_id) and raises InvoiceNotFoundError "
            "prior to calling update_invoice_status. Therefore, update_invoice_status is never invoked with an invalid "
            "invoice ID in the existing workflow. The storage-layer guard is redundant in the workflow corpus and its "
            "omission survives."
        ),
    ),
    Mutation(
        mutant_id="MUT-SURV-05",
        target_file="modern_app/billing/service.py",
        target_line=70,
        category="SURVIVOR-CANDIDATE",
        operator="input-normalization-omission",
        original_snippet='        customer_id = str(customer.get("id", "")).strip()',
        mutated_snippet='        customer_id = str(customer.get("id", ""))',
        description="Omit .strip() whitespace trimming on customer_id in create_invoice",
        survivor_rationale=(
            "All customer IDs throughout the 86 contract scenarios are pre-trimmed without leading or trailing "
            "whitespace (e.g. 'C-VIP-01'). Omitting the .strip() call leaves valid trimmed IDs unchanged. "
            "Dirty whitespace inputs are not included in the frozen contract suite."
        ),
    ),
    Mutation(
        mutant_id="MUT-SURV-06",
        target_file="modern_app/billing/shipping_policy.py",
        target_line=13,
        category="SURVIVOR-CANDIDATE",
        operator="unexercised-high-tier-rule",
        original_snippet='    return Decimal("35.00")  # EXPORT',
        mutated_snippet='    return Decimal("0.00") if subtotal >= Decimal("5000.00") else Decimal("35.00")',
        description="Add free shipping for EXPORT orders exceeding $5,000.00 subtotal",
        survivor_rationale=(
            "The maximum subtotal tested for EXPORT orders across the frozen scenario suite is $1,000.00 "
            "(shipping_export_flat_high). Subtotals >= $5,000.00 are completely unexercised for the EXPORT region, "
            "so adding a high-tier free shipping rule alters the policy semantics while surviving the finite contract."
        ),
    ),

    # -------------------------------------------------------------------------
    # INVALID / UNRUNNABLE MUTATION CANDIDATES (2 mutants)
    # Used to verify that syntax / import errors are properly classified as
    # INVALID_OR_UNRUNNABLE and excluded from the detection rate denominator.
    # -------------------------------------------------------------------------
    Mutation(
        mutant_id="MUT-INV-01",
        target_file="modern_app/billing/pricing_policy.py",
        target_line=10,
        category="INVALID-TEST",
        operator="syntax-error-injection",
        original_snippet='def calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal:',
        mutated_snippet='def calculate_tier_discount(tier: str, subtotal: Decimal) -> Decimal:::',
        description="Inject intentional Python syntax error (double colon :::) into pricing_policy.py",
    ),
    Mutation(
        mutant_id="MUT-INV-02",
        target_file="modern_app/billing/api.py",
        target_line=4,
        category="INVALID-TEST",
        operator="import-error-injection",
        original_snippet='from .events import AuditLog',
        mutated_snippet='from .nonexistent_module_to_trigger_import_error import BrokenClass\nfrom .events import AuditLog',
        description="Inject broken import into api.py to trigger ModuleNotFoundError on candidate load",
    ),
]
