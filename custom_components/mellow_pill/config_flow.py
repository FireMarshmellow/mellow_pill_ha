from __future__ import annotations
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_NODE_PREFIX, CONF_DEVICE_ID, CONF_SIDEBAR

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NODE_PREFIX): str,   # e.g. "pill_dispenser"
        vol.Optional(CONF_DEVICE_ID, default=""): str,
        vol.Optional(CONF_SIDEBAR, default=True): bool,
    }
)

class MellowPillConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=SCHEMA)

        title = "Mellow_labs Pill Dispenser"
        return self.async_create_entry(title=title, data={}, options=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return MellowPillOptionsFlow(config_entry)

class MellowPillOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self.entry.options
        schema = vol.Schema(
            {
                vol.Required(CONF_NODE_PREFIX, default=opts.get(CONF_NODE_PREFIX, "")): str,
                vol.Optional(CONF_DEVICE_ID, default=opts.get(CONF_DEVICE_ID, "")): str,
                vol.Optional(CONF_SIDEBAR, default=opts.get(CONF_SIDEBAR, True)): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)