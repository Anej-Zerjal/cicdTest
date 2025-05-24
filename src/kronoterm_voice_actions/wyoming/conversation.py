import logging

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.util import ulid as ulid_util

from .matcher import execute_command

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Wyoming conversation integration."""
    _LOGGER.info("🔥 Setting up Wyoming Custom Conversation Agent Entity 🔥")

    async_add_entities(
        [
            WyomingConversationEntity(config_entry, hass),
        ]
    )


class WyomingConversationEntity(
    conversation.ConversationEntity, conversation.AbstractConversationAgent
):
    """Wyoming conversation agent - Represents the custom Kronoterm agent."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        hass: HomeAssistant,
        #
    ) -> None:
        """Initialize the custom conversation agent."""
        super().__init__()
        self.entry = config_entry
        self.hass = hass

        self._attr_name = config_entry.title

        self._attr_supported_features = conversation.ConversationEntityFeature.CONTROL

        self._supported_languages = ["sl"]

        self._attr_unique_id = f"{config_entry.entry_id}-conversation"

        _LOGGER.debug(
            "Initialized custom conversation agent: %s (ID: %s)",
            self._attr_name,
            self._attr_unique_id,
        )

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""

        return self._supported_languages

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process user input using the custom matcher."""
        conversation_id = user_input.conversation_id or ulid_util.ulid_now()
        intent_response = intent.IntentResponse(language=user_input.language)

        username = self.entry.data.get(CONF_USERNAME)
        password = self.entry.data.get(CONF_PASSWORD)

        if username is None or password is None:
            _LOGGER.error("Credentials not found for custom conversation agent.")
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Agent configuration error: Missing credentials.",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )

        try:
            response = await execute_command(user_input.text, username, password, self.hass)
        except Exception as e:
            _LOGGER.exception("Error during command execution")
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN, f"Error: {e}"
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )

        intent_response.async_set_speech(response)
        # if matched_response is not None:
        #     _LOGGER.debug(
        #         "Custom matcher matched '%s' -> '%s'", user_input.text, matched_response
        #     )
        #     intent_response.async_set_speech(matched_response)
        # else:
        #
        #     _LOGGER.debug("Custom matcher did not match: '%s'", user_input.text)
        #
        #     intent_response.async_set_speech("Oprostite, tega ukaza ne razumem.")

        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )
