"""Data update coordinator for EZVIZ Enhanced integration."""
import logging
import re
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EzvizApi, EzvizOpenApi, StreamConverter
from .const import DOMAIN, CONF_USE_IEUOPEN, CONF_RTSP_PORT, CONF_CAMERAS
from .go2rtc_manager import Go2RtcManager

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=1)  # Vérification légère toutes les 1 minute


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
        
        # Initialize go2rtc manager for local RTSP streams
        self.go2rtc_manager = Go2RtcManager(hass)
        
        # Store camera data
        self.cameras: Dict[str, Dict[str, Any]] = {}
        self.stream_urls: Dict[str, str] = {}
        self.rtsp_urls: Dict[str, str] = {}  # URLs RTSP locales via go2rtc
        self.url_expiration: Dict[str, int] = {}  # Stocke les timestamps d'expiration

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
    
    def _extract_expiration_from_url(self, url: str) -> Optional[int]:
        """Extraire le timestamp d'expiration de l'URL HLS."""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'expire' in params:
                return int(params['expire'][0])
        except Exception as e:
            _LOGGER.debug(f"Impossible d'extraire l'expiration de l'URL: {e}")
        return None
    
    def _is_url_expired(self, serial: str, buffer_seconds: int = 300) -> bool:
        """Vérifier si l'URL est expirée ou proche de l'expiration (5 min de marge)."""
        if serial not in self.url_expiration:
            return True
        
        expiration = self.url_expiration[serial]
        now = int(datetime.now().timestamp())
        
        # Considérer comme expiré si moins de 5 minutes restantes
        if expiration - now < buffer_seconds:
            _LOGGER.error(f"🔴 URL pour {serial} expire dans {expiration - now}s, rafraîchissement nécessaire")
            return True
        
        _LOGGER.debug(f"URL pour {serial} encore valide pour {expiration - now}s")
        return False

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            # Get devices from EZVIZ cloud API
            ezviz_devices = await self.ezviz_api.async_get_devices()
            
            # Process each configured camera
            for camera_config in self.cameras_config:
                serial = camera_config.get("serial")
                channel = camera_config.get("channel", 1)
                name = camera_config.get("name", f"EZVIZ {serial}")
                enabled = camera_config.get("enabled", True)
                
                if not serial or not enabled:
                    continue
                
                camera_data = {
                    "serial": serial,
                    "channel": channel,
                    "name": name,
                    "enabled": enabled,
                    "device_type": "camera",
                }
                
                # Get stream information from EZVIZ Open Platform if enabled
                if self.use_ieuopen and self.ezviz_open_api:
                    # Vérifier si l'URL actuelle est encore valide
                    need_refresh = self._is_url_expired(serial)
                    
                    if need_refresh:
                        _LOGGER.error(f"🔴 Rafraîchissement de l'URL pour {serial} (expirée ou inexistante)")
                        stream_info = await self.ezviz_open_api.async_get_stream_info(serial, channel)
                        if stream_info:
                            camera_data.update(stream_info)
                            
                            # Get the best available stream URL
                            stream_url = None
                            stream_type = stream_info.get("stream_type", "hls_fluent")
                            
                            if stream_info.get("hls_url"):
                                stream_url = stream_info["hls_url"]
                            elif stream_info.get("flv_url"):
                                stream_url = stream_info["flv_url"]
                            elif stream_info.get("cloud_url"):
                                stream_url = stream_info["cloud_url"]
                            
                            if stream_url:
                                # Extraire et stocker la date d'expiration
                                expiration = self._extract_expiration_from_url(stream_url)
                                if expiration:
                                    self.url_expiration[serial] = expiration
                                    remaining = expiration - int(datetime.now().timestamp())
                                    _LOGGER.error(f"✅ Nouvelle URL pour {serial}, valide pour {remaining}s (~{remaining//60} min)")
                                
                                # For HLS streams, use direct URL (Home Assistant can handle it)
                                if stream_type.startswith("hls"):
                                    camera_data["stream_url"] = stream_url
                                    self.stream_urls[serial] = stream_url
                                    
                                    # Mettre à jour go2rtc configuration automatiquement
                                    if self.go2rtc_manager.is_available:
                                        rtsp_url = await self.go2rtc_manager.async_add_stream(serial, stream_url)
                                        if rtsp_url:
                                            camera_data["rtsp_local_url"] = rtsp_url
                                            self.rtsp_urls[serial] = rtsp_url
                            else:
                                # For other formats, convert to RTSP
                                rtsp_url = await self.stream_converter.start_rtsp_conversion(
                                    serial, stream_url, stream_type
                                )
                                camera_data["stream_url"] = rtsp_url
                                self.stream_urls[serial] = rtsp_url
                    else:
                        # URL encore valide, utiliser le cache
                        if serial in self.stream_urls:
                            camera_data["stream_url"] = self.stream_urls[serial]
                            camera_data["hls_url"] = self.stream_urls[serial]
                        if serial in self.rtsp_urls:
                            camera_data["rtsp_local_url"] = self.rtsp_urls[serial]
                
                # Add EZVIZ Open Platform URL
                if self.ezviz_open_api:
                    camera_data["ieuopen_url"] = self.ezviz_open_api.get_live_url(serial, channel)
                
                self.cameras[serial] = camera_data
            
            return {
                "cameras": self.cameras,
                "stream_urls": self.stream_urls,
                "rtsp_urls": self.rtsp_urls,
                "ezviz_devices": ezviz_devices,
            }
            
        except Exception as error:
            raise UpdateFailed(f"Error communicating with EZVIZ API: {error}")

    async def async_get_camera(self, serial: str) -> Optional[Dict[str, Any]]:
        """Get camera data by serial."""
        return self.cameras.get(serial)

    async def async_get_stream_url(self, serial: str, force_refresh: bool = False) -> Optional[str]:
        """Get stream URL for a camera."""
        _LOGGER.error(f"🔴 EZVIZ Coordinator: Demande d'URL pour {serial}, force_refresh={force_refresh}")
        
        # Force refresh if requested or if URL is not available
        if force_refresh or serial not in self.stream_urls:
            _LOGGER.error(f"🔴 EZVIZ Coordinator: Rafraîchissement de l'URL pour {serial}")
            
            if self.ezviz_open_api:
                camera = self.cameras.get(serial)
                if camera:
                    channel = camera.get("channel", 1)
                    stream_info = await self.ezviz_open_api.async_get_stream_info(serial, channel)
                    
                    if stream_info and stream_info.get("hls_url"):
                        self.stream_urls[serial] = stream_info["hls_url"]
                        _LOGGER.error(f"🔴 EZVIZ Coordinator: Nouvelle URL HLS obtenue: {self.stream_urls[serial][:100]}...")
                        
                        # Update camera data with new URL
                        camera["hls_url"] = stream_info["hls_url"]
                        camera["stream_url"] = stream_info["hls_url"]
                        self.cameras[serial] = camera
                    else:
                        _LOGGER.error(f"🔴 EZVIZ Coordinator: Échec de récupération de l'URL HLS")
        
        url = self.stream_urls.get(serial)
        if url:
            _LOGGER.error(f"🔴 EZVIZ Coordinator: URL retournée: {url[:100]}...")
        else:
            _LOGGER.error(f"🔴 EZVIZ Coordinator: Aucune URL disponible pour {serial}")
        
        return url

    async def async_stop_rtsp_conversion(self, serial: str):
        """Stop RTSP conversion for a camera."""
        await self.stream_converter.stop_rtsp_conversion(serial)

    async def async_cleanup(self):
        """Cleanup resources."""
        # Stop all RTSP conversions
        for serial in list(self.stream_urls.keys()):
            await self.async_stop_rtsp_conversion(serial)
        
        # Remove all go2rtc streams
        for serial in list(self.rtsp_urls.keys()):
            await self.go2rtc_manager.async_remove_stream(serial)
        
        # Close API sessions
        await self.ezviz_api.async_close()
        if self.ezviz_open_api:
            await self.ezviz_open_api.async_close()
    
    def get_rtsp_local_url(self, serial: str) -> Optional[str]:
        """Get local RTSP URL for a camera."""
        return self.rtsp_urls.get(serial)
