import logging
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status",
                data={"selected_services": ["Test Service"]}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=None,
            description_placeholders={},
        )
