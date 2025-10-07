"""Config flow for EZVIZ Enhanced integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .const import (
    DOMAIN,
    CONF_USE_IEUOPEN,
    CONF_RTSP_PORT,
    CONF_CAMERAS,
    CONF_SERIAL,
    CONF_CHANNEL,
    CONF_ENABLED,
    CONF_APP_KEY,
    CONF_APP_SECRET,
    CONF_GO2RTC_ADDON_ID,
    DEFAULT_RTSP_PORT,
    DEFAULT_USE_IEUOPEN,
    DEFAULT_GO2RTC_ADDON_ID,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_USE_IEUOPEN, default=DEFAULT_USE_IEUOPEN): bool,
        vol.Optional(CONF_APP_KEY): str,
        vol.Optional(CONF_APP_SECRET): str,
        vol.Optional(CONF_RTSP_PORT, default=DEFAULT_RTSP_PORT): int,
        vol.Optional(CONF_GO2RTC_ADDON_ID, default=DEFAULT_GO2RTC_ADDON_ID): str,
    }
)

STEP_CAMERA_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERIAL): str,
        vol.Optional(CONF_CHANNEL, default=1): int,
        vol.Optional("name"): str,
        vol.Optional(CONF_ENABLED, default=True): bool,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Here you would validate the credentials with EZVIZ API
    # For now, we'll just return the data
    return {"title": f"EZVIZ Enhanced ({data[CONF_USERNAME]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EZVIZ Enhanced."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self.cameras = []
        self.user_data = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            self.user_data = user_input
            return await self.async_step_cameras()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_cameras(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle camera configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="cameras", data_schema=STEP_CAMERA_DATA_SCHEMA
            )

        # Add camera to list
        camera_data = {
            CONF_SERIAL: user_input[CONF_SERIAL],
            CONF_CHANNEL: user_input[CONF_CHANNEL],
            "name": user_input.get("name", f"EZVIZ {user_input[CONF_SERIAL]}"),
            CONF_ENABLED: user_input[CONF_ENABLED],
        }
        self.cameras.append(camera_data)

        # Ask if user wants to add more cameras
        return self.async_show_form(
            step_id="add_more",
            data_schema=vol.Schema({
                vol.Required("add_more", default=False): bool,
            }),
        )

    async def async_step_add_more(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle add more cameras step."""
        if user_input is None:
            return self.async_show_form(
                step_id="add_more",
                data_schema=vol.Schema({
                    vol.Required("add_more", default=False): bool,
                }),
            )

        if user_input["add_more"]:
            return await self.async_step_cameras()

        # Finalize configuration
        config_data = {
            **self.user_data,
            CONF_CAMERAS: self.cameras,
        }

        return self.async_create_entry(
            title=f"EZVIZ Enhanced ({self.user_data[CONF_USERNAME]})",
            data=config_data,
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)
