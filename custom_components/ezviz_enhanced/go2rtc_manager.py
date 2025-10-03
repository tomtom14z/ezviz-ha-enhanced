"""go2rtc Manager for EZVIZ Enhanced integration."""
import logging
from typing import Optional, Dict
import os
import yaml
import aiohttp

_LOGGER = logging.getLogger(__name__)


class Go2RtcManager:
    """Manager for go2rtc streams via configuration file."""

    def __init__(self, hass):
        """Initialize go2rtc manager."""
        self.hass = hass
        self._streams: Dict[str, str] = {}
        # go2rtc peut utiliser configuration.yaml OU go2rtc.yaml
        self._config_file = os.path.join(hass.config.config_dir, "configuration.yaml")
        self._go2rtc_config_file = os.path.join(hass.config.config_dir, "go2rtc.yaml")
        self._go2rtc_url = "http://localhost:1984"
        
    async def async_add_stream(self, serial: str, hls_url: str) -> Optional[str]:
        """Add a stream to go2rtc configuration and return the RTSP URL."""
        
        stream_name = f"ezviz_{serial}"
        rtsp_url = f"rtsp://localhost:8554/{stream_name}"
        
        try:
            # Déterminer quel fichier utiliser
            # Si go2rtc.yaml existe, l'utiliser, sinon utiliser configuration.yaml
            config_file_to_use = self._go2rtc_config_file if os.path.exists(self._go2rtc_config_file) else self._config_file
            
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation du fichier: {config_file_to_use}")
            
            if not os.path.exists(config_file_to_use):
                # Créer go2rtc.yaml si aucun fichier n'existe
                config_file_to_use = self._go2rtc_config_file
                config = {'streams': {}}
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Création de {config_file_to_use}")
            else:
                with open(config_file_to_use, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # Si c'est configuration.yaml, on doit wrapper dans go2rtc:
            # Si c'est go2rtc.yaml, les streams sont à la racine
            if config_file_to_use == self._config_file:
                # configuration.yaml
                if 'go2rtc' not in config:
                    config['go2rtc'] = {}
                if 'streams' not in config['go2rtc']:
                    config['go2rtc']['streams'] = {}
                streams_dict = config['go2rtc']['streams']
            else:
                # go2rtc.yaml
                if 'streams' not in config:
                    config['streams'] = {}
                streams_dict = config['streams']
            
            # Ajouter ou mettre à jour le stream
            old_url = streams_dict.get(stream_name)
            
            if isinstance(old_url, list) and len(old_url) > 0:
                old_url = old_url[0]
            
            streams_dict[stream_name] = [hls_url]
            
            # Écrire la configuration mise à jour
            with open(config_file_to_use, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            if old_url != hls_url:
                _LOGGER.error("=" * 80)
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Stream go2rtc mis à jour pour {serial}")
                _LOGGER.error("=" * 80)
                _LOGGER.error(f"")
                _LOGGER.error(f"✅ Configuration go2rtc mise à jour automatiquement")
                _LOGGER.error(f"📍 Stream: {stream_name}")
                _LOGGER.error(f"🔗 URL RTSP: {rtsp_url}")
                _LOGGER.error(f"")
                
                # Recharger go2rtc sans redémarrage
                reload_success = await self._reload_go2rtc()
                if reload_success:
                    _LOGGER.error(f"✅ go2rtc rechargé automatiquement - Stream disponible immédiatement!")
                else:
                    _LOGGER.error(f"⚠️  Rechargement go2rtc échoué - Redémarrez Home Assistant")
                
                _LOGGER.error(f"")
                _LOGGER.error("=" * 80)
            
            self._streams[serial] = rtsp_url
            return rtsp_url
            
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la mise à jour de configuration.yaml: {e}")
            return None

    async def _reload_go2rtc(self) -> bool:
        """Reload go2rtc configuration via Home Assistant service."""
        try:
            # Utiliser le service Home Assistant pour recharger go2rtc
            await self.hass.services.async_call(
                "go2rtc",
                "reload",
                blocking=True,
                limit=10
            )
            return True
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors du rechargement go2rtc: {e}")
            
            # Fallback: essayer via l'API HTTP de go2rtc
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self._go2rtc_url}/api/config/reload",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status in [200, 204]:
                            return True
            except Exception as api_error:
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Fallback API échoué: {api_error}")
            
            return False

    async def async_update_stream(self, serial: str, hls_url: str) -> Optional[str]:
        """Update an existing stream with a new HLS URL."""
        return await self.async_add_stream(serial, hls_url)

    async def async_remove_stream(self, serial: str) -> bool:
        """Remove a stream from go2rtc configuration."""
        stream_name = f"ezviz_{serial}"
        
        try:
            if not os.path.exists(self._config_file):
                return True
            
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            if 'go2rtc' in config and 'streams' in config['go2rtc']:
                if stream_name in config['go2rtc']['streams']:
                    del config['go2rtc']['streams'][stream_name]
                    
                    with open(self._config_file, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    
                    _LOGGER.error(f"🔴 EZVIZ Enhanced: Stream go2rtc supprimé pour {serial}")
            
            self._streams.pop(serial, None)
            return True
            
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la suppression du stream: {e}")
            return False

    def get_rtsp_url(self, serial: str) -> Optional[str]:
        """Get the RTSP URL for a camera."""
        return self._streams.get(serial)

    def get_all_streams(self) -> Dict[str, str]:
        """Get all RTSP streams."""
        return self._streams.copy()

    @property
    def is_available(self) -> bool:
        """Return if go2rtc is available (always True as we write to config file)."""
        return os.path.exists(self._config_file)
