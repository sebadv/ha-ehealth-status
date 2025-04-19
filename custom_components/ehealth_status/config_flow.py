import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)


async def fetch_service_names():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=10) as response:
                text = await response.text()
                raw_data = json.loads(text)
                components = raw_data["data"] if isinstance(raw_data, dict) and "data" in raw_data else raw_data
                return sorted({c.get("group_name_nl") for c in components if "group_name_nl" in c})
    except Exception as e:
        _LOGGER.error("Failed to fetch service names: %s", e)
        return []


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        services = await fetch_service_names()

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status",
                data={"selected_services": user_input["services"]}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("services"): vol.All(
                    vol.EnsureList,
                    [vol.In(services)]
                )
            }),
            errors={}
        )

    async def async_step_options(self, user_input=None):
        services = await fetch_service_names()
        current_services = self.options.get("selected_services", [])

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Options",
                data={"selected_services": user_input["services"]}
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Required("services", default=current_services): vol.All(
                    vol.EnsureList,
                    [vol.In(services)]
                )
            }),
            errors={}
        )
