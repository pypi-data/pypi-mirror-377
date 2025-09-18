"""Simple import and basic functionality tests for coverage."""

import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

def test_main_module_import():
    """Test that main module can be imported and basic functions work."""
    from mcmqtt.main import setup_logging, version_callback, app
    
    # Test logging setup
    setup_logging("INFO")
    setup_logging("DEBUG")
    
    # Test version callback (should exit)
    with pytest.raises(SystemExit):
        version_callback(True)
    
    # Test that app exists
    assert app is not None

def test_mcmqtt_module_import():
    """Test that mcmqtt module can be imported and basic functions work."""
    from mcmqtt.mcmqtt import setup_logging, get_mqtt_config_from_env, parse_args
    
    # Test logging setup
    setup_logging()
    setup_logging("ERROR")
    
    with tempfile.NamedTemporaryFile() as f:
        setup_logging("INFO", f.name)
    
    # Test config from environment
    config = get_mqtt_config_from_env()
    assert config.broker_host == "localhost"
    assert config.broker_port == 1883
    
    # Test with environment variables
    with patch.dict(os.environ, {"MQTT_BROKER_HOST": "test.com", "MQTT_BROKER_PORT": "8883"}):
        config = get_mqtt_config_from_env()
        assert config.broker_host == "test.com"
        assert config.broker_port == 8883
    
    # Test argument parsing
    with patch('sys.argv', ['mcmqtt']):
        args = parse_args()
        assert args.transport == "stdio"

def test_broker_manager_import():
    """Test that broker manager can be imported and basic functions work."""
    from mcmqtt.broker.manager import BrokerConfig, BrokerInfo, BrokerManager, AMQTT_AVAILABLE
    
    # Test config creation
    config = BrokerConfig()
    assert config.port == 1883
    assert config.host == "127.0.0.1"
    
    config = BrokerConfig(port=8883, name="test")
    assert config.port == 8883
    assert config.name == "test"
    
    # Test broker info
    from datetime import datetime
    info = BrokerInfo(
        config=config,
        broker_id="test-123",
        started_at=datetime.now()
    )
    assert info.broker_id == "test-123"
    assert info.status == "running"
    assert info.url.startswith("mqtt://")
    
    # Test manager creation
    manager = BrokerManager()
    assert manager.is_available() == AMQTT_AVAILABLE
    
    # Test utility methods
    port = manager._find_free_port(start_port=19000)
    assert isinstance(port, int)
    assert port >= 19000

def test_server_imports():
    """Test that server modules import correctly."""
    from mcmqtt.mcp.server import MCMQTTServer
    from mcmqtt.mqtt.types import MQTTConfig
    
    # Create basic config
    config = MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="test"
    )
    
    # Create server instance
    server = MCMQTTServer(config)
    assert server is not None
    assert server.mqtt_config == config

def test_types_and_enums():
    """Test types and enums for coverage."""
    from mcmqtt.mqtt.types import (
        MQTTConfig, MQTTQoS, MQTTConnectionState, 
        MQTTMessage, MQTTStats, MQTTConnectionInfo
    )
    from datetime import datetime
    
    # Test QoS enum
    assert MQTTQoS.AT_MOST_ONCE.value == 0
    assert MQTTQoS.AT_LEAST_ONCE.value == 1
    assert MQTTQoS.EXACTLY_ONCE.value == 2
    
    # Test connection states
    assert MQTTConnectionState.DISCONNECTED.value == "disconnected"
    assert MQTTConnectionState.CONNECTING.value == "connecting"
    assert MQTTConnectionState.CONNECTED.value == "connected"
    
    # Test message creation
    msg = MQTTMessage("test/topic", "payload", MQTTQoS.AT_LEAST_ONCE)
    assert msg.topic == "test/topic"
    assert msg.payload_str == "payload"
    assert msg.qos == MQTTQoS.AT_LEAST_ONCE
    
    # Test stats
    stats = MQTTStats()
    assert stats.messages_sent == 0
    assert stats.messages_received == 0
    
    # Test connection info
    info = MQTTConnectionInfo(
        state=MQTTConnectionState.CONNECTED,
        broker_host="localhost",
        broker_port=1883,
        client_id="test"
    )
    assert info.state == MQTTConnectionState.CONNECTED
    assert info.broker_host == "localhost"

def test_middleware_imports():
    """Test middleware imports for coverage."""
    from mcmqtt.middleware.broker_middleware import MQTTBrokerMiddleware
    
    # Create middleware instance
    middleware = MQTTBrokerMiddleware()
    assert middleware is not None
    assert middleware._brokers == {}

def test_client_basic_functionality():
    """Test basic client functionality for coverage."""
    from mcmqtt.mqtt.client import MQTTClient
    from mcmqtt.mqtt.types import MQTTConfig
    
    config = MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="test-client"
    )
    
    client = MQTTClient(config)
    assert client.config == config
    assert not client.is_connected
    
    # Test stats property
    stats = client.stats
    assert stats.messages_sent == 0

def test_publisher_import():
    """Test publisher import for coverage."""
    from mcmqtt.mqtt.publisher import MQTTPublisher
    from mcmqtt.mqtt.client import MQTTClient
    from mcmqtt.mqtt.types import MQTTConfig
    
    config = MQTTConfig(broker_host="localhost", broker_port=1883, client_id="test")
    client = MQTTClient(config)
    publisher = MQTTPublisher(client)
    
    assert publisher._client == client

def test_subscriber_import():
    """Test subscriber import for coverage."""
    from mcmqtt.mqtt.subscriber import MQTTSubscriber
    from mcmqtt.mqtt.client import MQTTClient
    from mcmqtt.mqtt.types import MQTTConfig
    
    config = MQTTConfig(broker_host="localhost", broker_port=1883, client_id="test")
    client = MQTTClient(config)
    subscriber = MQTTSubscriber(client)
    
    assert subscriber._client == client
    assert subscriber._subscriptions == {}

async def test_async_methods():
    """Test async methods that require event loop."""
    from mcmqtt.mqtt.client import MQTTClient
    from mcmqtt.mqtt.types import MQTTConfig
    from mcmqtt.mcp.server import MCMQTTServer
    
    config = MQTTConfig(broker_host="localhost", broker_port=1883, client_id="test")
    
    # Test client async initialization
    client = MQTTClient(config)
    # Just test that methods exist and can be called
    assert hasattr(client, 'connect')
    assert hasattr(client, 'disconnect')
    assert hasattr(client, 'publish')
    
    # Test server async methods
    server = MCMQTTServer(config)
    assert hasattr(server, 'connect_to_broker')
    assert hasattr(server, 'disconnect_from_broker')

def test_configuration_edge_cases():
    """Test configuration edge cases for coverage."""
    from mcmqtt.mqtt.types import MQTTConfig, MQTTQoS
    
    # Test minimal config
    config = MQTTConfig(broker_host="test.com", broker_port=1883, client_id="test")
    assert config.username is None
    assert config.password is None
    assert config.use_tls is False
    
    # Test full config
    config = MQTTConfig(
        broker_host="secure.test.com",
        broker_port=8883,
        client_id="secure-client",
        username="user",
        password="pass",
        use_tls=True,
        ca_cert_path="/path/ca.crt",
        cert_path="/path/client.crt",
        key_path="/path/client.key",
        qos=MQTTQoS.EXACTLY_ONCE,
        clean_session=False,
        keepalive=120,
        reconnect_interval=10,
        max_reconnect_attempts=5,
        will_topic="client/will",
        will_payload="offline",
        will_qos=MQTTQoS.AT_LEAST_ONCE,
        will_retain=True
    )
    
    assert config.use_tls is True
    assert config.username == "user"
    assert config.qos == MQTTQoS.EXACTLY_ONCE
    assert config.will_topic == "client/will"

def test_error_handling_coverage():
    """Test error handling paths for coverage."""
    from mcmqtt.broker.manager import BrokerManager
    
    manager = BrokerManager()
    
    # Test port finding with invalid range (should raise error)
    with pytest.raises(RuntimeError, match="No free ports available"):
        # Use a very limited range to force error
        manager._find_free_port(start_port=65534)

def test_package_imports():
    """Test package-level imports for coverage."""
    import mcmqtt
    import mcmqtt.mqtt
    import mcmqtt.mcp
    import mcmqtt.broker
    import mcmqtt.middleware
    
    # These should not raise import errors
    assert mcmqtt is not None
    assert mcmqtt.mqtt is not None
    assert mcmqtt.mcp is not None
    assert mcmqtt.broker is not None
    assert mcmqtt.middleware is not None