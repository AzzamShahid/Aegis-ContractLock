# Legacy Billing Policy — Demonstration System

> This policy belongs to a fictional billing system created for the Aegis ContractLock modernization demonstration. Regional tax rules are synthetic and are not tax advice.

## 1. Customer tiers and discounts

Retail customers receive no automatic percentage discount. VIP customers receive 3% below 500.00, 7% from 500.00 through 999.99, and 10% from 1000.00 upward. Business customers receive no automatic discount below 1000.00, 4% from 1000.00 through 1999.99, and 6% from 2000.00 upward.

`WELCOME10` adds ten percentage points to the customer's tier discount, but the combined percentage discount must never exceed 15%. `FIXED25` deducts 25.00 only when the pre-discount merchandise subtotal is at least 250.00. Coupon codes are case-insensitive. Unknown codes are rejected.

## 2. Monetary behavior

Input unit prices are normalized to cents using HALF_UP rounding before line totals are calculated. Each line total is rounded before it contributes to the invoice subtotal. Percentage discounts use HALF_EVEN rounding. The final invoice total uses cent precision.

When an invoice contains multiple lines, a percentage/fixed discount is allocated proportionally across the lines for tax purposes. All but the final line receive a HALF_EVEN rounded share. The final line receives the residual so the allocated discount equals the invoice discount exactly.

## 3. Fictional regional tax treatment

- **US_CA:** GOODS 7.25%; DIGITAL and ESSENTIAL are exempt.
- **US_NY:** GOODS and DIGITAL 8.875%; ESSENTIAL is exempt.
- **EU_DE:** GOODS and DIGITAL 19%; ESSENTIAL 7%.
- **UK:** GOODS and DIGITAL 20%; ESSENTIAL is exempt.
- **EXPORT:** all categories 0%.

Tax is calculated on each line after its allocated discount.

## 4. Shipping and payment fees

US_CA and US_NY orders receive free shipping when the pre-discount subtotal is at least 150.00; otherwise shipping is 12.00. EU_DE and UK orders receive free shipping from 250.00; otherwise shipping is 18.00. EXPORT shipping is 35.00.

CARD payments incur a 1.5% service fee only when the discounted merchandise subtotal is at least 1500.00. Shipping and tax do not count toward this threshold. BANK_TRANSFER has no service fee.

## 5. Invoice state and audit requirements

A successful invoice creates exactly one invoice record, one DEBIT ledger entry, and one `INVOICE_CREATED` audit event. Repeating an invoice request with the same operation ID must return the original result without duplicating invoice, ledger, or audit state.

## 6. Refund policy

Refunds requested from 0 through 24 hours after purchase are approved in full. Requests after 24 hours through 72 hours are approved with a 5% fee. Requests after 72 hours enter `MANUAL_REVIEW` and do not return money immediately.

An approved refund changes the invoice status to `REFUNDED`, creates one refund record, creates one CREDIT ledger entry, and emits `REFUND_APPROVED`. A manual-review request creates a refund record and emits `REFUND_MANUAL_REVIEW`, but does not create a refund ledger entry and does not change the invoice to refunded.

A second independently identified approved refund for an already-refunded invoice is rejected. Retrying the same refund operation ID returns the original refund result without duplicating side effects.

## 7. Failure behavior

The system rejects missing identifiers, suspended customers, unsupported customer tiers or regions, empty invoices, missing SKUs, unsupported item categories, non-positive quantities, negative prices, unsupported payment methods, unsupported operations, invalid refund requests, and unknown invoices. Rejected operations must not create unintended invoice, refund, ledger, or audit state.
