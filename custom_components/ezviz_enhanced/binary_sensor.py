"""Binary sensor platform for EZVIZ Enhanced integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import EzvizDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EZVIZ Enhanced binary sensors from a config entry."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    
    # Add binary sensors for each camera
    for serial, camera_data in coordinator.cameras.items():
        if camera_data.get("enabled", True):
            entities.append(EzvizEnhancedBinarySensor(coordinator, serial))

    async_add_entities(entities)


class EzvizEnhancedBinarySensor(BinarySensorEntity):
    """Representation of an EZVIZ Enhanced binary sensor."""

    def __init__(self, coordinator: EzvizDataUpdateCoordinator, serial: str) -> None:
        """Initialize the binary sensor."""
        self.coordinator = coordinator
        self.serial = serial
        self._attr_name = f"EZVIZ {serial} Online"
        self._attr_unique_id = f"ezviz_enhanced_{serial}_online"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"EZVIZ Camera {serial}",
            "manufacturer": "EZVIZ",
            "model": "Enhanced Camera",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        camera_data = self.coordinator.cameras.get(self.serial, {})
        return camera_data.get("status") == "online"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_request_refresh()
