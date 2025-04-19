import logging
import json
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, API_URL_NL, API_URL_FR

_LOGGER = logging.getLogger(__name__)


async def _fetch_services(api_url: str) -> list[str]:
    """Fetch and return all name_nl values from the given API."""
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(api_url, timeout=10)
            text = await resp.text()
            raw = json.loads(text)
            data = raw.get("data", raw) if isinstance(raw, dict) else raw
            return sorted({c["name_nl"] for c in data if "name_nl" in c})
    except Exception as e:
        _LOGGER.error("Error fetching services from %s: %s", api_url, e)
        return []


class EHealthConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial config flow with language + service selection."""

    VERSION = 1

    def __init__(self):
        self._language = None

    async def async_step_user(self, user_input=None):
        """First step: ask for preferred language."""
        if user_input is not None:
            self._language = user_input["language"]
            return await self.async_step_services()

        schema = vol.Schema({
            vol.Required("language"): vol.In({
                "Nederlands": "Nederlands",
                "Français": "Français"
            })
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )

    async def async_step_services(self, user_input=None):
        """Second step: ask which services to monitor."""
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

        schema = vol.Schema({
            vol.Required("services", default=[]): cv.multi_select(services)
        })

        return self.async_show_form(
            step_id="services",
            data_schema=schema
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options flow: same two‑step but pre‑filled."""
        return EHealthOptionsFlow(config_entry)


class EHealthOptionsFlow(config_entries.OptionsFlow):
    """Allow users to change language and services later."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Show language selector first in options."""
        if user_input is not None and "language" in user_input:
            # user changed language
            self.entry.options = {"language": user_input["language"]}
            return await self.async_step_services()

        schema = vol.Schema({
            vol.Required("language", default=self.entry.options.get("language", self.entry.data["language"])): vol.In({
                "Nederlands": "Nederlands",
                "Français": "Français"
            })
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema
        )

    async def async_step_services(self, user_input=None):
        """Then show service multi‑select (with updated language)."""
        language = self.entry.options.get("language", self.entry.data["language"])
        api_url = API_URL_NL if language == "Nederlands" else API_URL_FR
        services = await _fetch_services(api_url)
        if not services:
            return self.async_abort(reason="cannot_connect")

        default = self.entry.options.get("services", self.entry.data["services"])
        if user_input is not None:
            return self.async_create_entry(
                title="eHealth Status Options",
                data={"language": language, "services": user_input["services"]}
            )

        schema = vol.Schema({
            vol.Required("services", default=default): cv.multi_select(services)
        })

        return self.async_show_form(
            step_id="services",
            data_schema=schema
        )
