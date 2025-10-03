"""Camera platform for EZVIZ Enhanced integration."""
import logging
from typing import Optional
import aiohttp
import asyncio

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_SERIAL, ATTR_CHANNEL, ATTR_DEVICE_TYPE, ATTR_RTSP_URL, ATTR_IEUOPEN_URL, ATTR_HLS_URL
from .coordinator import EzvizDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EZVIZ Enhanced camera entities."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    cameras = []
    for serial, camera_data in coordinator.data.get("cameras", {}).items():
        if camera_data.get("enabled", True):
            cameras.append(EzvizEnhancedCamera(coordinator, serial, camera_data, config_entry.entry_id))

    async_add_entities(cameras, True)


class EzvizEnhancedCamera(Camera):
    """Representation of an EZVIZ Enhanced camera."""

    def __init__(
        self,
        coordinator: EzvizDataUpdateCoordinator,
        serial: str,
        camera_data: dict,
        entry_id: str,
    ):
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self.serial = serial
        self.camera_data = camera_data
        self.entry_id = entry_id
        self._name = camera_data.get("name", f"EZVIZ {serial}")
        self._channel = camera_data.get("channel", 1)
        self._device_type = camera_data.get("device_type", "camera")
        self._rtsp_url = camera_data.get("rtsp_url")
        self._hls_url = camera_data.get("hls_url")
        self._stream_url = camera_data.get("stream_url")
        self._ieuopen_url = camera_data.get("ieuopen_url")
        self._stream_source = None
        self._ffmpeg_process = None

    @property
    def name(self) -> str:
        """Return the name of the camera."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{DOMAIN}_camera_{self.serial}_{self._channel}_{self.entry_id[:8]}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.serial)},
            "name": self._name,
            "manufacturer": "EZVIZ",
            "model": "CP2",
            "sw_version": "2025",
        }

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            ATTR_SERIAL: self.serial,
            ATTR_CHANNEL: self._channel,
            ATTR_DEVICE_TYPE: self._device_type,
            ATTR_RTSP_URL: self._rtsp_url,
            ATTR_HLS_URL: self._hls_url,
            ATTR_IEUOPEN_URL: self._ieuopen_url,
        }

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return bytes of camera image."""
        # For HLS streams, we'll let Home Assistant handle the stream
        # The stream_source method will provide the HLS URL
        return None

    async def stream_source(self) -> Optional[str]:
        """Return the source of the stream."""
        # For HLS streams, return the URL directly
        # Home Assistant should be able to handle HLS with FFmpeg
        if self._hls_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Using HLS stream for camera {self.serial}: {self._hls_url}")
            return self._hls_url
        
        if self._stream_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Using stream URL for camera {self.serial}: {self._stream_url}")
            return self._stream_url
        
        if self._rtsp_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Using RTSP stream for camera {self.serial}: {self._rtsp_url}")
            return self._rtsp_url
        
        # Try to get stream URL from coordinator
        stream_url = await self.coordinator.async_get_stream_url(self.serial)
        if stream_url:
            self._stream_url = stream_url
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Got stream URL from coordinator for camera {self.serial}: {stream_url}")
            return stream_url
        
        _LOGGER.error(f"🔴 EZVIZ Enhanced: No stream source available for camera {self.serial}")
        return None

    async def async_update(self):
        """Update camera data."""
        await self.coordinator.async_request_refresh()
        
        # Update camera data
        camera_data = await self.coordinator.async_get_camera(self.serial)
        if camera_data:
            self.camera_data = camera_data
            self._rtsp_url = camera_data.get("rtsp_url")
            self._hls_url = camera_data.get("hls_url")
            self._stream_url = camera_data.get("stream_url")
            self._ieuopen_url = camera_data.get("ieuopen_url")
            
            # Log current URLs for debugging - using ERROR level to ensure visibility
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Camera {self.serial} URLs - HLS: {self._hls_url}, Stream: {self._stream_url}, RTSP: {self._rtsp_url}")

    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed."""
        await self.coordinator.async_stop_rtsp_conversion(self.serial)
