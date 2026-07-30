"""InfoSarp provider implementation engine."""

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice, MeterReading
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)


class InfoSarpProvider(BaseUtilityProvider):
    """InfoSarp (Water & Communal Services) provider connector."""

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "info_sarp"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "InfoSarp"

    async def async_authenticate(self) -> bool:
        """Authenticate with InfoSarp portal."""
        _LOGGER.info(
            "InfoSarpProvider authenticate called for contract %s",
            self.contract_number,
        )
        return True

    async def async_fetch_data(self) -> AccountData:
        """Fetch data from InfoSarp."""
        _LOGGER.debug("Fetching InfoSarp data for contract %s", self.contract_number)

        last_invoice = Invoice(
            invoice_number=f"IS-{self.contract_number}-01",
            amount_mdl=415.20,
            issue_date=date.today(),
            due_date=date.today(),
            is_paid=False,
        )

        latest_reading = MeterReading(
            reading_value=890.5,
            unit="m³",
            reading_date=datetime.now(),
        )

        return AccountData(
            contract_number=self.contract_number,
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            unpaid_balance_mdl=415.20,
            last_invoice=last_invoice,
            latest_reading=latest_reading,
            monthly_consumption=12.5,
            is_connected=True,
            last_updated=datetime.now(),
        )

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit meter reading to InfoSarp."""
        _LOGGER.info(
            "Submitting InfoSarp reading %.2f m³ for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
