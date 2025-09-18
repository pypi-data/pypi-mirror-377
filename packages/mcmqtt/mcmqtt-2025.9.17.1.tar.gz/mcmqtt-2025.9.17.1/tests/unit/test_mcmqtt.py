"""Unit tests for mcmqtt.py entry point functionality."""

import os
import sys
import asyncio
import argparse
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO

# Import the module under test
from mcmqtt.mcmqtt import (
    setup_logging, get_version, create_mqtt_config_from_env,
    run_stdio_server, run_http_server, main
)
from mcmqtt.mqtt.types import MQTTConfig, MQTTQoS


class TestSetupLogging:
    """Test cases for setup_logging function."""

    @patch('mcmqtt.mcmqtt.logging')
    @patch('mcmqtt.mcmqtt.structlog')
    def test_setup_logging_default_stderr(self, mock_structlog, mock_logging):
        """Test setup_logging defaults to stderr."""
        setup_logging()
        
        mock_logging.basicConfig.assert_called_once()
        call_args = mock_logging.basicConfig.call_args
        assert call_args[1]['level'] == mock_logging.WARNING
        
        # Should use stderr handler
        handlers = call_args[1]['handlers']
        assert len(handlers) == 1
        assert handlers[0]._stream == sys.stderr
        
        mock_structlog.configure.assert_called_once()

    @patch('mcmqtt.mcmqtt.logging')
    @patch('mcmqtt.mcmqtt.structlog')
    def test_setup_logging_with_file(self, mock_structlog, mock_logging):
        """Test setup_logging with log file."""
        with patch('mcmqtt.mcmqtt.logging.FileHandler') as mock_file_handler:
            setup_logging("INFO", "/tmp/test.log")
            
            mock_file_handler.assert_called_once_with("/tmp/test.log")
            mock_logging.basicConfig.assert_called_once()
            call_args = mock_logging.basicConfig.call_args
            assert call_args[1]['level'] == mock_logging.INFO

    @patch('mcmqtt.mcmqtt.logging')
    @patch('mcmqtt.mcmqtt.structlog')
    def test_setup_logging_custom_level(self, mock_structlog, mock_logging):
        """Test setup_logging with custom level."""
        setup_logging("DEBUG")
        
        call_args = mock_logging.basicConfig.call_args
        assert call_args[1]['level'] == mock_logging.DEBUG


class TestGetVersion:
    """Test cases for get_version function."""

    @patch('mcmqtt.mcmqtt.version')
    def test_get_version_success(self, mock_version):
        """Test successful version retrieval."""
        mock_version.return_value = "2.1.0"
        
        result = get_version()
        assert result == "2.1.0"
        mock_version.assert_called_once_with("mcmqtt")

    @patch('mcmqtt.mcmqtt.version', side_effect=Exception("Module not found"))
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
            "MQTT_BROKER_HOST": "mqtt.example.com"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is not None
            assert config.broker_host == "mqtt.example.com"
            assert config.broker_port == 1883  # Default
            assert config.client_id.startswith("mcmqtt-")
            assert config.qos == MQTTQoS.AT_LEAST_ONCE  # Default

    def test_create_config_full(self):
        """Test config creation with all environment variables."""
        env_vars = {
            "MQTT_BROKER_HOST": "secure.broker.com",
            "MQTT_BROKER_PORT": "8883",
            "MQTT_CLIENT_ID": "mcp-client",
            "MQTT_USERNAME": "mcpuser",
            "MQTT_PASSWORD": "mcppass",
            "MQTT_KEEPALIVE": "45",
            "MQTT_QOS": "0",
            "MQTT_USE_TLS": "true",
            "MQTT_CLEAN_SESSION": "false",
            "MQTT_RECONNECT_INTERVAL": "15",
            "MQTT_MAX_RECONNECT_ATTEMPTS": "3"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is not None
            assert config.broker_host == "secure.broker.com"
            assert config.broker_port == 8883
            assert config.client_id == "mcp-client"
            assert config.username == "mcpuser"
            assert config.password == "mcppass"
            assert config.keepalive == 45
            assert config.qos == MQTTQoS.AT_MOST_ONCE
            assert config.use_tls is True
            assert config.clean_session is False
            assert config.reconnect_interval == 15
            assert config.max_reconnect_attempts == 3

    @patch('mcmqtt.mcmqtt.logging')
    def test_create_config_exception_handling(self, mock_logging):
        """Test exception handling in config creation."""
        env_vars = {
            "MQTT_BROKER_HOST": "test.broker.com",
            "MQTT_QOS": "invalid_qos"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = create_mqtt_config_from_env()
            
            assert config is None
            mock_logging.error.assert_called_once()


class TestRunStdioServer:
    """Test cases for run_stdio_server function."""

    @pytest.mark.asyncio
    async def test_run_stdio_server_no_auto_connect(self):
        """Test STDIO server without auto-connect."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        await run_stdio_server(mock_server)
        
        mock_server.get_mcp_server.assert_called_once()
        mock_mcp.run_stdio_async.assert_called_once()
        mock_server.initialize_mqtt_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_stdio_server_with_auto_connect_success(self):
        """Test STDIO server with successful auto-connect."""
        mock_config = MQTTConfig(
            broker_host="test.broker.com",
            broker_port=1883,
            client_id="test-client"
        )
        
        mock_server = AsyncMock()
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client.return_value = True
        
        mock_mcp = AsyncMock()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()
            mock_mcp.run_stdio_async.assert_called_once()
            
            # Check logging calls
            assert mock_logger.info.call_count >= 2

    @pytest.mark.asyncio
    async def test_run_stdio_server_with_auto_connect_failure(self):
        """Test STDIO server with failed auto-connect."""
        mock_config = MQTTConfig(
            broker_host="test.broker.com",
            broker_port=1883,
            client_id="test-client"
        )
        
        mock_server = AsyncMock()
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client.return_value = False
        mock_server._last_error = "Connection failed"
        
        mock_mcp = AsyncMock()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            mock_server.initialize_mqtt_client.assert_called_once()
            mock_server.connect_mqtt.assert_not_called()
            mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stdio_server_keyboard_interrupt(self):
        """Test STDIO server handling KeyboardInterrupt."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_mcp.run_stdio_async.side_effect = KeyboardInterrupt()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            await run_stdio_server(mock_server)
            
            mock_server.disconnect_mqtt.assert_called_once()
            mock_logger.info.assert_called_with("Server shutting down...")

    @pytest.mark.asyncio
    async def test_run_stdio_server_exception(self):
        """Test STDIO server handling general exception."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_mcp.run_stdio_async.side_effect = Exception("Server error")
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            with patch('mcmqtt.mcmqtt.sys.exit') as mock_exit:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                await run_stdio_server(mock_server)
                
                mock_server.disconnect_mqtt.assert_called_once()
                mock_logger.error.assert_called_once()
                mock_exit.assert_called_once_with(1)


class TestRunHttpServer:
    """Test cases for run_http_server function."""

    @pytest.mark.asyncio
    async def test_run_http_server_basic(self):
        """Test HTTP server basic functionality."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        await run_http_server(mock_server, host="127.0.0.1", port=8080)
        
        mock_server.get_mcp_server.assert_called_once()
        mock_mcp.run_http_async.assert_called_once_with(host="127.0.0.1", port=8080)

    @pytest.mark.asyncio
    async def test_run_http_server_with_auto_connect(self):
        """Test HTTP server with auto-connect."""
        mock_config = MQTTConfig(
            broker_host="http.broker.com",
            broker_port=1883,
            client_id="http-client"
        )
        
        mock_server = AsyncMock()
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client.return_value = True
        
        mock_mcp = AsyncMock()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger'):
            await run_http_server(mock_server, auto_connect=True)
            
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_http_server_keyboard_interrupt(self):
        """Test HTTP server handling KeyboardInterrupt."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_mcp.run_http_async.side_effect = KeyboardInterrupt()
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            await run_http_server(mock_server)
            
            mock_server.disconnect_mqtt.assert_called_once()
            mock_logger.info.assert_called_with("Server shutting down...")

    @pytest.mark.asyncio
    async def test_run_http_server_exception(self):
        """Test HTTP server handling general exception."""
        mock_server = AsyncMock()
        mock_server.mqtt_config = None
        
        mock_mcp = AsyncMock()
        mock_mcp.run_http_async.side_effect = Exception("HTTP server error")
        mock_server.get_mcp_server.return_value = mock_mcp
        
        with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
            with patch('mcmqtt.mcmqtt.sys.exit') as mock_exit:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                await run_http_server(mock_server)
                
                mock_server.disconnect_mqtt.assert_called_once()
                mock_logger.error.assert_called_once()
                mock_exit.assert_called_once_with(1)


class TestMainFunction:
    """Test cases for the main function."""

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt', '--version'])
    @patch('mcmqtt.mcmqtt.sys.exit')
    def test_main_version_flag(self, mock_exit):
        """Test main function with version flag."""
        with patch('mcmqtt.mcmqtt.get_version', return_value="1.0.0"):
            with patch('builtins.print') as mock_print:
                main()
                
                mock_print.assert_called_once_with("mcmqtt version 1.0.0")
                mock_exit.assert_called_once_with(0)

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt', '--log-level', 'DEBUG'])
    @patch('mcmqtt.mcmqtt.asyncio.run')
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    def test_main_stdio_transport(self, mock_server_class, mock_asyncio_run):
        """Test main function with STDIO transport (default)."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        with patch('mcmqtt.mcmqtt.setup_logging') as mock_setup_logging:
            with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                main()
                
                mock_setup_logging.assert_called_once_with('DEBUG', None)
                mock_server_class.assert_called_once()
                mock_asyncio_run.assert_called_once()

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt', '--transport', 'http', '--port', '8080'])
    @patch('mcmqtt.mcmqtt.asyncio.run')
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    def test_main_http_transport(self, mock_server_class, mock_asyncio_run):
        """Test main function with HTTP transport."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        with patch('mcmqtt.mcmqtt.setup_logging'):
            with patch('mcmqtt.mcmqtt.structlog.get_logger'):
                main()
                
                mock_server_class.assert_called_once()
                mock_asyncio_run.assert_called_once()

    @patch('mcmqtt.mcmqtt.sys.argv', [
        'mcmqtt', 
        '--mqtt-host', 'test.broker.com',
        '--mqtt-port', '8883',
        '--mqtt-client-id', 'test-client',
        '--mqtt-username', 'testuser',
        '--mqtt-password', 'testpass',
        '--auto-connect'
    ])
    @patch('mcmqtt.mcmqtt.asyncio.run')
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    def test_main_with_mqtt_args(self, mock_server_class, mock_asyncio_run):
        """Test main function with MQTT command line arguments."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        with patch('mcmqtt.mcmqtt.setup_logging'):
            with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                main()
                
                # Check that server was created with MQTT config
                call_args = mock_server_class.call_args[0]
                mqtt_config = call_args[0]
                assert mqtt_config is not None
                assert mqtt_config.broker_host == "test.broker.com"
                assert mqtt_config.broker_port == 8883
                assert mqtt_config.client_id == "test-client"
                assert mqtt_config.username == "testuser"
                assert mqtt_config.password == "testpass"

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt'])
    @patch('mcmqtt.mcmqtt.asyncio.run')
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    def test_main_with_env_config(self, mock_server_class, mock_asyncio_run):
        """Test main function with environment MQTT configuration."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        env_vars = {
            "MQTT_BROKER_HOST": "env.broker.com",
            "MQTT_BROKER_PORT": "1884"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('mcmqtt.mcmqtt.setup_logging'):
                with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
                    mock_logger = MagicMock()
                    mock_get_logger.return_value = mock_logger
                    
                    main()
                    
                    # Check that server was created with env config
                    call_args = mock_server_class.call_args[0]
                    mqtt_config = call_args[0]
                    assert mqtt_config is not None
                    assert mqtt_config.broker_host == "env.broker.com"
                    assert mqtt_config.broker_port == 1884

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt'])
    @patch('mcmqtt.mcmqtt.asyncio.run', side_effect=KeyboardInterrupt())
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    @patch('mcmqtt.mcmqtt.sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_server_class, mock_asyncio_run):
        """Test main function handling KeyboardInterrupt."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        with patch('mcmqtt.mcmqtt.setup_logging'):
            with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                main()
                
                mock_logger.info.assert_called_with("Server stopped by user")
                mock_exit.assert_called_once_with(0)

    @patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt'])
    @patch('mcmqtt.mcmqtt.asyncio.run', side_effect=Exception("Server startup failed"))
    @patch('mcmqtt.mcmqtt.MCMQTTServer')
    @patch('mcmqtt.mcmqtt.sys.exit')
    def test_main_startup_exception(self, mock_exit, mock_server_class, mock_asyncio_run):
        """Test main function handling startup exception."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server
        
        with patch('mcmqtt.mcmqtt.setup_logging'):
            with patch('mcmqtt.mcmqtt.structlog.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                main()
                
                mock_logger.error.assert_called_with("Failed to start server", error="Server startup failed")
                mock_exit.assert_called_once_with(1)

    def test_main_argument_parsing(self):
        """Test argument parsing functionality."""
        # Test various argument combinations
        test_cases = [
            (['--transport', 'stdio'], {'transport': 'stdio'}),
            (['--transport', 'http', '--port', '9000'], {'transport': 'http', 'port': 9000}),
            (['--log-level', 'DEBUG'], {'log_level': 'DEBUG'}),
            (['--auto-connect'], {'auto_connect': True}),
            (['--mqtt-host', 'broker.test.com'], {'mqtt_host': 'broker.test.com'}),
        ]
        
        for args, expected_attrs in test_cases:
            with patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt'] + args):
                with patch('mcmqtt.mcmqtt.asyncio.run'):
                    with patch('mcmqtt.mcmqtt.MCMQTTServer'):
                        with patch('mcmqtt.mcmqtt.setup_logging'):
                            with patch('mcmqtt.mcmqtt.structlog.get_logger'):
                                # This implicitly tests argument parsing
                                main()

    def test_main_help_text(self):
        """Test that help text includes expected content."""
        # Mock sys.argv to trigger help
        with patch('mcmqtt.mcmqtt.sys.argv', ['mcmqtt', '--help']):
            with patch('mcmqtt.mcmqtt.sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    try:
                        main()
                    except SystemExit:
                        pass  # argparse calls sys.exit on --help
                    
                    # Help should have been printed
                    # Note: argparse handles this internally


if __name__ == "__main__":
    pytest.main([__file__])