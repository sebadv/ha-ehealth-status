import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, API_URL_NL, API_URL_FR

_LOGGER = logging.getLogger(__name__)


async def _fetch_services(api_url: str) -> list[str]:
    """Fetch all name_nl values from the given API URL."""
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(api_url, timeout=10)
            raw = json.loads(await resp.text())
            data = raw.get("data", raw) if isinstance(raw, dict) else raw
            return sorted({c["name_nl"] for c in data if "name_nl" in c})
    except Exception as e:
        _LOGGER.error("Error fetching services from %s: %s", api_url, e)
        return []


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial config: language → services."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: select language."""
        if user_input is not None:
            self._language = user_input["language"]
            return await self.async_step_services()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("language"): vol.In(["Nederlands", "Français"])
            }),
        )

    async def async_step_services(self, user_input=None):
        """Step 2: multi‑select services."""
        api_url = API_URL_NL if self._language == "Nederlands" else API_URL_FR
        services = await _fetch_services(api_url)
        if not services:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            # Store EVERYTHING in options
            return self.async_create_entry(
                title="eHealth Status",
                data={},  # no static data
                options={
                    "language": self._language,
                    "services": user_input["services"],
                },
            )

        return self.async_show_form(
            step_id="services",
            data_schema=vol.Schema({
                vol.Required("services", default=[]): cv.multi_select(services)
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the external options flow handler."""
        return EHealthOptionsFlow(config_entry)


class EHealthOptionsFlow(config_entries.OptionsFlow):
    """Handle options: re‑select language and services."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Step 1: choose language."""
        current = self.config_entry.options.get("language")
        if user_input is not None and "language" in user_input:
            self._language = user_input["language"]
            return await self.async_step_services()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("language", default=current): vol.In(["Nederlands", "Français"])
            }),
        )

    async def async_step_services(self, user_input=None):
        """Step 2: multi‑select services."""
        language = user_input.get("language", self.config_entry.options["language"])
        api_url = API_URL_NL if language == "Nederlands" else API_URL_FR
        services = await _fetch_services(api_url)
        if not services:
            return self.async_abort(reason="cannot_connect")

        current_services = self.config_entry.options.get("services", [])
        if user_input is not None and "services" in user_input:
            # Update options only
            return self.async_create_entry(
                title="eHealth Status Options",
                data=None,
                options={
                    "language": language,
                    "services": user_input["services"],
                },
            )

        return self.async_show_form(
            step_id="services",
            data_schema=vol.Schema({
                vol.Required("services", default=current_services): cv.multi_select(services)
            }),
        )
