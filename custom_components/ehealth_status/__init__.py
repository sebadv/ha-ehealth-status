import logging
import aiohttp
import json

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Starting async_setup_entry")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=10) as response:
                if response.status != 200:
                    raise ConfigEntryNotReady(f"API status: {response.status}")
                text = await response.text()
                raw_data = json.loads(text)
                # extract list of components
                data = raw_data["data"] if isinstance(raw_data, dict) and "data" in raw_data else raw_data
    except Exception as e:
        raise ConfigEntryNotReady(f"Cannot connect to eHealth API: {e}")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["initial_data"] = data
    hass.data[DOMAIN]["entry"] = entry
    
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
