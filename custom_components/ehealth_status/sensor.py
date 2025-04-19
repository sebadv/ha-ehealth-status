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
from .const import API_URL_NL, API_URL_FR

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for selected services & language."""
    language = entry.options["language"]
    api_url = API_URL_NL if language == "Nederlands" else API_URL_FR
    selected = set(entry.options.get("services", []))

    # Fetch full component list once:
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(api_url, timeout=10)
            raw = json.loads(await resp.text())
            all_data = raw.get("data", raw) if isinstance(raw, dict) else raw
    except Exception as e:
        _LOGGER.error("Error fetching components list: %s", e)
        all_data = []

    # Map name_nl → id
    name_to_id = {c["name_nl"]: c["id"] for c in all_data if "name_nl" in c and "id" in c}
    selected_ids = {name_to_id[n] for n in selected if n in name_to_id}

    coordinator = EHealthCoordinator(hass, api_url)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for comp in coordinator.data:
        cid = comp.get("id")
        name = comp.get("name_nl")
        status = comp.get("status_name")
        if cid in selected_ids and name and status:
            sensors.append(EHealthSensor(coordinator, cid, name))

    async_add_entities(sensors, True)


class EHealthCoordinator(DataUpdateCoordinator):
    """Coordinator fetching data periodically."""

    def __init__(self, hass, api_url):
        super().__init__(hass, _LOGGER, name="eHealth Status Coordinator", update_interval=SCAN_INTERVAL)
        self.api_url = api_url

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self.api_url, timeout=10)
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                raw = json.loads(await resp.text())
                return raw.get("data", raw) if isinstance(raw, dict) else raw
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err


class EHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for one eHealth component."""

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
