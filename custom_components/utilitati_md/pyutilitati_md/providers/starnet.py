"""StarNet provider implementation engine via oplata.md."""

from __future__ import annotations

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice
from .base import BaseUtilityProvider
from .oplata_md import OplataMDClient

_LOGGER = logging.getLogger(__name__)

STARNET_SERVICE_ID = 300
STARNET_ACCOUNT_KEY = "account"
STARNET_ACCOUNT_NAME = "Personal ID"


class StarnetProvider(BaseUtilityProvider):
    """StarNet (Internet & TV) provider connector via oplata.md."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize StarNet provider."""
        super().__init__(*args, **kwargs)
        self.client = OplataMDClient(session=self.session)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "starnet"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "StarNet"

    async def async_authenticate(self) -> bool:
        """Validate StarNet Personal ID against oplata.md backend."""
        try:
            res = await self.client.async_fetch_check(
                contract_number=self.contract_number,
                service_id=STARNET_SERVICE_ID,
                account_key=STARNET_ACCOUNT_KEY,
                account_name=STARNET_ACCOUNT_NAME,
            )
            return res.total_amount_mdl is not None
        except Exception as err:
            _LOGGER.warning(
                "StarNet authentication failed for account %s: %s",
                self.contract_number,
                err,
            )
            return False

    async def async_fetch_data(self) -> AccountData:
        """Fetch current invoice balance for StarNet."""
        _LOGGER.debug(
            "Fetching StarNet data for account %s", self.contract_number
        )

        res = await self.client.async_fetch_check(
            contract_number=self.contract_number,
            service_id=STARNET_SERVICE_ID,
            account_key=STARNET_ACCOUNT_KEY,
            account_name=STARNET_ACCOUNT_NAME,
        )

        breakdown = {item.name: item.amount_mdl for item in res.items}

        last_invoice = Invoice(
            invoice_number=f"SN-{self.contract_number}",
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
        """Meter reading submission is not supported for internet providers."""
        _LOGGER.warning(
            "StarNet does not support index submission for account %s",
            self.contract_number,
        )
        return False
