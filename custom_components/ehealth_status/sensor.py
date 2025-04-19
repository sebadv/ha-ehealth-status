import logging
import json
import aiohttp

from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)
from homeassistant.helpers import entity_registry as er
from .const import API_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors only for user‑selected services, removing old ones."""

    selected = entry.options.get("services") or entry.data.get("services", [])
    # Extract selected component IDs for easy checking:
    # We’ll match by unique_id prefix ehealth_<id>
    # But to map name back to IDs, fetch all components first:
    async with aiohttp.ClientSession() as session:
        resp = await session.get(API_URL, timeout=10)
        text = await resp.text()
        raw = json.loads(text)
        all_data = raw.get("data", raw) if isinstance(raw, dict) else raw

    # Build a map from name_nl to id
    name_to_id = {c["name_nl"]: c["id"] for c in all_data if "name_nl" in c and "id" in c}
    selected_ids = {name_to_id[name] for name in selected if name in name_to_id}

    # 1) Remove any existing eHealth sensors not in selected_ids
    registry = er.async_get(hass)
    for entity in list(registry.entities.values()):
        if entity.domain != "sensor" or not entity.unique_id.startswith("ehealth_"):
            continue
        try:
            cid = int(entity.unique_id.split("_", 1)[1])
        except (ValueError, IndexError):
            continue
        if cid not in selected_ids:
            _LOGGER.debug("Removing deselected sensor: %s", entity.entity_id)
            registry.async_remove(entity.entity_id)

    # 2) Now set up coordinator and add new sensors
    coordinator = EHealthCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for comp in coordinator.data:
        cid = comp.get("id")
        name = comp.get("name_nl")
        status = comp.get("status_name")
        if cid in selected_ids and name and status:
            sensors.append(EHealthSensor(coordinator, cid, name))

    if not sensors:
        _LOGGER.warning("No selected eHealth services found to create sensors.")
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
                resp = await session.get(API_URL, timeout=10)
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
