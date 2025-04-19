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
from .const import API_URL_NL, API_URL_FR

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors only for selected services, using correct language API."""
    language = entry.data["language"]
    api_url = API_URL_NL if language == "Nederlands" else API_URL_FR
    selected = entry.options.get("services") or entry.data.get("services", [])

    # Fetch full list once for mapping name->id
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(api_url, timeout=10)
            text = await resp.text()
            raw = json.loads(text)
            all_data = raw.get("data", raw) if isinstance(raw, dict) else raw
    except Exception as e:
        _LOGGER.error("Error fetching full component list: %s", e)
        all_data = []

    name_to_id = {c["name_nl"]: c["id"] for c in all_data if "name_nl" in c and "id" in c}
    selected_ids = {name_to_id[n] for n in selected if n in name_to_id}

    # Remove old, add new
    coordinator = EHealthCoordinator(hass, api_url)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for comp in coordinator.data:
        cid = comp.get("id")
        name = comp.get("name_nl")
        status = comp.get("status_name")
        if cid in selected_ids and name and status:
            sensors.append(EHealthSensor(coordinator, cid, name))

    if not sensors:
        _LOGGER.warning("No eHealth services selected.")
    async_add_entities(sensors, True)


class EHealthCoordinator(DataUpdateCoordinator):
    """Fetch component status every minute from a given API URL."""

    def __init__(self, hass, api_url):
        super().__init__(
            hass, _LOGGER,
            name="eHealth Status Coordinator",
            update_interval=SCAN_INTERVAL
        )
        self.api_url = api_url

    async def _async_update_data(self):
        """Fetch data from the eHealth status API."""
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self.api_url, timeout=10)
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                text = await resp.text()
                raw = json.loads(text)
                return raw.get("data", raw) if isinstance(raw, dict) else raw
        except Exception as err:
            raise UpdateFailed(f"Error fetching eHealth data: {err}") from err


class EHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single eHealth service."""

    def __init__(self, coordinator, component_id, name):
        super().__init__(coordinator)
        self._component_id = component_id
        self._attr_name = name
        self._attr_unique_id = f"ehealth_{component_id}"

    @property
    def state(self):
        """Return the current status_name for this component."""
        for comp in self.coordinator.data:
            if comp.get("id") == self._component_id:
                return comp.get("status_name")
        return "unknown"
