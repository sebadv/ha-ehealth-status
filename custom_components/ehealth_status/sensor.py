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
    """Set up sensors for the selected language & services."""
    # 1) Read language & services (fallback to entry.data if options absent)
    language = entry.options.get("language", entry.data.get("language"))
    services = entry.options.get("services", entry.data.get("services", []))

    # 2) Pick the correct API URL
    api_url = API_URL_NL if language == "Nederlands" else API_URL_FR

    # 3) Fetch full component list once to map name_nl → id
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(api_url, timeout=10)
            raw = json.loads(await resp.text())
            all_data = raw.get("data", raw) if isinstance(raw, dict) else raw
    except Exception as e:
        _LOGGER.error("Error fetching component list: %s", e)
        all_data = []

    name_to_id = {
        comp["name_nl"]: comp["id"]
        for comp in all_data
        if "name_nl" in comp and "id" in comp
    }
    selected_ids = {name_to_id[n] for n in services if n in name_to_id}

    # 4) Create & prime the coordinator
    coordinator = EHealthCoordinator(hass, api_url)
    await coordinator.async_config_entry_first_refresh()

    # 5) Build sensor entities
    sensors = []
    for comp in coordinator.data:
        cid    = comp.get("id")
        name   = comp.get("name_nl")
        status = comp.get("status_name")
        if cid in selected_ids and name and status:
            sensors.append(EHealthSensor(coordinator, comp))

    if not sensors:
        _LOGGER.warning("No eHealth services selected; no sensors added.")
    async_add_entities(sensors, True)


class EHealthCoordinator(DataUpdateCoordinator):
    """Coordinator fetching eHealth data every minute from a given API URL."""

    def __init__(self, hass, api_url: str):
        super().__init__(
            hass,
            _LOGGER,
            name="eHealth Status Coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.api_url = api_url

    async def _async_update_data(self):
        """Fetch data from the eHealth status API."""
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self.api_url, timeout=10)
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                raw = json.loads(await resp.text())
                return raw.get("data", raw) if isinstance(raw, dict) else raw
        except Exception as err:
            raise UpdateFailed(f"Error fetching eHealth data: {err}") from err


class EHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single eHealth service component, with extra attributes."""

    def __init__(self, coordinator: EHealthCoordinator, component: dict):
        super().__init__(coordinator)
        self._component_id = component.get("id")
        self._attr_name = component.get("name_nl")
        self._attr_unique_id = f"ehealth_{self._component_id}"
        # Cache the static fields for attributes
        self._attrs = {
            "last_updated": component.get("last_updated"),
            "group_name_nl": component.get("group_name_nl"),
            "group_name_fr": component.get("group_name_fr"),
            "status_code": component.get("status_code"),
        }

    @property
    def state(self) -> str:
        """Return the current status_name for this component."""
        for comp in self.coordinator.data:
            if comp.get("id") == self._component_id:
                return comp.get("status_name")
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the extra attributes for this component."""
        return self._attrs
