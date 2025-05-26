# src/kronoterm_voice_actions/test/test_mqtt_client.py

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Adjust the import path based on your project structure
from kronoterm_voice_actions.wyoming.mqtt_client import MqttClient
from kronoterm_voice_actions.wyoming.kronoterm_models import RegisterAddress
from kronoterm_voice_actions.wyoming.const import MODBUS_SLAVE_ID

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.asyncio

@patch('kronoterm_voice_actions.wyoming.mqtt_client.pymodbus.client.ModbusSerialClient')
async def test_read_temperature(MockModbusClient):
    """Tests reading a temperature value."""
    mock_instance = MockModbusClient.return_value
    mock_instance.connect = MagicMock()
    mock_instance.close = MagicMock()

    # Create a mock response object for read_holding_registers
    mock_response = MagicMock()
    mock_response.registers = [255]  # Simulate reading 25.5 degrees

    # Mock asyncio.to_thread to return our mock_response directly
    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = mock_response

        client = MqttClient(usb_port=0)
        temperature = await client.read_temperature(RegisterAddress.OUTSIDE_TEMP, "Outside")

    assert temperature == 25.5
    mock_instance.connect.assert_called_once()
    mock_to_thread.assert_called_once()
    mock_instance.close.assert_called_once()


@patch('kronoterm_voice_actions.wyoming.mqtt_client.pymodbus.client.ModbusSerialClient')
async def test_read_direct(MockModbusClient):
    """Tests the base read method."""
    mock_instance = MockModbusClient.return_value
    mock_instance.connect = MagicMock()
    mock_instance.close = MagicMock()
    mock_response = MagicMock()
    mock_response.registers = [1]  # System ON

    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = mock_response
        client = MqttClient(usb_port=0)
        status = await client.read(RegisterAddress.SYSTEM_STATUS)

    assert status == 1
    mock_instance.connect.assert_called_once()
    mock_to_thread.assert_called_once()
    # Check that to_thread was called with the correct underlying function
    assert mock_to_thread.call_args[0][0] == mock_instance.read_holding_registers
    mock_instance.close.assert_called_once()


@patch('kronoterm_voice_actions.wyoming.mqtt_client.pymodbus.client.ModbusSerialClient')
async def test_write_direct(MockModbusClient):
    """Tests the base write method."""
    mock_instance = MockModbusClient.return_value
    mock_instance.connect = MagicMock()
    mock_instance.close = MagicMock()
    # The actual write_register doesn't need to be async, as to_thread handles it
    mock_instance.write_register = MagicMock(return_value=None) 

    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = None # asyncio.to_thread will return this
        client = MqttClient(usb_port=0)
        await client.write(RegisterAddress.SYSTEM_ON, 1) # Turn system ON

    mock_instance.connect.assert_called_once()
    mock_to_thread.assert_called_once()
    # Check that to_thread was called with the correct underlying function and args
    assert mock_to_thread.call_args[0][0] == mock_instance.write_register
    assert mock_to_thread.call_args[0][1] == RegisterAddress.SYSTEM_ON.to_int() - 1
    assert mock_to_thread.call_args[0][2] == 1 # value=raw
    mock_instance.close.assert_called_once()


@patch('kronoterm_voice_actions.wyoming.mqtt_client.MqttClient.set_temperature', new_callable=AsyncMock)
async def test_set_dhw_target_temp(mock_set_temp):
    """Tests setting the DHW temperature by mocking set_temperature."""
    # Configure mock to return a float value, as expected by the code
    mock_set_temp.return_value = 45.0 

    client = MqttClient(usb_port=0) # We need a real MqttClient instance
    
    response = await client.set_dhw_target_temperature(45.0)

    # Assert that the mocked set_temperature was called correctly
    mock_set_temp.assert_called_once_with(RegisterAddress.DHW_TARGET_TEMP, 45.0)
    # Assert that the response string is generated correctly
    assert "nastavljena na 45 stopinj" in response


@patch('kronoterm_voice_actions.wyoming.mqtt_client.MqttClient.read', new_callable=AsyncMock)
async def test_get_system_status_on(mock_read):
    """Tests getting system status when it's ON."""
    mock_read.return_value = 1 # Simulate system is ON
    
    client = MqttClient(usb_port=0)
    response = await client.get_system_status()

    mock_read.assert_called_once_with(RegisterAddress.SYSTEM_STATUS)
    assert response == "Sistem je vklopljen."

@patch('kronoterm_voice_actions.wyoming.mqtt_client.MqttClient.read', new_callable=AsyncMock)
async def test_get_system_status_off(mock_read):
    """Tests getting system status when it's OFF."""
    mock_read.return_value = 0 # Simulate system is OFF

    client = MqttClient(usb_port=0)
    response = await client.get_system_status()

    mock_read.assert_called_once_with(RegisterAddress.SYSTEM_STATUS)
    assert response == "Sistem je izklopljen."