from homeassistant import config_entries
from .const import DOMAIN

class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="eHealth Status", data={})
