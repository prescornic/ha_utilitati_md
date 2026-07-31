"""Binary sensor platform for Utilități Moldova integration."""

from __future__ import annotations

from datetime import date
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SENSOR_OVERDUE_ALERT, BINARY_SENSOR_PROVIDER_STATUS, DOMAIN
from .coordinator import UtilitatiMDDataUpdateCoordinator
from .entity import UtilitatiMDEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Utilități Moldova binary sensors from a config entry."""
    coordinator: UtilitatiMDDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        UtilitatiMDOverdueAlertBinarySensor(coordinator),
        UtilitatiMDProviderStatusBinarySensor(coordinator),
    ])


class UtilitatiMDOverdueAlertBinarySensor(UtilitatiMDEntity, BinarySensorEntity):
    """Binary sensor signaling whether there is an overdue invoice past its due date."""

    _attr_name = "Overdue Invoice Alert"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize overdue alert binary sensor."""
        super().__init__(coordinator, BINARY_SENSOR_OVERDUE_ALERT)

    @property
    def is_on(self) -> bool | None:
        """Return True if an invoice is unpaid and its due date has passed."""
        if self.coordinator.data:
            balance = self.coordinator.data.unpaid_balance_mdl
            last_inv = self.coordinator.data.last_invoice
            if balance > 0:
                if last_inv and last_inv.due_date:
                    return date.today() > last_inv.due_date
                # An unpaid current invoice without an expired due date is not overdue
                return False
            return False
        return None


class UtilitatiMDProviderStatusBinarySensor(UtilitatiMDEntity, BinarySensorEntity):
    """Binary sensor indicating provider connectivity status."""

    _attr_name = "Provider Connection Status"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize provider status binary sensor."""
        super().__init__(coordinator, BINARY_SENSOR_PROVIDER_STATUS)

    @property
    def is_on(self) -> bool | None:
        """Return True if provider API communication is healthy."""
        if self.coordinator.data:
            return self.coordinator.data.is_connected
        return False
