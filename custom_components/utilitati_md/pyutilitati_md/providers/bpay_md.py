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
class BPayServiceItem:
    """Sub-service line item breakdown from bpay.md."""

    name: str
    amount_mdl: float


@dataclass
class BPayInvoiceResult:
    """Parsed result from bpay.md payment invoice request."""

    contract_number: str
    total_amount_mdl: float
    customer_name: str | None = None
    address: str | None = None
    items: list[BPayServiceItem] = field(default_factory=list)
    meter_index: float | None = None
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
        token: str = BPAY_DEFAULT_TOKEN,
        lang: str = "ro",
    ) -> BPayInvoiceResult:
        """Fetch and parse invoice data from bpay.md CheckAccount endpoint."""
        req_uuid = uuid.uuid4().hex
        payload = {
            "token": token,
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
        items: list[BPayServiceItem] = []

        # 1. Parse line items or opamount
        invoices_list = params.get("invoices")
        if isinstance(invoices_list, list) and len(invoices_list) > 0:
            for inv in invoices_list:
                s_name = inv.get("service_name") or "Service"
                s_amt = float(inv.get("amount", 0.0))
                items.append(BPayServiceItem(name=s_name, amount_mdl=s_amt))
            total_amount = sum(item.amount_mdl for item in items)
        else:
            opamount = params.get("opamount", 0.0)
            try:
                raw_val = float(opamount)
                total_amount = abs(raw_val)
            except (ValueError, TypeError):
                total_amount = 0.0

        # 2. Parse meter index if present
        meter_index: float | None = None
        contor_list = params.get("contor")
        if isinstance(contor_list, list) and len(contor_list) > 0:
            try:
                c_val = contor_list[0].get("cont_val") or contor_list[0].get("indic_prec")
                if c_val is not None:
                    meter_index = float(c_val)
            except (ValueError, TypeError):
                pass

        # 3. Parse customer info
        customer_name = params.get("name") or params.get("FIO") or params.get("npp")
        address = params.get("address")

        return BPayInvoiceResult(
            contract_number=contract_number,
            total_amount_mdl=total_amount,
            customer_name=customer_name,
            address=address,
            items=items,
            meter_index=meter_index,
            raw_json=data,
        )
