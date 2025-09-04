from __future__ import annotations
import os
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN, STATIC_URL, PANEL_REL_PATH, CONF_SIDEBAR

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    panel_abs = hass.config.path(PANEL_REL_PATH)
    panel_dir = os.path.dirname(panel_abs)

    if os.path.exists(panel_abs):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, panel_dir, cache=True)]
        )
        url_cfg = {"url": f"{STATIC_URL}/panel.html"}
    else:
        _LOGGER.warning("Panel missing at %s; using /local fallback", panel_abs)
        url_cfg = {"url": "/local/mellow_pill/panel.html"}

    if entry.options.get(CONF_SIDEBAR, True):
        await hass.components.frontend.async_register_built_in_panel(
            component_name="iframe",
            sidebar_title="Pill Dispenser",
            sidebar_icon="mdi:pill",
            config=url_cfg,
            require_admin=False,
        )

    from .websocket_api import async_register_ws
    async_register_ws(hass, entry)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
