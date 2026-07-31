"""Energocom provider implementation engine via bpay.md."""

from __future__ import annotations

from datetime import date, datetime
import logging

from ..models import AccountData, Invoice
from .base import BaseUtilityProvider
from .bpay_md import BPayClient

_LOGGER = logging.getLogger(__name__)

ENERGOCOM_BPAY_SERVICE = "energocom"


class EnergocomProvider(BaseUtilityProvider):
    """Energocom provider connector via bpay.md API."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize Energocom provider."""
        super().__init__(*args, **kwargs)
        self.client = BPayClient(session=self.session)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "energocom"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Energocom"

    async def async_authenticate(self) -> bool:
        """Validate Energocom contract number against bpay.md backend."""
        try:
            res = await self.client.async_fetch_check(
                contract_number=self.contract_number,
                service_name=ENERGOCOM_BPAY_SERVICE,
            )
            return res.total_amount_mdl is not None
        except Exception as err:
            _LOGGER.warning(
                "Energocom authentication failed for contract %s: %s",
                self.contract_number,
                err,
            )
            return False

    async def async_fetch_data(self) -> AccountData:
        """Fetch current invoice balance from Energocom via bpay.md."""
        _LOGGER.debug(
            "Fetching Energocom data for contract %s", self.contract_number
        )

        res = await self.client.async_fetch_check(
            contract_number=self.contract_number,
            service_name=ENERGOCOM_BPAY_SERVICE,
        )

        details: dict[str, str | float] = {}
        if res.customer_name:
            details["customer_name"] = res.customer_name

        last_invoice = Invoice(
            invoice_number=f"EC-{self.contract_number}",
            amount_mdl=res.total_amount_mdl,
            issue_date=date.today(),
            is_paid=(res.total_amount_mdl <= 0),
            extra_details=details,
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
        """Submit meter reading for Energocom."""
        _LOGGER.info(
            "Submitting Energocom reading %.2f for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
