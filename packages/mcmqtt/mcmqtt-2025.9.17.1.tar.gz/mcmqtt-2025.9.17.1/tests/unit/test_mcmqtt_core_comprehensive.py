"""
Comprehensive unit tests for mcmqtt core module.

Tests all entry point functionality including CLI parsing, configuration,
logging setup, server runners, and version management.
"""

import pytest
import asyncio
import logging
import os
import sys
import tempfile
from unittest.mock import (
    Mock, MagicMock, patch, AsyncMock, call
)
from pathlib import Path
from io import StringIO

# Import the module under test
from mcmqtt.mcmqtt import (
    setup_logging,
    get_version,
    create_mqtt_config_from_env,
    run_stdio_server,
    run_http_server,
    main
)
from mcmqtt.mqtt.types import MQTTConfig, MQTTQoS


class TestSetupLogging:
    """Test logging configuration functionality."""
    
    def test_setup_logging_default_stderr(self):
        """Test logging setup with default stderr handler."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging()
            
            # Verify logging.basicConfig called with stderr handler
            mock_basic.assert_called_once()
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.WARNING
            assert len(call_args[1]['handlers']) == 1
            assert isinstance(call_args[1]['handlers'][0], logging.StreamHandler)
            assert call_args[1]['handlers'][0].stream == sys.stderr
            
            # Verify structlog configured
            mock_structlog.assert_called_once()
    
    def test_setup_logging_file_handler(self):
        """Test logging setup with file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            log_file = tf.name
        
        try:
            with patch('logging.basicConfig') as mock_basic, \
                 patch('structlog.configure') as mock_structlog:
                
                setup_logging(log_level="INFO", log_file=log_file)
                
                # Verify logging.basicConfig called with file handler
                mock_basic.assert_called_once()
                call_args = mock_basic.call_args
                assert call_args[1]['level'] == logging.INFO
                assert len(call_args[1]['handlers']) == 1
                assert isinstance(call_args[1]['handlers'][0], logging.FileHandler)
                
                # Verify structlog configured
                mock_structlog.assert_called_once()
        finally:
            os.unlink(log_file)
    
    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="DEBUG")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.DEBUG
    
    def test_setup_logging_error_level(self):
        """Test logging setup with ERROR level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="ERROR")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.ERROR


class TestGetVersion:
    """Test version retrieval functionality."""
    
    def test_get_version_success(self):
        """Test successful version retrieval."""
        with patch('mcmqtt.mcmqtt.version', return_value="1.2.3"):
            version = get_version()
            assert version == "1.2.3"
    
    def test_get_version_import_error(self):
        """Test version retrieval with import error fallback."""
        with patch('mcmqtt.mcmqtt.version', side_effect=ImportError("No module")):
            version = get_version()
            assert version == "0.1.0"
    
    def test_get_version_exception(self):
        """Test version retrieval with general exception fallback."""
        with patch('mcmqtt.mcmqtt.version', side_effect=Exception("Unknown error")):
            version = get_version()
            assert version == "0.1.0"


class TestCreateMqttConfigFromEnv:
    """Test MQTT configuration from environment variables."""
    
    def setUp(self):
        """Clear environment variables before each test."""
        env_vars = [
            'MQTT_BROKER_HOST', 'MQTT_BROKER_PORT', 'MQTT_CLIENT_ID',
            'MQTT_USERNAME', 'MQTT_PASSWORD', 'MQTT_KEEPALIVE',
            'MQTT_QOS', 'MQTT_USE_TLS', 'MQTT_CLEAN_SESSION',
            'MQTT_RECONNECT_INTERVAL', 'MQTT_MAX_RECONNECT_ATTEMPTS'
        ]
        for var in env_vars:
            os.environ.pop(var, None)
    
    def test_create_mqtt_config_no_host(self):
        """Test config creation with no broker host."""
        self.setUp()
        config = create_mqtt_config_from_env()
        assert config is None
    
    def test_create_mqtt_config_minimal(self):
        """Test config creation with minimal environment variables."""
        self.setUp()
        os.environ['MQTT_BROKER_HOST'] = 'localhost'
        
        config = create_mqtt_config_from_env()
        
        assert config is not None
        assert config.broker_host == 'localhost'
        assert config.broker_port == 1883  # default
        assert config.client_id.startswith('mcmqtt-')
        assert config.username is None
        assert config.password is None
        assert config.keepalive == 60
        assert config.qos == MQTTQoS.AT_LEAST_ONCE
        assert config.use_tls is False
        assert config.clean_session is True
        assert config.reconnect_interval == 5
        assert config.max_reconnect_attempts == 10
    
    def test_create_mqtt_config_complete(self):
        """Test config creation with all environment variables."""
        self.setUp()
        os.environ.update({
            'MQTT_BROKER_HOST': 'mqtt.example.com',
            'MQTT_BROKER_PORT': '8883',
            'MQTT_CLIENT_ID': 'test-client',
            'MQTT_USERNAME': 'testuser',
            'MQTT_PASSWORD': 'testpass',
            'MQTT_KEEPALIVE': '120',
            'MQTT_QOS': '2',
            'MQTT_USE_TLS': 'true',
            'MQTT_CLEAN_SESSION': 'false',
            'MQTT_RECONNECT_INTERVAL': '10',
            'MQTT_MAX_RECONNECT_ATTEMPTS': '5'
        })
        
        config = create_mqtt_config_from_env()
        
        assert config is not None
        assert config.broker_host == 'mqtt.example.com'
        assert config.broker_port == 8883
        assert config.client_id == 'test-client'
        assert config.username == 'testuser'
        assert config.password == 'testpass'
        assert config.keepalive == 120
        assert config.qos == MQTTQoS.EXACTLY_ONCE
        assert config.use_tls is True
        assert config.clean_session is False
        assert config.reconnect_interval == 10
        assert config.max_reconnect_attempts == 5
    
    def test_create_mqtt_config_invalid_port(self):
        """Test config creation with invalid port."""
        self.setUp()
        os.environ['MQTT_BROKER_HOST'] = 'localhost'
        os.environ['MQTT_BROKER_PORT'] = 'invalid'
        
        with patch('logging.error') as mock_error:
            config = create_mqtt_config_from_env()
            assert config is None
            mock_error.assert_called_once()
    
    def test_create_mqtt_config_invalid_qos(self):
        """Test config creation with invalid QoS."""
        self.setUp()
        os.environ['MQTT_BROKER_HOST'] = 'localhost'
        os.environ['MQTT_QOS'] = 'invalid'
        
        with patch('logging.error') as mock_error:
            config = create_mqtt_config_from_env()
            assert config is None
            mock_error.assert_called_once()


class TestRunStdioServer:
    """Test STDIO server runner functionality."""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock MQTT server."""
        server = Mock()
        server.mqtt_config = None
        server._last_error = None
        server.initialize_mqtt_client = AsyncMock(return_value=True)
        server.connect_mqtt = AsyncMock()
        server.disconnect_mqtt = AsyncMock()
        server.get_mcp_server = Mock()
        
        # Mock the FastMCP instance
        mock_mcp = Mock()
        mock_mcp.run_stdio_async = AsyncMock()
        server.get_mcp_server.return_value = mock_mcp
        
        return server
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_no_auto_connect(self, mock_server):
        """Test STDIO server without auto-connect."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=False)
            
            # Verify no MQTT operations
            mock_server.initialize_mqtt_client.assert_not_called()
            mock_server.connect_mqtt.assert_not_called()
            
            # Verify MCP server started
            mock_server.get_mcp_server.assert_called_once()
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_stdio_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_auto_connect_success(self, mock_server):
        """Test STDIO server with successful auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'localhost'
        mock_config.broker_port = 1883
        mock_server.mqtt_config = mock_config
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            # Verify MQTT operations
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()
            
            # Verify logging
            logger.info.assert_any_call(
                "Auto-connecting to MQTT broker",
                broker="localhost:1883"
            )
            logger.info.assert_any_call("Connected to MQTT broker")
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_auto_connect_failure(self, mock_server):
        """Test STDIO server with failed auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'localhost'
        mock_config.broker_port = 1883
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client.return_value = False
        mock_server._last_error = "Connection failed"
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            # Verify MQTT initialization attempted but connect not called
            mock_server.initialize_mqtt_client.assert_called_once()
            mock_server.connect_mqtt.assert_not_called()
            
            # Verify warning logged
            logger.warning.assert_called_once_with(
                "Failed to connect to MQTT broker",
                error="Connection failed"
            )
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_keyboard_interrupt(self, mock_server):
        """Test STDIO server handling KeyboardInterrupt."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_stdio_async.side_effect = KeyboardInterrupt()
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server)
            
            # Verify cleanup
            mock_server.disconnect_mqtt.assert_called_once()
            logger.info.assert_called_with("Server shutting down...")
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_exception(self, mock_server):
        """Test STDIO server handling general exception."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_stdio_async.side_effect = Exception("Server error")
        
        with patch('structlog.get_logger') as mock_logger, \
             patch('sys.exit') as mock_exit:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server)
            
            # Verify cleanup and exit
            mock_server.disconnect_mqtt.assert_called_once()
            logger.error.assert_called_with("Server error", error="Server error")
            mock_exit.assert_called_once_with(1)


class TestRunHttpServer:
    """Test HTTP server runner functionality."""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock MQTT server."""
        server = Mock()
        server.mqtt_config = None
        server._last_error = None
        server.initialize_mqtt_client = AsyncMock(return_value=True)
        server.connect_mqtt = AsyncMock()
        server.disconnect_mqtt = AsyncMock()
        server.get_mcp_server = Mock()
        
        # Mock the FastMCP instance
        mock_mcp = Mock()
        mock_mcp.run_http_async = AsyncMock()
        server.get_mcp_server.return_value = mock_mcp
        
        return server
    
    @pytest.mark.asyncio
    async def test_run_http_server_default_params(self, mock_server):
        """Test HTTP server with default parameters."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify MCP server started with defaults
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_http_async.assert_called_once_with(host="0.0.0.0", port=3000)
    
    @pytest.mark.asyncio
    async def test_run_http_server_custom_params(self, mock_server):
        """Test HTTP server with custom parameters."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, host="127.0.0.1", port=8080)
            
            # Verify MCP server started with custom params
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_http_async.assert_called_once_with(host="127.0.0.1", port=8080)
    
    @pytest.mark.asyncio
    async def test_run_http_server_auto_connect(self, mock_server):
        """Test HTTP server with auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'mqtt.example.com'
        mock_config.broker_port = 8883
        mock_server.mqtt_config = mock_config
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, auto_connect=True)
            
            # Verify MQTT connection
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()
            
            # Verify logging
            logger.info.assert_any_call(
                "Auto-connecting to MQTT broker",
                broker="mqtt.example.com:8883"
            )
    
    @pytest.mark.asyncio
    async def test_run_http_server_keyboard_interrupt(self, mock_server):
        """Test HTTP server handling KeyboardInterrupt."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_http_async.side_effect = KeyboardInterrupt()
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify cleanup
            mock_server.disconnect_mqtt.assert_called_once()
            logger.info.assert_called_with("Server shutting down...")
    
    @pytest.mark.asyncio
    async def test_run_http_server_exception(self, mock_server):
        """Test HTTP server handling general exception."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_http_async.side_effect = Exception("HTTP error")
        
        with patch('structlog.get_logger') as mock_logger, \
             patch('sys.exit') as mock_exit:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify cleanup and exit
            mock_server.disconnect_mqtt.assert_called_once()
            logger.error.assert_called_with("Server error", error="HTTP error")
            mock_exit.assert_called_once_with(1)


class TestMain:
    """Test main entry point functionality."""
    
    def test_main_version_flag(self):
        """Test main with version flag."""
        test_args = ['mcmqtt', '--version']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.get_version', return_value="1.0.0"), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            main()
            
            mock_print.assert_called_once_with("mcmqtt version 1.0.0")
            mock_exit.assert_called_once_with(0)
    
    def test_main_stdio_default(self):
        """Test main with default STDIO transport."""
        test_args = ['mcmqtt']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging') as mock_setup_log, \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify logging setup
            mock_setup_log.assert_called_once_with("WARNING", None)
            
            # Verify server creation
            mock_server_class.assert_called_once_with(None)
            
            # Verify asyncio.run called for STDIO
            mock_asyncio_run.assert_called_once()
            # The call should be to run_stdio_server
            call_args = mock_asyncio_run.call_args[0][0]
            assert hasattr(call_args, '__name__')  # It's a coroutine
    
    def test_main_http_transport(self):
        """Test main with HTTP transport."""
        test_args = ['mcmqtt', '--transport', 'http', '--port', '8080', '--host', '127.0.0.1']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('structlog.get_logger'):
            
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify asyncio.run called for HTTP
            mock_asyncio_run.assert_called_once()
            # The call should be to run_http_server
            call_args = mock_asyncio_run.call_args[0][0]
            assert hasattr(call_args, '__name__')  # It's a coroutine
    
    def test_main_mqtt_command_line_args(self):
        """Test main with MQTT configuration from command line."""
        test_args = [
            'mcmqtt',
            '--mqtt-host', 'mqtt.test.com',
            '--mqtt-port', '8883',
            '--mqtt-client-id', 'test-client',
            '--mqtt-username', 'testuser',
            '--mqtt-password', 'testpass',
            '--auto-connect'
        ]
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify server created with MQTT config
            mock_server_class.assert_called_once()
            mqtt_config = mock_server_class.call_args[0][0]
            assert mqtt_config is not None
            assert mqtt_config.broker_host == 'mqtt.test.com'
            assert mqtt_config.broker_port == 8883
            assert mqtt_config.client_id == 'test-client'
            assert mqtt_config.username == 'testuser'
            assert mqtt_config.password == 'testpass'
            
            # Verify command line config logging
            logger.info.assert_any_call(
                "MQTT configuration from command line",
                broker="mqtt.test.com:8883"
            )
    
    def test_main_mqtt_environment_config(self):
        """Test main with MQTT configuration from environment."""
        test_args = ['mcmqtt']
        mock_config = Mock()
        mock_config.broker_host = 'env.mqtt.com'
        mock_config.broker_port = 1883
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=mock_config), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify server created with env config
            mock_server_class.assert_called_once_with(mock_config)
            
            # Verify environment config logging
            logger.info.assert_any_call(
                "MQTT configuration from environment",
                broker="env.mqtt.com:1883"
            )
    
    def test_main_no_mqtt_config(self):
        """Test main with no MQTT configuration."""
        test_args = ['mcmqtt']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify server created with None config
            mock_server_class.assert_called_once_with(None)
            
            # Verify no config logging
            logger.info.assert_any_call(
                "No MQTT configuration provided - use tools to configure at runtime"
            )
    
    def test_main_logging_options(self):
        """Test main with logging options."""
        test_args = ['mcmqtt', '--log-level', 'DEBUG', '--log-file', '/tmp/test.log']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging') as mock_setup_log, \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('asyncio.run'), \
             patch('structlog.get_logger'):
            
            main()
            
            # Verify logging setup with custom options
            mock_setup_log.assert_called_once_with("DEBUG", "/tmp/test.log")
    
    def test_main_keyboard_interrupt(self):
        """Test main handling KeyboardInterrupt."""
        test_args = ['mcmqtt']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('asyncio.run', side_effect=KeyboardInterrupt()), \
             patch('sys.exit') as mock_exit, \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            
            main()
            
            # Verify graceful shutdown
            logger.info.assert_called_with("Server stopped by user")
            mock_exit.assert_called_once_with(0)
    
    def test_main_exception(self):
        """Test main handling general exception."""
        test_args = ['mcmqtt']
        
        with patch('sys.argv', test_args), \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('asyncio.run', side_effect=Exception("Startup failed")), \
             patch('sys.exit') as mock_exit, \
             patch('structlog.get_logger') as mock_logger:
            
            logger = Mock()
            mock_logger.return_value = logger
            
            main()
            
            # Verify error handling
            logger.error.assert_called_with("Failed to start server", error="Startup failed")
            mock_exit.assert_called_once_with(1)


class TestMainEntryPoint:
    """Test __main__ entry point."""
    
    def test_main_entry_point(self):
        """Test if __name__ == '__main__' entry point."""
        with patch('mcmqtt.mcmqtt.main') as mock_main:
            # Simulate running as main module
            import mcmqtt.mcmqtt
            
            # This would normally be called when running as __main__
            # We can't easily test this directly, but we can verify the function exists
            assert hasattr(mcmqtt.mcmqtt, 'main')
            assert callable(mcmqtt.mcmqtt.main)