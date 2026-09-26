from __future__ import annotations
from decimal import Decimal
from ._ref.api import ModernBillingSystem
from ._ref.discounts import DiscountPolicy
from ._ref.shipping import ShippingPolicy
from ._ref.taxes import TaxPolicy
from ._ref.invoice_service import InvoiceService
from ._ref.refund_service import RefundService
from ._ref.repository import Repository
from ._ref.events import AuditLog
from ._ref.money import money_round_even, money_round_up
from ._ref.models import ValidationError

class Vip1000Strict(DiscountPolicy):
    def rate(self,tier,subtotal):
        if tier=='VIP':
            if subtotal > Decimal('1000.00'): return Decimal('0.10')
            if subtotal >= Decimal('500.00'): return Decimal('0.07')
            return Decimal('0.03')
        return super().rate(tier,subtotal)

class Vip500Strict(DiscountPolicy):
    def rate(self,tier,subtotal):
        if tier=='VIP':
            if subtotal >= Decimal('1000.00'): return Decimal('0.10')
            if subtotal > Decimal('500.00'): return Decimal('0.07')
            return Decimal('0.03')
        return super().rate(tier,subtotal)

class Biz2000Strict(DiscountPolicy):
    def rate(self,tier,subtotal):
        if tier=='BUSINESS':
            if subtotal > Decimal('2000.00'): return Decimal('0.06')
            if subtotal >= Decimal('1000.00'): return Decimal('0.04')
            return Decimal('0.00')
        return super().rate(tier,subtotal)

class Biz1000Strict(DiscountPolicy):
    def rate(self,tier,subtotal):
        if tier=='BUSINESS':
            if subtotal >= Decimal('2000.00'): return Decimal('0.06')
            if subtotal > Decimal('1000.00'): return Decimal('0.04')
            return Decimal('0.00')
        return super().rate(tier,subtotal)

class WelcomeCap20(DiscountPolicy):
    def apply(self,tier,subtotal,coupon):
        rate=self.rate(tier,subtotal); fixed=Decimal('0.00')
        if coupon:
            code=str(coupon).upper()
            if code=='WELCOME10': rate=min(rate+Decimal('0.10'),Decimal('0.20'))
            elif code=='FIXED25':
                if subtotal>=Decimal('250.00'): fixed=Decimal('25.00')
            else: raise ValidationError(f'Unknown coupon: {code}')
        pct=money_round_even(subtotal*rate)
        discount=min(subtotal,money_round_even(pct+fixed))
        return rate,discount,money_round_up(subtotal-discount)

class Fixed25Strict(DiscountPolicy):
    def apply(self,tier,subtotal,coupon):
        rate=self.rate(tier,subtotal); fixed=Decimal('0.00')
        if coupon:
            code=str(coupon).upper()
            if code=='WELCOME10': rate=min(rate+Decimal('0.10'),Decimal('0.15'))
            elif code=='FIXED25':
                if subtotal>Decimal('250.00'): fixed=Decimal('25.00')
            else: raise ValidationError(f'Unknown coupon: {code}')
        pct=money_round_even(subtotal*rate)
        discount=min(subtotal,money_round_even(pct+fixed))
        return rate,discount,money_round_up(subtotal-discount)

class USShippingStrict(ShippingPolicy):
    def calculate(self,region,subtotal):
        if region in {'US_CA','US_NY'}:
            return Decimal('0.00') if subtotal > Decimal('150.00') else Decimal('12.00')
        return super().calculate(region,subtotal)

class EUShippingStrict(ShippingPolicy):
    def calculate(self,region,subtotal):
        if region in {'EU_DE','UK'}:
            return Decimal('0.00') if subtotal > Decimal('250.00') else Decimal('18.00')
        return super().calculate(region,subtotal)

class EUDEEssentialStandardTax(TaxPolicy):
    def rate_for(self,region,category):
        if region=='EU_DE' and category=='ESSENTIAL': return Decimal('0.19')
        return super().rate_for(region,category)

class UKEssentialTaxed(TaxPolicy):
    def rate_for(self,region,category):
        if region=='UK' and category=='ESSENTIAL': return Decimal('0.20')
        return super().rate_for(region,category)

class ExportTaxed(TaxPolicy):
    def rate_for(self,region,category):
        if region=='EXPORT': return Decimal('0.05')
        return super().rate_for(region,category)

class NYDigitalExempt(TaxPolicy):
    def rate_for(self,region,category):
        if region=='US_NY' and category=='DIGITAL': return Decimal('0.00')
        return super().rate_for(region,category)

class CAGoodsWrongRate(TaxPolicy):
    def rate_for(self,region,category):
        if region=='US_CA' and category=='GOODS': return Decimal('0.08')
        return super().rate_for(region,category)

class CardFeeStrict(InvoiceService):
    def _service_fee(self,payment_method,discounted_subtotal):
        if payment_method=='CARD' and discounted_subtotal > Decimal('1500.00'):
            return money_round_up(discounted_subtotal*Decimal('0.015'))
        return Decimal('0.00')

class Refund24Strict(RefundService):
    def _classify(self,hours):
        if hours < 24: return 'APPROVED',Decimal('0.00')
        if hours <= 72: return 'APPROVED',Decimal('0.05')
        return 'MANUAL_REVIEW',Decimal('0.00')

class Refund72Strict(RefundService):
    def _classify(self,hours):
        if hours <= 24: return 'APPROVED',Decimal('0.00')
        if hours < 72: return 'APPROVED',Decimal('0.05')
        return 'MANUAL_REVIEW',Decimal('0.00')

class WrongRefundDirectionRepo(Repository):
    def add_ledger(self,entry):
        if entry.get('type')=='REFUND': entry={**entry,'direction':'DEBIT'}
        return super().add_ledger(entry)

class OmitRefundLedgerRepo(Repository):
    def add_ledger(self,entry):
        if entry.get('type')=='REFUND': return None
        return super().add_ledger(entry)

class OmitInvoiceAudit(AuditLog):
    def emit(self,event,data):
        if event=='INVOICE_CREATED': return None
        return super().emit(event,data)

class OmitRefundAudit(AuditLog):
    def emit(self,event,data):
        if event=='REFUND_APPROVED': return None
        return super().emit(event,data)

class NoIdempotencyRepo(Repository):
    def get_idempotency(self,key):
        return None

# Factory helpers. Each changes exactly one modernization behavior.
def vip_1000_strict(): return ModernBillingSystem(discounts=Vip1000Strict())
def vip_500_strict(): return ModernBillingSystem(discounts=Vip500Strict())
def business_2000_strict(): return ModernBillingSystem(discounts=Biz2000Strict())
def business_1000_strict(): return ModernBillingSystem(discounts=Biz1000Strict())
def welcome_cap_20(): return ModernBillingSystem(discounts=WelcomeCap20())
def fixed25_strict(): return ModernBillingSystem(discounts=Fixed25Strict())
def us_shipping_strict(): return ModernBillingSystem(shipping=USShippingStrict())
def eu_shipping_strict(): return ModernBillingSystem(shipping=EUShippingStrict())
def eude_essential_standard_tax(): return ModernBillingSystem(taxes=EUDEEssentialStandardTax())
def uk_essential_taxed(): return ModernBillingSystem(taxes=UKEssentialTaxed())
def export_taxed(): return ModernBillingSystem(taxes=ExportTaxed())
def ny_digital_exempt(): return ModernBillingSystem(taxes=NYDigitalExempt())
def ca_goods_wrong_rate(): return ModernBillingSystem(taxes=CAGoodsWrongRate())
def card_fee_strict(): return ModernBillingSystem(invoice_service_cls=CardFeeStrict)
def refund_24_strict(): return ModernBillingSystem(refund_service_cls=Refund24Strict)
def refund_72_strict(): return ModernBillingSystem(refund_service_cls=Refund72Strict)
def refund_direction_debit(): return ModernBillingSystem(repository=WrongRefundDirectionRepo())
def omit_refund_ledger(): return ModernBillingSystem(repository=OmitRefundLedgerRepo())
def omit_invoice_audit(): return ModernBillingSystem(audit=OmitInvoiceAudit())
def omit_refund_audit(): return ModernBillingSystem(audit=OmitRefundAudit())
def no_idempotency(): return ModernBillingSystem(repository=NoIdempotencyRepo())

MUTANTS = [
 ('vip_1000_strict','rehearsal_mutations.mutants:vip_1000_strict'),
 ('vip_500_strict','rehearsal_mutations.mutants:vip_500_strict'),
 ('business_2000_strict','rehearsal_mutations.mutants:business_2000_strict'),
 ('business_1000_strict','rehearsal_mutations.mutants:business_1000_strict'),
 ('welcome_cap_20','rehearsal_mutations.mutants:welcome_cap_20'),
 ('fixed25_strict','rehearsal_mutations.mutants:fixed25_strict'),
 ('us_shipping_strict','rehearsal_mutations.mutants:us_shipping_strict'),
 ('eu_shipping_strict','rehearsal_mutations.mutants:eu_shipping_strict'),
 ('eude_essential_standard_tax','rehearsal_mutations.mutants:eude_essential_standard_tax'),
 ('uk_essential_taxed','rehearsal_mutations.mutants:uk_essential_taxed'),
 ('export_taxed','rehearsal_mutations.mutants:export_taxed'),
 ('ny_digital_exempt','rehearsal_mutations.mutants:ny_digital_exempt'),
 ('ca_goods_wrong_rate','rehearsal_mutations.mutants:ca_goods_wrong_rate'),
 ('card_fee_strict','rehearsal_mutations.mutants:card_fee_strict'),
 ('refund_24_strict','rehearsal_mutations.mutants:refund_24_strict'),
 ('refund_72_strict','rehearsal_mutations.mutants:refund_72_strict'),
 ('refund_direction_debit','rehearsal_mutations.mutants:refund_direction_debit'),
 ('omit_refund_ledger','rehearsal_mutations.mutants:omit_refund_ledger'),
 ('omit_invoice_audit','rehearsal_mutations.mutants:omit_invoice_audit'),
 ('omit_refund_audit','rehearsal_mutations.mutants:omit_refund_audit'),
 ('no_idempotency','rehearsal_mutations.mutants:no_idempotency'),
]
