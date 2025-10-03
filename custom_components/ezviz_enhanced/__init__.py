"""EZVIZ Enhanced Integration for Home Assistant."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, CONF_APP_KEY, CONF_APP_SECRET
from .coordinator import EzvizDataUpdateCoordinator
from .api import EzvizApi, EzvizOpenApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["camera", "binary_sensor", "sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EZVIZ Enhanced from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize APIs
    ezviz_api = EzvizApi(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )
    
    # Initialize EZVIZ Open Platform API if credentials provided
    ezviz_open_api = None
    if CONF_APP_KEY in entry.data and CONF_APP_SECRET in entry.data:
        ezviz_open_api = EzvizOpenApi(
            app_key=entry.data[CONF_APP_KEY],
            app_secret=entry.data[CONF_APP_SECRET],
        )
    
    # Initialize coordinator
    coordinator = EzvizDataUpdateCoordinator(
        hass, ezviz_api, ezviz_open_api, entry.data
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
