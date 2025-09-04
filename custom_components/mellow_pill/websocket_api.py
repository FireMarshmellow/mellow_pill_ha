from __future__ import annotations
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import websocket_api
from homeassistant.helpers.storage import Store
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_NODE_PREFIX, CONF_DEVICE_ID

STORE_SCHEDULES = "mellow_pill_schedules.json"
STORE_SETTINGS  = "mellow_pill_settings.json"

def _store(hass: HomeAssistant, fname: str) -> Store:
    return Store(hass, 1, fname)

@callback
def async_register_ws(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register websocket commands. Uses config entry options as defaults."""
    def _opts():
        return entry.options or {}

    # --- Health / debug ---
    @websocket_api.websocket_command({"type": "mellow_pill/ping"})
    @websocket_api.async_response
    async def ws_ping(hass, connection, msg):
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({"type": "mellow_pill/get_config"})
    @websocket_api.async_response
    async def ws_get_config(hass, connection, msg):
        connection.send_result(msg["id"], {
            "node_service_prefix": _opts().get(CONF_NODE_PREFIX, ""),
            "device_id": _opts().get(CONF_DEVICE_ID, "")
        })

    # --- Schedules / Settings persistence ---
    @websocket_api.websocket_command({ "type": "mellow_pill/get_schedules" })
    @websocket_api.async_response
    async def ws_get_schedules(hass, connection, msg):
        data = await _store(hass, STORE_SCHEDULES).async_load() or []
        connection.send_result(msg["id"], data)

    @websocket_api.websocket_command({
        "type": "mellow_pill/save_schedules",
        "schedules": list
    })
    @websocket_api.async_response
    async def ws_save_schedules(hass, connection, msg):
        await _store(hass, STORE_SCHEDULES).async_save(msg["schedules"])
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({ "type": "mellow_pill/get_settings" })
    @websocket_api.async_response
    async def ws_get_settings(hass, connection, msg):
        data = await _store(hass, STORE_SETTINGS).async_load() or {}
        connection.send_result(msg["id"], data)

    @websocket_api.websocket_command({
        "type": "mellow_pill/save_settings",
        "settings": dict
    })
    @websocket_api.async_response
    async def ws_save_settings(hass, connection, msg):
        await _store(hass, STORE_SETTINGS).async_save(msg["settings"])
        connection.send_result(msg["id"], {"ok": True})

    # --- Actions against ESPHome ---
    def _svc_prefix(msg):
        # Allow explicit override in call; else use config option.
        return msg.get("node_service_prefix") or _opts().get(CONF_NODE_PREFIX, "")

    def _device_id(msg):
        return msg.get("device_id") or _opts().get(CONF_DEVICE_ID, "")

    @websocket_api.websocket_command({
        "type": "mellow_pill/test_motor",
        "container": int,
        "motor_speed": int,
        "trigger_threshold": int,
        # optional:
        "device_id": str,
        "node_service_prefix": str
    })
    @websocket_api.async_response
    async def ws_test_motor(hass, connection, msg):
        node = _svc_prefix(msg)
        if not node:
            connection.send_error(msg["id"], "invalid", "Missing node_service_prefix (set it in integration options).")
            return
        # Call the ESPHome service esphome.<node>_test_motor
        await hass.services.async_call(
            "esphome",
            f"{node}_test_motor",
            {
                "container": msg["container"],
                "speed": msg["motor_speed"],
                "threshold": msg["trigger_threshold"],
            },
            blocking=True,
        )
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({
        "type": "mellow_pill/dispense",
        "container": int,
        "pills": int,
        # optional overrides:
        "speed": int,
        "threshold": int,
        "device_id": str,
        "node_service_prefix": str
    })
    @websocket_api.async_response
    async def ws_dispense(hass, connection, msg):
        node = _svc_prefix(msg)
        if not node:
            connection.send_error(msg["id"], "invalid", "Missing node_service_prefix (set it in integration options).")
            return
        data = {
            "container": msg["container"],
            "pills": msg["pills"],
        }
        if "speed" in msg: data["speed"] = msg["speed"]
        if "threshold" in msg: data["threshold"] = msg["threshold"]

        await hass.services.async_call(
            "esphome",
            f"{node}_dispense",
            data,
            blocking=True,
        )
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({
        "type": "mellow_pill/set_rtc",
        # optional:
        "device_id": str,
        "node_service_prefix": str
    })
    @websocket_api.async_response
    async def ws_set_rtc(hass, connection, msg):
        node = _svc_prefix(msg)
        if not node:
            connection.send_error(msg["id"], "invalid", "Missing node_service_prefix (set it in integration options).")
            return
        await hass.services.async_call(
            "esphome",
            f"{node}_set_rtc",
            {},
            blocking=True,
        )
        connection.send_result(msg["id"], {"ok": True})
