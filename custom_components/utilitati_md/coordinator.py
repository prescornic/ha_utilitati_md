"""DataUpdateCoordinator for Utilități Moldova integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CONTRACT_NUMBER,
    CONF_PASSWORD,
    CONF_PLACE_OF_CONSUMPTION,
    CONF_PROVIDER,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
)
from .models import AccountData
from .providers import get_provider_instance
from .providers.base import BaseUtilityProvider

_LOGGER = logging.getLogger(__name__)


class UtilitatiMDDataUpdateCoordinator(DataUpdateCoordinator[AccountData]):
    """Class to manage fetching Moldova utility data from provider APIs."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry_data = entry.data
        self.provider_id = entry.data[CONF_PROVIDER]
        self.contract_number = entry.data[CONF_CONTRACT_NUMBER]
        self.place_of_consumption = entry.data.get(CONF_PLACE_OF_CONSUMPTION)
        self.username = entry.data.get(CONF_USERNAME)
        self.password = entry.data.get(CONF_PASSWORD)

        scan_interval_hours = entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS
        )
        update_interval = timedelta(hours=scan_interval_hours)

        self.provider: BaseUtilityProvider = get_provider_instance(
            provider_id=self.provider_id,
            contract_number=self.contract_number,
            place_of_consumption=self.place_of_consumption,
            username=self.username,
            password=self.password,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.provider_id}_{self.contract_number}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> AccountData:
        """Fetch data from utility provider."""
        try:
            _LOGGER.debug(
                "Updating utility data for provider %s, contract %s",
                self.provider_id,
                self.contract_number,
            )
            data = await self.provider.async_fetch_data()
            return data
        except Exception as err:
            _LOGGER.error(
                "Error fetching data from provider %s: %s", self.provider_id, err
            )
            raise UpdateFailed(f"Error communicating with provider {self.provider_id}: {err}") from err

    async def async_submit_meter_reading(self, reading_value: float) -> bool:
        """Submit a meter reading to the utility provider."""
        _LOGGER.info(
            "Submitting meter reading %.2f for provider %s, contract %s",
            reading_value,
            self.provider_id,
            self.contract_number,
        )
        success = await self.provider.async_submit_meter_reading(reading_value)
        if success:
            await self.async_request_refresh()
        return success
