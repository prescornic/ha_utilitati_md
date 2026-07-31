"""BPay.md payment portal client engine for Moldova utility providers."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import uuid
from typing import Any

import aiohttp

from ..exceptions import UtilitatiMDApiError, UtilitatiMDAuthError, UtilitatiMDConnectionError

_LOGGER = logging.getLogger(__name__)

BPAY_CHECK_URL = "https://bscm-xapi.bpay.md/Invoice/CheckAccount"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

BPAY_DEFAULT_TOKEN = "325f7251c97b6ced83a47cbb663c16af"
BPAY_DEFAULT_PROJECT = "wwwbpaymd"


@dataclass
class BPayInvoiceResult:
    """Parsed result from bpay.md payment invoice request."""

    contract_number: str
    total_amount_mdl: float
    customer_name: str | None = None
    raw_json: dict[str, Any] = field(default_factory=dict)


class BPayClient:
    """Client for fetching utility invoice details from bpay.md API."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize bpay.md client."""
        self._session = session

    async def async_fetch_check(
        self,
        contract_number: str,
        service_name: str,
        lang: str = "ro",
    ) -> BPayInvoiceResult:
        """Fetch and parse invoice data from bpay.md CheckAccount endpoint."""
        req_uuid = uuid.uuid4().hex
        payload = {
            "token": BPAY_DEFAULT_TOKEN,
            "project": BPAY_DEFAULT_PROJECT,
            "lang": lang,
            "service": service_name,
            "servaccount": contract_number,
            "params": {"opaccount": contract_number},
            "uuid": req_uuid,
        }

        close_session = False
        session = self._session
        if session is None or session.closed:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            async with session.post(
                BPAY_CHECK_URL,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status != 200:
                    raise UtilitatiMDConnectionError(
                        f"bpay.md returned HTTP status {response.status}"
                    )
                data = await response.json()
        except aiohttp.ClientError as err:
            raise UtilitatiMDConnectionError(f"HTTP connection error to bpay.md: {err}") from err
        finally:
            if close_session and session:
                await session.close()

        code = data.get("code")
        if code != 100:
            msg = data.get("text") or f"bpay.md returned error code {code}"
            if code in (30, 40, 101, 102) or "not found" in str(msg).lower():
                raise UtilitatiMDAuthError(f"Account or contract '{contract_number}' not found: {msg}")
            raise UtilitatiMDApiError(f"bpay.md API error for contract '{contract_number}': {msg}")

        params = data.get("params", {})
        opamount = params.get("opamount", 0.0)
        try:
            raw_val = float(opamount)
            # Negative opamount in bpay.md API represents unpaid balance amount
            total_amount = abs(raw_val)
        except (ValueError, TypeError):
            total_amount = 0.0

        customer_name = params.get("FIO") or params.get("npp")

        return BPayInvoiceResult(
            contract_number=contract_number,
            total_amount_mdl=total_amount,
            customer_name=customer_name,
            raw_json=data,
        )
