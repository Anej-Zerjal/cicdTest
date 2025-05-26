# src/kronoterm_voice_actions/test/test_config_flow.py

import pytest
from unittest.mock import patch, AsyncMock
from ipaddress import ip_address

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
# For MockConfigEntry:
from pytest_homeassistant_custom_component.common import MockConfigEntry

from kronoterm_voice_actions.wyoming.const import DOMAIN
from kronoterm_voice_actions.wyoming.config_flow import (
    CONF_TYPE,
    ENTRY_TYPE_CUSTOM,
    ENTRY_TYPE_REMOTE,
    CUSTOM_AGENT_UNIQUE_ID,
)

pytestmark = pytest.mark.asyncio

# This broad mock for component setup can sometimes cause issues if it interferes
# with how the flow manager expects integrations to be loaded.
# We'll keep it for now to try and bypass deeper dependency issues,
# but if schema errors persist, this might need to be more targeted.
MOCK_HA_SETUP_COMPONENT = "homeassistant.setup.async_setup_component"

# It's often better to mock the specific integration that's failing, if known.
# e.g. @patch("homeassistant.components.ffmpeg.async_setup", return_value=True)
# @patch("homeassistant.components.conversation.async_setup", return_value=True)


@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
async def test_flow_user_chooses_custom_agent(mock_setup_component, hass: HomeAssistant):
    """Test user step choosing custom agent type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Reverted CONF_TYPE to single string based on "extra keys not allowed" error.
    # If this still fails, the issue is likely the wrong config flow's schema being used.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_CUSTOM}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Kronoterm Conversation Agent"
    assert result["data"] == {CONF_TYPE: ENTRY_TYPE_CUSTOM}

@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
async def test_flow_user_chooses_remote_service(mock_setup_component, hass: HomeAssistant):
    """Test user step choosing remote service type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # ... (rest of the test as before, with CONF_TYPE as single string)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"


@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create") # Path to *your* component's service
async def test_flow_remote_service_success(mock_wyoming_service_create, mock_setup_component, hass: HomeAssistant):
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = True
    mock_service_instance.get_name.return_value = "Mocked Wyoming STT"
    mock_wyoming_service_create.return_value = mock_service_instance

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE} # single string
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    # ... (rest of assertions)
    assert result["title"] == "Mocked Wyoming STT"
    assert result["data"] == {
        CONF_HOST: "test.host",
        CONF_PORT: 1234,
        CONF_TYPE: ENTRY_TYPE_REMOTE,
    }
    mock_wyoming_service_create.assert_called_once_with("test.host", 1234)


@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_cannot_connect(mock_wyoming_service_create, mock_setup_component, hass: HomeAssistant):
    mock_wyoming_service_create.return_value = None 
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE} # single string
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    # ... (rest of assertions)
    assert result["errors"] == {"base": "cannot_connect"}


@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_no_services(mock_wyoming_service_create, mock_setup_component, hass: HomeAssistant):
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = False 
    mock_service_instance.get_name.return_value = "Empty Service"
    mock_wyoming_service_create.return_value = mock_service_instance
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE} # single string
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    # ... (rest of assertions)
    assert result["errors"] == {"base": "no_services"}


@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
async def test_flow_custom_agent_already_configured(mock_setup_component, hass: HomeAssistant):
    """Test custom agent aborts if already configured."""
    # FIX 2: Use MockConfigEntry and provide necessary defaults if any
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=CUSTOM_AGENT_UNIQUE_ID,
        data={CONF_TYPE: ENTRY_TYPE_CUSTOM},
        version=1,
        title="Kronoterm Conversation Agent" # Title is good to have
        # Add other fields like minor_version, options if MockConfigEntry requires them
    )
    entry.add_to_hass(hass) # MockConfigEntry should have this method
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_CUSTOM} # single string
    )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"


# Patching the function within your custom component's config_flow that makes the network call
@patch(MOCK_HA_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow._validate_remote_connection", new_callable=AsyncMock)
async def test_flow_zeroconf_success(mock_validate_connection, mock_setup_component, hass: HomeAssistant):
    """Test zeroconf discovery flow for a remote service."""
    mock_validate_connection.return_value = (None, "Discovered Wyoming Mic")

    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("1.2.3.4"),
        ip_addresses=[ip_address("1.2.3.4")], 
        hostname="discovered-mic.local.",
        name="Wyoming Mic", 
        port=10300,
        properties={},
        type="_wyoming._tcp.local.",
    )
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=discovery_info
    )
    # This now assumes _validate_remote_connection is called from your custom flow's async_step_zeroconf
    # If the core flow is still being hit, this mock won't apply to it.
    mock_validate_connection.assert_called_once_with(hass, "1.2.3.4", 10300)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"
    
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Discovered Wyoming Mic"
    assert result["data"] == {
        CONF_HOST: "1.2.3.4", 
        CONF_PORT: 10300,
        CONF_TYPE: ENTRY_TYPE_REMOTE,
    }