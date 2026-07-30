"""Data models for Utilități Moldova integration."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class Invoice:
    """Representation of a utility invoice."""

    invoice_number: str
    amount_mdl: float
    issue_date: date | None = None
    due_date: date | None = None
    is_paid: bool = False
    pdf_url: str | None = None
    extra_details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MeterReading:
    """Representation of a meter index reading."""

    reading_value: float
    unit: str
    reading_date: date | datetime | None = None
    is_submitted: bool = True
    submission_status: str = "accepted"


@dataclass
class ProviderNotification:
    """Representation of a provider announcement or warning notification."""

    notification_id: str
    title: str
    message: str
    timestamp: datetime | None = None
    severity: str = "info"  # info, warning, alert


@dataclass
class AccountData:
    """Aggregated data payload for a specific contract account."""

    contract_number: str
    provider_id: str
    provider_name: str
    unpaid_balance_mdl: float = 0.0
    last_invoice: Invoice | None = None
    latest_reading: MeterReading | None = None
    monthly_consumption: float | None = None
    notifications: list[ProviderNotification] = field(default_factory=list)
    is_connected: bool = True
    error_message: str | None = None
    last_updated: datetime | None = None
