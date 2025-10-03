"""Constants for EZVIZ Enhanced integration."""

DOMAIN = "ezviz_enhanced"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_USE_IEUOPEN = "use_ieuopen"
CONF_RTSP_PORT = "rtsp_port"
CONF_CAMERAS = "cameras"
CONF_SERIAL = "serial"
CONF_CHANNEL = "channel"
CONF_ENABLED = "enabled"
CONF_IEUOPEN_API_KEY = "ieuopen_api_key"
CONF_IEUOPEN_ACCESS_TOKEN = "ieuopen_access_token"
CONF_APP_KEY = "app_key"
CONF_APP_SECRET = "app_secret"

# Default values
DEFAULT_RTSP_PORT = 8554
DEFAULT_USE_IEUOPEN = True

# EZVIZ Open Platform API endpoints (IeuOpen)
EZVIZ_OPEN_BASE_URL = "https://open.ezvizlife.com"
EZVIZ_OPEN_API_BASE = f"{EZVIZ_OPEN_BASE_URL}/api/lapp"
EZVIZ_OPEN_AUTH_URL = f"{EZVIZ_OPEN_API_BASE}/token/get"
EZVIZ_OPEN_DEVICE_URL = f"{EZVIZ_OPEN_API_BASE}/device/list"
EZVIZ_OPEN_LIVE_URL = f"{EZVIZ_OPEN_API_BASE}/live/address/get"
EZVIZ_OPEN_CAPABILITY_URL = f"{EZVIZ_OPEN_API_BASE}/device/capability"
EZVIZ_OPEN_LIVE_CONSOLE_URL = "https://ieuopen.ezviz.com/console/setnormallive.html"

# EZVIZ Cloud API endpoints
EZVIZ_API_BASE = "https://api.ezvizlife.com"
EZVIZ_AUTH_URL = f"{EZVIZ_API_BASE}/api/user/login"  # URL corrigée
EZVIZ_DEVICE_URL = f"{EZVIZ_API_BASE}/api/device/list"

# Device types
DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_DOORBELL = "doorbell"

# Stream types
STREAM_TYPE_MAIN = "main"
STREAM_TYPE_SUB = "sub"
STREAM_TYPE_HLS = "hls"
STREAM_TYPE_RTSP = "rtsp"

# Attributes
ATTR_SERIAL = "serial"
ATTR_CHANNEL = "channel"
ATTR_DEVICE_TYPE = "device_type"
ATTR_RTSP_URL = "rtsp_url"
ATTR_HLS_URL = "hls_url"
ATTR_IEUOPEN_URL = "ieuopen_url"
ATTR_CLOUD_URL = "cloud_url"
ATTR_ACCESS_TOKEN = "access_token"