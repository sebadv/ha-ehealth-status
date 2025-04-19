import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)


async def _fetch_services():
    """Return a sorted list of all available name_nl service groups."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=10) as resp:
                text = await resp.text()
                raw = json.loads(text)
                data = raw.get("data", raw) if isinstance(raw, dict) else raw
                return sorted({c.get("name_nl") for c in data if c.get("name_nl")})
    except Exception as e:
        _LOGGER.error("Error fetching eHealth services: %s", e)
        return []


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for eHealth Status."""

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
            vol.Required("services", default=[]): vol.All(
                cv.ensure_list,
                [vol.In(services)],
            )
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors={},
        )

    async def async_get_options_flow(self, entry):
        return EHealthOptionsFlow(entry)


class EHealthOptionsFlow(config_entries.OptionsFlow):
    """Allow users to change their service selection later."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        services = await _fetch_services()
        current = self.entry.options.get("services", self.entry.data.get("services", []))

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status Options",
                data={"services": user_input["services"]},
            )

        schema = vol.Schema({
            vol.Required("services", default=current): vol.All(
                cv.ensure_list,
                [vol.In(services)],
            )
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
