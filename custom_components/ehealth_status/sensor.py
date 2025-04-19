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
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up eHealth sensors from a config entry."""
    coordinator = EHealthCoordinator(hass)
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for comp in coordinator.data:
        # comp should be a dict with keys 'id', 'group_name_nl', 'status_name'
        cid = comp.get("id")
        name = comp.get("group_name_nl")
        status = comp.get("status_name")
        if cid is None or name is None or status is None:
            continue
        sensors.append(EHealthSensor(coordinator, cid, name))

    if not sensors:
        _LOGGER.warning("No eHealth components found to create sensors for.")
    async_add_entities(sensors, True)


class EHealthCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch eHealth component statuses."""

    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="eHealth Status Coordinator",
            update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self):
        """Fetch data from the eHealth status API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API returned HTTP {resp.status}")
                    text = await resp.text()
                    raw = json.loads(text)
                    # API returns either a list or {"data": [...]}
                    return raw.get("data", raw) if isinstance(raw, dict) else raw
        except Exception as err:
            raise UpdateFailed(f"Error fetching eHealth data: {err}") from err


class EHealthSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single eHealth component."""

    def __init__(self, coordinator, component_id, group_name):
        super().__init__(coordinator)
        self._component_id = component_id
        # Friendly name: group_name_nl
        self._attr_name = group_name
        # Unique ID: use the numeric id
        self._attr_unique_id = f"ehealth_{component_id}"

    @property
    def state(self):
        """Return the current status_name for this component."""
        for comp in self.coordinator.data:
            if isinstance(comp, dict) and comp.get("id") == self._component_id:
                return comp.get("status_name")
        return "unknown"
