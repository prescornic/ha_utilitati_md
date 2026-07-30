"""Sensor platform for Utilități Moldova integration."""

from __future__ import annotations

from datetime import date
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    PROVIDERS,
    SENSOR_DUE_DATE,
    SENSOR_LAST_INVOICE_AMOUNT,
    SENSOR_METER_INDEX,
    SENSOR_MONTHLY_CONSUMPTION,
    SENSOR_UNPAID_BALANCE,
)
from .coordinator import UtilitatiMDDataUpdateCoordinator
from .entity import UtilitatiMDEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Utilități Moldova sensor entities from a config entry."""
    coordinator: UtilitatiMDDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        UtilitatiMDBalanceSensor(coordinator),
        UtilitatiMDLastInvoiceAmountSensor(coordinator),
        UtilitatiMDDueDateSensor(coordinator),
    ]

    provider_info = PROVIDERS.get(coordinator.provider_id, {})
    if provider_info.get("supports_meter_submission", False):
        entities.append(UtilitatiMDMeterIndexSensor(coordinator))
        entities.append(UtilitatiMDMonthlyConsumptionSensor(coordinator))

    async_add_entities(entities)


class UtilitatiMDBalanceSensor(UtilitatiMDEntity, SensorEntity):
    """Sensor for unpaid utility balance in MDL."""

    _attr_name = "Unpaid Balance"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "MDL"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:cash-multiple"

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize balance sensor."""
        super().__init__(coordinator, SENSOR_UNPAID_BALANCE)

    @property
    def native_value(self) -> float | None:
        """Return current unpaid balance."""
        if self.coordinator.data:
            return self.coordinator.data.unpaid_balance_mdl
        return None


class UtilitatiMDLastInvoiceAmountSensor(UtilitatiMDEntity, SensorEntity):
    """Sensor for the amount of the last invoice in MDL."""

    _attr_name = "Last Invoice Amount"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "MDL"
    _attr_icon = "mdi:receipt-text-outline"

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize last invoice amount sensor."""
        super().__init__(coordinator, SENSOR_LAST_INVOICE_AMOUNT)

    @property
    def native_value(self) -> float | None:
        """Return last invoice amount."""
        if self.coordinator.data and self.coordinator.data.last_invoice:
            return self.coordinator.data.last_invoice.amount_mdl
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return invoice metadata attributes."""
        attrs = {}
        if self.coordinator.data and self.coordinator.data.last_invoice:
            inv = self.coordinator.data.last_invoice
            attrs["invoice_number"] = inv.invoice_number
            attrs["is_paid"] = inv.is_paid
            if inv.issue_date:
                attrs["issue_date"] = inv.issue_date.isoformat()
            if inv.pdf_url:
                attrs["pdf_url"] = inv.pdf_url
        return attrs


class UtilitatiMDDueDateSensor(UtilitatiMDEntity, SensorEntity):
    """Sensor for invoice payment due date."""

    _attr_name = "Payment Due Date"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize due date sensor."""
        super().__init__(coordinator, SENSOR_DUE_DATE)

    @property
    def native_value(self) -> date | None:
        """Return due date."""
        if self.coordinator.data and self.coordinator.data.last_invoice:
            return self.coordinator.data.last_invoice.due_date
        return None


class UtilitatiMDMeterIndexSensor(UtilitatiMDEntity, SensorEntity):
    """Sensor for current meter index reading."""

    _attr_name = "Meter Index"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize meter index sensor."""
        super().__init__(coordinator, SENSOR_METER_INDEX)
        provider_info = PROVIDERS.get(coordinator.provider_id, {})
        self._attr_native_unit_of_measurement = provider_info.get("unit_of_measurement")
        self._attr_icon = provider_info.get("icon", "mdi:gauge")

    @property
    def native_value(self) -> float | None:
        """Return meter index value."""
        if self.coordinator.data and self.coordinator.data.latest_reading:
            return self.coordinator.data.latest_reading.reading_value
        return None


class UtilitatiMDMonthlyConsumptionSensor(UtilitatiMDEntity, SensorEntity):
    """Sensor for monthly energy/gas/water consumption."""

    _attr_name = "Monthly Consumption"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: UtilitatiMDDataUpdateCoordinator) -> None:
        """Initialize consumption sensor."""
        super().__init__(coordinator, SENSOR_MONTHLY_CONSUMPTION)
        provider_info = PROVIDERS.get(coordinator.provider_id, {})
        self._attr_native_unit_of_measurement = provider_info.get("unit_of_measurement")
        self._attr_icon = provider_info.get("icon", "mdi:chart-line")

    @property
    def native_value(self) -> float | None:
        """Return monthly consumption."""
        if self.coordinator.data:
            return self.coordinator.data.monthly_consumption
        return None
