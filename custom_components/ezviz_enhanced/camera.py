"""Camera platform for EZVIZ Enhanced integration."""
import asyncio
import logging
from typing import Optional

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_SERIAL, ATTR_CHANNEL, ATTR_DEVICE_TYPE, ATTR_RTSP_URL, ATTR_IEUOPEN_URL, ATTR_HLS_URL, ATTR_RTSP_LOCAL_URL
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
            cameras.append(EzvizEnhancedCamera(coordinator, config_entry, serial, camera_data))

    async_add_entities(cameras, True)


class EzvizEnhancedCamera(Camera):
    """Representation of an EZVIZ Enhanced camera."""
    
    # Déclarer explicitement le support du streaming
    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_brand = "EZVIZ"

    def __init__(
        self,
        coordinator: EzvizDataUpdateCoordinator,
        config_entry: ConfigEntry,
        serial: str,
        camera_data: dict,
    ):
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.serial = serial
        self.camera_data = camera_data
        self._name = camera_data.get("name", f"EZVIZ {serial}")
        self._channel = camera_data.get("channel", 1)
        self._device_type = camera_data.get("device_type", "camera")
        self._rtsp_url = camera_data.get("rtsp_url")
        self._hls_url = camera_data.get("hls_url")
        self._stream_url = camera_data.get("stream_url")
        self._ieuopen_url = camera_data.get("ieuopen_url")
        self._rtsp_local_url = camera_data.get("rtsp_local_url")
        self._last_url = None
        
        _LOGGER.error(f"🔴 EZVIZ Enhanced Camera initialisée: {self._name}, HLS: {bool(self._hls_url)}, RTSP Local: {bool(self._rtsp_local_url)}")

    @property
    def name(self) -> str:
        """Return the name of the camera."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"ezviz_enhanced_camera_{self.config_entry.entry_id[:8]}_{self.serial}_{self._channel}"
    
    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return CameraEntityFeature.STREAM

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
        attrs = {
            ATTR_SERIAL: self.serial,
            ATTR_CHANNEL: self._channel,
            ATTR_DEVICE_TYPE: self._device_type,
            ATTR_RTSP_URL: self._rtsp_url,
            ATTR_HLS_URL: self._hls_url,
            ATTR_IEUOPEN_URL: self._ieuopen_url,
        }
        
        # Ajouter l'URL RTSP locale si disponible
        if self._rtsp_local_url:
            attrs[ATTR_RTSP_LOCAL_URL] = self._rtsp_local_url
            _LOGGER.error(f"🔴 EZVIZ Enhanced: URL RTSP locale exposée dans les attributs: {self._rtsp_local_url}")
        
        return attrs

    @property
    def is_streaming(self) -> bool:
        """Return true if the camera is streaming."""
        return self._hls_url is not None or self._stream_url is not None

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return bytes of camera image."""
        _LOGGER.error(f"🔴 EZVIZ Enhanced: Demande d'image miniature pour {self.serial}")
        
        # Obtenir l'URL du stream
        stream_url = await self.stream_source()
        
        if not stream_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Pas d'URL pour générer la miniature de {self.serial}")
            return None
        
        try:
            # Utiliser FFmpeg pour extraire une image du stream HLS
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", stream_url,
                "-frames:v", "1",  # Une seule frame
                "-f", "image2",
                "-c:v", "mjpeg",
                "-q:v", "2",  # Qualité (2-31, 2 = meilleure)
                "pipe:1"
            ]
            
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Génération de la miniature avec FFmpeg...")
            
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0 and stdout:
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Miniature générée avec succès ({len(stdout)} bytes)")
                return stdout
            else:
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Échec FFmpeg: {stderr.decode()[:200]}")
                return None
                
        except asyncio.TimeoutError:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Timeout lors de la génération de la miniature")
            return None
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la génération de la miniature: {e}")
            return None

    async def stream_source(self) -> Optional[str]:
        """Return the source of the stream."""
        _LOGGER.error(f"🔴 EZVIZ Enhanced: Demande de source de stream pour {self.serial}")
        
        # Récupérer l'URL fraîche depuis le coordinator
        stream_url = await self.coordinator.async_get_stream_url(self.serial, force_refresh=False)
        
        if stream_url:
            self._last_url = stream_url
            self._hls_url = stream_url
            self._stream_url = stream_url
            _LOGGER.error(f"🔴 EZVIZ Enhanced: URL stream retournée: {stream_url[:100]}...")
            return stream_url
        
        # Fallback sur les URLs stockées
        if self._last_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation dernière URL connue: {self._last_url[:100]}...")
            return self._last_url
            
        if self._hls_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation HLS URL initiale: {self._hls_url[:100]}...")
            return self._hls_url
        
        if self._stream_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation stream URL: {self._stream_url[:100]}...")
            return self._stream_url
        
        if self._rtsp_url:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation RTSP URL: {self._rtsp_url[:100]}...")
            return self._rtsp_url
        
        _LOGGER.error(f"🔴 EZVIZ Enhanced: Aucune source de stream trouvée pour {self.serial}")
        return None
    
    @property
    def frontend_stream_type(self):
        """Return the type of stream supported by this camera."""
        # Indiquer explicitement que c'est un stream HLS
        return "hls"

    async def async_update(self):
        """Update camera data."""
        await self.coordinator.async_request_refresh()
        
        # Update camera data
        camera_data = await self.coordinator.async_get_camera(self.serial)
        if camera_data:
            self.camera_data = camera_data
            old_hls = self._hls_url
            self._rtsp_url = camera_data.get("rtsp_url")
            self._hls_url = camera_data.get("hls_url")
            self._stream_url = camera_data.get("stream_url")
            self._ieuopen_url = camera_data.get("ieuopen_url")
            self._rtsp_local_url = camera_data.get("rtsp_local_url")
            
            if self._hls_url != old_hls:
                _LOGGER.error(f"🔴 EZVIZ Enhanced: URL HLS mise à jour pour {self.serial}: {bool(self._hls_url)}")

    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed."""
        if hasattr(self.coordinator, 'async_stop_rtsp_conversion'):
            await self.coordinator.async_stop_rtsp_conversion(self.serial)
