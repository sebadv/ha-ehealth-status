import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)


async def _fetch_services():
    """Fetch and return all Belgian eHealth service names (name_nl)."""
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL, timeout=10)
            text = await resp.text()
            raw = json.loads(text)
            data = raw.get("data", raw) if isinstance(raw, dict) else raw
            return sorted({c["name_nl"] for c in data if "name_nl" in c})
    except Exception as e:
        _LOGGER.error("Error fetching eHealth services: %s", e)
        return []


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Initial config flow for selecting services."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        services = await _fetch_services()
        if not services:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status",
                data={"services": user_input["services"]},
            )

        schema = vol.Schema({
            vol.Required("services", default=[]): cv.multi_select(services)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for modifying selected services."""
        return EHealthOptionsFlow(config_entry)


class EHealthOptionsFlow(config_entries.OptionsFlow):
    """Options flow to update service selection after install."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        services = await _fetch_services()
        current = self.config_entry.options.get("services", self.config_entry.data.get("services", []))

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status Options",
                data={"services": user_input["services"]},
            )

        schema = vol.Schema({
            vol.Required("services", default=current): cv.multi_select(services)
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
