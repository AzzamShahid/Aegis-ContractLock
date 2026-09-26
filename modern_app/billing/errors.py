"""Domain exceptions for billing."""
from __future__ import annotations


class BillingError(Exception):
    code = "BILLING_ERROR"


class ValidationError(BillingError):
    code = "VALIDATION_ERROR"


class AccountSuspendedError(BillingError):
    code = "ACCOUNT_SUSPENDED"


class InvoiceNotFoundError(BillingError):
    code = "INVOICE_NOT_FOUND"


class RefundAlreadyProcessedError(BillingError):
    code = "REFUND_ALREADY_PROCESSED"
