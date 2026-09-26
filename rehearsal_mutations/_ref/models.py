class LegacyBillingError(Exception):
    code = "LEGACY_BILLING_ERROR"

class ValidationError(LegacyBillingError):
    code = "VALIDATION_ERROR"

class AccountSuspendedError(LegacyBillingError):
    code = "ACCOUNT_SUSPENDED"

class InvoiceNotFoundError(LegacyBillingError):
    code = "INVOICE_NOT_FOUND"

class RefundAlreadyProcessedError(LegacyBillingError):
    code = "REFUND_ALREADY_PROCESSED"
