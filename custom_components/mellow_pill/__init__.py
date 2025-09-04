from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.components import http, websocket_api

DOMAIN = "mellow_pill"
PANEL_URL_PATH = "/mellow_pill"
STATIC_URL = "/mellow_pill_static"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # Serve your static panel files
    hass.http.register_static_path(
        STATIC_URL, hass.config.path("www/mellow_pill"), cache_headers=True
    )

    # Register a sidebar panel pointing to the static HTML
    await hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Pill Dispenser",
        sidebar_icon="mdi:pill",
        config={"url": f"{STATIC_URL}/panel.html"},
        require_admin=False,
    )

    # Websocket commands (get/save schedules, test motor, etc.)
    from .websocket_api import async_register_ws
    async_register_ws(hass)

    return True
