"""Tests for mcmqtt.py MCP server entry point with real imports."""

import os
import sys
import tempfile
import argparse
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from io import StringIO

import pytest


def test_mcmqtt_imports():
    """Test all mcmqtt.py imports and basic functionality."""
    # Import everything to get coverage
    from mcmqtt.mcmqtt import (
        setup_logging, get_version, create_mqtt_config_from_env,
        run_stdio_server, run_http_server, main
    )
    
    # Test version function
    version_str = get_version()
    assert isinstance(version_str, str)
    assert len(version_str) > 0
    
    # Test MQTT config creation with no env vars (clear environment first)
    with patch.dict(os.environ, {}, clear=True):
        config_result = create_mqtt_config_from_env()
        assert config_result is None  # No MQTT_BROKER_HOST set


def test_setup_logging_to_stderr():
    """Test logging setup to stderr (default)."""
    from mcmqtt.mcmqtt import setup_logging
    
    with patch('logging.basicConfig') as mock_basic, \
         patch('logging.StreamHandler') as mock_handler, \
         patch('mcmqtt.mcmqtt.structlog.configure') as mock_structlog:
        
        setup_logging("INFO")
        
        mock_basic.assert_called_once()
        mock_handler.assert_called_once_with(sys.stderr)
        mock_structlog.assert_called_once()


def test_setup_logging_to_file():
    """Test logging setup with file output."""
    from mcmqtt.mcmqtt import setup_logging
    
    with patch('logging.basicConfig') as mock_basic, \
         patch('logging.FileHandler') as mock_handler, \
         patch('mcmqtt.mcmqtt.structlog.configure') as mock_structlog:
        
        setup_logging("DEBUG", "/tmp/test.log")
        
        mock_basic.assert_called_once()
        mock_handler.assert_called_once_with("/tmp/test.log")
        mock_structlog.assert_called_once()


def test_get_version_fallback():
    """Test version function fallback behavior."""
    from mcmqtt.mcmqtt import get_version
    
    # Mock importlib.metadata.version to raise exception
    with patch('importlib.metadata.version', side_effect=Exception("Package not found")):
        version_str = get_version()
        assert version_str == "0.1.0"


def test_create_mqtt_config_from_env_with_values():
    """Test MQTT config creation with environment variables."""
    from mcmqtt.mcmqtt import create_mqtt_config_from_env
    
    env_vars = {
        'MQTT_BROKER_HOST': 'test-broker',
        'MQTT_BROKER_PORT': '1884',
        'MQTT_CLIENT_ID': 'test-client',
        'MQTT_USERNAME': 'testuser',
        'MQTT_PASSWORD': 'testpass',
        'MQTT_KEEPALIVE': '120',
        'MQTT_QOS': '2',
        'MQTT_USE_TLS': 'true',
        'MQTT_CLEAN_SESSION': 'false',
        'MQTT_RECONNECT_INTERVAL': '10',
        'MQTT_MAX_RECONNECT_ATTEMPTS': '5'
    }
    
    with patch.dict(os.environ, env_vars):
        config = create_mqtt_config_from_env()
        
        assert config is not None
        assert config.broker_host == 'test-broker'
        assert config.broker_port == 1884
        assert config.client_id == 'test-client'
        assert config.username == 'testuser'
        assert config.password == 'testpass'
        assert config.keepalive == 120
        assert config.qos.value == 2
        assert config.use_tls is True
        assert config.clean_session is False
        assert config.reconnect_interval == 10
        assert config.max_reconnect_attempts == 5


def test_create_mqtt_config_from_env_error_handling():
    """Test MQTT config creation with invalid environment variables."""
    from mcmqtt.mcmqtt import create_mqtt_config_from_env
    
    # Test with invalid port
    env_vars = {
        'MQTT_BROKER_HOST': 'test-broker',
        'MQTT_BROKER_PORT': 'invalid-port'
    }
    
    with patch.dict(os.environ, env_vars):
        config = create_mqtt_config_from_env()
        assert config is None  # Should fail gracefully


def test_create_mqtt_config_from_env_missing_host():
    """Test MQTT config creation without broker host."""
    from mcmqtt.mcmqtt import create_mqtt_config_from_env
    
    # Clear any existing env vars
    with patch.dict(os.environ, {}, clear=True):
        config = create_mqtt_config_from_env()
        assert config is None


@pytest.mark.asyncio
async def test_run_stdio_server_basic():
    """Test STDIO server runner basic functionality."""
    from mcmqtt.mcmqtt import run_stdio_server
    
    mock_server = AsyncMock()
    mock_server.mqtt_config = None
    mock_mcp = AsyncMock()
    mock_server.get_mcp_server.return_value = mock_mcp
    
    # Mock the stdio async run to raise KeyboardInterrupt to exit cleanly
    mock_mcp.run_stdio_async = AsyncMock(side_effect=KeyboardInterrupt())
    mock_server.disconnect_mqtt = AsyncMock()
    
    await run_stdio_server(mock_server, auto_connect=False)
    
    mock_server.get_mcp_server.assert_called_once()
    mock_mcp.run_stdio_async.assert_called_once()
    mock_server.disconnect_mqtt.assert_called_once()


@pytest.mark.asyncio
async def test_run_stdio_server_with_auto_connect():
    """Test STDIO server with auto-connect enabled."""
    from mcmqtt.mcmqtt import run_stdio_server
    from mcmqtt.mqtt.types import MQTTConfig
    
    mock_server = AsyncMock()
    mock_server.mqtt_config = MQTTConfig(
        broker_host="localhost",
        client_id="test-client"
    )
    mock_server.initialize_mqtt_client = AsyncMock(return_value=True)
    mock_server.connect_mqtt = AsyncMock()
    mock_server.disconnect_mqtt = AsyncMock()
    
    mock_mcp = AsyncMock()
    mock_server.get_mcp_server.return_value = mock_mcp
    mock_mcp.run_stdio_async = AsyncMock(side_effect=KeyboardInterrupt())
    
    await run_stdio_server(mock_server, auto_connect=True)
    
    mock_server.initialize_mqtt_client.assert_called_once()
    mock_server.connect_mqtt.assert_called_once()
    mock_server.disconnect_mqtt.assert_called_once()


@pytest.mark.asyncio
async def test_run_stdio_server_connect_failure():
    """Test STDIO server with MQTT connection failure."""
    from mcmqtt.mcmqtt import run_stdio_server
    from mcmqtt.mqtt.types import MQTTConfig
    
    mock_server = AsyncMock()
    mock_server.mqtt_config = MQTTConfig(
        broker_host="localhost",
        client_id="test-client"
    )
    mock_server.initialize_mqtt_client = AsyncMock(return_value=False)
    mock_server._last_error = "Connection failed"
    mock_server.disconnect_mqtt = AsyncMock()
    
    mock_mcp = AsyncMock()
    mock_server.get_mcp_server.return_value = mock_mcp
    mock_mcp.run_stdio_async = AsyncMock(side_effect=KeyboardInterrupt())
    
    await run_stdio_server(mock_server, auto_connect=True)
    
    mock_server.initialize_mqtt_client.assert_called_once()
    # Should continue running despite connection failure
    mock_mcp.run_stdio_async.assert_called_once()
    mock_server.disconnect_mqtt.assert_called_once()


@pytest.mark.asyncio
async def test_run_http_server_basic():
    """Test HTTP server runner basic functionality."""
    from mcmqtt.mcmqtt import run_http_server
    
    mock_server = AsyncMock()
    mock_server.mqtt_config = None
    mock_server.disconnect_mqtt = AsyncMock()
    mock_mcp = AsyncMock()
    mock_server.get_mcp_server.return_value = mock_mcp
    mock_mcp.run_http_async = AsyncMock(side_effect=KeyboardInterrupt())
    
    await run_http_server(mock_server, host="127.0.0.1", port=8080)
    
    mock_server.get_mcp_server.assert_called_once()
    mock_mcp.run_http_async.assert_called_once_with(host="127.0.0.1", port=8080)
    mock_server.disconnect_mqtt.assert_called_once()


@pytest.mark.asyncio
async def test_run_http_server_with_auto_connect():
    """Test HTTP server with auto-connect enabled."""
    from mcmqtt.mcmqtt import run_http_server
    from mcmqtt.mqtt.types import MQTTConfig
    
    mock_server = AsyncMock()
    mock_server.mqtt_config = MQTTConfig(
        broker_host="localhost",
        client_id="test-client"
    )
    mock_server.initialize_mqtt_client = AsyncMock(return_value=True)
    mock_server.connect_mqtt = AsyncMock()
    mock_server.disconnect_mqtt = AsyncMock()
    
    mock_mcp = AsyncMock()
    mock_server.get_mcp_server.return_value = mock_mcp
    mock_mcp.run_http_async = AsyncMock(side_effect=KeyboardInterrupt())
    
    await run_http_server(mock_server, auto_connect=True)
    
    mock_server.initialize_mqtt_client.assert_called_once()
    mock_server.connect_mqtt.assert_called_once()
    mock_server.disconnect_mqtt.assert_called_once()


def test_main_version_flag():
    """Test main function with version flag."""
    from mcmqtt.mcmqtt import main
    
    test_args = ["mcmqtt", "--version"]
    
    with patch('sys.argv', test_args), \
         patch('sys.exit') as mock_exit, \
         patch('builtins.print') as mock_print, \
         patch('mcmqtt.mcmqtt.get_version', return_value="1.0.0"):
        
        main()
        
        mock_print.assert_called_once_with("mcmqtt version 1.0.0")
        mock_exit.assert_called_once_with(0)


@patch('mcmqtt.mcmqtt.asyncio.run')
@patch('mcmqtt.mcmqtt.MCMQTTServer')
@patch('mcmqtt.mcmqtt.setup_logging')
def test_main_stdio_transport(mock_setup_logging, mock_server_class, mock_asyncio_run):
    """Test main function with STDIO transport."""
    from mcmqtt.mcmqtt import main
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    test_args = ["mcmqtt", "--transport", "stdio"]
    
    with patch('sys.argv', test_args), \
         patch.dict(os.environ, {}, clear=True):
        
        main()
        
        mock_server_class.assert_called_once()
        mock_asyncio_run.assert_called_once()
        mock_setup_logging.assert_called_once()


@patch('mcmqtt.mcmqtt.asyncio.run')
@patch('mcmqtt.mcmqtt.MCMQTTServer')
@patch('mcmqtt.mcmqtt.setup_logging')
def test_main_http_transport(mock_setup_logging, mock_server_class, mock_asyncio_run):
    """Test main function with HTTP transport."""
    from mcmqtt.mcmqtt import main
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    test_args = ["mcmqtt", "--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
    
    with patch('sys.argv', test_args), \
         patch.dict(os.environ, {}, clear=True):
        
        main()
        
        mock_server_class.assert_called_once()
        mock_asyncio_run.assert_called_once()
        mock_setup_logging.assert_called_once()


@patch('mcmqtt.mcmqtt.asyncio.run')
@patch('mcmqtt.mcmqtt.MCMQTTServer')
@patch('mcmqtt.mcmqtt.setup_logging')
def test_main_with_mqtt_args(mock_setup_logging, mock_server_class, mock_asyncio_run):
    """Test main function with MQTT command line arguments."""
    from mcmqtt.mcmqtt import main
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    test_args = [
        "mcmqtt", 
        "--mqtt-host", "localhost",
        "--mqtt-port", "1884",
        "--mqtt-client-id", "test-client",
        "--mqtt-username", "testuser",
        "--mqtt-password", "testpass",
        "--auto-connect"
    ]
    
    with patch('sys.argv', test_args):
        main()
        
        mock_server_class.assert_called_once()
        mock_asyncio_run.assert_called_once()
        # Check that MQTT config was created with args
        call_args = mock_server_class.call_args[0]
        mqtt_config = call_args[0]
        assert mqtt_config is not None
        assert mqtt_config.broker_host == "localhost"
        assert mqtt_config.broker_port == 1884


def test_main_with_env_mqtt_config():
    """Test main function with MQTT config from environment."""
    from mcmqtt.mcmqtt import main
    
    env_vars = {
        'MQTT_BROKER_HOST': 'env-broker',
        'MQTT_BROKER_PORT': '1885'
    }
    
    test_args = ["mcmqtt"]
    
    with patch('sys.argv', test_args), \
         patch.dict(os.environ, env_vars), \
         patch('mcmqtt.mcmqtt.asyncio.run'), \
         patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
         patch('mcmqtt.mcmqtt.setup_logging'):
        
        main()
        
        mock_server_class.assert_called_once()
        # Check that MQTT config was created from env
        call_args = mock_server_class.call_args[0]
        mqtt_config = call_args[0]
        assert mqtt_config is not None
        assert mqtt_config.broker_host == "env-broker"


def test_main_no_mqtt_config():
    """Test main function with no MQTT configuration."""
    from mcmqtt.mcmqtt import main
    
    test_args = ["mcmqtt"]
    
    with patch('sys.argv', test_args), \
         patch.dict(os.environ, {}, clear=True), \
         patch('mcmqtt.mcmqtt.asyncio.run'), \
         patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
         patch('mcmqtt.mcmqtt.setup_logging'):
        
        main()
        
        mock_server_class.assert_called_once()
        # Check that server was created with None config
        call_args = mock_server_class.call_args[0]
        mqtt_config = call_args[0]
        assert mqtt_config is None


def test_main_keyboard_interrupt():
    """Test main function handling KeyboardInterrupt."""
    from mcmqtt.mcmqtt import main
    
    test_args = ["mcmqtt"]
    
    with patch('sys.argv', test_args), \
         patch('mcmqtt.mcmqtt.asyncio.run', side_effect=KeyboardInterrupt()), \
         patch('mcmqtt.mcmqtt.MCMQTTServer'), \
         patch('mcmqtt.mcmqtt.setup_logging'), \
         patch('sys.exit') as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(0)


def test_main_general_exception():
    """Test main function handling general exceptions."""
    from mcmqtt.mcmqtt import main
    
    test_args = ["mcmqtt"]
    
    with patch('sys.argv', test_args), \
         patch('mcmqtt.mcmqtt.asyncio.run', side_effect=Exception("Server failed")), \
         patch('mcmqtt.mcmqtt.MCMQTTServer'), \
         patch('mcmqtt.mcmqtt.setup_logging'), \
         patch('sys.exit') as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(1)


def test_main_logging_setup():
    """Test that main function sets up logging correctly."""
    from mcmqtt.mcmqtt import main
    
    test_args = ["mcmqtt", "--log-level", "DEBUG", "--log-file", "/tmp/test.log"]
    
    with patch('sys.argv', test_args), \
         patch('mcmqtt.mcmqtt.setup_logging') as mock_setup, \
         patch('mcmqtt.mcmqtt.asyncio.run'), \
         patch('mcmqtt.mcmqtt.MCMQTTServer'), \
         patch.dict(os.environ, {}, clear=True):
        
        main()
        
        mock_setup.assert_called_once_with("DEBUG", "/tmp/test.log")


def test_import_all_dependencies():
    """Test that all required dependencies can be imported."""
    from mcmqtt.mcmqtt import (
        asyncio, logging, os, sys, argparse, structlog,
        FastMCP, MCMQTTServer, MQTTConfig
    )
    
    # All imports should succeed
    assert asyncio is not None
    assert logging is not None
    assert os is not None
    assert sys is not None
    assert argparse is not None
    assert structlog is not None
    assert FastMCP is not None
    assert MCMQTTServer is not None
    assert MQTTConfig is not None


def test_structlog_configuration():
    """Test structlog configuration in logging setup."""
    from mcmqtt.mcmqtt import setup_logging
    import structlog
    
    # Test that structlog is properly configured
    setup_logging("DEBUG")
    
    # Should be able to get a logger
    logger = structlog.get_logger()
    assert logger is not None