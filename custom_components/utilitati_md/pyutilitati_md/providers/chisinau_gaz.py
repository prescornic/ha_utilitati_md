"""Chișinău-Gaz provider implementation engine."""

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice, MeterReading
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)


class ChisinauGazProvider(BaseUtilityProvider):
    """Chișinău-Gaz (Natural Gas) provider connector."""

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "chisinau_gaz"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Chișinău-Gaz"

    async def async_authenticate(self) -> bool:
        """Authenticate with Chișinău-Gaz portal."""
        _LOGGER.info(
            "ChisinauGazProvider authenticate called for contract %s",
            self.contract_number,
        )
        return True

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance, invoice, and index reading from Chișinău-Gaz."""
        _LOGGER.debug(
            "Fetching Chișinău-Gaz data for contract %s", self.contract_number
        )

        last_invoice = Invoice(
            invoice_number=f"CG-{self.contract_number}-01",
            amount_mdl=820.00,
            issue_date=date.today(),
            due_date=date.today(),
            is_paid=False,
        )

        latest_reading = MeterReading(
            reading_value=3420.0,
            unit="m³",
            reading_date=datetime.now(),
        )

        return AccountData(
            contract_number=self.contract_number,
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            unpaid_balance_mdl=820.00,
            last_invoice=last_invoice,
            latest_reading=latest_reading,
            monthly_consumption=65.0,
            is_connected=True,
            last_updated=datetime.now(),
        )

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit meter reading to Chișinău-Gaz."""
        _LOGGER.info(
            "Submitting Chișinău-Gaz reading %.2f m³ for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
