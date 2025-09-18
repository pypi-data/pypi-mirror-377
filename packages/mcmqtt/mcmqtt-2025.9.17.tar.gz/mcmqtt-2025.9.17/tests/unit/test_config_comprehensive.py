"""
Comprehensive unit tests for configuration modules.

Tests environment variable and command-line argument configuration handling.
"""

import pytest
import os
from unittest.mock import patch, Mock
from argparse import Namespace

from mcmqtt.config.env_config import create_mqtt_config_from_env, create_mqtt_config_from_args
from mcmqtt.mqtt.types import MQTTConfig, MQTTQoS


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
    
    def test_create_mqtt_config_boolean_variations(self):
        """Test config creation with boolean variations."""
        self.setUp()
        
        # Test TLS true variations
        for tls_value in ['true', 'True', 'TRUE', '1']:
            os.environ['MQTT_BROKER_HOST'] = 'localhost'
            os.environ['MQTT_USE_TLS'] = tls_value
            
            config = create_mqtt_config_from_env()
            assert config.use_tls is True
            
            os.environ.pop('MQTT_USE_TLS', None)
        
        # Test TLS false variations
        for tls_value in ['false', 'False', 'FALSE', '0', 'no']:
            os.environ['MQTT_BROKER_HOST'] = 'localhost'
            os.environ['MQTT_USE_TLS'] = tls_value
            
            config = create_mqtt_config_from_env()
            assert config.use_tls is False
            
            os.environ.pop('MQTT_USE_TLS', None)
    
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
    
    def test_create_mqtt_config_invalid_keepalive(self):
        """Test config creation with invalid keepalive."""
        self.setUp()
        os.environ['MQTT_BROKER_HOST'] = 'localhost'
        os.environ['MQTT_KEEPALIVE'] = 'invalid'
        
        with patch('logging.error') as mock_error:
            config = create_mqtt_config_from_env()
            assert config is None
            mock_error.assert_called_once()
    
    def test_create_mqtt_config_default_client_id_varies(self):
        """Test that default client ID includes PID."""
        self.setUp()
        os.environ['MQTT_BROKER_HOST'] = 'localhost'
        
        config = create_mqtt_config_from_env()
        
        assert config is not None
        assert config.client_id.startswith('mcmqtt-')
        assert str(os.getpid()) in config.client_id


class TestCreateMqttConfigFromArgs:
    """Test MQTT configuration from command-line arguments."""
    
    def test_create_mqtt_config_no_host(self):
        """Test config creation with no broker host."""
        args = Namespace(mqtt_host=None)
        
        config = create_mqtt_config_from_args(args)
        assert config is None
    
    def test_create_mqtt_config_minimal(self):
        """Test config creation with minimal arguments."""
        args = Namespace(
            mqtt_host='localhost',
            mqtt_port=1883,
            mqtt_client_id=None,
            mqtt_username=None,
            mqtt_password=None
        )
        
        config = create_mqtt_config_from_args(args)
        
        assert config is not None
        assert config.broker_host == 'localhost'
        assert config.broker_port == 1883
        assert config.client_id.startswith('mcmqtt-')
        assert config.username is None
        assert config.password is None
    
    def test_create_mqtt_config_complete(self):
        """Test config creation with all arguments."""
        args = Namespace(
            mqtt_host='mqtt.example.com',
            mqtt_port=8883,
            mqtt_client_id='test-client',
            mqtt_username='testuser',
            mqtt_password='testpass'
        )
        
        config = create_mqtt_config_from_args(args)
        
        assert config is not None
        assert config.broker_host == 'mqtt.example.com'
        assert config.broker_port == 8883
        assert config.client_id == 'test-client'
        assert config.username == 'testuser'
        assert config.password == 'testpass'
    
    def test_create_mqtt_config_default_client_id(self):
        """Test config creation with default client ID generation."""
        args = Namespace(
            mqtt_host='localhost',
            mqtt_port=1883,
            mqtt_client_id=None,
            mqtt_username=None,
            mqtt_password=None
        )
        
        config = create_mqtt_config_from_args(args)
        
        assert config is not None
        assert config.client_id.startswith('mcmqtt-')
        assert str(os.getpid()) in config.client_id
    
    def test_create_mqtt_config_exception_handling(self):
        """Test config creation with exception handling."""
        # Mock args object that raises exception when accessed
        args = Mock()
        args.mqtt_host = 'localhost'
        args.mqtt_port = Mock(side_effect=Exception("Port error"))
        
        with patch('logging.error') as mock_error:
            config = create_mqtt_config_from_args(args)
            assert config is None
            mock_error.assert_called_once()
    
    def test_create_mqtt_config_custom_port(self):
        """Test config creation with custom port."""
        args = Namespace(
            mqtt_host='broker.local',
            mqtt_port=9883,
            mqtt_client_id='custom-client',
            mqtt_username='user123',
            mqtt_password='pass456'
        )
        
        config = create_mqtt_config_from_args(args)
        
        assert config is not None
        assert config.broker_host == 'broker.local'
        assert config.broker_port == 9883
        assert config.client_id == 'custom-client'
        assert config.username == 'user123'
        assert config.password == 'pass456'