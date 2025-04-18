import logging
import json
from datetime import timedelta
import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.debug("Setting up eHealth sensors")

    initial_data = hass.data[DOMAIN].get("initial_data", [])
    coordinator = EHealthCoordinator(hass)
    coordinator.data = initial_data
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for component in coordinator.data:
        if not isinstance(component, dict):
            continue
        name = component.get("group_name_nl")
        status = component.get("status_name")
        if name and status:
            sensors.append(EHealthSensor(coordinator, name))

    async_add_entities(sensors, True)
    _LOGGER.debug("Added %d sensors", len(sensors))

class EHealthCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="eHealth Status Coordinator",
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"API error: {response.status}")
                    text = await response.text()
                    data = json.loads(text)
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

class EHealthSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = f"eHealth {name}"
        self._attr_unique_id = f"ehealth_{name.lower().replace(' ', '_')}"
        self._name_in_api = name

    @property
    def state(self):
        for component in self.coordinator.data:
            if not isinstance(component, dict):
                continue
            if component.get("group_name_nl") == self._name_in_api:
                return component.get("status_name")
        return "Unknown"
