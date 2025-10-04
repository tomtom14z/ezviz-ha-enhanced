"""go2rtc Manager for EZVIZ Enhanced integration."""
import logging
from typing import Optional, Dict
import os
import aiohttp
from homeassistant.util import yaml as ha_yaml

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
            # Imports nécessaires
            import aiofiles
            import yaml as pyyaml
            
            # Créer un loader personnalisé qui ignore les tags inconnus (métadonnées HA)
            class SafeLoaderIgnoreUnknown(pyyaml.SafeLoader):
                pass
            
            def construct_undefined(loader, node):
                if isinstance(node, pyyaml.MappingNode):
                    return loader.construct_mapping(node)
                elif isinstance(node, pyyaml.SequenceNode):
                    return loader.construct_sequence(node)
                else:
                    return loader.construct_scalar(node)
            
            SafeLoaderIgnoreUnknown.add_constructor(None, construct_undefined)
            
            # Toujours utiliser go2rtc.yaml pour éviter les problèmes avec !include
            config_file_to_use = self._go2rtc_config_file
            
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Utilisation du fichier: {config_file_to_use}")
            
            if not os.path.exists(config_file_to_use):
                # Créer go2rtc.yaml
                config = {'streams': {}}
                _LOGGER.error(f"🔴 EZVIZ Enhanced: Création de {config_file_to_use}")
            else:
                async with aiofiles.open(config_file_to_use, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    # Utiliser le loader personnalisé pour ignorer les métadonnées HA
                    config = pyyaml.load(content, Loader=SafeLoaderIgnoreUnknown) or {}
            
            # go2rtc.yaml : les streams sont à la racine
            if 'streams' not in config:
                config['streams'] = {}
            streams_dict = config['streams']
            
            # Ajouter ou mettre à jour le stream
            old_url = streams_dict.get(stream_name)
            
            if isinstance(old_url, list) and len(old_url) > 0:
                old_url = old_url[0]
            
            streams_dict[stream_name] = [hls_url]
            
            # Écrire la configuration mise à jour de façon asynchrone
            yaml_content = pyyaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            async with aiofiles.open(config_file_to_use, 'w', encoding='utf-8') as f:
                await f.write(yaml_content)
            
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
                blocking=True
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
        config_file_to_use = self._go2rtc_config_file
        
        try:
            import aiofiles
            import yaml as pyyaml
            
            # Créer un loader personnalisé qui ignore les tags inconnus (métadonnées HA)
            class SafeLoaderIgnoreUnknown(pyyaml.SafeLoader):
                pass
            
            def construct_undefined(loader, node):
                if isinstance(node, pyyaml.MappingNode):
                    return loader.construct_mapping(node)
                elif isinstance(node, pyyaml.SequenceNode):
                    return loader.construct_sequence(node)
                else:
                    return loader.construct_scalar(node)
            
            SafeLoaderIgnoreUnknown.add_constructor(None, construct_undefined)
            
            if not os.path.exists(config_file_to_use):
                return True
            
            async with aiofiles.open(config_file_to_use, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = pyyaml.load(content, Loader=SafeLoaderIgnoreUnknown) or {}
            
            if 'streams' in config:
                if stream_name in config['streams']:
                    del config['streams'][stream_name]
                    
                    yaml_content = pyyaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    async with aiofiles.open(config_file_to_use, 'w', encoding='utf-8') as f:
                        await f.write(yaml_content)
                    
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
