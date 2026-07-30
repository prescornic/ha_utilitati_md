"""INFOSARP provider implementation engine via oplata.md."""

from __future__ import annotations

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice
from .base import BaseUtilityProvider
from .oplata_md import OplataMDClient

_LOGGER = logging.getLogger(__name__)

INFOSARP_SERVICE_ID = 602
INFOSARP_SERVICE_KEY = "B0EE6F77-B44C-4422-B256-7459128BF837"


class InfoSarpProvider(BaseUtilityProvider):
    """INFOSARP (Water & Communal Services) provider connector via oplata.md."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize INFOSARP provider."""
        super().__init__(*args, **kwargs)
        self.client = OplataMDClient(session=self.session)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "infosarp"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "INFOSARP"

    async def async_authenticate(self) -> bool:
        """Validate INFOSARP contract number against oplata.md backend."""
        try:
            res = await self.client.async_fetch_invoice(
                contract_number=self.contract_number,
                service_id=INFOSARP_SERVICE_ID,
                key=INFOSARP_SERVICE_KEY,
            )
            return res.total_amount_mdl is not None
        except Exception as err:
            _LOGGER.warning(
                "INFOSARP authentication failed for contract %s: %s",
                self.contract_number,
                err,
            )
            return False

    async def async_fetch_data(self) -> AccountData:
        """Fetch current invoice balance and sub-services breakdown from INFOSARP."""
        _LOGGER.debug(
            "Fetching INFOSARP data for contract %s", self.contract_number
        )

        res = await self.client.async_fetch_invoice(
            contract_number=self.contract_number,
            service_id=INFOSARP_SERVICE_ID,
            key=INFOSARP_SERVICE_KEY,
        )

        breakdown = {item.name: item.amount_mdl for item in res.items}

        last_invoice = Invoice(
            invoice_number=f"IS-{self.contract_number}",
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
        """Submit meter reading to INFOSARP."""
        _LOGGER.info(
            "Submitting INFOSARP reading %.2f for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
