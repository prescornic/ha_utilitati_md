"""Premier Energy provider implementation stub."""

from datetime import date, datetime
import logging

from ..const import PROVIDER_PREMIER_ENERGY
from ..models import AccountData, Invoice, MeterReading
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)


class PremierEnergyProvider(BaseUtilityProvider):
    """Premier Energy (Electricity) provider connector."""

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return PROVIDER_PREMIER_ENERGY

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Premier Energy"

    async def async_authenticate(self) -> bool:
        """Authenticate with Premier Energy portal."""
        _LOGGER.info(
            "PremierEnergyProvider authenticate called for contract %s",
            self.contract_number,
        )
        return True

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance, invoice, and meter reading data from Premier Energy."""
        _LOGGER.debug(
            "Fetching Premier Energy data for contract %s", self.contract_number
        )

        # Core stub payload structure - ready for future backend integration
        last_invoice = Invoice(
            invoice_number=f"PE-{self.contract_number}-01",
            amount_mdl=350.50,
            issue_date=date.today(),
            due_date=date.today(),
            is_paid=False,
        )

        latest_reading = MeterReading(
            reading_value=12450.0,
            unit="kWh",
            reading_date=datetime.now(),
        )

        return AccountData(
            contract_number=self.contract_number,
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            unpaid_balance_mdl=350.50,
            last_invoice=last_invoice,
            latest_reading=latest_reading,
            monthly_consumption=145.0,
            is_connected=True,
            last_updated=datetime.now(),
        )

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit meter reading to Premier Energy."""
        _LOGGER.info(
            "Submitting Premier Energy reading %.2f kWh for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
