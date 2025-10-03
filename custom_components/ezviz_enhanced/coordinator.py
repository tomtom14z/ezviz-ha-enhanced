"""Data update coordinator for EZVIZ Enhanced integration."""
import logging
from datetime import timedelta
from typing import Dict, List, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EzvizApi, EzvizOpenApi, StreamConverter
from .const import DOMAIN, CONF_USE_IEUOPEN, CONF_RTSP_PORT, CONF_CAMERAS

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class EzvizDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from EZVIZ APIs."""

    def __init__(
        self,
        hass: HomeAssistant,
        ezviz_api: EzvizApi,
        ezviz_open_api: Optional[EzvizOpenApi],
        config_data: Dict[str, Any],
    ):
        """Initialize coordinator."""
        self.ezviz_api = ezviz_api
        self.ezviz_open_api = ezviz_open_api
        self.config_data = config_data
        self.use_ieuopen = config_data.get(CONF_USE_IEUOPEN, True)
        self.rtsp_port = config_data.get(CONF_RTSP_PORT, 8554)
        self.cameras_config = config_data.get(CONF_CAMERAS, [])
        
        # Initialize stream converter
        self.stream_converter = StreamConverter(self.rtsp_port)
        
        # Store camera data
        self.cameras: Dict[str, Dict[str, Any]] = {}
        self.stream_urls: Dict[str, str] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Starting data update...")
            
            # Get devices from EZVIZ cloud API
            ezviz_devices = await self.ezviz_api.async_get_devices()
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Got {len(ezviz_devices)} devices from EZVIZ cloud API")
            
            # Process each configured camera
            for camera_config in self.cameras_config:
                serial = camera_config.get("serial")
                channel = camera_config.get("channel", 1)
                name = camera_config.get("name", f"EZVIZ {serial}")
                enabled = camera_config.get("enabled", True)
                
                if not serial or not enabled:
                    _LOGGER.error(f"🔴 EZVIZ Enhanced: Skipping camera {serial} - not enabled or no serial")
                    continue
                
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Processing camera {serial} (channel {channel})")
                
                camera_data = {
                    "serial": serial,
                    "channel": channel,
                    "name": name,
                    "enabled": enabled,
                    "device_type": "camera",
                    "status": "offline",  # Default status
                }
                
                # Get stream information from EZVIZ Open Platform if enabled
                if self.use_ieuopen and self.ezviz_open_api:
                    _LOGGER.error(f"🔴 EZVIZ Enhanced: Getting stream info for camera {serial} from IeuOpen")
                    stream_info = await self.ezviz_open_api.async_get_stream_info(serial, channel)
                    if stream_info:
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Got stream info for {serial}: {stream_info}")
                        camera_data.update(stream_info)
                        camera_data["status"] = "online"
                        
                        # Get the best available stream URL
                        stream_url = None
                        stream_type = stream_info.get("stream_type", "hls_fluent")
                        
                        if stream_info.get("hls_url"):
                            stream_url = stream_info["hls_url"]
                            camera_data["hls_url"] = stream_url  # Store HLS URL separately
                            _LOGGER.error(f"🔴 EZVIZ Enhanced: Found HLS URL for {serial}: {stream_url}")
                        elif stream_info.get("flv_url"):
                            stream_url = stream_info["flv_url"]
                            _LOGGER.error(f"🔴 EZVIZ Enhanced: Found FLV URL for {serial}: {stream_url}")
                        elif stream_info.get("cloud_url"):
                            stream_url = stream_info["cloud_url"]
                            _LOGGER.error(f"🔴 EZVIZ Enhanced: Found cloud URL for {serial}: {stream_url}")
                        
                        if stream_url:
                            # For HLS streams, use direct URL (Home Assistant can handle it)
                            if stream_type.startswith("hls"):
                                camera_data["stream_url"] = stream_url
                                self.stream_urls[serial] = stream_url
                                _LOGGER.error(f"🔴 EZVIZ Enhanced: Using HLS stream for {serial}: {stream_url}")
                            else:
                                # For other formats, convert to RTSP
                                rtsp_url = await self.stream_converter.start_rtsp_conversion(
                                    serial, stream_url, stream_type
                                )
                                camera_data["stream_url"] = rtsp_url
                                self.stream_urls[serial] = rtsp_url
                                _LOGGER.error(f"🔴 EZVIZ Enhanced: Using RTSP stream for {serial}: {rtsp_url}")
                        else:
                            _LOGGER.error(f"🔴 EZVIZ Enhanced: No stream URL found for camera {serial}")
                    else:
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Failed to get stream info for camera {serial}")
                else:
                    _LOGGER.error(f"🔴 EZVIZ Enhanced: IeuOpen disabled or API not available for camera {serial}")
                
                # Add EZVIZ Open Platform URL
                if self.ezviz_open_api:
                    camera_data["ieuopen_url"] = self.ezviz_open_api.get_live_url(serial, channel)
                    _LOGGER.error(f"🔴 EZVIZ Enhanced: IeuOpen URL for {serial}: {camera_data['ieuopen_url']}")
                
                self.cameras[serial] = camera_data
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Camera {serial} configured: {camera_data}")
            
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Data update completed. Cameras: {list(self.cameras.keys())}")
            
            return {
                "cameras": self.cameras,
                "stream_urls": self.stream_urls,
                "ezviz_devices": ezviz_devices,
            }
            
        except Exception as error:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Error communicating with EZVIZ API: {error}")
            raise UpdateFailed(f"Error communicating with EZVIZ API: {error}")

    async def async_get_camera(self, serial: str) -> Optional[Dict[str, Any]]:
        """Get camera data by serial."""
        return self.cameras.get(serial)

    async def async_get_stream_url(self, serial: str) -> Optional[str]:
        """Get stream URL for a camera."""
        return self.stream_urls.get(serial)

    async def async_stop_rtsp_conversion(self, serial: str):
        """Stop RTSP conversion for a camera."""
        await self.stream_converter.stop_rtsp_conversion(serial)

    async def async_cleanup(self):
        """Cleanup resources."""
        # Stop all RTSP conversions
        for serial in list(self.stream_urls.keys()):
            await self.async_stop_rtsp_conversion(serial)
        
        # Close API sessions
        await self.ezviz_api.async_close()
        if self.ezviz_open_api:
            await self.ezviz_open_api.async_close()
