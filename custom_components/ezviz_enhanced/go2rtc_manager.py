"""go2rtc Manager for EZVIZ Enhanced integration."""
import logging
from typing import Optional, Dict
import aiohttp
import asyncio
import os
import yaml

_LOGGER = logging.getLogger(__name__)


class Go2RtcManager:
    """Manager for go2rtc streams."""

    def __init__(self, hass):
        """Initialize go2rtc manager."""
        self.hass = hass
        self._streams: Dict[str, str] = {}
        self._go2rtc_available = False
        self._base_url = "http://localhost:1984"  # Port par défaut de go2rtc
        self._config_file = os.path.join(hass.config.config_dir, ".storage", "go2rtc")
        
    async def async_check_availability(self) -> bool:
        """Check if go2rtc is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._base_url}/api/streams", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    self._go2rtc_available = response.status == 200
                    if self._go2rtc_available:
                        _LOGGER.error("🔴 EZVIZ Enhanced: go2rtc détecté et disponible")
                    return self._go2rtc_available
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: go2rtc non disponible: {e}")
            self._go2rtc_available = False
            return False

    async def async_add_stream(self, serial: str, hls_url: str) -> Optional[str]:
        """Add a stream to go2rtc and return the RTSP URL."""
        if not self._go2rtc_available:
            await self.async_check_availability()
            if not self._go2rtc_available:
                _LOGGER.error(f"🔴 EZVIZ Enhanced: go2rtc non disponible, impossible d'ajouter le stream {serial}")
                return None

        stream_name = f"ezviz_{serial}"
        
        # go2rtc intégré à Home Assistant ne supporte pas l'ajout dynamique de streams
        # On crée simplement l'URL RTSP qui sera disponible quand le stream sera demandé
        # go2rtc va automatiquement proxyfier l'URL HLS source
        
        _LOGGER.error(f"🔴 EZVIZ Enhanced: Configuration du stream RTSP pour {serial}")
        
        # Vérifier si go2rtc peut accéder au stream
        try:
            async with aiohttp.ClientSession() as session:
                # Tester si on peut lire le stream depuis go2rtc
                # go2rtc supporte la lecture directe d'URLs HLS comme source
                test_url = f"{self._base_url}/api/stream.mp4?src={hls_url}"
                
                async with session.get(
                    test_url,
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        # go2rtc peut lire le stream, créer l'URL RTSP
                        rtsp_url = f"rtsp://localhost:8554/{stream_name}"
                        self._streams[serial] = rtsp_url
                        
                        # Stocker la source HLS pour go2rtc
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Stream RTSP configuré pour {serial}: {rtsp_url}")
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Pour utiliser ce stream, ajoutez dans configuration.yaml:")
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: go2rtc:")
                        _LOGGER.error(f"🔴 EZVIZ Enhanced:   streams:")
                        _LOGGER.error(f"🔴 EZVIZ Enhanced:     {stream_name}: {hls_url}")
                        
                        return rtsp_url
                    else:
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: go2rtc ne peut pas accéder au stream HLS (status {response.status})")
                        return None
                        
        except asyncio.TimeoutError:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Timeout lors du test du stream")
            return None
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors du test du stream: {e}")
            # Même en cas d'erreur, on retourne l'URL RTSP
            # Elle sera disponible si l'utilisateur configure manuellement go2rtc
            rtsp_url = f"rtsp://localhost:8554/{stream_name}"
            self._streams[serial] = rtsp_url
            
            _LOGGER.error(f"🔴 EZVIZ Enhanced: ⚠️ Configuration manuelle requise")
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Ajoutez dans configuration.yaml :")
            _LOGGER.error(f"🔴 EZVIZ Enhanced: go2rtc:")
            _LOGGER.error(f"🔴 EZVIZ Enhanced:   streams:")
            _LOGGER.error(f"🔴 EZVIZ Enhanced:     {stream_name}: {hls_url}")
            
            return rtsp_url

    async def async_update_stream(self, serial: str, hls_url: str) -> Optional[str]:
        """Update an existing stream with a new HLS URL."""
        # go2rtc gère automatiquement les mises à jour d'URL
        return await self.async_add_stream(serial, hls_url)

    async def async_remove_stream(self, serial: str) -> bool:
        """Remove a stream from go2rtc."""
        if serial not in self._streams:
            return True

        stream_name = f"ezviz_{serial}"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Supprimer le stream de go2rtc
                async with session.delete(
                    f"{self._base_url}/api/streams",
                    params={"name": stream_name},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status in [200, 204]:
                        self._streams.pop(serial, None)
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Stream RTSP supprimé pour {serial}")
                        return True
                    else:
                        _LOGGER.error(f"🔴 EZVIZ Enhanced: Échec de suppression du stream RTSP pour {serial}")
                        return False
                        
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la suppression du stream RTSP pour {serial}: {e}")
            return False

    def get_rtsp_url(self, serial: str) -> Optional[str]:
        """Get the RTSP URL for a camera."""
        return self._streams.get(serial)

    def get_all_streams(self) -> Dict[str, str]:
        """Get all RTSP streams."""
        return self._streams.copy()

    @property
    def is_available(self) -> bool:
        """Return if go2rtc is available."""
        return self._go2rtc_available

