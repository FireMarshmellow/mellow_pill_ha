from homeassistant.core import HomeAssistant

DOMAIN = "mellow_pill"
STATIC_URL = "/mellow_pill_static"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # Serve static panel files
    hass.http.register_static_path(
        STATIC_URL, hass.config.path("www/mellow_pill"), cache_headers=True
    )
    # Sidebar panel to the static HTML
    await hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Pill Dispenser",
        sidebar_icon="mdi:pill",
        config={"url": f"{STATIC_URL}/panel.html"},
        require_admin=False,
    )
    from .websocket_api import async_register_ws
    async_register_ws(hass)
    return True
