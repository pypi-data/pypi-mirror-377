"""
Comprehensive unit tests for CLI modules.

Tests argument parsing, version management, and command-line interface.
"""

import pytest
from unittest.mock import patch, Mock
from argparse import Namespace

from mcmqtt.cli.version import get_version
from mcmqtt.cli.parser import create_argument_parser, parse_arguments


class TestGetVersion:
    """Test version retrieval functionality."""
    
    def test_get_version_success(self):
        """Test successful version retrieval."""
        with patch('importlib.metadata.version', return_value="1.2.3"):
            version = get_version()
            assert version == "1.2.3"
    
    def test_get_version_import_error(self):
        """Test version retrieval with import error fallback."""
        with patch('importlib.metadata.version', side_effect=ImportError("No module")):
            version = get_version()
            assert version == "0.1.0"
    
    def test_get_version_exception(self):
        """Test version retrieval with general exception fallback."""
        with patch('importlib.metadata.version', side_effect=Exception("Unknown error")):
            version = get_version()
            assert version == "0.1.0"


class TestArgumentParser:
    """Test argument parser functionality."""
    
    def test_create_argument_parser(self):
        """Test argument parser creation."""
        parser = create_argument_parser()
        assert parser is not None
        assert parser.description == "mcmqtt - FastMCP MQTT Server"
    
    def test_parse_arguments_default(self):
        """Test parsing with default arguments."""
        args = parse_arguments([])
        
        # Transport defaults
        assert args.transport == "stdio"
        assert args.host == "0.0.0.0"
        assert args.port == 3000
        
        # MQTT defaults
        assert args.mqtt_host is None
        assert args.mqtt_port == 1883
        assert args.mqtt_client_id is None
        assert args.mqtt_username is None
        assert args.mqtt_password is None
        assert args.auto_connect is False
        
        # Logging defaults
        assert args.log_level == "WARNING"
        assert args.log_file is None
        
        # Version default
        assert args.version is False
    
    def test_parse_arguments_transport_stdio(self):
        """Test parsing STDIO transport arguments."""
        args = parse_arguments(['--transport', 'stdio'])
        assert args.transport == "stdio"
    
    def test_parse_arguments_transport_http(self):
        """Test parsing HTTP transport arguments."""
        args = parse_arguments(['--transport', 'http', '--host', '127.0.0.1', '--port', '8080'])
        assert args.transport == "http"
        assert args.host == "127.0.0.1"
        assert args.port == 8080
    
    def test_parse_arguments_mqtt_config(self):
        """Test parsing MQTT configuration arguments."""
        args = parse_arguments([
            '--mqtt-host', 'mqtt.example.com',
            '--mqtt-port', '8883',
            '--mqtt-client-id', 'test-client',
            '--mqtt-username', 'testuser',
            '--mqtt-password', 'testpass',
            '--auto-connect'
        ])
        
        assert args.mqtt_host == 'mqtt.example.com'
        assert args.mqtt_port == 8883
        assert args.mqtt_client_id == 'test-client'
        assert args.mqtt_username == 'testuser'
        assert args.mqtt_password == 'testpass'
        assert args.auto_connect is True
    
    def test_parse_arguments_logging_config(self):
        """Test parsing logging configuration arguments."""
        args = parse_arguments(['--log-level', 'DEBUG', '--log-file', '/tmp/test.log'])
        
        assert args.log_level == 'DEBUG'
        assert args.log_file == '/tmp/test.log'
    
    def test_parse_arguments_version_flag(self):
        """Test parsing version flag."""
        args = parse_arguments(['--version'])
        assert args.version is True
    
    def test_parse_arguments_short_flags(self):
        """Test parsing short flag arguments."""
        args = parse_arguments(['-t', 'http', '-p', '9000'])
        
        assert args.transport == 'http'
        assert args.port == 9000
    
    def test_parse_arguments_invalid_transport(self):
        """Test parsing with invalid transport."""
        with pytest.raises(SystemExit):
            parse_arguments(['--transport', 'invalid'])
    
    def test_parse_arguments_invalid_log_level(self):
        """Test parsing with invalid log level."""
        with pytest.raises(SystemExit):
            parse_arguments(['--log-level', 'INVALID'])
    
    def test_parse_arguments_invalid_port(self):
        """Test parsing with invalid port."""
        with pytest.raises(SystemExit):
            parse_arguments(['--port', 'invalid'])
    
    def test_parse_arguments_help(self):
        """Test help argument."""
        with pytest.raises(SystemExit):
            parse_arguments(['--help'])
    
    def test_parse_arguments_complex_combination(self):
        """Test parsing complex argument combination."""
        args = parse_arguments([
            '--transport', 'http',
            '--host', '192.168.1.100',
            '--port', '4000',
            '--mqtt-host', 'broker.local',
            '--mqtt-port', '8883',
            '--mqtt-client-id', 'production-client',
            '--mqtt-username', 'prod_user',
            '--mqtt-password', 'secret123',
            '--auto-connect',
            '--log-level', 'INFO',
            '--log-file', '/var/log/mcmqtt.log'
        ])
        
        # Verify all settings
        assert args.transport == 'http'
        assert args.host == '192.168.1.100'
        assert args.port == 4000
        assert args.mqtt_host == 'broker.local'
        assert args.mqtt_port == 8883
        assert args.mqtt_client_id == 'production-client'
        assert args.mqtt_username == 'prod_user'
        assert args.mqtt_password == 'secret123'
        assert args.auto_connect is True
        assert args.log_level == 'INFO'
        assert args.log_file == '/var/log/mcmqtt.log'
        assert args.version is False