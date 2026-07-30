"""Config flow for Utilități Moldova integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CONTRACT_NUMBER,
    CONF_PASSWORD,
    CONF_PLACE_OF_CONSUMPTION,
    CONF_PROVIDER,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    PROVIDERS,
)
from .providers import get_provider_instance

_LOGGER = logging.getLogger(__name__)


class UtilitatiMDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Utilități Moldova."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step where user configures provider credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            provider_id = user_input[CONF_PROVIDER]
            contract_number = user_input[CONF_CONTRACT_NUMBER]
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            place_of_consumption = user_input.get(CONF_PLACE_OF_CONSUMPTION)

            # Prevent duplicate entries for the same provider and contract number
            await self.async_set_unique_id(f"{provider_id}_{contract_number}")
            self._abort_if_unique_id_configured()

            # Test authentication with provider connector
            try:
                provider_inst = get_provider_instance(
                    provider_id=provider_id,
                    contract_number=contract_number,
                    place_of_consumption=place_of_consumption,
                    username=username,
                    password=password,
                )
                auth_success = await provider_inst.async_authenticate()
                if not auth_success:
                    errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.error("Failed to authenticate with provider %s: %s", provider_id, err)
                errors["base"] = "cannot_connect"

            if not errors:
                provider_name = PROVIDERS.get(provider_id, {}).get("name", provider_id)
                title = f"{provider_name} ({contract_number})"

                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )

        provider_options = {k: v["name"] for k, v in PROVIDERS.items()}

        schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER): vol.In(provider_options),
                vol.Required(CONF_CONTRACT_NUMBER): str,
                vol.Optional(CONF_PLACE_OF_CONSUMPTION): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow handler."""
        return UtilitatiMDOptionsFlowHandler(config_entry)


class UtilitatiMDOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Utilități Moldova."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage option updates (e.g. scan interval)."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
