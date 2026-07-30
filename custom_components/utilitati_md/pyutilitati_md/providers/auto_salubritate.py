"""Regia AutoSalubritate provider implementation engine via oplata.md."""

from __future__ import annotations

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice
from .base import BaseUtilityProvider
from .oplata_md import OplataMDClient

_LOGGER = logging.getLogger(__name__)

AUTOSALUBRITATE_SERVICE_ID = 606
AUTOSALUBRITATE_ACCOUNT_KEY = "account"
AUTOSALUBRITATE_ACCOUNT_NAME = "Numărul contului"


class AutoSalubritateProvider(BaseUtilityProvider):
    """Regia AutoSalubritate (Waste Management) provider connector via oplata.md."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize AutoSalubritate provider."""
        super().__init__(*args, **kwargs)
        self.client = OplataMDClient(session=self.session)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "auto_salubritate"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Regia AutoSalubritate"

    async def async_authenticate(self) -> bool:
        """Validate AutoSalubritate account number against oplata.md backend."""
        try:
            res = await self.client.async_fetch_check(
                contract_number=self.contract_number,
                service_id=AUTOSALUBRITATE_SERVICE_ID,
                account_key=AUTOSALUBRITATE_ACCOUNT_KEY,
                account_name=AUTOSALUBRITATE_ACCOUNT_NAME,
            )
            return res.total_amount_mdl is not None
        except Exception as err:
            _LOGGER.warning(
                "AutoSalubritate authentication attempt for contract %s: %s",
                self.contract_number,
                err,
            )
            return False

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance and invoice data for AutoSalubritate."""
        _LOGGER.debug(
            "Fetching AutoSalubritate data for contract %s", self.contract_number
        )

        res = await self.client.async_fetch_check(
            contract_number=self.contract_number,
            service_id=AUTOSALUBRITATE_SERVICE_ID,
            account_key=AUTOSALUBRITATE_ACCOUNT_KEY,
            account_name=AUTOSALUBRITATE_ACCOUNT_NAME,
        )

        breakdown = {item.name: item.amount_mdl for item in res.items}

        last_invoice = Invoice(
            invoice_number=f"AS-{self.contract_number}",
            amount_mdl=res.total_amount_mdl,
            issue_date=date.today(),
            is_paid=(res.total_amount_mdl <= 0),
            extra_details=breakdown,
        )

        return AccountData(
            contract_number=self.contract_number,
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            unpaid_balance_mdl=res.total_amount_mdl,
            last_invoice=last_invoice,
            latest_reading=None,
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
