from homeassistant.components.sensor import SensorEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([EHealthTestSensor()], True)

class EHealthTestSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "eHealth Test"
        self._attr_unique_id = "ehealth_test_sensor"

    @property
    def state(self):
        return "ok"
