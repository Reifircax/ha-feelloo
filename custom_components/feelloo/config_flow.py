"""Config flow for Feelloo integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CATS_UPDATE_INTERVAL,
    CONF_ACTIVITY_UPDATE_INTERVAL,
    CONF_ACTIVITY_WEEK_UPDATE_INTERVAL,
    CONF_ACTIVITY_MONTH_UPDATE_INTERVAL,
    CONF_TERRITORY_UPDATE_INTERVAL,
    CONF_SESSION_UPDATE_INTERVAL,
    DEFAULT_CATS_UPDATE_INTERVAL,
    DEFAULT_ACTIVITY_UPDATE_INTERVAL,
    DEFAULT_ACTIVITY_WEEK_UPDATE_INTERVAL,
    DEFAULT_ACTIVITY_MONTH_UPDATE_INTERVAL,
    DEFAULT_TERRITORY_UPDATE_INTERVAL,
    DEFAULT_SESSION_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL_MINUTES,
    MAX_UPDATE_INTERVAL_MINUTES,
    FIREBASE_API_KEY,
    FIREBASE_SIGNIN_URL,
)

_LOGGER = logging.getLogger(__name__)

AUTH_TIMEOUT = aiohttp.ClientTimeout(total=30)

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

UPDATE_INTERVAL_VALIDATOR = vol.All(
    vol.Coerce(int),
    vol.Range(min=MIN_UPDATE_INTERVAL_MINUTES, max=MAX_UPDATE_INTERVAL_MINUTES),
)

# Configurable polling intervals: (conf_key, default_minutes)
POLLING_INTERVAL_FIELDS = [
    (CONF_CATS_UPDATE_INTERVAL, DEFAULT_CATS_UPDATE_INTERVAL),
    (CONF_ACTIVITY_UPDATE_INTERVAL, DEFAULT_ACTIVITY_UPDATE_INTERVAL),
    (CONF_ACTIVITY_WEEK_UPDATE_INTERVAL, DEFAULT_ACTIVITY_WEEK_UPDATE_INTERVAL),
    (CONF_ACTIVITY_MONTH_UPDATE_INTERVAL, DEFAULT_ACTIVITY_MONTH_UPDATE_INTERVAL),
    (CONF_TERRITORY_UPDATE_INTERVAL, DEFAULT_TERRITORY_UPDATE_INTERVAL),
    (CONF_SESSION_UPDATE_INTERVAL, DEFAULT_SESSION_UPDATE_INTERVAL),
]


async def _async_test_credentials(hass, email: str, password: str) -> tuple[bool, str | None]:
    """Test Firebase credentials.
    
    Returns (success, error_key) where error_key is None on success,
    or 'cannot_connect', 'invalid_auth' on failure.
    """
    url = f"{FIREBASE_SIGNIN_URL}?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    session = async_get_clientsession(hass)
    try:
        async with session.post(url, json=payload, timeout=AUTH_TIMEOUT) as resp:
            if resp.status == 200:
                return True, None
            try:
                data = await resp.json()
                error = data.get("error", {}).get("message", "")
                _LOGGER.debug("Firebase auth error: %s", error)
            except Exception:
                error = ""
            if "INVALID_PASSWORD" in error or "EMAIL_NOT_FOUND" in error or "INVALID_EMAIL" in error:
                return False, "invalid_auth"
            return False, "cannot_connect"
    except asyncio.TimeoutError:
        _LOGGER.warning("Firebase auth timeout for %s", email)
        return False, "cannot_connect"
    except aiohttp.ClientError as err:
        _LOGGER.warning("Firebase auth connection error: %s", err)
        return False, "cannot_connect"


class FeellooConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Feelloo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].strip().casefold()
            password = user_input[CONF_PASSWORD]

            valid, error_key = await _async_test_credentials(self.hass, email, password)
            if valid:
                await self.async_set_unique_id(email)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=email,
                    data={CONF_EMAIL: email, CONF_PASSWORD: password},
                )
            errors["base"] = error_key or "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=AUTH_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> FeellooOptionsFlowHandler:
        """Get the options flow for this handler."""
        # Modern OptionsFlow (HA >= 2026.9) exposes a read-only `config_entry`
        # property resolved from hass.config_entries — no need to pass it here.
        return FeellooOptionsFlowHandler()


class FeellooOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Feelloo."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Start the options flow by showing the menu."""
        return await self.async_step_menu()

    async def async_step_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the configuration menu."""
        if user_input is not None:
            next_step = user_input["next_step_id"]
            if next_step == "polling":
                return await self.async_step_polling()
            return await self.async_step_credentials()
        return self.async_show_menu(
            step_id="menu",
            menu_options=["credentials", "polling"],
        )

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Update Feelloo account credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].strip().casefold()
            password = user_input[CONF_PASSWORD]

            valid, error_key = await _async_test_credentials(self.hass, email, password)
            if valid:
                # Update config entry data with new credentials
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={CONF_EMAIL: email, CONF_PASSWORD: password},
                )
                # Keep existing options (polling intervals) untouched
                result = self.async_create_entry(
                    title=email,
                    data=dict(self.config_entry.options or {}),
                )
                # Reload the integration so the new credentials take effect immediately
                # (async_schedule_reload is synchronous and schedules the reload itself)
                self.hass.config_entries.async_schedule_reload(
                    self.config_entry.entry_id
                )
                return result
            errors["base"] = error_key or "invalid_auth"

        return self.async_show_form(
            step_id="credentials",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL, default=self.config_entry.data.get(CONF_EMAIL)
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_polling(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Update the polling intervals (no credentials required)."""
        current_options = self.config_entry.options or {}

        if user_input is not None:
            result = self.async_create_entry(
                title=self.config_entry.title,
                data={
                    conf_key: user_input[conf_key]
                    for conf_key, _default in POLLING_INTERVAL_FIELDS
                },
            )
            # Reload the integration so the new intervals take effect immediately
            # (async_schedule_reload is synchronous and schedules the reload itself)
            self.hass.config_entries.async_schedule_reload(
                self.config_entry.entry_id
            )
            return result

        data_schema: dict = {}
        for conf_key, default in POLLING_INTERVAL_FIELDS:
            data_schema[
                vol.Required(
                    conf_key,
                    default=current_options.get(conf_key, default),
                )
            ] = UPDATE_INTERVAL_VALIDATOR

        return self.async_show_form(
            step_id="polling",
            data_schema=vol.Schema(data_schema),
        )
