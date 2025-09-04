from __future__ import annotations
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import websocket_api
from homeassistant.helpers.storage import Store

DOMAIN = "mellow_pill"
STORE_SCHEDULES = "mellow_pill_schedules.json"
STORE_SETTINGS  = "mellow_pill_settings.json"

def _store(hass: HomeAssistant, fname: str) -> Store:
    return Store(hass, 1, fname)

@callback
def async_register_ws(hass: HomeAssistant) -> None:
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

    @websocket_api.websocket_command({
        "type": "mellow_pill/test_motor",
        "device_id": str,
        "container": int,
        "motor_speed": int,
        "trigger_threshold": int
    })
    @websocket_api.async_response
    async def ws_test_motor(hass, connection, msg):
        await hass.services.async_call(
            "esphome",
            "pill_dispenser_test_motor",
            {
                "device_id": msg["device_id"],
                "container": msg["container"],
                "speed": msg["motor_speed"],
                "threshold": msg["trigger_threshold"],
            },
            blocking=True,
        )
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({
        "type": "mellow_pill/dispense",
        "device_id": str,
        "container": int,
        "pills": int,
        "speed": int,
        "threshold": int
    })
    @websocket_api.async_response
    async def ws_dispense(hass, connection, msg):
        await hass.services.async_call(
            "esphome",
            "pill_dispenser_dispense",
            {
                "device_id": msg["device_id"],
                "container": msg["container"],
                "pills": msg["pills"],
                "speed": msg["speed"],
                "threshold": msg["threshold"],
            },
            blocking=True,
        )
        connection.send_result(msg["id"], {"ok": True})
