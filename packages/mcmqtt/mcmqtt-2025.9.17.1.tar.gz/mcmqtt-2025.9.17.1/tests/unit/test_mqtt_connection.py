"""Tests for MQTT connection management."""

import asyncio
import ssl
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from mcmqtt.mqtt.connection import MQTTConnectionManager
from mcmqtt.mqtt.types import MQTTConfig, MQTTConnectionState, MQTTQoS


@pytest.fixture
def mqtt_config():
    """Create test MQTT config."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="test-client",
        username="testuser",
        password="testpass",
        keepalive=60,
        qos=MQTTQoS.AT_LEAST_ONCE,
        clean_session=True,
        reconnect_interval=5,
        max_reconnect_attempts=3
    )


@pytest.fixture
def tls_config():
    """Create test MQTT config with TLS."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=8883,
        client_id="test-client",
        use_tls=True,
        ca_cert_path="/path/to/ca.pem",
        cert_path="/path/to/cert.pem",
        key_path="/path/to/key.pem"
    )


@pytest.fixture
def will_config():
    """Create test MQTT config with last will."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="test-client",
        will_topic="status/client",
        will_payload="offline",
        will_qos=MQTTQoS.AT_LEAST_ONCE,
        will_retain=True
    )


class TestMQTTConnectionManager:
    """Test MQTT connection manager."""

    def test_init(self, mqtt_config):
        """Test connection manager initialization."""
        manager = MQTTConnectionManager(mqtt_config)
        
        assert manager.config == mqtt_config
        assert manager.state == MQTTConnectionState.DISCONNECTED
        assert not manager.is_connected
        assert manager._client is None
        assert manager._reconnect_task is None
        assert manager._reconnect_attempts == 0

    def test_properties(self, mqtt_config):
        """Test connection manager properties."""
        manager = MQTTConnectionManager(mqtt_config)
        
        # Test state property
        assert manager.state == MQTTConnectionState.DISCONNECTED
        
        # Test is_connected property
        assert not manager.is_connected
        manager._state = MQTTConnectionState.CONNECTED
        assert manager.is_connected
        
        # Test connection_info property
        info = manager.connection_info
        assert info.state == MQTTConnectionState.CONNECTED
        assert info.broker_host == "localhost"
        assert info.broker_port == 1883
        assert info.client_id == "test-client"

    def test_set_callbacks(self, mqtt_config):
        """Test setting callbacks."""
        manager = MQTTConnectionManager(mqtt_config)
        
        on_connect = AsyncMock()
        on_disconnect = AsyncMock()
        on_message = AsyncMock()
        on_error = AsyncMock()
        
        manager.set_callbacks(
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            on_message=on_message,
            on_error=on_error
        )
        
        assert manager._on_connect == on_connect
        assert manager._on_disconnect == on_disconnect
        assert manager._on_message == on_message
        assert manager._on_error == on_error

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_success(self, mock_client_class, mqtt_config):
        """Test successful connection."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.return_value = 0  # MQTT_ERR_SUCCESS
        
        manager = MQTTConnectionManager(mqtt_config)
        
        # Simulate the state change that would happen in the actual connection process
        def simulate_connect(*args):
            # Simulate the paho callback that sets state to CONNECTED
            manager._state = MQTTConnectionState.CONNECTED
            return 0
            
        mock_client.connect.side_effect = simulate_connect
        
        result = await manager.connect()
        
        assert result is True
        assert manager.state == MQTTConnectionState.CONNECTED
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        mock_client.loop_start.assert_called_once()

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_already_connected(self, mock_client_class, mqtt_config):
        """Test connect when already connected."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._state = MQTTConnectionState.CONNECTED
        
        result = await manager.connect()
        
        assert result is True
        mock_client_class.assert_not_called()

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_with_auth(self, mock_client_class, mqtt_config):
        """Test connection with authentication."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.return_value = 0
        
        manager = MQTTConnectionManager(mqtt_config)
        
        def simulate_connect(*args):
            manager._state = MQTTConnectionState.CONNECTED
            
        mock_client.connect.side_effect = simulate_connect
        
        await manager.connect()
        
        mock_client.username_pw_set.assert_called_once_with("testuser", "testpass")

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    @patch('ssl.create_default_context')
    async def test_connect_with_tls(self, mock_ssl_context, mock_client_class, tls_config):
        """Test connection with TLS."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.return_value = 0
        
        mock_context = MagicMock()
        mock_ssl_context.return_value = mock_context
        
        manager = MQTTConnectionManager(tls_config)
        
        def simulate_connect(*args):
            manager._state = MQTTConnectionState.CONNECTED
            
        mock_client.connect.side_effect = simulate_connect
        
        await manager.connect()
        
        mock_ssl_context.assert_called_once()
        mock_context.load_verify_locations.assert_called_once_with("/path/to/ca.pem")
        mock_context.load_cert_chain.assert_called_once_with("/path/to/cert.pem", "/path/to/key.pem")
        mock_client.tls_set_context.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_with_will(self, mock_client_class, will_config):
        """Test connection with last will and testament."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.return_value = 0
        
        manager = MQTTConnectionManager(will_config)
        
        def simulate_connect(*args):
            manager._state = MQTTConnectionState.CONNECTED
            
        mock_client.connect.side_effect = simulate_connect
        
        await manager.connect()
        
        mock_client.will_set.assert_called_once_with(
            "status/client", "offline", qos=1, retain=True
        )

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_failure(self, mock_client_class, mqtt_config):
        """Test connection failure."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.return_value = 1  # Connection failed
        
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.connect()
        
        assert result is False
        assert manager.state == MQTTConnectionState.ERROR
        mock_client.loop_stop.assert_called_once()

    @pytest.mark.asyncio
    @patch('paho.mqtt.client.Client')
    async def test_connect_exception(self, mock_client_class, mqtt_config):
        """Test connection with exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection error")
        
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.connect()
        
        assert result is False
        assert manager.state == MQTTConnectionState.ERROR

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self, mqtt_config):
        """Test disconnect when not connected."""
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.disconnect()
        
        assert result is True

    @pytest.mark.asyncio
    async def test_disconnect_success(self, mqtt_config):
        """Test successful disconnect."""
        manager = MQTTConnectionManager(mqtt_config)
        mock_client = MagicMock()
        manager._client = mock_client
        manager._state = MQTTConnectionState.CONNECTED
        
        result = await manager.disconnect()
        
        assert result is True
        assert manager.state == MQTTConnectionState.DISCONNECTED
        mock_client.disconnect.assert_called_once()
        mock_client.loop_stop.assert_called_once()
        assert manager._client is None  # Client is set to None after disconnect

    @pytest.mark.asyncio
    async def test_disconnect_with_reconnect_task(self, mqtt_config):
        """Test disconnect with active reconnect task."""
        manager = MQTTConnectionManager(mqtt_config)
        mock_client = MagicMock()
        mock_reconnect_task = MagicMock()
        manager._client = mock_client
        manager._reconnect_task = mock_reconnect_task
        manager._state = MQTTConnectionState.CONNECTED
        
        result = await manager.disconnect()
        
        assert result is True
        mock_reconnect_task.cancel.assert_called_once()
        assert manager._reconnect_task is None  # Task is set to None after cancel

    @pytest.mark.asyncio
    async def test_disconnect_exception(self, mqtt_config):
        """Test disconnect with exception."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._client.disconnect.side_effect = Exception("Disconnect error")
        manager._state = MQTTConnectionState.CONNECTED
        
        result = await manager.disconnect()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_success(self, mqtt_config):
        """Test successful publish."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        
        mock_result = MagicMock()
        mock_result.rc = 0  # MQTT_ERR_SUCCESS
        manager._client.publish.return_value = mock_result
        
        result = await manager.publish("test/topic", "test message")
        
        assert result is True
        manager._client.publish.assert_called_once_with(
            "test/topic", "test message", qos=1, retain=False
        )

    @pytest.mark.asyncio
    async def test_publish_not_connected(self, mqtt_config):
        """Test publish when not connected."""
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.publish("test/topic", "test message")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_with_qos(self, mqtt_config):
        """Test publish with specific QoS."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        
        mock_result = MagicMock()
        mock_result.rc = 0
        manager._client.publish.return_value = mock_result
        
        result = await manager.publish("test/topic", "test message", 
                                       qos=MQTTQoS.EXACTLY_ONCE, retain=True)
        
        assert result is True
        manager._client.publish.assert_called_once_with(
            "test/topic", "test message", qos=2, retain=True
        )

    @pytest.mark.asyncio
    async def test_publish_failure(self, mqtt_config):
        """Test publish failure."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        
        mock_result = MagicMock()
        mock_result.rc = 1  # Error
        manager._client.publish.return_value = mock_result
        
        result = await manager.publish("test/topic", "test message")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_exception(self, mqtt_config):
        """Test publish with exception."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.publish.side_effect = Exception("Publish error")
        
        result = await manager.publish("test/topic", "test message")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_subscribe_success(self, mqtt_config):
        """Test successful subscribe."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.subscribe.return_value = (0, 1)  # (result, mid)
        
        result = await manager.subscribe("test/topic")
        
        assert result is True
        manager._client.subscribe.assert_called_once_with("test/topic", qos=1)

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self, mqtt_config):
        """Test subscribe when not connected."""
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.subscribe("test/topic")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_subscribe_with_qos(self, mqtt_config):
        """Test subscribe with specific QoS."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.subscribe.return_value = (0, 1)
        
        result = await manager.subscribe("test/topic", MQTTQoS.EXACTLY_ONCE)
        
        assert result is True
        manager._client.subscribe.assert_called_once_with("test/topic", qos=2)

    @pytest.mark.asyncio
    async def test_subscribe_failure(self, mqtt_config):
        """Test subscribe failure."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.subscribe.return_value = (1, 1)  # Error
        
        result = await manager.subscribe("test/topic")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_subscribe_exception(self, mqtt_config):
        """Test subscribe with exception."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.subscribe.side_effect = Exception("Subscribe error")
        
        result = await manager.subscribe("test/topic")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, mqtt_config):
        """Test successful unsubscribe."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.unsubscribe.return_value = (0, 1)
        
        result = await manager.unsubscribe("test/topic")
        
        assert result is True
        manager._client.unsubscribe.assert_called_once_with("test/topic")

    @pytest.mark.asyncio
    async def test_unsubscribe_not_connected(self, mqtt_config):
        """Test unsubscribe when not connected."""
        manager = MQTTConnectionManager(mqtt_config)
        
        result = await manager.unsubscribe("test/topic")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe_failure(self, mqtt_config):
        """Test unsubscribe failure."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.unsubscribe.return_value = (1, 1)  # Error
        
        result = await manager.unsubscribe("test/topic")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe_exception(self, mqtt_config):
        """Test unsubscribe with exception."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._client = MagicMock()
        manager._state = MQTTConnectionState.CONNECTED
        manager._client.unsubscribe.side_effect = Exception("Unsubscribe error")
        
        result = await manager.unsubscribe("test/topic")
        
        assert result is False

    def test_set_state(self, mqtt_config):
        """Test state setting."""
        manager = MQTTConnectionManager(mqtt_config)
        
        manager._set_state(MQTTConnectionState.CONNECTING)
        assert manager.state == MQTTConnectionState.CONNECTING
        
        manager._set_state(MQTTConnectionState.CONNECTED)
        assert manager.state == MQTTConnectionState.CONNECTED
        assert manager._connected_at is not None
        
        manager._set_state(MQTTConnectionState.DISCONNECTED)
        assert manager.state == MQTTConnectionState.DISCONNECTED
        assert manager._connected_at is None

    def test_set_state_with_error(self, mqtt_config):
        """Test state setting with error message."""
        manager = MQTTConnectionManager(mqtt_config)
        
        manager._set_state(MQTTConnectionState.ERROR, "Test error")
        assert manager.state == MQTTConnectionState.ERROR
        assert manager.connection_info.error_message == "Test error"

    @pytest.mark.asyncio
    async def test_paho_connect_callback_success(self, mqtt_config):
        """Test paho connect callback success."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._loop = asyncio.get_event_loop()
        
        on_connect = AsyncMock()
        manager.set_callbacks(on_connect=on_connect)
        
        manager._on_paho_connect(None, None, None, 0)  # rc=0 = success
        
        assert manager.state == MQTTConnectionState.CONNECTED
        await asyncio.sleep(0.01)  # Let callback task run
        on_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_paho_connect_callback_failure(self, mqtt_config):
        """Test paho connect callback failure."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._loop = asyncio.get_event_loop()
        
        on_error = AsyncMock()
        manager.set_callbacks(on_error=on_error)
        
        manager._on_paho_connect(None, None, None, 1)  # rc=1 = failure
        
        assert manager.state == MQTTConnectionState.ERROR
        await asyncio.sleep(0.01)  # Let callback task run
        on_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_paho_disconnect_callback_clean(self, mqtt_config):
        """Test paho disconnect callback (clean)."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._loop = asyncio.get_event_loop()
        
        on_disconnect = AsyncMock()
        manager.set_callbacks(on_disconnect=on_disconnect)
        
        manager._on_paho_disconnect(None, None, 0)  # rc=0 = clean disconnect
        
        assert manager.state == MQTTConnectionState.DISCONNECTED
        await asyncio.sleep(0.01)  # Let callback task run
        on_disconnect.assert_called_once_with(0)

    @pytest.mark.asyncio
    @patch('asyncio.create_task')
    async def test_paho_disconnect_callback_unexpected(self, mock_create_task, mqtt_config):
        """Test paho disconnect callback (unexpected)."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._loop = asyncio.get_event_loop()
        
        on_disconnect = AsyncMock()
        manager.set_callbacks(on_disconnect=on_disconnect)
        
        manager._on_paho_disconnect(None, None, 1)  # rc=1 = unexpected disconnect
        
        assert manager.state == MQTTConnectionState.ERROR
        # Should start reconnect
        mock_create_task.assert_called()

    @pytest.mark.asyncio
    async def test_paho_message_callback(self, mqtt_config):
        """Test paho message callback."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._loop = asyncio.get_event_loop()
        
        on_message = AsyncMock()
        manager.set_callbacks(on_message=on_message)
        
        mock_msg = MagicMock()
        mock_msg.topic = "test/topic"
        mock_msg.payload = b"test payload"
        mock_msg.qos = 1
        mock_msg.retain = False
        
        manager._on_paho_message(None, None, mock_msg)
        
        await asyncio.sleep(0.01)  # Let callback task run
        on_message.assert_called_once_with("test/topic", b"test payload", 1, False)

    def test_paho_log_callback(self, mqtt_config):
        """Test paho log callback."""
        manager = MQTTConnectionManager(mqtt_config)
        
        with patch('mcmqtt.mqtt.connection.logger') as mock_logger:
            manager._on_paho_log(None, None, 16, "Test log message")
            mock_logger.debug.assert_called_once_with("MQTT Log [16]: Test log message")

    @pytest.mark.asyncio
    @patch('asyncio.create_task')
    async def test_start_reconnect(self, mock_create_task, mqtt_config):
        """Test starting reconnection."""
        manager = MQTTConnectionManager(mqtt_config)
        
        manager._start_reconnect()
        
        mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    @patch('asyncio.create_task')
    async def test_start_reconnect_max_attempts_reached(self, mock_create_task, mqtt_config):
        """Test reconnect not started when max attempts reached."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._reconnect_attempts = 3  # equals max_reconnect_attempts
        
        manager._start_reconnect()
        
        mock_create_task.assert_not_called()

    @pytest.mark.asyncio
    @patch('asyncio.create_task')
    async def test_start_reconnect_task_already_running(self, mock_create_task, mqtt_config):
        """Test reconnect not started when task already running."""
        manager = MQTTConnectionManager(mqtt_config)
        manager._reconnect_task = MagicMock()  # Already running
        
        manager._start_reconnect()
        
        mock_create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_reconnect_loop_success(self, mqtt_config):
        """Test successful reconnection loop."""
        manager = MQTTConnectionManager(mqtt_config)
        
        with patch.object(manager, 'connect', return_value=True) as mock_connect:
            await manager._reconnect_loop()
            
            mock_connect.assert_called_once()
            assert manager._reconnect_attempts == 1

    @pytest.mark.asyncio
    async def test_reconnect_loop_max_attempts(self, mqtt_config):
        """Test reconnection loop reaching max attempts."""
        manager = MQTTConnectionManager(mqtt_config)
        
        with patch.object(manager, 'connect', return_value=False) as mock_connect, \
             patch('asyncio.sleep') as mock_sleep:
            
            await manager._reconnect_loop()
            
            assert mock_connect.call_count == 3  # max_reconnect_attempts
            assert manager._reconnect_attempts == 3
            assert manager.state == MQTTConnectionState.ERROR
            assert mock_sleep.call_count == 3  # Called before each attempt


def test_import_all_dependencies():
    """Test that all required dependencies can be imported."""
    from mcmqtt.mqtt.connection import (
        asyncio, logging, ssl, datetime, 
        MQTTConnectionManager, mqtt, PahoMessage,
        MQTTConfig, MQTTConnectionState, MQTTConnectionInfo, MQTTQoS
    )
    
    # All imports should succeed
    assert asyncio is not None
    assert logging is not None
    assert ssl is not None
    assert datetime is not None
    assert MQTTConnectionManager is not None
    assert mqtt is not None
    assert PahoMessage is not None
    assert MQTTConfig is not None
    assert MQTTConnectionState is not None
    assert MQTTConnectionInfo is not None
    assert MQTTQoS is not None