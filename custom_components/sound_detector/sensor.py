from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, JSON_URL

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    async_add_entities([SoundDetectorSensor(hass)])


class SoundDetectorSensor(SensorEntity):

    _attr_name = "Sound Detector"
    _attr_unique_id = "sound_detector"

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._state = "waiting"
        self._confidence = 0.0

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "confidence": self._confidence
        }

    async def async_update(self):

        session = async_get_clientsession(self.hass)

        try:

            async with session.get(JSON_URL) as response:

                if response.status != 200:
                    _LOGGER.warning("No se pudo leer el JSON")
                    return

                text = await response.text()

                _LOGGER.warning("Contenido recibido: %s", text)

                import json
                data = json.loads(text)

                self._state = data.get("sound", "waiting")
                self._confidence = data.get("confidence", 0.0)

        except Exception as err:
            _LOGGER.error("Error leyendo JSON: %s", err)

