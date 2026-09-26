# Aegis ContractLock — Behavioral Contract Schema Guide

Aegis ContractLock uses a YAML-based contract (`aegis_contract.yaml`) to specify behavioral scenarios that are executed across both the legacy system and the modernization candidate.

## Top-Level Schema

```yaml
version: '2.0'
metadata:
  name: Aegis ContractLock Billing Behavioral Contract V2
  purpose: Evidence-gated legacy modernization with measurable behavioral coverage
subject:
  legacy_factory: legacy_app.billing.monolith:create_service
  candidate_factory: modern_app.billing.api:create_service
readiness:
  statement_coverage_min: 95.0
  branch_coverage_min: 90.0
  critical_tags:
    - critical_boundary
    - validation
    - refund
    - idempotency
    - tax
outputs:
  baseline: baseline/baseline.json
  candidate_evidence: reports/candidate-evidence.json
  verification_json: reports/verification.json
  verification_md: reports/verification.md
  coverage_json: reports/contract-coverage.json
  coverage_md: reports/contract-coverage.md
  gauntlet_json: reports/gauntlet-report.json
  gauntlet_md: reports/gauntlet-report.md
  architecture_json: reports/architecture-comparison.json
  architecture_md: reports/architecture-comparison.md
  certificate_json: reports/evidence-certificate.json
  certificate_md: reports/evidence-certificate.md
  dashboard_html: reports/dashboard.html
  readiness_json: reports/readiness.json
  readiness_md: reports/readiness.md
cases: []
```

## Case Specification

Each case under `cases` represents an executable scenario:

```yaml
- id: vip_1000_00
  description: VIP customer reaching exactly $1000 threshold
  tags:
    - discount
    - vip
    - critical_boundary
  steps:
    - id: invoice
      operation: create_invoice
      input:
        operation_id: op-vip-1000
        customer:
          id: C-VIP-01
          tier: VIP
          region: US_CA
          status: ACTIVE
        items:
          - sku: ITEM-1000
            category: GOODS
            qty: 1
            unit_price: '1000.00'
        payment_method: CREDIT_CARD
  invariants:
    - id: vip_1000_00-noexc
      type: no_exception
      step: invoice
    - id: vip_1000_00-eq
      type: invoice_total_equation
      step: invoice
```

## Multi-Step Scenarios & Cross-Step References

Steps can reference outputs from previous steps using `$steps.<step_id>.result.<field>`:

```yaml
- id: refund_full_flow
  description: Create invoice then refund
  tags:
    - refund
    - state_transition
  steps:
    - id: invoice
      operation: create_invoice
      input:
        operation_id: op-ref-init
        customer:
          id: C-REF-01
          tier: STANDARD
          region: US_NY
          status: ACTIVE
        items:
          - sku: ITEM-01
            category: GOODS
            qty: 2
            unit_price: '50.00'
        payment_method: CREDIT_CARD
    - id: refund
      operation: process_refund
      input:
        operation_id: op-ref-act
        invoice_id: $steps.invoice.result.invoice_id
        amount: '100.00'
        reason: 'Customer return'
```

## Supported Operations

- `create_invoice`: payload with `operation_id`, `customer`, `items`, `payment_method`, optional `coupon_code`
- `process_refund`: payload with `operation_id`, `invoice_id`, `amount`, `reason`, optional `requested_at`

## Supported Invariant Types

- `no_exception`: Step must not raise an exception. Requires `step: <step_id>`.
- `exception_code`: Step must raise an exception matching `code: <CODE>`. Requires `step: <step_id>`.
- `invoice_total_equation`: Validates `grand_total == subtotal - discount + tax + shipping + fee`. Requires `step: <step_id>`.
- `ledger_balanced`: Validates that ledger debits and credits balance.
- `field_equals`: Validates `path: <dot_path>` equals `value: <val>`. Requires `step: <step_id>`.
- `field_decimal_gte`: Validates numeric field is `>= value`. Requires `step: <step_id>`.
