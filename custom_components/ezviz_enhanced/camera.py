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
        # Try to get image from HLS stream first
        if self._hls_url:
            try:
                # For HLS streams, we need to extract a frame
                # This is a simplified approach - in production you might want to use ffmpeg
                async with aiohttp.ClientSession() as session:
                    async with session.get(self._hls_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            # For now, return None to let Home Assistant handle the stream
                            # The stream_source method will provide the HLS URL for live viewing
                            return None
            except Exception as e:
                _LOGGER.error(f"Error getting camera image from HLS: {e}")
        
        # Try to get image from stream URL
        if self._stream_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self._stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return None  # Let Home Assistant handle the stream
            except Exception as e:
                _LOGGER.error(f"Error getting camera image from stream: {e}")
        
        # Try to get image from IeuOpen platform
        if self._ieuopen_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self._ieuopen_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return None  # Let Home Assistant handle the stream
            except Exception as e:
                _LOGGER.error(f"Error getting camera image from IeuOpen: {e}")
        
        # If no stream is available, return None to show "inactive" state
        _LOGGER.warning(f"No valid stream URL available for camera {self.serial}")
        return None

    async def stream_source(self) -> Optional[str]:
        """Return the source of the stream."""
        # Prioritize HLS URL as it works directly with Home Assistant
        if self._hls_url:
            _LOGGER.info(f"Using HLS stream for camera {self.serial}: {self._hls_url}")
            return self._hls_url
        
        if self._stream_url:
            _LOGGER.info(f"Using stream URL for camera {self.serial}: {self._stream_url}")
            return self._stream_url
        
        if self._rtsp_url:
            _LOGGER.info(f"Using RTSP stream for camera {self.serial}: {self._rtsp_url}")
            return self._rtsp_url
        
        # Try to get stream URL from coordinator
        stream_url = await self.coordinator.async_get_stream_url(self.serial)
        if stream_url:
            self._stream_url = stream_url
            _LOGGER.info(f"Got stream URL from coordinator for camera {self.serial}: {stream_url}")
            return stream_url
        
        _LOGGER.error(f"No stream source available for camera {self.serial}")
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
            
            # Log current URLs for debugging
            _LOGGER.info(f"Camera {self.serial} URLs - HLS: {self._hls_url}, Stream: {self._stream_url}, RTSP: {self._rtsp_url}")

    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed."""
        await self.coordinator.async_stop_rtsp_conversion(self.serial)
