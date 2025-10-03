"""API classes for EZVIZ Enhanced integration."""
import logging
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from .const import (
    EZVIZ_OPEN_BASE_URL, EZVIZ_OPEN_API_BASE, EZVIZ_OPEN_AUTH_URL, EZVIZ_OPEN_DEVICE_URL, 
    EZVIZ_OPEN_LIVE_URL, EZVIZ_OPEN_CAPABILITY_URL, EZVIZ_OPEN_LIVE_CONSOLE_URL,
    EZVIZ_API_BASE, EZVIZ_AUTH_URL, EZVIZ_DEVICE_URL
)

_LOGGER = logging.getLogger(__name__)


class EzvizApi:
    """EZVIZ Cloud API client."""
    
    def __init__(self, username: str, password: str):
        """Initialize EZVIZ API client."""
        self.username = username
        self.password = password
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def async_get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def async_close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def async_get_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices from EZVIZ cloud."""
        # This would integrate with the original pyEzvizApi
        # For now, return empty list as placeholder
        return []


class EzvizOpenApi:
    """EZVIZ Open Platform API client (IeuOpen) with authentication."""

    def __init__(self, app_key: str = None, app_secret: str = None):
        """Initialize EZVIZ Open Platform API client."""
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def async_get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def async_close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def async_authenticate(self) -> bool:
        """Authenticate with EZVIZ Open Platform."""
        try:
            session = await self.async_get_session()

            if not self.app_key or not self.app_secret:
                _LOGGER.error("App Key and App Secret are required for EZVIZ Open authentication")
                return False

            # EZVIZ Open Platform authentication
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "appKey": self.app_key,
                "appSecret": self.app_secret
            }

            async with session.post(EZVIZ_OPEN_AUTH_URL, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("code") == "200":
                        self.access_token = result.get("data", {}).get("accessToken")
                        _LOGGER.info("Authenticated with EZVIZ Open Platform")
                        return True
                    else:
                        _LOGGER.error(f"EZVIZ Open authentication failed: {result.get('msg', 'Unknown error')}")
                        return False
                else:
                    _LOGGER.error(f"EZVIZ Open authentication HTTP error: {response.status}")
                    return False

        except Exception as e:
            _LOGGER.error(f"EZVIZ Open authentication error: {e}")
            return False
    
    async def _authenticate_ezviz_cloud(self) -> bool:
        """Authenticate with EZVIZ cloud API as fallback."""
        try:
            session = await self.async_get_session()
            
            # EZVIZ cloud authentication
            auth_data = {
                "account": self.username,
                "password": self.password
            }
            
            async with session.post(EZVIZ_AUTH_URL, json=auth_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("resultCode") == "0":
                        self.access_token = data.get("accessToken")
                        _LOGGER.info("Authenticated with EZVIZ cloud API")
                        return True
                    else:
                        _LOGGER.error(f"EZVIZ authentication failed: {data.get('resultDes', 'Unknown error')}")
                        return False
                    
        except Exception as e:
            _LOGGER.error(f"EZVIZ cloud authentication error: {e}")
            
        return False
    
    def get_live_url(self, serial: str, channel: int = 1, address_type: int = 1) -> str:
        """Generate live stream URL for EZVIZ Open Platform."""
        params = {
            "serial": serial,
            "channelNo": channel,
            "addressType": address_type
        }
        return f"{EZVIZ_OPEN_LIVE_CONSOLE_URL}?{urlencode(params)}"
    
    async def async_get_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices from EZVIZ Open Platform."""
        if not self.access_token:
            await self.async_authenticate()
            
        if not self.access_token:
            return []
            
        try:
            session = await self.async_get_session()
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # EZVIZ Open API uses form data
            data = {
                "accessToken": self.access_token
            }
            
            async with session.post(EZVIZ_OPEN_DEVICE_URL, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("code") == "200":
                        return result.get("data", [])
                    else:
                        _LOGGER.error(f"Error getting devices: {result.get('msg', 'Unknown error')}")
                        return []
                else:
                    _LOGGER.error(f"Failed to get devices: {response.status}")
                    return []
                    
        except Exception as e:
            _LOGGER.error(f"Error getting devices: {e}")
            return []
    
    async def async_get_stream_info(self, serial: str, channel: int = 1) -> Dict[str, Any]:
        """Get stream information from EZVIZ Open Platform with multiple protocols and qualities."""
        if not self.access_token:
            await self.async_authenticate()
            
        if not self.access_token:
            return {}
            
        try:
            session = await self.async_get_session()
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Try to get HLS Fluent (sub-bitrate) first as it's more stable
            protocols_to_try = [
                {"protocol": "2", "quality": "2", "name": "hls_fluent"},  # HLS Fluent
                {"protocol": "2", "quality": "1", "name": "hls_hd"},      # HLS HD
                {"protocol": "4", "quality": "2", "name": "flv_fluent"},  # FLV Fluent
                {"protocol": "4", "quality": "1", "name": "flv_hd"},      # FLV HD
            ]
            
            for protocol_config in protocols_to_try:
                data = {
                    "accessToken": self.access_token,
                    "deviceSerial": serial,
                    "channelNo": str(channel),
                    "protocol": protocol_config["protocol"],
                    "quality": protocol_config["quality"],
                    "expireTime": "3600"  # 1 hour validity
                }
                
                async with session.post(EZVIZ_OPEN_LIVE_URL, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("code") == "200":
                            stream_data = result.get("data", {})
                            url = stream_data.get("url")
                            expire_time = stream_data.get("expireTime")
                            
                            if url:
                                _LOGGER.info(f"Successfully got {protocol_config['name']} stream for {serial}")
                                return {
                                    "serial": serial,
                                    "channel": channel,
                                    "status": "online",
                                    "stream_type": protocol_config["name"],
                                    "hls_url": url if "hls" in protocol_config["name"] else None,
                                    "flv_url": url if "flv" in protocol_config["name"] else None,
                                    "rtsp_url": None,  # Will be generated by converter
                                    "cloud_url": url,
                                    "expire_time": expire_time,
                                    "protocol": protocol_config["protocol"],
                                    "quality": protocol_config["quality"]
                                }
                        else:
                            _LOGGER.warning(f"Failed to get {protocol_config['name']}: {result.get('msg', 'Unknown error')}")
                    else:
                        _LOGGER.warning(f"HTTP error for {protocol_config['name']}: {response.status}")
            
            _LOGGER.error(f"No working stream found for {serial}")
            return {}
                    
        except Exception as e:
            _LOGGER.error(f"Error getting stream info: {e}")
            return {}
    
    async def async_get_hls_url(self, serial: str, channel: int = 1) -> Optional[str]:
        """Get HLS URL for the camera."""
        stream_info = await self.async_get_stream_info(serial, channel)
        return stream_info.get("hls_url")
    
    async def async_get_rtsp_url(self, serial: str, channel: int = 1) -> Optional[str]:
        """Get RTSP URL for the camera."""
        stream_info = await self.async_get_stream_info(serial, channel)
        return stream_info.get("rtsp_url")
    
    async def async_get_cloud_url(self, serial: str, channel: int = 1) -> Optional[str]:
        """Get cloud stream URL for the camera."""
        stream_info = await self.async_get_stream_info(serial, channel)
        return stream_info.get("cloud_url")


class StreamConverter:
    """Convert various stream formats to RTSP."""
    
    def __init__(self, rtsp_port: int = 8554):
        """Initialize stream converter."""
        self.rtsp_port = rtsp_port
        self.conversion_tasks: Dict[str, asyncio.Task] = {}
        self.rtsp_server_process = None
    
    async def start_rtsp_server(self):
        """Start RTSP server (if needed)."""
        # For now, we'll use direct HLS URLs
        # In a full implementation, you might want to start an RTSP server
        pass
    
    async def start_rtsp_conversion(self, serial: str, source_url: str, stream_type: str = "hls") -> str:
        """Start converting a stream to RTSP."""
        rtsp_url = f"rtsp://localhost:{self.rtsp_port}/ezviz_enhanced_{serial}"
        
        # For HLS streams, we can use FFmpeg to convert to RTSP
        if stream_type.startswith("hls"):
            cmd = [
                "ffmpeg",
                "-i", source_url,
                "-c", "copy",
                "-f", "rtsp",
                rtsp_url
            ]
        else:
            # For other formats, use different FFmpeg parameters
            cmd = [
                "ffmpeg",
                "-i", source_url,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-f", "rtsp",
                rtsp_url
            ]
        
        # Store the task for later cleanup
        task = asyncio.create_task(self._run_ffmpeg(cmd))
        self.conversion_tasks[serial] = task
        
        return rtsp_url
    
    async def get_direct_stream_url(self, serial: str, source_url: str, stream_type: str = "hls") -> str:
        """Get direct stream URL (preferred for HLS)."""
        # For HLS streams, return the URL directly as Home Assistant can handle it
        if stream_type.startswith("hls"):
            return source_url
        
        # For other formats, we might need conversion
        return await self.start_rtsp_conversion(serial, source_url, stream_type)
    
    async def stop_rtsp_conversion(self, serial: str):
        """Stop RTSP conversion for a camera."""
        if serial in self.conversion_tasks:
            task = self.conversion_tasks[serial]
            task.cancel()
            del self.conversion_tasks[serial]
    
    async def _run_ffmpeg(self, cmd: List[str]):
        """Run FFmpeg process."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
        except asyncio.CancelledError:
            if process:
                process.terminate()
                await process.wait()
        except Exception as e:
            _LOGGER.error(f"FFmpeg error: {e}")
