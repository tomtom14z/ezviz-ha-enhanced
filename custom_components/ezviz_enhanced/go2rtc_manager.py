"""go2rtc Manager for EZVIZ Enhanced integration."""
import asyncio
import logging
from typing import Optional, Dict
import os
import aiohttp

_LOGGER = logging.getLogger(__name__)


class Go2RtcManager:
    """Manager for go2rtc streams via configuration file."""

    def __init__(self, hass, go2rtc_addon_id: str = None, stream_quality: str = "smooth"):
        """Initialize go2rtc manager."""
        self.hass = hass
        self._streams: Dict[str, str] = {}
        # go2rtc peut utiliser configuration.yaml OU go2rtc.yaml
        self._config_file = os.path.join(hass.config.config_dir, "configuration.yaml")
        self._go2rtc_config_file = os.path.join(hass.config.config_dir, "go2rtc.yaml")
        self._go2rtc_url = "http://localhost:1984"
        self._keepalive_tasks: Dict[str, asyncio.Task] = {}
        self._go2rtc_addon_id = go2rtc_addon_id
        self._stream_quality = stream_quality
        
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
                # Lire le fichier avec yaml standard (pas ha_yaml pour éviter les métadonnées)
                def read_yaml():
                    try:
                        with open(config_file_to_use, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Si le fichier contient des tags annotatedyaml, on le recrée
                            if 'annotatedyaml' in content or '!!python' in content:
                                _LOGGER.info(f"♻️ EZVIZ Enhanced: go2rtc.yaml contient des métadonnées, recréation...")
                                return None
                            return pyyaml.safe_load(content) or {}
                    except Exception as e:
                        _LOGGER.info(f"♻️ EZVIZ Enhanced: Erreur lecture go2rtc.yaml, recréation...")
                        _LOGGER.debug(f"Détails: {e}")
                        return None
                
                config = await self.hass.async_add_executor_job(read_yaml)
                if config is None:
                    config = {'streams': {}}
            
            # go2rtc.yaml : les streams sont à la racine
            if 'streams' not in config:
                config['streams'] = {}
            streams_dict = config['streams']
            
            # Ajouter les options globales go2rtc optimisées si elles n'existent pas
            if 'ffmpeg' not in config:
                config['ffmpeg'] = {
                    'bin': 'ffmpeg',
                    'rtsp': '-rtsp_transport tcp -timeout 5000000',
                    'hls': '-hls_time 2 -hls_list_size 3 -hls_flags delete_segments+independent_segments',
                    'webrtc': '-c:v libvpx -deadline realtime -cpu-used 4 -b:v 1M -maxrate 1M -bufsize 2M'
                }
            
            if 'rtsp' not in config:
                config['rtsp'] = {
                    'listen': ':8554',
                    'timeout': '10s',
                    'keepalive': '30s'
                }
            
            if 'webrtc' not in config:
                config['webrtc'] = {
                    'listen': ':8555',
                    'ice_servers': ['stun:stun.l.google.com:19302']
                }
            
            # Ajouter des options de performance
            if 'log' not in config:
                config['log'] = {
                    'level': 'info'
                }
            
            if 'api' not in config:
                config['api'] = {
                    'listen': ':1984',
                    'origin': '*'
                }
            
            # Ajouter ou mettre à jour le stream
            old_url = streams_dict.get(stream_name)
            
            if isinstance(old_url, list) and len(old_url) > 0:
                old_url = old_url[0]
            
            # Configuration go2rtc optimisée selon le mode choisi
            if self._stream_quality == "smooth":
                # Mode fluide : priorité à la fluidité, moins de buffer
                ffmpeg_source = (
                    f"ffmpeg:{stream_name}#video=copy#audio=copy"
                    f"#raw=-fflags +nobuffer+fastseek+flush_packets "
                    f"-flags low_delay -strict experimental "
                    f"-avioflags direct -fflags +genpts+igndts "
                    f"-analyzeduration 500000 -probesize 500000 "
                    f"-timeout 5000000 -reconnect 1 -reconnect_streamed 1 "
                    f"-reconnect_delay_max 1 -max_reconnect_attempts 2 "
                    f"-use_wallclock_as_timestamps 1 -avoid_negative_ts make_zero "
                    f"-max_delay 100000 -rtbufsize 512k -maxrate 1M -bufsize 1M"
                )
            else:
                # Mode qualité : priorité à la qualité, plus de buffer
                ffmpeg_source = (
                    f"ffmpeg:{stream_name}#video=copy#audio=copy"
                    f"#raw=-fflags +genpts+igndts "
                    f"-flags low_delay -strict experimental "
                    f"-avioflags direct "
                    f"-analyzeduration 2000000 -probesize 2000000 "
                    f"-timeout 5000000 -reconnect 1 -reconnect_streamed 1 "
                    f"-reconnect_delay_max 2 -max_reconnect_attempts 3 "
                    f"-use_wallclock_as_timestamps 1 -avoid_negative_ts make_zero "
                    f"-max_delay 1000000 -rtbufsize 4M -maxrate 4M -bufsize 8M"
                )
            
            streams_dict[stream_name] = [
                hls_url,           # Essayer d'abord l'URL directe
                ffmpeg_source      # Fallback avec FFmpeg si l'URL directe ne marche pas
            ]
            
            # Écrire la configuration mise à jour
            def write_yaml():
                yaml_content = pyyaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
                with open(config_file_to_use, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
            
            await self.hass.async_add_executor_job(write_yaml)
            
            # Forcer rechargement go2rtc après écriture du fichier (avec nom du stream)
            reload_success = await self._reload_go2rtc(stream_name=stream_name)
            
            if old_url != hls_url:
                _LOGGER.info("=" * 80)
                _LOGGER.info(f"✅ EZVIZ Enhanced: Stream go2rtc configuré pour {serial}")
                _LOGGER.info("=" * 80)
                _LOGGER.info(f"📍 Stream: {stream_name}")
                _LOGGER.info(f"🔗 URL RTSP: {rtsp_url}")
                _LOGGER.info(f"📁 Fichier: {config_file_to_use}")
                _LOGGER.info(f"🎬 Sources: URL directe HLS + FFmpeg (reconnexion automatique)")
                _LOGGER.info("")
                
                if reload_success:
                    _LOGGER.info(f"✅ go2rtc rechargé automatiquement!")
                    _LOGGER.info(f"")
                    _LOGGER.info(f"📺 Interface go2rtc: http://localhost:1984/")
                    _LOGGER.info(f"   → Cliquez sur '{stream_name}' pour visualiser le stream")
                    _LOGGER.info(f"")
                    _LOGGER.info(f"🔗 URL RTSP pour VLC/Homebridge: {rtsp_url}")
                else:
                    _LOGGER.warning(f"⚠️  go2rtc n'est pas installé ou ne fonctionne pas")
                    _LOGGER.warning(f"")
                    _LOGGER.warning(f"Pour utiliser les streams RTSP, installez go2rtc:")
                    _LOGGER.warning(f"1. Dans HACS, recherchez et installez 'WebRTC Camera'")
                    _LOGGER.warning(f"2. OU installez l'add-on go2rtc dans Modules complémentaires")
                    _LOGGER.warning(f"3. Redémarrez Home Assistant")
                    _LOGGER.warning(f"")
                    _LOGGER.warning(f"Documentation: https://github.com/AlexxIT/go2rtc")
                
                _LOGGER.info("=" * 80)
            
            self._streams[serial] = rtsp_url
            return rtsp_url
            
        except Exception as e:
            _LOGGER.error(f"🔴 EZVIZ Enhanced: Erreur lors de la mise à jour de configuration.yaml: {e}")
            return None

    async def _reload_go2rtc(self, stream_name: str = None) -> bool:
        """Reload go2rtc configuration via API or service."""
        # Méthode 1 : Utiliser l'ID configuré ou découvrir l'add-on go2rtc automatiquement
        go2rtc_addon_id = self._go2rtc_addon_id
        
        if not go2rtc_addon_id:
            try:
                # Lister les add-ons installés via l'API Supervisor
                if self.hass.services.has_service("hassio", "addon_info"):
                    # Chercher parmi les add-ons connus
                    known_addons = [
                        "a0d7b954_go2rtc",
                        "alexxit_go2rtc", 
                        "core_go2rtc",
                        "local_go2rtc",
                    ]
                    
                    for addon_id in known_addons:
                        try:
                            result = await self.hass.services.async_call(
                                "hassio",
                                "addon_info",
                                {"addon": addon_id},
                                blocking=True,
                                return_response=True
                            )
                            if result and "data" in result:
                                go2rtc_addon_id = addon_id
                                _LOGGER.info(f"✅ Add-on go2rtc détecté : {addon_id}")
                                break
                        except:
                            continue
            except Exception as e:
                _LOGGER.debug(f"Détection automatique add-on échouée: {e}")
        else:
            _LOGGER.info(f"🔄 Utilisation de l'ID go2rtc configuré : {go2rtc_addon_id}")
        
        # Méthode 2 : Redémarrer l'add-on si trouvé
        if go2rtc_addon_id:
            try:
                _LOGGER.info(f"🔄 Redémarrage add-on go2rtc ({go2rtc_addon_id})...")
                await self.hass.services.async_call(
                    "hassio",
                    "addon_restart",
                    {"addon": go2rtc_addon_id},
                    blocking=False
                )
                await asyncio.sleep(3)
                
                # Vérifier que go2rtc répond
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self._go2rtc_url}/api/streams",
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        if response.status == 200:
                            _LOGGER.info(f"✅ Add-on go2rtc redémarré avec succès!")
                            return True
            except Exception as e:
                _LOGGER.warning(f"⚠️ Échec redémarrage add-on: {e}")
        
        _LOGGER.warning("⚠️ Add-on go2rtc non trouvé, tentative reload API...")
        
        # Méthode 2 : Reload via API (moins fiable mais fonctionne sans add-on)
        try:
            async with aiohttp.ClientSession() as session:
                # Étape 1 : Recharger la configuration
                async with session.post(
                    f"{self._go2rtc_url}/api/config/reload",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status in [200, 204]:
                        _LOGGER.info("✅ Configuration go2rtc rechargée via API")
                        _LOGGER.warning("⚠️ Reload API utilisé : stream peut nécessiter reconnexion manuelle")
                        return True
        except Exception as api_error:
            _LOGGER.debug(f"API reload échouée: {api_error}")
        
        # Méthode 3 : Vérifier que go2rtc fonctionne au moins
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._go2rtc_url}/api/streams",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        _LOGGER.info("⚠️  go2rtc fonctionne mais rechargement auto échoué")
                        _LOGGER.info("   → Rechargement manuel requis dans ~2h (expiration URL)")
                        return True
        except Exception:
            pass
        
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
            
            # Lire le fichier avec yaml standard (pas ha_yaml pour éviter les métadonnées)
            def read_yaml():
                try:
                    with open(config_file_to_use, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Si le fichier contient des tags annotatedyaml, on le recrée
                        if 'annotatedyaml' in content or '!!python' in content:
                            return None
                        return pyyaml.safe_load(content) or {}
                except Exception as e:
                    _LOGGER.debug(f"EZVIZ Enhanced: Impossible de lire go2rtc.yaml: {e}")
                    return None
            
            config = await self.hass.async_add_executor_job(read_yaml)
            if config is None:
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
        """Return if go2rtc configuration is available (always True - we create go2rtc.yaml)."""
        # On retourne toujours True car on crée go2rtc.yaml automatiquement
        # go2rtc chargera les streams au démarrage ou au prochain accès
        return True
