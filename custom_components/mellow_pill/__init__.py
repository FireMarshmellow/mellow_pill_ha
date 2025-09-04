from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, STATIC_URL, CONF_SIDEBAR

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # YAML not required; purely UI/config-entry driven.
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Serve static panel files
    hass.http.register_static_path(
        STATIC_URL, hass.config.path("www/mellow_pill"), cache_headers=True
    )

    # Optional sidebar
    add_sidebar = entry.options.get(CONF_SIDEBAR, True)
    if add_sidebar:
        await hass.components.frontend.async_register_built_in_panel(
            component_name="iframe",
            sidebar_title="Pill Dispenser",
            sidebar_icon="mdi:pill",
            config={"url": f"{STATIC_URL}/panel.html"},
            require_admin=False,
        )

    # Register WS API with access to this entry's options
    from .websocket_api import async_register_ws
    async_register_ws(hass, entry)

    # Keep reference (not strictly needed now)
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = entry

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    # Panel removal requires restart; acceptable for now.
    return True
