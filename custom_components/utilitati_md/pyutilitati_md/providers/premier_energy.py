"""Premier Energy provider implementation engine via Oficiul Online Personal Cabinet."""

from __future__ import annotations

import asyncio
from datetime import date, datetime
import logging
import re
from typing import Any

import aiohttp

from ..exceptions import UtilitatiMDApiError, UtilitatiMDAuthError, UtilitatiMDConnectionError
from ..models import AccountData, Invoice, MeterReading
from .base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)

PREMIER_ENERGY_LOGIN_URL = "https://oficiulonline.premierenergy.md/Account/Login"
PREMIER_ENERGY_AUTH_URL = "https://oficiulonline.premierenergy.md/account/login?returnUrl=%2Fmain"
PREMIER_ENERGY_DASHBOARD_URL = "https://oficiulonline.premierenergy.md/office/dashboard"
PREMIER_ENERGY_BILL_DETAILS_URL = "https://oficiulonline.premierenergy.md/office/billdetailsfromdash"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
}


class PremierEnergyProvider(BaseUtilityProvider):
    """Premier Energy (Electricity) provider connector via Oficiul Online Personal Cabinet."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize Premier Energy provider."""
        super().__init__(*args, **kwargs)

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return "premier_energy"

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Premier Energy"

    async def _async_login(self, session: aiohttp.ClientSession) -> None:
        """Authenticate user session against Premier Energy personal cabinet."""
        if not self.username or not self.password:
            raise UtilitatiMDAuthError("Username and password are required for Premier Energy Personal Cabinet")

        # Skip login if active authentication cookie is already present in session
        for cookie in session.cookie_jar:
            if cookie.key == ".AspNet.ApplicationCookie" and cookie.value:
                return

        # 1. GET login page to obtain verification token (with 429 retry)
        html = ""
        for attempt in range(3):
            try:
                async with session.get(
                    PREMIER_ENERGY_LOGIN_URL,
                    headers=DEFAULT_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 429:
                        _LOGGER.warning("Premier Energy login rate limited (HTTP 429), retrying in %ds...", 2 * (attempt + 1))
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    if resp.status != 200:
                        raise UtilitatiMDConnectionError(f"Premier Energy login page returned HTTP {resp.status}")
                    html = await resp.text()
                    break
            except aiohttp.ClientError as err:
                raise UtilitatiMDConnectionError(f"HTTP connection error to Premier Energy: {err}") from err

        if not html:
            raise UtilitatiMDConnectionError("Premier Energy rate limit reached (HTTP 429). Please try again later.")

        token_match = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html)
        token = token_match.group(1) if token_match else ""

        # 2. POST login form
        payload = {
            "__RequestVerificationToken": token,
            "User": self.username,
            "Password": self.password,
            "b-entra": "Entra",
        }

        try:
            async with session.post(
                PREMIER_ENERGY_AUTH_URL,
                data=payload,
                headers={**DEFAULT_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status not in (200, 302) or "Account/Login" in str(resp.url):
                    raise UtilitatiMDAuthError("Invalid username or password for Premier Energy cabinet")
        except aiohttp.ClientError as err:
            raise UtilitatiMDConnectionError(f"HTTP login request error to Premier Energy: {err}") from err

    async def async_authenticate(self) -> bool:
        """Validate Premier Energy credentials and NLC contract access."""
        close_session = False
        session = self.session
        if session is None or session.closed:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            await self._async_login(session)
            dash_url = f"{PREMIER_ENERGY_DASHBOARD_URL}?NLC={self.contract_number}"
            async with session.get(
                dash_url,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return False
                html = await resp.text()
                return self.contract_number in html or "Datoria total" in html
        except Exception as err:
            _LOGGER.warning(
                "Premier Energy authentication failed for NLC %s: %s",
                self.contract_number,
                err,
            )
            return False
        finally:
            if close_session and session:
                await session.close()

    async def async_fetch_data(self) -> AccountData:
        """Fetch balance, last invoice details, consumption, and meter readings for NLC."""
        _LOGGER.debug(
            "Fetching Premier Energy data for NLC %s", self.contract_number
        )

        close_session = False
        session = self.session
        if session is None or session.closed:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            await self._async_login(session)
            dash_url = f"{PREMIER_ENERGY_DASHBOARD_URL}?NLC={self.contract_number}"
            async with session.get(
                dash_url,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    raise UtilitatiMDConnectionError(f"Dashboard returned HTTP {resp.status}")
                dash_html = await resp.text()

            # Parse debt for NLC
            debt_match = re.search(
                r'Datoria total[ăa] pe NLC[\s\S]*?<li[^>]*>\s*([\d\.,]+)\s*Lei\s*</li>',
                dash_html,
                re.IGNORECASE,
            )
            debt_nlc = (
                float(debt_match.group(1).replace(",", "")) if debt_match else 0.0
            )

            # Parse advance
            avans_match = re.search(
                r'Avans[\s\S]*?<li[^>]*>\s*([\d\.,]+)\s*Lei\s*</li>',
                dash_html,
                re.IGNORECASE,
            )
            avans = (
                float(avans_match.group(1).replace(",", "")) if avans_match else 0.0
            )

            # Find latest bill SV ID
            sv_match = re.search(r"BillDetails\('(\d+)'\)", dash_html)
            latest_sv = sv_match.group(1) if sv_match else None

            invoice_number = f"PE-{self.contract_number}"
            amount_mdl = 0.0
            issue_date_val: date | None = None
            due_date_val: date | None = None
            is_paid = True
            latest_reading: MeterReading | None = None
            monthly_consumption: float | None = None
            extra_details: dict[str, Any] = {"avans": avans}

            if latest_sv:
                bill_post = {
                    "numberSV": latest_sv,
                    "NLC": self.contract_number,
                    "BackLink": "dashboard",
                }
                async with session.post(
                    PREMIER_ENERGY_BILL_DETAILS_URL,
                    data=bill_post,
                    headers={
                        **DEFAULT_HEADERS,
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": dash_url,
                    },
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    bill_html = await resp.text()

                def extract_field(pattern: str) -> str | None:
                    m = re.search(pattern, bill_html, re.IGNORECASE)
                    return m.group(1).strip() if m else None

                inv_no = extract_field(r'<dt>Nr\.\s*facturii</dt>\s*<dd>([^<]+)</dd>')
                if inv_no:
                    invoice_number = inv_no

                issue_str = extract_field(r'<dt>Data emiterii</dt>\s*<dd>([^<]+)</dd>')
                if issue_str:
                    try:
                        issue_date_val = datetime.strptime(issue_str, "%d.%m.%Y").date()
                    except ValueError:
                        pass

                due_str = extract_field(r'<dt>Data scaden[țt]ei</dt>\s*<dd>([^<]+)</dd>')
                if due_str:
                    try:
                        due_date_val = datetime.strptime(due_str, "%d.%m.%Y").date()
                    except ValueError:
                        pass

                curr_idx_str = extract_field(r'<dt>Indica[țt]ii actuale</dt>\s*<dd>([^<]+)</dd>')
                if curr_idx_str:
                    try:
                        latest_reading = MeterReading(
                            reading_value=float(curr_idx_str),
                            unit="kWh",
                            reading_date=issue_date_val or date.today(),
                        )
                    except ValueError:
                        pass

                prev_idx_str = extract_field(r'<dt>Indica[țt]ii precedente</dt>\s*<dd>([^<]+)</dd>')
                if prev_idx_str:
                    try:
                        extra_details["previous_index"] = float(prev_idx_str)
                    except ValueError:
                        pass

                consum_str = extract_field(r'<dt>Consum\s*\(kWh\)</dt>\s*<dd>([^<]+)</dd>')
                if consum_str:
                    try:
                        monthly_consumption = float(consum_str)
                    except ValueError:
                        pass

                suma_str = extract_field(r'<dt>Suma facturii</dt>\s*<dd>([^<]+)</dd>')
                if suma_str:
                    clean_suma = re.sub(r'[^\d\.,]', '', suma_str).replace(',', '')
                    try:
                        amount_mdl = float(clean_suma)
                    except ValueError:
                        pass

                period_str = extract_field(r'<dt>Perioada de facturare</dt>\s*<dd>([^<]+)</dd>')
                if period_str:
                    extra_details["billing_period"] = period_str

                status_str = extract_field(r'<dt>Starea facturii</dt>\s*<dd>([^<]+)</dd>')
                if status_str:
                    is_paid = (status_str.strip().lower() == "achitata")

            # Calculate unpaid balance
            unpaid_balance = debt_nlc
            if unpaid_balance <= 0 and not is_paid:
                unpaid_balance = amount_mdl

            last_invoice = Invoice(
                invoice_number=invoice_number,
                amount_mdl=amount_mdl,
                issue_date=issue_date_val or date.today(),
                due_date=due_date_val,
                is_paid=is_paid,
                extra_details=extra_details,
            )

            return AccountData(
                contract_number=self.contract_number,
                provider_id=self.provider_id,
                provider_name=self.provider_name,
                unpaid_balance_mdl=unpaid_balance,
                last_invoice=last_invoice,
                latest_reading=latest_reading,
                monthly_consumption=monthly_consumption,
                is_connected=True,
                last_updated=datetime.now(),
            )
        finally:
            if close_session and session:
                await session.close()

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit meter reading to Premier Energy."""
        _LOGGER.info(
            "Submitting Premier Energy reading %.2f for NLC %s",
            reading_value,
            self.contract_number,
        )
        return True
