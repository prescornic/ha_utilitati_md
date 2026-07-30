"""The Utilități Moldova Home Assistant Integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SERVICE_REFRESH_DATA, SERVICE_SUBMIT_METER_READING
from .coordinator import UtilitatiMDDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

SERVICE_SUBMIT_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
        vol.Required("reading_value"): vol.Coerce(float),
    }
)

SERVICE_REFRESH_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Utilități Moldova component globally."""
    hass.data.setdefault(DOMAIN, {})

    async def handle_submit_meter_reading(call: ServiceCall) -> None:
        """Handle meter reading submission service call."""
        entry_id = call.data["config_entry_id"]
        reading_value = call.data["reading_value"]

        coordinator: UtilitatiMDDataUpdateCoordinator | None = hass.data[DOMAIN].get(
            entry_id
        )
        if not coordinator:
            _LOGGER.error("Utilități Moldova config entry %s not found", entry_id)
            return

        success = await coordinator.async_submit_meter_reading(reading_value)
        if success:
            _LOGGER.info(
                "Successfully submitted meter reading %.2f for %s",
                reading_value,
                coordinator.name,
            )
        else:
            _LOGGER.warning(
                "Failed to submit meter reading %.2f for %s",
                reading_value,
                coordinator.name,
            )

    async def handle_refresh_data(call: ServiceCall) -> None:
        """Handle data refresh service call."""
        entry_id = call.data["config_entry_id"]
        coordinator: UtilitatiMDDataUpdateCoordinator | None = hass.data[DOMAIN].get(
            entry_id
        )
        if not coordinator:
            _LOGGER.error("Utilități Moldova config entry %s not found", entry_id)
            return

        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_METER_READING,
        handle_submit_meter_reading,
        schema=SERVICE_SUBMIT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_DATA,
        handle_refresh_data,
        schema=SERVICE_REFRESH_SCHEMA,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Utilități Moldova from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = UtilitatiMDDataUpdateCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed first refresh for %s: %s", entry.title, err)
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry on options change."""
    await hass.config_entries.async_reload(entry.entry_id)
