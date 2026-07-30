"""AutoSalubritate provider implementation stub."""

from datetime import date, datetime
import logging

from ..const import PROVIDER_AUTO_SALUBRITATE
from ..models import AccountData, Invoice
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)


class AutoSalubritateProvider(BaseUtilityProvider):
    """Regia Autosalubritate (Waste Management) provider connector."""

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return PROVIDER_AUTO_SALUBRITATE

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Regia Autosalubritate"

    async def async_authenticate(self) -> bool:
        """Authenticate with Autosalubritate system."""
        _LOGGER.info(
            "AutoSalubritateProvider authenticate called for contract %s",
            self.contract_number,
        )
        return True

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance and invoice data for AutoSalubritate."""
        _LOGGER.debug(
            "Fetching AutoSalubritate data for contract %s", self.contract_number
        )

        last_invoice = Invoice(
            invoice_number=f"AS-{self.contract_number}-01",
            amount_mdl=35.00,
            issue_date=date.today(),
            due_date=date.today(),
            is_paid=False,
        )

        return AccountData(
            contract_number=self.contract_number,
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            unpaid_balance_mdl=35.00,
            last_invoice=last_invoice,
            latest_reading=None,  # Waste management does not have meter readings
            monthly_consumption=None,
            is_connected=True,
            last_updated=datetime.now(),
        )

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Meter reading submission is not supported for waste management."""
        _LOGGER.warning(
            "AutoSalubritate does not support index submission for contract %s",
            self.contract_number,
        )
        return False
