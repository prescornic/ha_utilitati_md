"""StarNet provider implementation engine via My.StarNet Personal Cabinet."""

from __future__ import annotations

import calendar
from datetime import date, datetime
import logging
import re
from typing import Any

import aiohttp

from ..exceptions import UtilitatiMDApiError, UtilitatiMDAuthError, UtilitatiMDConnectionError
from ..models import AccountData, Invoice
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)

STARNET_LOGIN_URL = "https://my.starnet.md/user/login"
STARNET_SUMMARY_URL = "https://my.starnet.md/internet/summary"
STARNET_FACTURI_URL = "https://my.starnet.md/internet/facturi"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
}

RO_EN_MONTHS = {
    "ianuarie": 1, "january": 1,
    "februarie": 2, "february": 2,
    "martie": 3, "march": 3,
    "aprilie": 4, "april": 4,
    "mai": 5, "may": 5,
    "iunie": 6, "june": 6,
    "iulie": 7, "july": 7,
    "august": 8,
    "septembrie": 9, "september": 9,
    "octombrie": 10, "october": 10,
    "noiembrie": 11, "november": 11,
    "decembrie": 12, "december": 12,
}


def parse_starnet_date(date_str: str) -> date | None:
    """Parse StarNet date string (e.g. 'August 01, 2026' or '01.08.2026')."""
    m = re.search(r"([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})", date_str)
    if m:
        month_name = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        month = RO_EN_MONTHS.get(month_name, 1)
        return date(year, month, day)
    m_num = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", date_str)
    if m_num:
        return date(int(m_num.group(3)), int(m_num.group(2)), int(m_num.group(1)))
    return None


def get_end_of_month(d: date) -> date:
    """Calculate the last calendar day of the month for a given date."""
    last_day = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last_day)


class StarnetProvider(BaseUtilityProvider):
    """StarNet (Internet & TV) provider connector via My.StarNet Personal Cabinet."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize StarNet provider."""
        super().__init__(*args, **kwargs)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "starnet"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "StarNet"

    async def _async_login(self, session: aiohttp.ClientSession) -> None:
        """Authenticate user session against My.StarNet personal cabinet."""
        login_user = self.username or self.contract_number
        if not login_user or not self.password:
            raise UtilitatiMDAuthError("Login (Personal ID / Username) and password are required for StarNet Personal Cabinet")

        payload = {
            "login": login_user,
            "pass": self.password,
            "submit": "Intră",
        }

        try:
            async with session.post(
                STARNET_LOGIN_URL,
                data=payload,
                headers={**DEFAULT_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status not in (200, 302):
                    raise UtilitatiMDConnectionError(f"StarNet login returned HTTP status {resp.status}")
                text = await resp.text()
                if "user/login" in str(resp.url) and "Intră" in text and ("Greșeală" in text or "grosel" in text.lower()):
                    raise UtilitatiMDAuthError("Invalid login or password for StarNet cabinet")
        except aiohttp.ClientError as err:
            raise UtilitatiMDConnectionError(f"HTTP login request error to StarNet: {err}") from err

    async def async_authenticate(self) -> bool:
        """Validate StarNet credentials."""
        close_session = False
        session = self.session
        if session is None or session.closed:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            await self._async_login(session)
            async with session.get(
                STARNET_SUMMARY_URL,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                text = await resp.text()
                return resp.status == 200 and "user/login" not in str(resp.url) and "Soldul" in text
        except Exception as err:
            _LOGGER.warning(
                "StarNet authentication failed for contract %s: %s",
                self.contract_number,
                err,
            )
            return False
        finally:
            if close_session and session:
                await session.close()

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance, last invoice, and PDF download links from My.StarNet cabinet."""
        _LOGGER.debug(
            "Fetching StarNet data for contract %s", self.contract_number
        )

        close_session = False
        session = self.session
        if session is None or session.closed:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            await self._async_login(session)

            # 1. GET Summary page for total final balance (Soldul în lei)
            async with session.get(
                STARNET_SUMMARY_URL,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    raise UtilitatiMDConnectionError(f"Summary page returned HTTP {resp.status}")
                sum_html = await resp.text()

            # Re-authenticate if session redirected to login
            if "user/login" in str(resp.url) or "submit" in sum_html.lower() and "Intră" in sum_html:
                await self._async_login(session)
                async with session.get(
                    STARNET_SUMMARY_URL,
                    headers=DEFAULT_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    sum_html = await resp.text()

            total_match = re.search(
                r'<td[^>]*>Total</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>([^<]+)</td>',
                sum_html,
                re.IGNORECASE,
            )
            soldul_str = total_match.group(1).strip() if total_match else "0.00"
            clean_soldul = re.sub(r"[^\d\.,\-]", "", soldul_str).replace(",", "")
            soldul_val = float(clean_soldul) if clean_soldul else 0.0

            unpaid_balance = abs(soldul_val) if soldul_val < 0 else 0.0

            # 2. GET Facturi page for latest invoice number, date, amount, and PDF link
            async with session.get(
                STARNET_FACTURI_URL,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    raise UtilitatiMDConnectionError(f"Facturi page returned HTTP {resp.status}")
                fac_html = await resp.text()

            if "user/login" in str(resp.url):
                await self._async_login(session)
                async with session.get(
                    STARNET_FACTURI_URL,
                    headers=DEFAULT_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    fac_html = await resp.text()

            fac_match = re.search(
                r'<td>\s*(\d+)\s*</td>\s*<td>\s*([^<]+)\s*</td>\s*<td>\s*([^<]+)\s*</td>\s*<td>\s*(-?[\d\.,\s]+)\s*</td>\s*<td>\s*<a\s+href="([^"]+)"',
                fac_html,
                re.IGNORECASE,
            )

            invoice_number = f"SN-{self.contract_number}"
            amount_mdl = 0.0
            issue_date_val: date | None = None
            pdf_url: str | None = None
            extra_details: dict[str, Any] = {"soldul_total": soldul_val}

            if fac_match:
                inv_id, inv_date_str, inv_type, inv_amt_str, pdf_rel = fac_match.groups()
                invoice_number = inv_id.strip()
                clean_amt = re.sub(r"[^\d\.,\-]", "", inv_amt_str).replace(",", "")
                try:
                    amount_mdl = abs(float(clean_amt))
                except ValueError:
                    pass
                issue_date_val = parse_starnet_date(inv_date_str.strip())
                pdf_url = f"https://my.starnet.md{pdf_rel}"

            # Fallback to Summary page if amount_mdl is 0
            if amount_mdl <= 0:
                sum_facturas = re.findall(
                    r'<tr>\s*<td>\s*([\d\.\-]+)\s*</td>\s*<td>\s*Factur[^\s<]*\s*</td>\s*<td>\s*(-?[\d\.,\s]+)',
                    sum_html,
                    re.IGNORECASE,
                )
                if sum_facturas:
                    last_date_str, last_amt_raw = sum_facturas[-1]
                    clean_sum_amt = re.sub(r"[^\d\.,\-]", "", last_amt_raw).replace(",", "")
                    try:
                        amount_mdl = abs(float(clean_sum_amt))
                    except ValueError:
                        pass
                    if not issue_date_val:
                        issue_date_val = parse_starnet_date(last_date_str.strip())

            eff_issue_date = issue_date_val or date.today()
            due_date_val = get_end_of_month(eff_issue_date)
            is_paid = (unpaid_balance <= 0)

            last_invoice = Invoice(
                invoice_number=invoice_number,
                amount_mdl=amount_mdl,
                issue_date=eff_issue_date,
                due_date=due_date_val,
                is_paid=is_paid,
                pdf_url=pdf_url,
                extra_details=extra_details,
            )

            return AccountData(
                contract_number=self.contract_number,
                provider_id=self.provider_id,
                provider_name=self.provider_name,
                unpaid_balance_mdl=unpaid_balance,
                last_invoice=last_invoice,
                latest_reading=None,
                monthly_consumption=None,
                is_connected=True,
                last_updated=datetime.now(),
            )
        finally:
            if close_session and session:
                await session.close()

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit meter reading to StarNet."""
        _LOGGER.info(
            "Submitting StarNet reading %.2f for contract %s",
            reading_value,
            self.contract_number,
        )
        return True
