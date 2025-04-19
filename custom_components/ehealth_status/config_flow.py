import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, API_URL_NL, API_URL_FR

_LOGGER = logging.getLogger(__name__)


async def _fetch_services(api_url: str) -> list[str]:
    """Fetch and return all name_nl values from the given API URL."""
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
    """Handle initial config: select language, then services."""

    VERSION = 1

    def __init__(self):
        self._language = None

    async def async_step_user(self, user_input=None):
        """Step 1: Choose language."""
        if user_input is not None:
            self._language = user_input["language"]
            return await self.async_step_services()

        schema = vol.Schema({
            vol.Required("language"): vol.In(["Nederlands", "Français"])
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_services(self, user_input=None):
        """Step 2: Multi‑select services."""
        api_url = API_URL_NL if self._language == "Nederlands" else API_URL_FR
        services = await _fetch_services(api_url)
        if not services:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status",
                data={
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
    @callback
    def async_get_options_flow(config_entry):
        """Hook to the options flow."""
        return EHealthOptionsFlow(config_entry)


class EHealthOptionsFlow(config_entries.OptionsFlow):
    """Allow users to reconfigure language and services."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._language = config_entry.data["language"]

    async def async_step_init(self, user_input=None):
        """Step 1 (options): Choose language."""
        if user_input is not None and "language" in user_input:
            self._language = user_input["language"]
            return await self.async_step_services()

        schema = vol.Schema({
            vol.Required(
                "language",
                default=self.config_entry.data["language"]
            ): vol.In(["Nederlands", "Français"])
        })
        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_services(self, user_input=None):
        """Step 2 (options): Multi‑select services."""
        api_url = API_URL_NL if self._language == "Nederlands" else API_URL_FR
        services = await _fetch_services(api_url)
        if not services:
            return self.async_abort(reason="cannot_connect")

        current = self.config_entry.data.get("services", [])
        if user_input is not None and "services" in user_input:
            # Only pass 'data'; Home Assistant will stash it in entry.options
            return self.async_create_entry(
                title="eHealth Status Options",
                data={
                    "language": self._language,
                    "services": user_input["services"],
                },
            )

        return self.async_show_form(
            step_id="services",
            data_schema=vol.Schema({
                vol.Required("services", default=current): cv.multi_select(services)
            }),
        )
