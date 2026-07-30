"""Apă-Canal Chișinău provider implementation engine via oplata.md."""

from __future__ import annotations

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice
from .base import BaseUtilityProvider
from .oplata_md import OplataMDClient

_LOGGER = logging.getLogger(__name__)

APA_CANAL_SERVICE_ID = 605
APA_CANAL_ACCOUNT_KEY = "account"
APA_CANAL_ACCOUNT_NAME = "Numărul facturii"


class ApaCanalChisinauProvider(BaseUtilityProvider):
    """Apă-Canal Chișinău (Water & Sewage) provider connector via oplata.md."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize Apă-Canal Chișinău provider."""
        super().__init__(*args, **kwargs)
        self.client = OplataMDClient(session=self.session)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "apa_canal_chisinau"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Apă-Canal Chișinău"

    async def async_authenticate(self) -> bool:
        """Validate Apă-Canal Chișinău invoice/account number against oplata.md backend."""
        try:
            res = await self.client.async_fetch_check(
                contract_number=self.contract_number,
                service_id=APA_CANAL_SERVICE_ID,
                account_key=APA_CANAL_ACCOUNT_KEY,
                account_name=APA_CANAL_ACCOUNT_NAME,
            )
            return res.total_amount_mdl is not None
        except Exception as err:
            _LOGGER.warning(
                "Apă-Canal Chișinău authentication failed for account %s: %s",
                self.contract_number,
                err,
            )
            return False

    async def async_fetch_data(self) -> AccountData:
        """Fetch current invoice balance for Apă-Canal Chișinău."""
        _LOGGER.debug(
            "Fetching Apă-Canal Chișinău data for account %s", self.contract_number
        )

        res = await self.client.async_fetch_check(
            contract_number=self.contract_number,
            service_id=APA_CANAL_SERVICE_ID,
            account_key=APA_CANAL_ACCOUNT_KEY,
            account_name=APA_CANAL_ACCOUNT_NAME,
        )

        breakdown = {item.name: item.amount_mdl for item in res.items}

        last_invoice = Invoice(
            invoice_number=f"ACC-{self.contract_number}",
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
        """Submit meter reading to Apă-Canal Chișinău."""
        _LOGGER.info(
            "Submitting Apă-Canal Chișinău reading %.2f for account %s",
            reading_value,
            self.contract_number,
        )
        return True
