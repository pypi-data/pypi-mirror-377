"""Comprehensive unit tests for MQTT Client functionality."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from mcmqtt.mqtt.client import MQTTClient
from mcmqtt.mqtt.connection import MQTTConnectionManager
from mcmqtt.mqtt.types import MQTTConfig, MQTTMessage, MQTTQoS, MQTTStats, MQTTConnectionState


class TestMQTTClientComprehensive:
    """Comprehensive test cases for MQTTClient class."""

    @pytest.fixture
    def mqtt_config(self):
        """Create a test MQTT configuration."""
        return MQTTConfig(
            broker_host="localhost",
            broker_port=1883,
            client_id="test-client",
            qos=MQTTQoS.AT_LEAST_ONCE
        )

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        manager = MagicMock(spec=MQTTConnectionManager)
        manager.is_connected = False
        manager._connected_at = None
        manager.connection_info = MagicMock()
        
        # Mock async methods
        manager.connect = AsyncMock(return_value=True)
        manager.disconnect = AsyncMock(return_value=True)
        manager.publish = AsyncMock(return_value=True)
        manager.subscribe = AsyncMock(return_value=True)
        manager.unsubscribe = AsyncMock(return_value=True)
        manager.set_callbacks = MagicMock()
        
        return manager

    @pytest.fixture
    def client(self, mqtt_config, mock_connection_manager):
        """Create a client instance with mocked connection."""
        with patch('mcmqtt.mqtt.client.MQTTConnectionManager', return_value=mock_connection_manager):
            client = MQTTClient(mqtt_config)
            client._connection_manager = mock_connection_manager
            return client

    def test_client_initialization(self, mqtt_config, mock_connection_manager):
        """Test client initialization with proper setup."""
        with patch('mcmqtt.mqtt.client.MQTTConnectionManager', return_value=mock_connection_manager):
            client = MQTTClient(mqtt_config)
            
            assert client.config == mqtt_config
            assert client._connection_manager == mock_connection_manager
            assert isinstance(client._stats, MQTTStats)
            assert client._message_handlers == {}
            assert client._pattern_handlers == {}
            assert client._subscriptions == {}
            assert client._offline_queue == []
            assert client._max_offline_queue == 1000
            
            # Verify callbacks were set
            mock_connection_manager.set_callbacks.assert_called_once()

    def test_is_connected_property(self, client, mock_connection_manager):
        """Test is_connected property."""
        mock_connection_manager.is_connected = False
        assert client.is_connected is False
        
        mock_connection_manager.is_connected = True
        assert client.is_connected is True

    def test_connection_info_property(self, client, mock_connection_manager):
        """Test connection_info property."""
        mock_info = MagicMock()
        mock_connection_manager.connection_info = mock_info
        assert client.connection_info == mock_info

    def test_stats_property_without_connection(self, client, mock_connection_manager):
        """Test stats property when not connected."""
        mock_connection_manager.is_connected = False
        mock_connection_manager._connected_at = None
        
        stats = client.stats
        assert isinstance(stats, MQTTStats)
        assert stats.connection_uptime is None

    def test_stats_property_with_connection(self, client, mock_connection_manager):
        """Test stats property when connected."""
        mock_connection_manager.is_connected = True
        mock_connection_manager._connected_at = datetime.utcnow()
        
        stats = client.stats
        assert isinstance(stats, MQTTStats)
        assert stats.connection_uptime is not None
        assert stats.connection_uptime >= 0

    @pytest.mark.asyncio
    async def test_connect_success(self, client, mock_connection_manager):
        """Test successful connection."""
        mock_connection_manager.connect.return_value = True
        
        result = await client.connect()
        
        assert result is True
        mock_connection_manager.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, client, mock_connection_manager):
        """Test connection failure."""
        mock_connection_manager.connect.return_value = False
        
        result = await client.connect()
        
        assert result is False
        mock_connection_manager.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_success(self, client, mock_connection_manager):
        """Test successful disconnection."""
        mock_connection_manager.disconnect.return_value = True
        
        result = await client.disconnect()
        
        assert result is True
        mock_connection_manager.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_when_connected(self, client, mock_connection_manager):
        """Test publish when connected."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        result = await client.publish("test/topic", "test message")
        
        assert result is True
        mock_connection_manager.publish.assert_called_once()
        assert client._stats.messages_sent == 1
        assert client._stats.bytes_sent > 0
        assert client._stats.last_message_time is not None

    @pytest.mark.asyncio
    async def test_publish_dict_payload(self, client, mock_connection_manager):
        """Test publish with dictionary payload."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        test_dict = {"key": "value", "number": 42}
        result = await client.publish("test/topic", test_dict)
        
        assert result is True
        # Verify the payload was JSON encoded
        call_args = mock_connection_manager.publish.call_args[0]
        payload_bytes = call_args[1]
        assert isinstance(payload_bytes, bytes)
        assert json.loads(payload_bytes.decode()) == test_dict

    @pytest.mark.asyncio
    async def test_publish_bytes_payload(self, client, mock_connection_manager):
        """Test publish with bytes payload."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        test_bytes = b"binary data"
        result = await client.publish("test/topic", test_bytes)
        
        assert result is True
        call_args = mock_connection_manager.publish.call_args[0]
        payload_bytes = call_args[1]
        assert payload_bytes == test_bytes

    @pytest.mark.asyncio
    async def test_publish_when_offline_queue_not_full(self, client, mock_connection_manager):
        """Test publish when offline and queue not full."""
        mock_connection_manager.is_connected = False
        
        result = await client.publish("test/topic", "test message")
        
        assert result is False
        assert len(client._offline_queue) == 1
        assert client._offline_queue[0].topic == "test/topic"
        assert client._offline_queue[0].payload == "test message"

    @pytest.mark.asyncio
    async def test_publish_when_offline_queue_full(self, client, mock_connection_manager):
        """Test publish when offline and queue is full."""
        mock_connection_manager.is_connected = False
        client._max_offline_queue = 2
        
        # Fill the queue
        await client.publish("test/topic1", "message1")
        await client.publish("test/topic2", "message2")
        
        # This should be dropped
        result = await client.publish("test/topic3", "message3")
        
        assert result is False
        assert len(client._offline_queue) == 2

    @pytest.mark.asyncio
    async def test_publish_failure_when_connected(self, client, mock_connection_manager):
        """Test publish failure when connected."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = False
        
        result = await client.publish("test/topic", "test message")
        
        assert result is False
        assert client._stats.messages_sent == 0

    @pytest.mark.asyncio
    async def test_subscribe_with_default_qos(self, client, mock_connection_manager):
        """Test subscribe with default QoS."""
        mock_connection_manager.subscribe.return_value = True
        
        result = await client.subscribe("test/topic")
        
        assert result is True
        mock_connection_manager.subscribe.assert_called_once_with("test/topic", MQTTQoS.AT_LEAST_ONCE)
        assert "test/topic" in client._subscriptions
        assert client._subscriptions["test/topic"] == MQTTQoS.AT_LEAST_ONCE
        assert client._stats.topics_subscribed == 1

    @pytest.mark.asyncio
    async def test_subscribe_with_custom_qos(self, client, mock_connection_manager):
        """Test subscribe with custom QoS."""
        mock_connection_manager.subscribe.return_value = True
        
        result = await client.subscribe("test/topic", qos=MQTTQoS.EXACTLY_ONCE)
        
        assert result is True
        mock_connection_manager.subscribe.assert_called_once_with("test/topic", MQTTQoS.EXACTLY_ONCE)
        assert client._subscriptions["test/topic"] == MQTTQoS.EXACTLY_ONCE

    @pytest.mark.asyncio
    async def test_subscribe_with_handler(self, client, mock_connection_manager):
        """Test subscribe with message handler."""
        mock_connection_manager.subscribe.return_value = True
        
        def test_handler(message):
            pass
        
        result = await client.subscribe("test/topic", handler=test_handler)
        
        assert result is True
        assert "test/topic" in client._message_handlers
        assert test_handler in client._message_handlers["test/topic"]

    @pytest.mark.asyncio
    async def test_subscribe_failure(self, client, mock_connection_manager):
        """Test subscribe failure."""
        mock_connection_manager.subscribe.return_value = False
        
        result = await client.subscribe("test/topic")
        
        assert result is False
        assert "test/topic" not in client._subscriptions
        assert client._stats.topics_subscribed == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, client, mock_connection_manager):
        """Test successful unsubscribe."""
        # First subscribe
        client._subscriptions["test/topic"] = MQTTQoS.AT_LEAST_ONCE
        client._message_handlers["test/topic"] = [lambda x: None]
        client._stats.topics_subscribed = 1
        
        mock_connection_manager.unsubscribe.return_value = True
        
        result = await client.unsubscribe("test/topic")
        
        assert result is True
        assert "test/topic" not in client._subscriptions
        assert "test/topic" not in client._message_handlers
        assert client._stats.topics_subscribed == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_failure(self, client, mock_connection_manager):
        """Test unsubscribe failure."""
        client._subscriptions["test/topic"] = MQTTQoS.AT_LEAST_ONCE
        
        mock_connection_manager.unsubscribe.return_value = False
        
        result = await client.unsubscribe("test/topic")
        
        assert result is False
        assert "test/topic" in client._subscriptions

    def test_add_message_handler_new_topic(self, client):
        """Test adding message handler for new topic."""
        def test_handler(message):
            pass
        
        client.add_message_handler("test/topic", test_handler)
        
        assert "test/topic" in client._message_handlers
        assert test_handler in client._message_handlers["test/topic"]

    def test_add_message_handler_existing_topic(self, client):
        """Test adding message handler for existing topic."""
        def handler1(message):
            pass
        
        def handler2(message):
            pass
        
        client.add_message_handler("test/topic", handler1)
        client.add_message_handler("test/topic", handler2)
        
        assert len(client._message_handlers["test/topic"]) == 2
        assert handler1 in client._message_handlers["test/topic"]
        assert handler2 in client._message_handlers["test/topic"]

    def test_add_pattern_handler(self, client):
        """Test adding pattern handler."""
        def test_handler(message):
            pass
        
        client.add_pattern_handler("test/+/sensor", test_handler)
        
        assert "test/+/sensor" in client._pattern_handlers
        assert test_handler in client._pattern_handlers["test/+/sensor"]

    def test_remove_message_handler_success(self, client):
        """Test removing message handler successfully."""
        def test_handler(message):
            pass
        
        client.add_message_handler("test/topic", test_handler)
        client.remove_message_handler("test/topic", test_handler)
        
        assert "test/topic" not in client._message_handlers

    def test_remove_message_handler_nonexistent(self, client):
        """Test removing nonexistent message handler."""
        def test_handler(message):
            pass
        
        # Should not raise exception
        client.remove_message_handler("test/topic", test_handler)

    def test_remove_message_handler_wrong_handler(self, client):
        """Test removing wrong handler from topic."""
        def handler1(message):
            pass
        
        def handler2(message):
            pass
        
        client.add_message_handler("test/topic", handler1)
        client.remove_message_handler("test/topic", handler2)
        
        # Handler1 should still be there
        assert "test/topic" in client._message_handlers
        assert handler1 in client._message_handlers["test/topic"]

    @pytest.mark.asyncio
    async def test_publish_json(self, client, mock_connection_manager):
        """Test publish_json method."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        test_data = {"key": "value", "number": 42}
        result = await client.publish_json("test/topic", test_data)
        
        assert result is True
        mock_connection_manager.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_message_new_subscription(self, client, mock_connection_manager):
        """Test wait_for_message with new subscription."""
        mock_connection_manager.subscribe.return_value = True
        mock_connection_manager.unsubscribe.return_value = True
        
        # Simulate timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(client.wait_for_message("test/topic", timeout=0.1), timeout=0.2)
        
        # Verify subscribe and unsubscribe were called
        mock_connection_manager.subscribe.assert_called_once_with("test/topic")
        mock_connection_manager.unsubscribe.assert_called_once_with("test/topic")

    @pytest.mark.asyncio
    async def test_wait_for_message_existing_subscription(self, client, mock_connection_manager):
        """Test wait_for_message with existing subscription."""
        client._subscriptions["test/topic"] = MQTTQoS.AT_LEAST_ONCE
        
        # Simulate timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(client.wait_for_message("test/topic", timeout=0.1), timeout=0.2)
        
        # Should not unsubscribe from existing subscription
        mock_connection_manager.unsubscribe.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_response_pattern(self, client, mock_connection_manager):
        """Test request/response pattern."""
        mock_connection_manager.subscribe.return_value = True
        mock_connection_manager.publish.return_value = True
        mock_connection_manager.unsubscribe.return_value = True
        
        # Simulate timeout since we can't easily simulate actual response
        result = await client.request_response(
            "request/topic", "response/topic", "test request", timeout=0.1
        )
        
        assert result is None  # Timeout
        mock_connection_manager.subscribe.assert_called_with("response/topic")
        mock_connection_manager.publish.assert_called_once()
        mock_connection_manager.unsubscribe.assert_called_with("response/topic")

    def test_get_subscriptions(self, client):
        """Test get_subscriptions method."""
        client._subscriptions = {
            "topic1": MQTTQoS.AT_LEAST_ONCE,
            "topic2": MQTTQoS.EXACTLY_ONCE
        }
        
        subscriptions = client.get_subscriptions()
        
        assert subscriptions == client._subscriptions
        assert subscriptions is not client._subscriptions  # Should be a copy

    @pytest.mark.asyncio
    async def test_on_connect_callback(self, client, mock_connection_manager):
        """Test _on_connect callback functionality."""
        client._subscriptions = {
            "topic1": MQTTQoS.AT_LEAST_ONCE,
            "topic2": MQTTQoS.EXACTLY_ONCE
        }
        
        # Add some offline messages
        client._offline_queue = [
            MQTTMessage(topic="offline/topic", payload="message1"),
            MQTTMessage(topic="offline/topic", payload="message2")
        ]
        
        mock_connection_manager.subscribe.return_value = True
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        # Call the callback
        await client._on_connect()
        
        # Verify resubscription
        assert mock_connection_manager.subscribe.call_count == 2
        
        # Verify offline messages were processed
        assert mock_connection_manager.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_on_disconnect_callback_clean(self, client):
        """Test _on_disconnect callback for clean disconnection."""
        await client._on_disconnect(0)  # Clean disconnect
        # Should log info message

    @pytest.mark.asyncio
    async def test_on_disconnect_callback_unexpected(self, client):
        """Test _on_disconnect callback for unexpected disconnection."""
        await client._on_disconnect(1)  # Unexpected disconnect
        # Should log warning message

    @pytest.mark.asyncio
    async def test_on_message_callback_with_topic_handler(self, client):
        """Test _on_message callback with topic-specific handler."""
        handler_called = []
        
        def test_handler(message):
            handler_called.append(message)
        
        client._message_handlers["test/topic"] = [test_handler]
        
        await client._on_message("test/topic", b"test payload", 1, False)
        
        assert len(handler_called) == 1
        assert handler_called[0].topic == "test/topic"
        assert handler_called[0].payload == b"test payload"
        assert client._stats.messages_received == 1
        assert client._stats.bytes_received == len(b"test payload")

    @pytest.mark.asyncio
    async def test_on_message_callback_with_async_handler(self, client):
        """Test _on_message callback with async handler."""
        handler_called = []
        
        async def async_handler(message):
            handler_called.append(message)
        
        client._message_handlers["test/topic"] = [async_handler]
        
        await client._on_message("test/topic", b"test payload", 1, False)
        
        assert len(handler_called) == 1

    @pytest.mark.asyncio
    async def test_on_message_callback_with_pattern_handler(self, client):
        """Test _on_message callback with pattern handler."""
        handler_called = []
        
        def pattern_handler(message):
            handler_called.append(message)
        
        client._pattern_handlers["test/+"] = [pattern_handler]
        
        await client._on_message("test/sensor", b"sensor data", 1, False)
        
        assert len(handler_called) == 1
        assert handler_called[0].topic == "test/sensor"

    @pytest.mark.asyncio
    async def test_on_message_callback_handler_exception(self, client):
        """Test _on_message callback when handler raises exception."""
        def failing_handler(message):
            raise Exception("Handler error")
        
        client._message_handlers["test/topic"] = [failing_handler]
        
        # Should not raise exception
        await client._on_message("test/topic", b"test payload", 1, False)
        
        # Stats should still be updated
        assert client._stats.messages_received == 1

    @pytest.mark.asyncio
    async def test_on_error_callback(self, client):
        """Test _on_error callback."""
        await client._on_error("Connection failed")
        # Should log error message

    @pytest.mark.asyncio
    async def test_send_offline_messages_empty_queue(self, client):
        """Test _send_offline_messages with empty queue."""
        await client._send_offline_messages()
        # Should return early

    @pytest.mark.asyncio
    async def test_send_offline_messages_with_success(self, client, mock_connection_manager):
        """Test _send_offline_messages with successful sends."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = True
        
        client._offline_queue = [
            MQTTMessage(topic="offline/topic1", payload="message1"),
            MQTTMessage(topic="offline/topic2", payload="message2")
        ]
        
        await client._send_offline_messages()
        
        assert len(client._offline_queue) == 0
        assert mock_connection_manager.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_send_offline_messages_with_failure(self, client, mock_connection_manager):
        """Test _send_offline_messages with failed sends."""
        mock_connection_manager.is_connected = True
        mock_connection_manager.publish.return_value = False
        
        original_message = MQTTMessage(topic="offline/topic", payload="message")
        client._offline_queue = [original_message]
        
        await client._send_offline_messages()
        
        # Failed message should be re-queued
        assert len(client._offline_queue) == 1

    def test_topic_matches_pattern_exact_match(self, client):
        """Test topic pattern matching with exact match."""
        assert client._topic_matches_pattern("test/topic", "test/topic") is True

    def test_topic_matches_pattern_single_wildcard(self, client):
        """Test topic pattern matching with single-level wildcard."""
        assert client._topic_matches_pattern("test/sensor", "test/+") is True
        assert client._topic_matches_pattern("test/sensor/data", "test/+") is False

    def test_topic_matches_pattern_multi_wildcard(self, client):
        """Test topic pattern matching with multi-level wildcard."""
        assert client._topic_matches_pattern("test/sensor/data", "test/#") is True
        assert client._topic_matches_pattern("test/sensor/data/value", "test/#") is True
        assert client._topic_matches_pattern("other/sensor", "test/#") is False

    def test_topic_matches_pattern_complex(self, client):
        """Test topic pattern matching with complex patterns."""
        assert client._topic_matches_pattern("home/bedroom/temperature", "home/+/temperature") is True
        assert client._topic_matches_pattern("home/bedroom/humidity", "home/+/temperature") is False
        assert client._topic_matches_pattern("home/bedroom/sensor/temperature", "home/+/temperature") is False

    def test_topic_matches_pattern_pattern_longer_than_topic(self, client):
        """Test topic pattern matching when pattern is longer than topic."""
        assert client._topic_matches_pattern("test", "test/sensor/data") is False


if __name__ == "__main__":
    pytest.main([__file__])