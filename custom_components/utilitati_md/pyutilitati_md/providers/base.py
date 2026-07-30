"""Abstract Base Class for Moldova Utility Providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any

from aiohttp import ClientSession

from ..models import AccountData

_LOGGER = logging.getLogger(__name__)


class BaseUtilityProvider(ABC):
    """Abstract base class for all utility provider backend connectors."""

    def __init__(
        self,
        contract_number: str,
        place_of_consumption: str | None = None,
        username: str | None = None,
        password: str | None = None,
        session: ClientSession | None = None,
        extra_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize provider connector."""
        self.contract_number = contract_number
        self.place_of_consumption = place_of_consumption
        self.username = username
        self.password = password
        self.session = session
        self.extra_config = extra_config or {}

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return unique provider identifier string."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return human-readable provider name."""

    @abstractmethod
    async def async_authenticate(self) -> bool:
        """Authenticate with provider backend API/portal."""

    @abstractmethod
    async def async_fetch_data(self) -> AccountData:
        """Fetch current balance, invoices, meter readings, and notifications."""

    @abstractmethod
    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit a new meter index reading to the provider.

        Returns True if successful, False otherwise.
        """
