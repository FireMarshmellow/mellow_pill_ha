from __future__ import annotations
import os
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig  # <-- NEW

from .const import DOMAIN, STATIC_URL, PANEL_REL_PATH, CONF_SIDEBAR

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # YAML-less; config entries drive setup.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    panel_abs = hass.config.path(PANEL_REL_PATH)
    panel_dir = os.path.dirname(panel_abs)

    # Register static path asynchronously (HA forbids the old blocking call)
    if os.path.exists(panel_abs):
        try:
            await hass.http.async_register_static_paths(  # <-- NEW
                [StaticPathConfig(STATIC_URL, panel_dir, cache=True)]
            )
        except Exception as e:
            _LOGGER.exception("Failed to register static path: %s", e)
    else:
        _LOGGER.warning(
            "Panel file missing at %s. The sidebar will point to /local/mellow_pill/panel.html. "
            "Place your file at /config/%s.",
            panel_abs, PANEL_REL_PATH
        )

    # Add sidebar (use STATIC_URL if we registered it, else /local/)
    add_sidebar = entry.options.get(CONF_SIDEBAR, True)
    if add_sidebar:
        url_cfg = (
            {"url": f"{STATIC_URL}/panel.html"}
            if os.path.exists(panel_abs)
            else {"url": "/local/mellow_pill/panel.html"}
        )
        try:
            await hass.components.frontend.async_register_built_in_panel(
                component_name="iframe",
                sidebar_title="Pill Dispenser",
                sidebar_icon="mdi:pill",
                config=url_cfg,
                require_admin=False,
            )
        except Exception as e:
            _LOGGER.exception("Failed to add sidebar panel: %s", e)

    # WebSocket API
    try:
        from .websocket_api import async_register_ws
        async_register_ws(hass, entry)
    except Exception as e:
        _LOGGER.exception("Failed to register websocket API: %s", e)
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry
    _LOGGER.info("Mellow_labs Pill Dispenser set up OK")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    # Static paths/panels are removed on restart; acceptable for now.
    return True
