"""Base entity class for Utilități Moldova integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER, PROVIDERS
from .coordinator import UtilitatiMDDataUpdateCoordinator


class UtilitatiMDEntity(CoordinatorEntity[UtilitatiMDDataUpdateCoordinator]):
    """Base class for all Utilități Moldova entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: UtilitatiMDDataUpdateCoordinator,
        entity_type: str,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self.entity_type = entity_type
        provider_info = PROVIDERS.get(coordinator.provider_id, {})
        provider_name = provider_info.get("name", coordinator.provider_id)

        self._attr_unique_id = (
            f"{coordinator.provider_id}_{coordinator.contract_number}_{entity_type}"
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.provider_id}_{coordinator.contract_number}")},
            name=f"{provider_name} ({coordinator.contract_number})",
            manufacturer=MANUFACTURER,
            model=provider_name,
            sw_version="0.1.0",
        )
