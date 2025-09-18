"""
Comprehensive unit tests for the new simplified mcmqtt main module.

Tests the main entry point orchestration and startup logic.
"""

import pytest
import sys
from unittest.mock import patch, Mock, AsyncMock
from argparse import Namespace

from mcmqtt.mcmqtt import main


class TestMain:
    """Test main entry point functionality."""
    
    def test_main_version_flag(self):
        """Test main with version flag."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.get_version', return_value="1.0.0"), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            # Mock version argument
            args = Mock()
            args.version = True
            args.log_level = "INFO"
            args.log_file = None
            mock_parse.return_value = args
            
            main()
            
            mock_print.assert_called_once_with("mcmqtt version 1.0.0")
            mock_exit.assert_called_once_with(0)
    
    def test_main_stdio_default(self):
        """Test main with default STDIO transport."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging') as mock_setup_log, \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments
            args = Mock()
            args.version = False
            args.log_level = "WARNING"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
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
    
    def test_main_http_transport(self):
        """Test main with HTTP transport."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('structlog.get_logger'):
            
            # Mock arguments for HTTP transport
            args = Mock()
            args.version = False
            args.log_level = "INFO"
            args.log_file = "/tmp/test.log"
            args.mqtt_host = None
            args.transport = "http"
            args.host = "127.0.0.1"
            args.port = 8080
            args.auto_connect = True
            mock_parse.return_value = args
            
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify asyncio.run called for HTTP
            mock_asyncio_run.assert_called_once()
    
    def test_main_mqtt_command_line_args(self):
        """Test main with MQTT configuration from command line."""
        mock_config = Mock()
        mock_config.broker_host = 'mqtt.test.com'
        mock_config.broker_port = 8883
        
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=mock_config), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments with MQTT settings
            args = Mock()
            args.version = False
            args.log_level = "DEBUG"
            args.log_file = None
            args.mqtt_host = 'mqtt.test.com'
            args.mqtt_port = 8883
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify server created with MQTT config
            mock_server_class.assert_called_once_with(mock_config)
            
            # Verify command line config logging
            logger.info.assert_any_call(
                "MQTT configuration from command line",
                broker="mqtt.test.com:8883"
            )
    
    def test_main_mqtt_environment_config(self):
        """Test main with MQTT configuration from environment."""
        mock_config = Mock()
        mock_config.broker_host = 'env.mqtt.com'
        mock_config.broker_port = 1883
        
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=mock_config), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments with no MQTT settings
            args = Mock()
            args.version = False
            args.log_level = "WARNING"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
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
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments with no MQTT settings
            args = Mock()
            args.version = False
            args.log_level = "ERROR"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
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
    
    def test_main_startup_logging(self):
        """Test main startup information logging."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('mcmqtt.mcmqtt.get_version', return_value="2.0.0"), \
             patch('asyncio.run'), \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments
            args = Mock()
            args.version = False
            args.log_level = "INFO"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "http"
            args.auto_connect = True
            mock_parse.return_value = args
            
            logger = Mock()
            mock_logger.return_value = logger
            
            main()
            
            # Verify startup logging
            logger.info.assert_any_call(
                "Starting mcmqtt FastMCP server",
                version="2.0.0",
                transport="http",
                auto_connect=True
            )
    
    def test_main_keyboard_interrupt(self):
        """Test main handling KeyboardInterrupt."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('asyncio.run', side_effect=KeyboardInterrupt()), \
             patch('sys.exit') as mock_exit, \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments
            args = Mock()
            args.version = False
            args.log_level = "WARNING"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
            logger = Mock()
            mock_logger.return_value = logger
            
            main()
            
            # Verify graceful shutdown
            logger.info.assert_called_with("Server stopped by user")
            mock_exit.assert_called_once_with(0)
    
    def test_main_exception(self):
        """Test main handling general exception."""
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging'), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=None), \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_env', return_value=None), \
             patch('mcmqtt.mcmqtt.MCMQTTServer'), \
             patch('asyncio.run', side_effect=Exception("Startup failed")), \
             patch('sys.exit') as mock_exit, \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock arguments
            args = Mock()
            args.version = False
            args.log_level = "WARNING"
            args.log_file = None
            args.mqtt_host = None
            args.transport = "stdio"
            args.auto_connect = False
            mock_parse.return_value = args
            
            logger = Mock()
            mock_logger.return_value = logger
            
            main()
            
            # Verify error handling
            logger.error.assert_called_with("Failed to start server", error="Startup failed")
            mock_exit.assert_called_once_with(1)
    
    def test_main_complex_scenario(self):
        """Test main with complex real-world scenario."""
        mock_config = Mock()
        mock_config.broker_host = 'production.mqtt.com'
        mock_config.broker_port = 8883
        
        with patch('mcmqtt.mcmqtt.parse_arguments') as mock_parse, \
             patch('mcmqtt.mcmqtt.setup_logging') as mock_setup_log, \
             patch('mcmqtt.mcmqtt.create_mqtt_config_from_args', return_value=mock_config), \
             patch('mcmqtt.mcmqtt.MCMQTTServer') as mock_server_class, \
             patch('mcmqtt.mcmqtt.get_version', return_value="1.5.0"), \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('structlog.get_logger') as mock_logger:
            
            # Mock complex production-like arguments
            args = Mock()
            args.version = False
            args.log_level = "INFO"
            args.log_file = "/var/log/mcmqtt.log"
            args.mqtt_host = 'production.mqtt.com'
            args.mqtt_port = 8883
            args.transport = "http"
            args.host = "0.0.0.0"
            args.port = 3000
            args.auto_connect = True
            mock_parse.return_value = args
            
            logger = Mock()
            mock_logger.return_value = logger
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            main()
            
            # Verify all components called correctly
            mock_setup_log.assert_called_once_with("INFO", "/var/log/mcmqtt.log")
            mock_server_class.assert_called_once_with(mock_config)
            mock_asyncio_run.assert_called_once()
            
            # Verify comprehensive logging
            logger.info.assert_any_call(
                "MQTT configuration from command line",
                broker="production.mqtt.com:8883"
            )
            logger.info.assert_any_call(
                "Starting mcmqtt FastMCP server",
                version="1.5.0",
                transport="http",
                auto_connect=True
            )