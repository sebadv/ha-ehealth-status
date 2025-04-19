import logging
import json
import aiohttp

from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed
)
from .const import API_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors only for user‑selected services."""
    selected = entry.options.get("services") or entry.data.get("services", [])
    coordinator = EHealthCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for comp in coordinator.data:
        cid    = comp.get("id")
        name   = comp.get("name_nl")
        status = comp.get("status_name")
        if not (cid and name and status):
            continue
        if name not in selected:
            continue
        sensors.append(EHealthSensor(coordinator, cid, name))

    if not sensors:
        _LOGGER.warning("No selected eHealth services found.")
    async_add_entities(sensors, True)


class EHealthCoordinator(DataUpdateCoordinator):
    """Fetch component status every minute."""

    def __init__(self, hass):
        super().__init__(
            hass, _LOGGER,
            name="eHealth Status Coordinator",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    text = await resp.text()
                    raw = json.loads(text)
                    return raw.get("data", raw) if isinstance(raw, dict) else raw
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}") from e


class EHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single eHealth service."""

    def __init__(self, coordinator, component_id, name):
        super().__init__(coordinator)
        self._component_id = component_id
        self._attr_name = name
        self._attr_unique_id = f"ehealth_{component_id}"

    @property
    def state(self):
        for comp in self.coordinator.data:
            if comp.get("id") == self._component_id:
                return comp.get("status_name")
        return "unknown"
