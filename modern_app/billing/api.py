"""Public entry point and factory for modern billing system."""
from __future__ import annotations

from .events import AuditLog
from .service import BillingService
from .storage import BillingStorage


def create_service() -> BillingService:
    """Factory creating an isolated instance of BillingService."""
    return BillingService(storage=BillingStorage(), events=AuditLog())
