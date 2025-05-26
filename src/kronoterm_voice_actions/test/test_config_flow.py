# src/kronoterm_voice_actions/test/test_config_flow.py

import pytest
from unittest.mock import patch, AsyncMock

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.service_info.hassio import HassioServiceInfo
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

# Adjust the import path to your constants and config_flow
from kronoterm_voice_actions.wyoming.const import DOMAIN
from kronoterm_voice_actions.wyoming.config_flow import (
    CONF_TYPE,
    ENTRY_TYPE_CUSTOM,
    ENTRY_TYPE_REMOTE,
    CUSTOM_AGENT_UNIQUE_ID,
    WyomingConfigFlow, # Assuming this is how you import it or import the module
)

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.asyncio

async def test_flow_user_chooses_custom_agent(hass: HomeAssistant):
    """Test user step choosing custom agent type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_CUSTOM}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Kronoterm Conversation Agent"
    assert result["data"] == {CONF_TYPE: ENTRY_TYPE_CUSTOM}

async def test_flow_user_chooses_remote_service(hass: HomeAssistant):
    """Test user step choosing remote service type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"


@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_success(mock_wyoming_service_create, hass: HomeAssistant):
    """Test remote service step with successful connection."""
    # Configure the mock for WyomingService.create
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = True
    mock_service_instance.get_name.return_value = "Mocked Wyoming STT"
    mock_wyoming_service_create.return_value = mock_service_instance

    # Start with the user step, choose remote
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE}
    )

    # Now configure the remote service step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Mocked Wyoming STT"
    assert result["data"] == {
        CONF_HOST: "test.host",
        CONF_PORT: 1234,
        CONF_TYPE: ENTRY_TYPE_REMOTE,
    }
    mock_wyoming_service_create.assert_called_once_with("test.host", 1234)

@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_cannot_connect(mock_wyoming_service_create, hass: HomeAssistant):
    """Test remote service step with connection failure."""
    mock_wyoming_service_create.return_value = None # Simulate cannot connect

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"
    assert result["errors"] == {"base": "cannot_connect"}

@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_no_services(mock_wyoming_service_create, hass: HomeAssistant):
    """Test remote service step when service has no usable features."""
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = False # No services
    mock_service_instance.get_name.return_value = "Empty Service"
    mock_wyoming_service_create.return_value = mock_service_instance

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_REMOTE}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"
    assert result["errors"] == {"base": "no_services"}

async def test_flow_custom_agent_already_configured(hass: HomeAssistant,ਗਾconfig_entry):
    """Test custom agent aborts if already configured."""
    # Pre-configure an entry for the custom agent
    # This uses a hypothetical fixture 'config_entry' which you'd set up
    # to create an entry with unique_id CUSTOM_AGENT_UNIQUE_ID.
    # For simplicity, let's assume one exists for this test concept.
    # You might need to use `MockConfigEntry` from `tests.common`
    
    # Example using a mock entry:
    entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Kronoterm Conversation Agent",
        data={CONF_TYPE: ENTRY_TYPE_CUSTOM},
        source="user",
        unique_id=CUSTOM_AGENT_UNIQUE_ID,
    )
    entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: ENTRY_TYPE_CUSTOM}
    )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_zeroconf_success(mock_wyoming_service_create, hass: HomeAssistant):
    """Test zeroconf discovery flow for a remote service."""
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = True
    mock_service_instance.get_name.return_value = "Discovered Wyoming Mic"
    mock_wyoming_service_create.return_value = mock_service_instance

    discovery_info = ZeroconfServiceInfo(
        host="1.2.3.4",
        hostname="discovered-mic.local.",
        name="Wyoming Mic._wyoming._tcp.local.",
        port=10300,
        properties={},
        type="_wyoming._tcp.local.",
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=discovery_info
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"

    # Simulate user confirmation
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Discovered Wyoming Mic"
    assert result["data"] == {
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 10300,
        CONF_TYPE: ENTRY_TYPE_REMOTE,
    }
    mock_wyoming_service_create.assert_called_once_with("1.2.3.4", 10300)