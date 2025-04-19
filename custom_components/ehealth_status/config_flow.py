from homeassistant import config_entries
from .const import DOMAIN, API_URL
import aiohttp
import json
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status",
                data={"selected_services": user_input["services"]}
            )

        # Fetch available services from API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as response:
                    text = await response.text()
                    raw_data = json.loads(text)
                    components = raw_data["data"] if isinstance(raw_data, dict) and "data" in raw_data else raw_data
                    service_names = sorted(
                        {comp.get("group_name_nl") for comp in components if "group_name_nl" in comp}
                    )
        except Exception as e:
            _LOGGER.error("Failed to fetch eHealth services: %s", e)
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("services"): vol.All(
                    vol.In(service_names),
                    lambda val: [val] if isinstance(val, str) else val
                )
            }),
            errors={}
        )
