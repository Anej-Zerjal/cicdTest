# src/kronoterm_voice_actions/test/test_config_flow.py

import pytest
from unittest.mock import patch, AsyncMock
from ipaddress import ip_address

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from kronoterm_voice_actions.wyoming.const import DOMAIN
from kronoterm_voice_actions.wyoming.config_flow import (
    CONF_TYPE,
    ENTRY_TYPE_CUSTOM,
    ENTRY_TYPE_REMOTE,
    CUSTOM_AGENT_UNIQUE_ID,
)

pytestmark = pytest.mark.asyncio

# Path for mocking component setup - This might not be needed if HA's test setup handles it
# or if the dependency errors were due to other issues now resolved.
# However, for config flow tests, it's often safer to ensure dependencies don't block flow logic.
MOCK_SETUP_COMPONENT = "homeassistant.setup.async_setup_component"


@patch(MOCK_SETUP_COMPONENT, return_value=True)
async def test_flow_user_chooses_custom_agent(mock_setup, hass: HomeAssistant):
    """Test user step choosing custom agent type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_CUSTOM]}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Kronoterm Conversation Agent"
    assert result["data"] == {CONF_TYPE: ENTRY_TYPE_CUSTOM}

@patch(MOCK_SETUP_COMPONENT, return_value=True)
async def test_flow_user_chooses_remote_service(mock_setup, hass: HomeAssistant):
    """Test user step choosing remote service type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_REMOTE]}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"


@patch(MOCK_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_success(mock_wyoming_service_create, mock_setup, hass: HomeAssistant):
    """Test remote service step with successful connection."""
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = True
    mock_service_instance.get_name.return_value = "Mocked Wyoming STT"
    mock_wyoming_service_create.return_value = mock_service_instance

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_REMOTE]}
    )
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

@patch(MOCK_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_cannot_connect(mock_wyoming_service_create, mock_setup, hass: HomeAssistant):
    """Test remote service step with connection failure."""
    mock_wyoming_service_create.return_value = None 

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_REMOTE]}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"
    assert result["errors"] == {"base": "cannot_connect"}

@patch(MOCK_SETUP_COMPONENT, return_value=True)
@patch("kronoterm_voice_actions.wyoming.config_flow.WyomingService.create")
async def test_flow_remote_service_no_services(mock_wyoming_service_create, mock_setup, hass: HomeAssistant):
    """Test remote service step when service has no usable features."""
    mock_service_instance = AsyncMock()
    mock_service_instance.has_services.return_value = False 
    mock_service_instance.get_name.return_value = "Empty Service"
    mock_wyoming_service_create.return_value = mock_service_instance

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_REMOTE]}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "test.host", CONF_PORT: 1234}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "remote_service"
    assert result["errors"] == {"base": "no_services"}

@patch(MOCK_SETUP_COMPONENT, return_value=True)
async def test_flow_custom_agent_already_configured(mock_setup, hass: HomeAssistant):
    """Test custom agent aborts if already configured."""
    # FIX 2: Provide missing keyword arguments for ConfigEntry
    entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Kronoterm Conversation Agent",
        data={CONF_TYPE: ENTRY_TYPE_CUSTOM},
        source="user",
        unique_id=CUSTOM_AGENT_UNIQUE_ID,
        minor_version=1,  # Added
        options={},       # Added
        discovery_keys=(),# Added
        subentries_data={},# Added
    )
    entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # FIX 1: Provide CONF_TYPE as a list
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TYPE: [ENTRY_TYPE_CUSTOM]}
    )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@patch(MOCK_SETUP_COMPONENT, return_value=True)
# FIX 3: Patch _validate_remote_connection directly to avoid socket error
@patch("kronoterm_voice_actions.wyoming.config_flow._validate_remote_connection", new_callable=AsyncMock)
async def test_flow_zeroconf_success(mock_validate_connection, mock_setup, hass: HomeAssistant):
    """Test zeroconf discovery flow for a remote service."""
    # Configure the mock for _validate_remote_connection
    mock_validate_connection.return_value = (None, "Discovered Wyoming Mic") # (error_reason, service_name)

    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("1.2.3.4"),
        ip_addresses=[ip_address("1.2.3.4")], 
        hostname="discovered-mic.local.",
        name="Wyoming Mic", 
        port=10300,
        properties={},
        type="_wyoming._tcp.local.",
    )
    # The config_flow's async_step_zeroconf uses discovery_info.host, 
    # ZeroconfServiceInfo makes `host` property available from ip_address/hostname
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=discovery_info
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"
    
    # Check if _validate_remote_connection was called (it's called by async_step_zeroconf)
    # The host passed to _validate_remote_connection will be discovery_info.host
    mock_validate_connection.assert_called_once_with(hass, "1.2.3.4", 10300)


    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Discovered Wyoming Mic" # This comes from mock_validate_connection
    assert result["data"] == {
        CONF_HOST: "1.2.3.4", 
        CONF_PORT: 10300,
        CONF_TYPE: ENTRY_TYPE_REMOTE,
    }