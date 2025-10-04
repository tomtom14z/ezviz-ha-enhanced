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
            import yaml as pyyaml
            
            # Toujours utiliser go2rtc.yaml pour éviter les problèmes avec !include
            config_file_to_use = self._go2rtc_config_file
            
            _LOGGER.debug(f"EZVIZ Enhanced: Utilisation du fichier: {config_file_to_use}")
            
            if not os.path.exists(config_file_to_use):
                # Créer go2rtc.yaml
                config = {'streams': {}}
                _LOGGER.info(f"📝 EZVIZ Enhanced: Création de {config_file_to_use}")
            else:
                # Utiliser une lecture synchrone avec l'utilitaire HA YAML
                try:
                    config = await self.hass.async_add_executor_job(
                        ha_yaml.load_yaml, config_file_to_use
                    ) or {}
                except Exception as yaml_error:
                    _LOGGER.info(f"♻️ EZVIZ Enhanced: Recréation de go2rtc.yaml (métadonnées incompatibles détectées)")
                    _LOGGER.debug(f"Détails: {yaml_error}")
                    # Si le fichier contient des métadonnées problématiques,
                    # on repart de zéro avec un fichier propre
                    config = {'streams': {}}
            
            # go2rtc.yaml : les streams sont à la racine
            if 'streams' not in config:
                config['streams'] = {}
            streams_dict = config['streams']
            
            # Ajouter ou mettre à jour le stream
            old_url = streams_dict.get(stream_name)
            
            if isinstance(old_url, list) and len(old_url) > 0:
                old_url = old_url[0]
            
            streams_dict[stream_name] = [hls_url]
            
            # Écrire la configuration mise à jour
            def write_yaml():
                yaml_content = pyyaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
                with open(config_file_to_use, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
            
            await self.hass.async_add_executor_job(write_yaml)
            
            if old_url != hls_url:
                _LOGGER.info("=" * 80)
                _LOGGER.info(f"✅ EZVIZ Enhanced: Stream go2rtc configuré pour {serial}")
                _LOGGER.info("=" * 80)
                _LOGGER.info(f"📍 Stream: {stream_name}")
                _LOGGER.info(f"🔗 URL RTSP: {rtsp_url}")
                _LOGGER.info(f"📁 Fichier: {config_file_to_use}")
                
                # Vérifier la disponibilité de go2rtc
                reload_success = await self._reload_go2rtc()
                if reload_success:
                    _LOGGER.info(f"✅ go2rtc est disponible - Stream prêt à l'emploi!")
                else:
                    _LOGGER.info(f"💡 go2rtc détectera le nouveau stream automatiquement")
                    _LOGGER.info(f"   Note: go2rtc recharge sa configuration à chaque accès")
                
                _LOGGER.info("=" * 80)
            
            self._streams[serial] = rtsp_url
            return rtsp_url
            
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la mise à jour de configuration.yaml: {e}")
            return None

    async def _reload_go2rtc(self) -> bool:
        """Reload go2rtc configuration via API or service."""
        # Essayer d'abord l'API HTTP de go2rtc (méthode la plus fiable)
        try:
            async with aiohttp.ClientSession() as session:
                # go2rtc recharge automatiquement au prochain appel de stream
                # On teste simplement la disponibilité de l'API
                async with session.get(
                    f"{self._go2rtc_url}/api/streams",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        return True
        except Exception as api_error:
            _LOGGER.debug(f"🔴 EZVIZ Enhanced: API go2rtc non disponible: {api_error}")
        
        # Fallback: essayer le service Home Assistant si disponible
        try:
            if self.hass.services.has_service("go2rtc", "restart"):
                await self.hass.services.async_call(
                    "go2rtc",
                    "restart",
                    blocking=True
                )
                return True
        except Exception as e:
            _LOGGER.debug(f"🔴 EZVIZ Enhanced: Service HA go2rtc non disponible: {e}")
        
        return False

    async def async_update_stream(self, serial: str, hls_url: str) -> Optional[str]:
        """Update an existing stream with a new HLS URL."""
        return await self.async_add_stream(serial, hls_url)

    async def async_remove_stream(self, serial: str) -> bool:
        """Remove a stream from go2rtc configuration."""
        stream_name = f"ezviz_{serial}"
        config_file_to_use = self._go2rtc_config_file
        
        try:
            import yaml as pyyaml
            
            if not os.path.exists(config_file_to_use):
                return True
            
            # Utiliser une lecture synchrone avec l'utilitaire HA YAML
            try:
                config = await self.hass.async_add_executor_job(
                    ha_yaml.load_yaml, config_file_to_use
                ) or {}
            except Exception as yaml_error:
                _LOGGER.debug(f"EZVIZ Enhanced: Impossible de lire go2rtc.yaml: {yaml_error}")
                config = {'streams': {}}
            
            if 'streams' in config:
                if stream_name in config['streams']:
                    del config['streams'][stream_name]
                    
                    # Écrire la configuration mise à jour
                    def write_yaml():
                        yaml_content = pyyaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
                        with open(config_file_to_use, 'w', encoding='utf-8') as f:
                            f.write(yaml_content)
                    
                    await self.hass.async_add_executor_job(write_yaml)
                    
                    _LOGGER.info(f"🗑️ EZVIZ Enhanced: Stream go2rtc supprimé pour {serial}")
            
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
