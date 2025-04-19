from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "ehealth_status"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up integration (no-op)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Forward config entry to sensor platform."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
