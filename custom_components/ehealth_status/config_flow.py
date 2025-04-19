from homeassistant import config_entries
from .const import DOMAIN, API_URL
import aiohttp
import json
import logging

_LOGGER = logging.getLogger(__name__)

class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="eHealth Status", data={"selected_services": user_input["services"]})

        # Fetch available services
        options = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as response:
                    text = await response.text()
                    raw_data = json.loads(text)
                    components = raw_data["data"] if isinstance(raw_data, dict) and "data" in raw_data else raw_data
                    options = sorted({comp["group_name_nl"] for comp in components if "group_name_nl" in comp})
        except Exception as e:
            _LOGGER.error("Failed to fetch services: %s", e)
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="user",
            data_schema=config_entries.FLOW_DATA_SCHEMA({
                "services": config_entries.selector({
                    "select": {
                        "multiple": True,
                        "options": options,
                        "translation_key": "services"
                    }
                })
            })
        )
