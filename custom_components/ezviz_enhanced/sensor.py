"""Sensor platform for EZVIZ Enhanced integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
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
    """Set up EZVIZ Enhanced sensors from a config entry."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    
    # Add sensors for each camera
    for serial, camera_data in coordinator.cameras.items():
        if camera_data.get("enabled", True):
            entities.append(EzvizEnhancedSensor(coordinator, serial, config_entry.entry_id))

    async_add_entities(entities)


class EzvizEnhancedSensor(SensorEntity):
    """Representation of an EZVIZ Enhanced sensor."""

    def __init__(self, coordinator: EzvizDataUpdateCoordinator, serial: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.serial = serial
        self.entry_id = entry_id
        self._attr_name = f"EZVIZ {serial} Stream Info"
        self._attr_unique_id = f"{DOMAIN}_sensor_{serial}_stream_info_{entry_id[:8]}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"EZVIZ Camera {serial}",
            "manufacturer": "EZVIZ",
            "model": "Enhanced Camera",
        }

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        camera_data = self.coordinator.cameras.get(self.serial, {})
        return camera_data.get("stream_type", "unknown")

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
