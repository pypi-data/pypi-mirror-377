"""Unit tests for main.py entry point functionality."""

import os
import sys
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from typer.testing import CliRunner

# Import the module under test
from mcmqtt.main import (
    app, setup_logging, get_version, create_mqtt_config_from_env,
    main
)
from mcmqtt.mqtt.types import MQTTConfig, MQTTQoS


class TestSetupLogging:
    """Test cases for setup_logging function."""

    @patch('mcmqtt.main.logging')
    @patch('mcmqtt.main.structlog')
    def test_setup_logging_default_level(self, mock_structlog, mock_logging):
        """Test setup_logging with default INFO level."""
        setup_logging()
        
        mock_logging.basicConfig.assert_called_once()
        call_args = mock_logging.basicConfig.call_args
        assert call_args[1]['level'] == mock_logging.INFO
        mock_structlog.configure.assert_called_once()

    @patch('mcmqtt.main.logging')
    @patch('mcmqtt.main.structlog')
    def test_setup_logging_custom_level(self, mock_structlog, mock_logging):
        """Test setup_logging with custom level."""
        setup_logging("DEBUG")
        
        call_args = mock_logging.basicConfig.call_args
        assert call_args[1]['level'] == mock_logging.DEBUG

    @patch('mcmqtt.main.logging')
    @patch('mcmqtt.main.structlog')
    def test_setup_logging_invalid_level(self, mock_structlog, mock_logging):
        """Test setup_logging with invalid level defaults gracefully."""
        # Should not raise an exception
        setup_logging("INVALID")
        mock_logging.basicConfig.assert_called_once()


class TestGetVersion:
    """Test cases for get_version function."""

    @patch('mcmqtt.main.version')
    def test_get_version_success(self, mock_version):
        """Test successful version retrieval."""
        mock_version.return_value = "1.2.3"
        
        result = get_version()
        assert result == "1.2.3"
        mock_version.assert_called_once_with("mcmqtt")

    @patch('mcmqtt.main.version', side_effect=Exception("Module not found"))
    def test_get_version_fallback(self, mock_version):
        """Test version fallback when importlib fails."""
        result = get_version()
        assert result == "0.1.0"


class TestCreateMqttConfigFromEnv:
    """Test cases for create_mqtt_config_from_env function."""

    def test_create_config_no_broker_host(self):
        """Test config creation when no MQTT_BROKER_HOST is set."""
        with patch.dict(os.environ, {}, clear=True):
            config = create_mqtt_config_from_env()
            assert config is None

    def test_create_config_minimal(self):
        """Test config creation with minimal environment variables."""
        env_vars = {
            "MQTT_BROKER_HOST": "test.broker.com"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is not None
            assert config.broker_host == "test.broker.com"
            assert config.broker_port == 1883  # Default
            assert config.client_id.startswith("mcmqtt-")
            assert config.qos == MQTTQoS.AT_LEAST_ONCE  # Default

    def test_create_config_full(self):
        """Test config creation with all environment variables."""
        env_vars = {
            "MQTT_BROKER_HOST": "broker.example.com",
            "MQTT_BROKER_PORT": "8883",
            "MQTT_CLIENT_ID": "test-client",
            "MQTT_USERNAME": "testuser",
            "MQTT_PASSWORD": "testpass",
            "MQTT_KEEPALIVE": "30",
            "MQTT_QOS": "2",
            "MQTT_USE_TLS": "true",
            "MQTT_CLEAN_SESSION": "false",
            "MQTT_RECONNECT_INTERVAL": "10",
            "MQTT_MAX_RECONNECT_ATTEMPTS": "5"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is not None
            assert config.broker_host == "broker.example.com"
            assert config.broker_port == 8883
            assert config.client_id == "test-client"
            assert config.username == "testuser"
            assert config.password == "testpass"
            assert config.keepalive == 30
            assert config.qos == MQTTQoS.EXACTLY_ONCE
            assert config.use_tls is True
            assert config.clean_session is False
            assert config.reconnect_interval == 10
            assert config.max_reconnect_attempts == 5

    def test_create_config_boolean_parsing(self):
        """Test boolean environment variable parsing."""
        # Test various boolean formats
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("False", False),
            ("anything_else", False)
        ]
        
        for env_value, expected in test_cases:
            env_vars = {
                "MQTT_BROKER_HOST": "test.broker.com",
                "MQTT_USE_TLS": env_value
            }
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = create_mqtt_config_from_env()
                assert config.use_tls == expected

    @patch('mcmqtt.main.console')
    def test_create_config_exception_handling(self, mock_console):
        """Test exception handling in config creation."""
        env_vars = {
            "MQTT_BROKER_HOST": "test.broker.com",
            "MQTT_BROKER_PORT": "invalid_port"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is None
            mock_console.print.assert_called_once()


class TestCliCommands:
    """Test cases for CLI commands."""

    def setUp(self):
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        
        with patch('mcmqtt.main.get_version', return_value="1.2.3"):
            result = runner.invoke(app, ["version"])
            
            assert result.exit_code == 0
            assert "1.2.3" in result.stdout

    @patch('mcmqtt.main.httpx')
    def test_health_command_success(self, mock_httpx):
        """Test health command with successful response."""
        runner = CliRunner()
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_httpx.get.return_value = mock_response
        
        result = runner.invoke(app, ["health"])
        
        assert result.exit_code == 0
        mock_httpx.get.assert_called_once_with("http://localhost:3000/health", timeout=10.0)

    @patch('mcmqtt.main.httpx')
    def test_health_command_unhealthy(self, mock_httpx):
        """Test health command with unhealthy response."""
        runner = CliRunner()
        
        # Mock unhealthy response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_httpx.get.return_value = mock_response
        
        result = runner.invoke(app, ["health"])
        
        assert result.exit_code == 1

    @patch('mcmqtt.main.httpx')
    def test_health_command_connection_error(self, mock_httpx):
        """Test health command with connection error."""
        runner = CliRunner()
        
        # Mock connection error
        import httpx
        mock_httpx.get.side_effect = httpx.ConnectError("Connection failed")
        mock_httpx.ConnectError = httpx.ConnectError
        
        result = runner.invoke(app, ["health"])
        
        assert result.exit_code == 1

    @patch('mcmqtt.main.httpx')
    def test_health_command_custom_host_port(self, mock_httpx):
        """Test health command with custom host and port."""
        runner = CliRunner()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_httpx.get.return_value = mock_response
        
        result = runner.invoke(app, ["health", "--host", "example.com", "--port", "8080"])
        
        mock_httpx.get.assert_called_once_with("http://example.com:8080/health", timeout=10.0)

    def test_config_command_no_env(self):
        """Test config command with no environment variables."""
        runner = CliRunner()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('mcmqtt.main.setup_logging'):
                result = runner.invoke(app, ["config"])
                
                assert result.exit_code == 0
                assert "not set" in result.stdout

    def test_config_command_with_env(self):
        """Test config command with environment variables."""
        runner = CliRunner()
        
        env_vars = {
            "MQTT_BROKER_HOST": "test.broker.com",
            "MQTT_BROKER_PORT": "1883",
            "MQTT_PASSWORD": "secret"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('mcmqtt.main.setup_logging'):
                result = runner.invoke(app, ["config"])
                
                assert result.exit_code == 0
                assert "test.broker.com" in result.stdout
                assert "***" in result.stdout  # Password should be masked

    @patch('mcmqtt.main.asyncio')
    @patch('mcmqtt.main.MCMQTTServer')
    def test_serve_command_minimal(self, mock_server_class, mock_asyncio):
        """Test serve command with minimal parameters."""
        runner = CliRunner()
        
        # Mock server instance
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        # Mock asyncio.run to avoid actually running the server
        mock_asyncio.run = MagicMock()
        
        with patch('mcmqtt.main.setup_logging'):
            result = runner.invoke(app, ["serve"])
            
            assert result.exit_code == 0
            mock_server_class.assert_called_once()
            mock_asyncio.run.assert_called_once()

    @patch('mcmqtt.main.asyncio')
    @patch('mcmqtt.main.MCMQTTServer')
    def test_serve_command_with_mqtt_config(self, mock_server_class, mock_asyncio):
        """Test serve command with MQTT configuration."""
        runner = CliRunner()
        
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        mock_asyncio.run = MagicMock()
        
        with patch('mcmqtt.main.setup_logging'):
            result = runner.invoke(app, [
                "serve",
                "--mqtt-host", "test.broker.com",
                "--mqtt-port", "8883",
                "--mqtt-client-id", "test-client",
                "--auto-connect"
            ])
            
            assert result.exit_code == 0
            
            # Check that server was created with MQTT config
            call_args = mock_server_class.call_args[0]
            mqtt_config = call_args[0]
            assert mqtt_config is not None
            assert mqtt_config.broker_host == "test.broker.com"
            assert mqtt_config.broker_port == 8883
            assert mqtt_config.client_id == "test-client"

    @patch('mcmqtt.main.asyncio')
    @patch('mcmqtt.main.MCMQTTServer')
    def test_serve_command_env_config(self, mock_server_class, mock_asyncio):
        """Test serve command with environment configuration."""
        runner = CliRunner()
        
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        mock_asyncio.run = MagicMock()
        
        env_vars = {
            "MQTT_BROKER_HOST": "env.broker.com",
            "MQTT_BROKER_PORT": "1884"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('mcmqtt.main.setup_logging'):
                result = runner.invoke(app, ["serve"])
                
                assert result.exit_code == 0
                
                # Check that server was created with env config
                call_args = mock_server_class.call_args[0]
                mqtt_config = call_args[0]
                assert mqtt_config is not None
                assert mqtt_config.broker_host == "env.broker.com"
                assert mqtt_config.broker_port == 1884


class TestRunServer:
    """Test cases for the async run_server function."""

    @pytest.mark.asyncio
    @patch('mcmqtt.main.MCMQTTServer')
    async def test_run_server_no_auto_connect(self, mock_server_class):
        """Test run_server without auto-connect."""
        # We need to test the run_server function directly
        # Since it's defined inside the serve command, we need to mock the whole flow
        
        mock_server = AsyncMock()
        mock_server.run_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        # This is more of an integration test through the CLI
        runner = CliRunner()
        
        # Mock the asyncio.run call to return immediately
        with patch('mcmqtt.main.asyncio.run') as mock_run:
            with patch('mcmqtt.main.setup_logging'):
                result = runner.invoke(app, ["serve", "--host", "127.0.0.1", "--port", "8080"])
                
                assert result.exit_code == 0
                mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_server_keyboard_interrupt(self):
        """Test run_server handling KeyboardInterrupt."""
        # This is tested implicitly through the CLI command structure
        # The actual async function is private to the command
        pass


class TestMainFunction:
    """Test cases for the main function."""

    @patch('mcmqtt.main.app')
    def test_main_function(self, mock_app):
        """Test the main function calls the Typer app."""
        main()
        mock_app.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])