"""Tests for main.py CLI entry point with real imports."""

import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner

import pytest

def test_main_imports():
    """Test all main.py imports and basic functionality."""
    # Import everything to get coverage
    from mcmqtt.main import (
        app, setup_logging, get_version, create_mqtt_config_from_env, 
        serve, version, health, config, main, console
    )
    
    # Test console exists
    assert console is not None
    
    # Test logging setup variations
    setup_logging("INFO")
    setup_logging("DEBUG") 
    setup_logging("WARNING")
    setup_logging("ERROR")
    setup_logging("CRITICAL")
    
    # Test version function
    version_str = get_version()
    assert isinstance(version_str, str)
    assert len(version_str) > 0
    
    # Test MQTT config creation with no env vars (clear environment first)
    with patch.dict(os.environ, {}, clear=True):
        config_result = create_mqtt_config_from_env()
        assert config_result is None  # No MQTT_BROKER_HOST set

def test_cli_help():
    """Test CLI help command."""
    from mcmqtt.main import app
    runner = CliRunner()
    
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "serve" in result.stdout

def test_cli_version():
    """Test CLI version command.""" 
    from mcmqtt.main import app
    runner = CliRunner()
    
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "mcmqtt version:" in result.stdout

@patch('mcmqtt.main.asyncio.run')
@patch('mcmqtt.main.MCMQTTServer')
def test_serve_basic(mock_server_class, mock_asyncio_run):
    """Test basic serve command."""
    from mcmqtt.main import app
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    runner = CliRunner()
    result = runner.invoke(app, ["serve"])
    
    assert result.exit_code == 0
    mock_server_class.assert_called_once()
    mock_asyncio_run.assert_called_once()

@patch('mcmqtt.main.asyncio.run')
@patch('mcmqtt.main.MCMQTTServer')
def test_serve_with_mqtt_options(mock_server_class, mock_asyncio_run):
    """Test serve command with MQTT options."""
    from mcmqtt.main import app
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "serve",
        "--host", "127.0.0.1",
        "--port", "8883", 
        "--mqtt-host", "localhost",
        "--mqtt-port", "1884",
        "--mqtt-client-id", "test-client",
        "--mqtt-username", "testuser",
        "--mqtt-password", "testpass",
        "--log-level", "DEBUG",
        "--auto-connect"
    ])
    
    assert result.exit_code == 0
    mock_server_class.assert_called_once()

def test_config_command():
    """Test config command."""
    from mcmqtt.main import app
    runner = CliRunner()
    
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Configuration Sources:" in result.stdout
    assert "Environment Variables:" in result.stdout

def test_health_command_success():
    """Test health command with successful response."""
    from mcmqtt.main import app
    import httpx
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}
    
    with patch('httpx.get', return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(app, ["health", "--host", "localhost", "--port", "3000"])
        
        assert result.exit_code == 0
        assert "Server is healthy" in result.stdout

def test_health_command_connection_error():
    """Test health command with connection error."""
    from mcmqtt.main import app
    import httpx
    
    with patch('httpx.get', side_effect=httpx.ConnectError("Connection failed")):
        runner = CliRunner()
        result = runner.invoke(app, ["health"])
        
        assert result.exit_code == 1
        assert "Cannot connect to server" in result.stdout

def test_health_command_unhealthy():
    """Test health command with unhealthy response."""
    from mcmqtt.main import app
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    
    with patch('httpx.get', return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(app, ["health"])
        
        assert result.exit_code == 1
        assert "Server unhealthy" in result.stdout

def test_mqtt_config_from_env_with_values():
    """Test MQTT config creation with environment variables."""
    from mcmqtt.main import create_mqtt_config_from_env
    
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

def test_mqtt_config_from_env_error_handling():
    """Test MQTT config creation with invalid environment variables."""
    from mcmqtt.main import create_mqtt_config_from_env
    
    # Test with invalid port
    env_vars = {
        'MQTT_BROKER_HOST': 'test-broker',
        'MQTT_BROKER_PORT': 'invalid-port'
    }
    
    with patch.dict(os.environ, env_vars):
        config = create_mqtt_config_from_env()
        assert config is None  # Should fail gracefully

def test_mqtt_config_from_env_missing_host():
    """Test MQTT config creation without broker host."""
    from mcmqtt.main import create_mqtt_config_from_env
    
    # Clear any existing env vars
    with patch.dict(os.environ, {}, clear=True):
        config = create_mqtt_config_from_env()
        assert config is None

@patch('mcmqtt.main.app')
def test_main_function_direct_call(mock_app):
    """Test calling main function directly."""
    from mcmqtt.main import main
    
    main()
    mock_app.assert_called_once()

def test_import_all_dependencies():
    """Test that all required dependencies can be imported."""
    from mcmqtt.main import (
        typer, Console, RichHandler, structlog,
        MQTTConfig, MQTTQoS, MCMQTTServer
    )
    
    # All imports should succeed
    assert typer is not None
    assert Console is not None
    assert RichHandler is not None
    assert structlog is not None
    assert MQTTConfig is not None
    assert MQTTQoS is not None
    assert MCMQTTServer is not None

def test_structlog_configuration():
    """Test structlog configuration in logging setup."""
    from mcmqtt.main import setup_logging
    import structlog
    
    # Test that structlog is properly configured
    setup_logging("DEBUG")
    
    # Should be able to get a logger
    logger = structlog.get_logger()
    assert logger is not None

def test_get_version_fallback():
    """Test version function fallback behavior."""
    from mcmqtt.main import get_version
    
    # Mock importlib.metadata.version to raise exception
    with patch('mcmqtt.main.version', side_effect=Exception("Package not found")):
        version_str = get_version()
        assert version_str == "0.1.0"

@patch('mcmqtt.main.asyncio.run')
@patch('mcmqtt.main.MCMQTTServer')
def test_serve_with_auto_connect(mock_server_class, mock_asyncio_run):
    """Test serve command with auto-connect enabled."""
    from mcmqtt.main import app
    
    mock_server = AsyncMock()
    mock_server_class.return_value = mock_server
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "serve", 
        "--mqtt-host", "localhost", 
        "--auto-connect"
    ])
    
    assert result.exit_code == 0
    mock_server_class.assert_called_once()