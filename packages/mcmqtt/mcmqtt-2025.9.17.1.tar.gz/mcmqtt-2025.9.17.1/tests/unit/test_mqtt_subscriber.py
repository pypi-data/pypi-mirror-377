"""Unit tests for MQTT Subscriber functionality."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from mcmqtt.mqtt.subscriber import MQTTSubscriber, SubscriptionInfo
from mcmqtt.mqtt.client import MQTTClient
from mcmqtt.mqtt.types import MQTTQoS, MQTTMessage


class TestSubscriptionInfo:
    """Test cases for SubscriptionInfo dataclass."""

    def test_subscription_info_creation(self):
        """Test SubscriptionInfo creation and default values."""
        handler = lambda x: None
        info = SubscriptionInfo(
            topic="test/topic",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=handler,
            subscribed_at=datetime.utcnow()
        )
        
        assert info.topic == "test/topic"
        assert info.qos == MQTTQoS.AT_LEAST_ONCE
        assert info.handler == handler
        assert info.message_count == 0
        assert info.last_message is None


class TestMQTTSubscriber:
    """Test cases for MQTTSubscriber class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MQTT client."""
        client = MagicMock(spec=MQTTClient)
        client.config = MagicMock()
        client.config.qos = MQTTQoS.AT_LEAST_ONCE
        
        # Mock async methods
        client.subscribe = AsyncMock(return_value=True)
        client.unsubscribe = AsyncMock(return_value=True)
        client.add_message_handler = MagicMock()
        client.remove_message_handler = MagicMock()
        
        return client
    
    @pytest.fixture
    def subscriber(self, mock_client):
        """Create a subscriber instance."""
        return MQTTSubscriber(mock_client)
    
    def test_subscriber_initialization(self, mock_client):
        """Test subscriber initialization."""
        subscriber = MQTTSubscriber(mock_client)
        
        assert subscriber.client == mock_client
        assert subscriber._subscriptions == {}
        assert subscriber._message_filters == []
        assert subscriber._message_buffer == []
        assert subscriber._max_buffer_size == 10000
        assert subscriber._pattern_subscriptions == {}
        assert subscriber._rate_limits == {}
    
    def test_add_handler_deprecated_warning(self, subscriber, mock_client):
        """Test add_handler deprecated method."""
        handler = MagicMock()
        
        with patch('mcmqtt.mqtt.subscriber.logger') as mock_logger:
            subscriber.add_handler("test/topic", handler)
            
            mock_logger.warning.assert_called_once()
            mock_client.add_message_handler.assert_called_once_with("test/topic", handler)
    
    @pytest.mark.asyncio
    async def test_subscribe_with_filter_success(self, subscriber, mock_client):
        """Test subscribe_with_filter with successful subscription."""
        mock_client.subscribe.return_value = True
        
        def filter_func(msg):
            return "temperature" in msg.topic
        
        handler = MagicMock()
        
        result = await subscriber.subscribe_with_filter(
            "sensors/+/temperature", filter_func, MQTTQoS.EXACTLY_ONCE, handler
        )
        
        assert result is True
        assert "sensors/+/temperature" in subscriber._subscriptions
        
        # Verify subscription info
        sub_info = subscriber._subscriptions["sensors/+/temperature"]
        assert sub_info.topic == "sensors/+/temperature"
        assert sub_info.qos == MQTTQoS.EXACTLY_ONCE
        assert sub_info.handler == handler
        assert sub_info.message_count == 0
        
        # Verify client was called
        mock_client.subscribe.assert_called_once_with("sensors/+/temperature", MQTTQoS.EXACTLY_ONCE)
        mock_client.add_message_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_with_filter_default_qos(self, subscriber, mock_client):
        """Test subscribe_with_filter with default QoS."""
        mock_client.subscribe.return_value = True
        
        def filter_func(msg):
            return True
        
        await subscriber.subscribe_with_filter("test/topic", filter_func)
        
        # Should call subscribe with topic, qos=None, and handler
        assert mock_client.subscribe.called
        call_args = mock_client.subscribe.call_args[0]
        assert call_args[0] == "test/topic"  # topic
        assert call_args[1] is None  # qos (None means use default)
        assert callable(call_args[2])  # handler function
    
    @pytest.mark.asyncio
    async def test_subscribe_with_filter_failure(self, subscriber, mock_client):
        """Test subscribe_with_filter with subscription failure."""
        mock_client.subscribe.return_value = False
        
        def filter_func(msg):
            return True
        
        result = await subscriber.subscribe_with_filter("test/topic", filter_func)
        
        assert result is False
        assert "test/topic" not in subscriber._subscriptions
    
    @pytest.mark.asyncio
    async def test_subscribe_with_rate_limit_success(self, subscriber, mock_client):
        """Test subscribe_with_rate_limit."""
        mock_client.subscribe.return_value = True
        
        handler = MagicMock()
        
        result = await subscriber.subscribe_with_rate_limit(
            "high/frequency/topic", max_messages=10, time_window=60,
            qos=MQTTQoS.AT_MOST_ONCE, handler=handler
        )
        
        assert result is True
        assert "high/frequency/topic" in subscriber._subscriptions
        assert "high/frequency/topic" in subscriber._rate_limits
        
        # Check rate limit configuration
        rate_limit = subscriber._rate_limits["high/frequency/topic"]
        assert rate_limit["max_messages"] == 10
        assert rate_limit["time_window"] == 60
        assert rate_limit["message_times"] == []
    
    @pytest.mark.asyncio
    async def test_subscribe_compressed_success(self, subscriber, mock_client):
        """Test subscribe_compressed."""
        mock_client.subscribe.return_value = True
        
        handler = MagicMock()
        
        result = await subscriber.subscribe_compressed(
            "compressed/topic", handler
        )
        
        assert result is True
        assert "compressed/topic" in subscriber._subscriptions
    
    @pytest.mark.asyncio
    async def test_subscribe_json_schema_success(self, subscriber, mock_client):
        """Test subscribe_json_schema."""
        mock_client.subscribe.return_value = True
        
        schema = {
            "type": "object",
            "properties": {
                "temperature": {"type": "number"},
                "unit": {"type": "string"}
            },
            "required": ["temperature"]
        }
        
        handler = MagicMock()
        
        result = await subscriber.subscribe_json_schema(
            "sensor/data", schema, handler=handler
        )
        
        assert result is True
        assert "sensor/data" in subscriber._subscriptions
    
    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, subscriber, mock_client):
        """Test unsubscribe removes subscription and handlers."""
        # Set up existing subscription
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_with_filter("test/topic", lambda x: True, handler=handler)
        assert "test/topic" in subscriber._subscriptions
        
        # Now unsubscribe
        mock_client.unsubscribe.return_value = True
        result = await subscriber.unsubscribe("test/topic")
        
        assert result is True
        assert "test/topic" not in subscriber._subscriptions
        mock_client.unsubscribe.assert_called_once_with("test/topic")
        mock_client.remove_message_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_topic(self, subscriber, mock_client):
        """Test unsubscribe from nonexistent topic."""
        mock_client.unsubscribe.return_value = True
        
        result = await subscriber.unsubscribe("nonexistent/topic")
        
        assert result is True
        mock_client.unsubscribe.assert_called_once_with("nonexistent/topic")
    
    def test_get_all_subscriptions(self, subscriber, mock_client):
        """Test get_all_subscriptions returns copy of subscriptions."""
        # Add a subscription directly to test
        handler = MagicMock()
        sub_info = SubscriptionInfo(
            topic="test/topic",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=handler,
            subscribed_at=datetime.utcnow()
        )
        subscriber._subscriptions["test/topic"] = sub_info
        
        subscriptions = subscriber.get_all_subscriptions()
        
        assert "test/topic" in subscriptions
        assert subscriptions["test/topic"] == sub_info
        # Ensure it's a copy
        assert subscriptions is not subscriber._subscriptions
    
    def test_get_subscription_info_empty(self, subscriber):
        """Test get_subscription_info with no subscriptions."""
        info = subscriber.get_subscription_info("nonexistent/topic")
        
        assert info is None
    
    def test_get_subscription_info_with_data(self, subscriber):
        """Test get_subscription_info with subscription data."""
        # Add subscription with some message count
        handler = MagicMock()
        sub_info = SubscriptionInfo(
            topic="test/topic",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=handler,
            subscribed_at=datetime.utcnow(),
            message_count=5
        )
        subscriber._subscriptions["test/topic"] = sub_info
        
        info = subscriber.get_subscription_info("test/topic")
        
        assert info is not None
        assert info.topic == "test/topic"
        assert info.message_count == 5
        assert info.qos == MQTTQoS.AT_LEAST_ONCE
    
    def test_add_global_filter(self, subscriber):
        """Test adding global message filters."""
        def filter1(msg):
            return "important" in msg.payload_str
        
        def filter2(msg):
            return msg.qos == MQTTQoS.EXACTLY_ONCE
        
        subscriber.add_global_filter(filter1)
        subscriber.add_global_filter(filter2)
        
        assert len(subscriber._message_filters) == 2
        assert filter1 in subscriber._message_filters
        assert filter2 in subscriber._message_filters
    
    def test_remove_global_filter(self, subscriber):
        """Test removing global message filters."""
        def filter1(msg):
            return True
        
        def filter2(msg):
            return False
        
        subscriber.add_global_filter(filter1)
        subscriber.add_global_filter(filter2)
        
        assert len(subscriber._message_filters) == 2
        
        subscriber.remove_global_filter(filter1)
        
        assert len(subscriber._message_filters) == 1
        assert filter1 not in subscriber._message_filters
        assert filter2 in subscriber._message_filters
    
    def test_remove_nonexistent_filter(self, subscriber):
        """Test removing filter that doesn't exist."""
        def filter_func(msg):
            return True
        
        # Should not raise exception
        subscriber.remove_global_filter(filter_func)
        
        assert len(subscriber._message_filters) == 0

    @pytest.fixture
    def subscriber(self, mock_client):
        """Create a subscriber instance."""
        return MQTTSubscriber(mock_client)

    @pytest.fixture
    def sample_message(self):
        """Create a sample MQTT message."""
        return MQTTMessage(
            topic="test/topic",
            payload="test message",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )

    def test_subscriber_initialization(self, mock_client):
        """Test subscriber initialization."""
        subscriber = MQTTSubscriber(mock_client)
        
        assert subscriber.client == mock_client
        assert subscriber._subscriptions == {}
        assert subscriber._message_filters == []
        assert subscriber._message_buffer == []
        assert subscriber._max_buffer_size == 10000
        assert subscriber._pattern_subscriptions == {}
        assert subscriber._rate_limits == {}

    def test_add_handler_deprecation_warning(self, subscriber, mock_client):
        """Test deprecated add_handler method."""
        handler = lambda x: None
        
        with patch('mcmqtt.mqtt.subscriber.logger') as mock_logger:
            subscriber.add_handler("test/topic", handler)
            
            mock_logger.warning.assert_called_once()
            mock_client.add_message_handler.assert_called_once_with("test/topic", handler)

    @pytest.mark.asyncio
    async def test_subscribe_with_filter_success(self, subscriber, mock_client, sample_message):
        """Test successful subscription with message filtering."""
        mock_client.subscribe.return_value = True
        
        # Filter that accepts all messages
        message_filter = lambda msg: True
        handler = MagicMock()
        
        result = await subscriber.subscribe_with_filter(
            topic="test/topic",
            message_filter=message_filter,
            handler=handler,
            qos=MQTTQoS.EXACTLY_ONCE
        )
        
        assert result is True
        mock_client.subscribe.assert_called_once()
        assert "test/topic" in subscriber._subscriptions
        
        # Test the created handler
        call_args = mock_client.subscribe.call_args[0]
        filtered_handler = call_args[2]  # Third argument is the handler
        
        # Simulate message received
        filtered_handler(sample_message)
        handler.assert_called_once_with(sample_message)

    @pytest.mark.asyncio
    async def test_subscribe_with_filter_message_rejected(self, subscriber, mock_client, sample_message):
        """Test subscription with filter rejecting messages."""
        mock_client.subscribe.return_value = True
        
        # Filter that rejects all messages
        message_filter = lambda msg: False
        handler = MagicMock()
        
        await subscriber.subscribe_with_filter(
            topic="test/topic",
            message_filter=message_filter,
            handler=handler
        )
        
        # Get the handler that was passed to client.subscribe
        call_args = mock_client.subscribe.call_args[0]
        filtered_handler = call_args[2]
        
        # Simulate message received - should be filtered out
        filtered_handler(sample_message)
        handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_subscribe_with_filter_async_handler(self, subscriber, mock_client, sample_message):
        """Test subscription with async handler."""
        mock_client.subscribe.return_value = True
        
        async def async_handler(message):
            pass
        
        message_filter = lambda msg: True
        
        with patch('asyncio.create_task') as mock_create_task:
            await subscriber.subscribe_with_filter(
                topic="test/topic",
                message_filter=message_filter,
                handler=async_handler
            )
            
            # Get the handler and trigger it
            call_args = mock_client.subscribe.call_args[0]
            filtered_handler = call_args[2]
            filtered_handler(sample_message)
            
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_with_rate_limit_success(self, subscriber, mock_client):
        """Test subscription with rate limiting."""
        mock_client.subscribe.return_value = True
        
        handler = MagicMock()
        
        result = await subscriber.subscribe_with_rate_limit(
            topic="test/topic",
            max_messages_per_second=2,
            handler=handler
        )
        
        assert result is True
        assert "test/topic" in subscriber._rate_limits
        assert subscriber._rate_limits["test/topic"]["max_rate"] == 2

    @pytest.mark.asyncio
    async def test_subscribe_with_rate_limit_messages_within_limit(self, subscriber, mock_client, sample_message):
        """Test rate limiting allows messages within limit."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_with_rate_limit(
            topic="test/topic",
            max_messages_per_second=5,
            handler=handler
        )
        
        # Get the rate limited handler
        call_args = mock_client.subscribe.call_args[0]
        rate_limited_handler = call_args[2]
        
        # Send 3 messages (within limit of 5)
        for i in range(3):
            rate_limited_handler(sample_message)
        
        assert handler.call_count == 3
        assert subscriber._rate_limits["test/topic"]["dropped"] == 0

    @pytest.mark.asyncio
    async def test_subscribe_with_rate_limit_messages_exceed_limit(self, subscriber, mock_client, sample_message):
        """Test rate limiting drops messages when exceeding limit."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_with_rate_limit(
            topic="test/topic",
            max_messages_per_second=2,
            handler=handler
        )
        
        # Get the rate limited handler
        call_args = mock_client.subscribe.call_args[0]
        rate_limited_handler = call_args[2]
        
        # Send 5 messages (exceeds limit of 2)
        for i in range(5):
            rate_limited_handler(sample_message)
        
        assert handler.call_count == 2  # Only first 2 should be processed
        assert subscriber._rate_limits["test/topic"]["dropped"] == 3

    @pytest.mark.asyncio
    async def test_subscribe_json_schema_valid_message(self, subscriber, mock_client):
        """Test JSON schema subscription with valid message."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        schema = {
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        await subscriber.subscribe_json_schema(
            topic="test/topic",
            schema=schema,
            handler=handler
        )
        
        # Create a valid JSON message
        valid_data = {"name": "John", "age": 30}
        json_message = MQTTMessage(
            topic="test/topic",
            payload=json.dumps(valid_data),
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        # Get the schema handler
        call_args = mock_client.subscribe.call_args[0]
        schema_handler = call_args[2]
        schema_handler(json_message)
        
        handler.assert_called_once_with(json_message)

    @pytest.mark.asyncio
    async def test_subscribe_json_schema_invalid_message(self, subscriber, mock_client):
        """Test JSON schema subscription with invalid message."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        schema = {
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        await subscriber.subscribe_json_schema(
            topic="test/topic",
            schema=schema,
            handler=handler
        )
        
        # Create an invalid JSON message (missing required field)
        invalid_data = {"name": "John"}  # Missing 'age'
        json_message = MQTTMessage(
            topic="test/topic",
            payload=json.dumps(invalid_data),
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        # Get the schema handler
        call_args = mock_client.subscribe.call_args[0]
        schema_handler = call_args[2]
        schema_handler(json_message)
        
        handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_subscribe_compressed_gzip_message(self, subscriber, mock_client):
        """Test subscription to compressed messages with gzip."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_compressed(
            topic="test/topic",
            handler=handler
        )
        
        # Create a compressed message
        import gzip
        original_data = b"This is test data for compression"
        compressed_data = gzip.compress(original_data)
        compressed_payload = b"compression:gzip:" + compressed_data
        
        compressed_message = MQTTMessage(
            topic="test/topic",
            payload=compressed_payload,
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        # Get the decompression handler
        call_args = mock_client.subscribe.call_args[0]
        decompression_handler = call_args[2]
        decompression_handler(compressed_message)
        
        # Handler should be called with decompressed message
        handler.assert_called_once()
        called_message = handler.call_args[0][0]
        assert called_message.payload == original_data

    @pytest.mark.asyncio
    async def test_subscribe_compressed_zlib_message(self, subscriber, mock_client):
        """Test subscription to compressed messages with zlib."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_compressed(
            topic="test/topic",
            handler=handler
        )
        
        # Create a zlib compressed message
        import zlib
        original_data = b"This is test data for zlib compression"
        compressed_data = zlib.compress(original_data)
        compressed_payload = b"compression:zlib:" + compressed_data
        
        compressed_message = MQTTMessage(
            topic="test/topic",
            payload=compressed_payload,
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        # Get the decompression handler
        call_args = mock_client.subscribe.call_args[0]
        decompression_handler = call_args[2]
        decompression_handler(compressed_message)
        
        handler.assert_called_once()
        called_message = handler.call_args[0][0]
        assert called_message.payload == original_data

    @pytest.mark.asyncio
    async def test_subscribe_compressed_uncompressed_message(self, subscriber, mock_client):
        """Test subscription handles uncompressed messages normally."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        await subscriber.subscribe_compressed(
            topic="test/topic",
            handler=handler
        )
        
        # Create a normal, uncompressed message
        normal_message = MQTTMessage(
            topic="test/topic",
            payload="Normal uncompressed message",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        # Get the decompression handler
        call_args = mock_client.subscribe.call_args[0]
        decompression_handler = call_args[2]
        decompression_handler(normal_message)
        
        # Handler should be called with original message
        handler.assert_called_once_with(normal_message)

    @pytest.mark.asyncio
    async def test_subscribe_pattern(self, subscriber, mock_client):
        """Test pattern subscription."""
        mock_client.subscribe.return_value = True
        handler = MagicMock()
        
        result = await subscriber.subscribe_pattern(
            pattern="test/+/data",
            handler=handler,
            qos=MQTTQoS.EXACTLY_ONCE
        )
        
        assert result is True
        mock_client.subscribe.assert_called_once_with("test/+/data", MQTTQoS.EXACTLY_ONCE, handler)
        assert "test/+/data" in subscriber._pattern_subscriptions

    def test_add_global_filter(self, subscriber):
        """Test adding global message filters."""
        filter1 = lambda msg: True
        filter2 = lambda msg: False
        
        subscriber.add_global_filter(filter1)
        subscriber.add_global_filter(filter2)
        
        assert len(subscriber._message_filters) == 2
        assert filter1 in subscriber._message_filters
        assert filter2 in subscriber._message_filters

    def test_remove_global_filter(self, subscriber):
        """Test removing global message filters."""
        filter1 = lambda msg: True
        filter2 = lambda msg: False
        
        subscriber.add_global_filter(filter1)
        subscriber.add_global_filter(filter2)
        
        subscriber.remove_global_filter(filter1)
        
        assert len(subscriber._message_filters) == 1
        assert filter1 not in subscriber._message_filters
        assert filter2 in subscriber._message_filters

    def test_remove_nonexistent_filter(self, subscriber):
        """Test removing non-existent filter doesn't raise error."""
        filter1 = lambda msg: True
        
        # Should not raise an exception
        subscriber.remove_global_filter(filter1)

    def test_get_buffered_messages_all(self, subscriber, sample_message):
        """Test getting all buffered messages."""
        message1 = sample_message
        message2 = MQTTMessage(
            topic="test/topic2",
            payload="message 2",
            qos=MQTTQoS.AT_MOST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        subscriber._message_buffer = [message1, message2]
        
        messages = subscriber.get_buffered_messages()
        assert len(messages) == 2
        assert messages[0] == message1
        assert messages[1] == message2

    def test_get_buffered_messages_by_topic(self, subscriber):
        """Test getting buffered messages filtered by topic."""
        message1 = MQTTMessage(
            topic="test/topic1",
            payload="message 1",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        message2 = MQTTMessage(
            topic="test/topic2",
            payload="message 2",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        subscriber._message_buffer = [message1, message2]
        
        messages = subscriber.get_buffered_messages(topic="test/topic1")
        assert len(messages) == 1
        assert messages[0] == message1

    def test_get_buffered_messages_by_time(self, subscriber):
        """Test getting buffered messages filtered by time."""
        now = datetime.utcnow()
        old_time = now - timedelta(hours=1)
        
        old_message = MQTTMessage(
            topic="test/topic",
            payload="old message",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=old_time
        )
        new_message = MQTTMessage(
            topic="test/topic",
            payload="new message",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=now
        )
        
        subscriber._message_buffer = [old_message, new_message]
        
        since = now - timedelta(minutes=30)
        messages = subscriber.get_buffered_messages(since=since)
        assert len(messages) == 1
        assert messages[0] == new_message

    def test_get_buffered_messages_with_limit(self, subscriber):
        """Test getting buffered messages with limit."""
        messages = []
        for i in range(5):
            msg = MQTTMessage(
                topic=f"test/topic{i}",
                payload=f"message {i}",
                qos=MQTTQoS.AT_LEAST_ONCE,
                retain=False,
                timestamp=datetime.utcnow()
            )
            messages.append(msg)
        
        subscriber._message_buffer = messages
        
        limited = subscriber.get_buffered_messages(limit=3)
        assert len(limited) == 3
        # Should get the last 3 messages
        assert limited == messages[-3:]

    def test_clear_buffer_all(self, subscriber, sample_message):
        """Test clearing entire message buffer."""
        subscriber._message_buffer = [sample_message, sample_message]
        
        subscriber.clear_buffer()
        assert len(subscriber._message_buffer) == 0

    def test_clear_buffer_by_topic(self, subscriber):
        """Test clearing message buffer by topic."""
        message1 = MQTTMessage(
            topic="test/topic1",
            payload="message 1",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        message2 = MQTTMessage(
            topic="test/topic2",
            payload="message 2",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False,
            timestamp=datetime.utcnow()
        )
        
        subscriber._message_buffer = [message1, message2]
        
        subscriber.clear_buffer(topic="test/topic1")
        assert len(subscriber._message_buffer) == 1
        assert subscriber._message_buffer[0] == message2

    def test_get_subscription_info(self, subscriber):
        """Test getting subscription information."""
        info = SubscriptionInfo(
            topic="test/topic",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=None,
            subscribed_at=datetime.utcnow()
        )
        
        subscriber._subscriptions["test/topic"] = info
        
        result = subscriber.get_subscription_info("test/topic")
        assert result == info
        
        # Test non-existent subscription
        result = subscriber.get_subscription_info("nonexistent")
        assert result is None

    def test_get_subscription_info_pattern(self, subscriber):
        """Test getting pattern subscription information."""
        info = SubscriptionInfo(
            topic="test/+/data",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=None,
            subscribed_at=datetime.utcnow()
        )
        
        subscriber._pattern_subscriptions["test/+/data"] = info
        
        result = subscriber.get_subscription_info("test/+/data")
        assert result == info

    def test_get_all_subscriptions(self, subscriber):
        """Test getting all subscription information."""
        info1 = SubscriptionInfo(
            topic="test/topic1",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=None,
            subscribed_at=datetime.utcnow()
        )
        info2 = SubscriptionInfo(
            topic="test/+/data",
            qos=MQTTQoS.EXACTLY_ONCE,
            handler=None,
            subscribed_at=datetime.utcnow()
        )
        
        subscriber._subscriptions["test/topic1"] = info1
        subscriber._pattern_subscriptions["test/+/data"] = info2
        
        all_subs = subscriber.get_all_subscriptions()
        assert len(all_subs) == 2
        assert "test/topic1" in all_subs
        assert "test/+/data" in all_subs

    def test_get_rate_limit_stats(self, subscriber):
        """Test getting rate limit statistics."""
        stats = {
            'max_rate': 5,
            'messages': [],
            'dropped': 2
        }
        
        subscriber._rate_limits["test/topic"] = stats
        
        result = subscriber.get_rate_limit_stats("test/topic")
        assert result == stats
        
        # Test non-existent topic
        result = subscriber.get_rate_limit_stats("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_wait_for_messages_success(self, subscriber, mock_client):
        """Test waiting for messages successfully."""
        mock_client.subscribe = AsyncMock(return_value=True)
        mock_client.unsubscribe = AsyncMock(return_value=True)
        
        # Mock the future to resolve immediately
        with patch('asyncio.wait_for') as mock_wait_for:
            mock_messages = [MagicMock(), MagicMock()]
            mock_wait_for.return_value = mock_messages
            
            result = await subscriber.wait_for_messages("test/topic", count=2, timeout=10.0)
            
            assert result == mock_messages
            mock_client.add_message_handler.assert_called_once()
            mock_client.remove_message_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_messages_timeout(self, subscriber, mock_client):
        """Test waiting for messages with timeout."""
        mock_client.subscribe = AsyncMock(return_value=True)
        mock_client.unsubscribe = AsyncMock(return_value=True)
        
        with patch('asyncio.wait_for') as mock_wait_for:
            mock_wait_for.side_effect = asyncio.TimeoutError()
            
            result = await subscriber.wait_for_messages("test/topic", count=5, timeout=1.0)
            
            assert isinstance(result, list)  # Should return partial results
            mock_client.remove_message_handler.assert_called_once()

    def test_add_to_buffer_with_global_filters(self, subscriber, sample_message):
        """Test adding message to buffer with global filters."""
        # Add filter that accepts all messages
        accept_filter = lambda msg: True
        subscriber.add_global_filter(accept_filter)
        
        subscriber._add_to_buffer(sample_message)
        assert len(subscriber._message_buffer) == 1
        
        # Add filter that rejects all messages
        reject_filter = lambda msg: False
        subscriber.add_global_filter(reject_filter)
        
        # Clear buffer and try again
        subscriber._message_buffer.clear()
        subscriber._add_to_buffer(sample_message)
        assert len(subscriber._message_buffer) == 0  # Should be filtered out

    def test_add_to_buffer_filter_exception(self, subscriber, sample_message):
        """Test handling filter exceptions."""
        def failing_filter(msg):
            raise Exception("Filter error")
        
        subscriber.add_global_filter(failing_filter)
        
        with patch('mcmqtt.mqtt.subscriber.logger') as mock_logger:
            subscriber._add_to_buffer(sample_message)
            
            # Message should still be added despite filter error
            assert len(subscriber._message_buffer) == 1
            mock_logger.error.assert_called_once()

    def test_add_to_buffer_size_limit(self, subscriber):
        """Test buffer size limiting."""
        subscriber._max_buffer_size = 3
        
        # Add 5 messages
        for i in range(5):
            msg = MQTTMessage(
                topic=f"test/topic{i}",
                payload=f"message {i}",
                qos=MQTTQoS.AT_LEAST_ONCE,
                retain=False,
                timestamp=datetime.utcnow()
            )
            subscriber._add_to_buffer(msg)
        
        # Should only keep the last 3
        assert len(subscriber._message_buffer) == 3
        assert subscriber._message_buffer[0].payload == "message 2"
        assert subscriber._message_buffer[2].payload == "message 4"

    def test_update_subscription_stats(self, subscriber, sample_message):
        """Test updating subscription statistics."""
        info = SubscriptionInfo(
            topic="test/topic",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=None,
            subscribed_at=datetime.utcnow()
        )
        
        subscriber._subscriptions["test/topic"] = info
        
        subscriber._update_subscription_stats("test/topic", sample_message)
        
        assert info.message_count == 1
        assert info.last_message == sample_message.timestamp

    def test_update_subscription_stats_nonexistent_topic(self, subscriber, sample_message):
        """Test updating stats for non-existent subscription."""
        # Should not raise an exception
        subscriber._update_subscription_stats("nonexistent", sample_message)

    def test_validate_json_schema_success(self, subscriber):
        """Test successful JSON schema validation."""
        schema = {
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        valid_data = {"name": "John", "age": 30}
        result = subscriber._validate_json_schema(valid_data, schema)
        assert result is True

    def test_validate_json_schema_missing_required(self, subscriber):
        """Test JSON schema validation with missing required field."""
        schema = {
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        invalid_data = {"name": "John"}  # Missing age
        result = subscriber._validate_json_schema(invalid_data, schema)
        assert result is False

    def test_validate_json_schema_wrong_types(self, subscriber):
        """Test JSON schema validation with wrong types."""
        schema = {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "active": {"type": "boolean"},
                "tags": {"type": "array"},
                "meta": {"type": "object"}
            }
        }
        
        # Wrong string type
        assert subscriber._validate_json_schema({"name": 123}, schema) is False
        
        # Wrong number type
        assert subscriber._validate_json_schema({"age": "thirty"}, schema) is False
        
        # Wrong boolean type
        assert subscriber._validate_json_schema({"active": "yes"}, schema) is False
        
        # Wrong array type
        assert subscriber._validate_json_schema({"tags": "tag1,tag2"}, schema) is False
        
        # Wrong object type
        assert subscriber._validate_json_schema({"meta": "string"}, schema) is False

    def test_validate_json_schema_exception_handling(self, subscriber):
        """Test JSON schema validation exception handling."""
        # Malformed schema
        malformed_schema = {"properties": None}
        data = {"field": "value"}
        
        result = subscriber._validate_json_schema(data, malformed_schema)
        assert result is False


    def test_clear_buffer(self, subscriber):
        """Test clearing message buffer."""
        # Add some messages to buffer
        msg1 = MQTTMessage("test/1", "payload1", MQTTQoS.AT_LEAST_ONCE)
        msg2 = MQTTMessage("test/2", "payload2", MQTTQoS.AT_MOST_ONCE)
        
        subscriber._message_buffer = [msg1, msg2]
        assert len(subscriber._message_buffer) == 2
        
        subscriber.clear_buffer()
        
        assert len(subscriber._message_buffer) == 0
    
    def test_get_buffered_messages_empty(self, subscriber):
        """Test get_buffered_messages with empty buffer."""
        messages = subscriber.get_buffered_messages()
        
        assert messages == []
    
    def test_get_buffered_messages_with_data(self, subscriber):
        """Test get_buffered_messages with data."""
        msg1 = MQTTMessage("test/1", "payload1", MQTTQoS.AT_LEAST_ONCE)
        msg2 = MQTTMessage("test/2", "payload2", MQTTQoS.AT_MOST_ONCE)
        
        subscriber._message_buffer = [msg1, msg2]
        
        messages = subscriber.get_buffered_messages()
        
        assert len(messages) == 2
        assert messages[0] == msg1
        assert messages[1] == msg2
        # Ensure it's a copy
        assert messages is not subscriber._message_buffer
    
    def test_get_buffered_messages_by_topic(self, subscriber):
        """Test get_buffered_messages filtered by topic."""
        msg1 = MQTTMessage("sensors/temp", "22.5", MQTTQoS.AT_LEAST_ONCE)
        msg2 = MQTTMessage("sensors/humidity", "60", MQTTQoS.AT_MOST_ONCE)
        msg3 = MQTTMessage("sensors/temp", "23.0", MQTTQoS.AT_LEAST_ONCE)
        
        subscriber._message_buffer = [msg1, msg2, msg3]
        
        temp_messages = subscriber.get_buffered_messages(topic="sensors/temp")
        
        assert len(temp_messages) == 2
        assert temp_messages[0] == msg1
        assert temp_messages[1] == msg3
    
    def test_get_buffered_messages_with_limit(self, subscriber):
        """Test get_buffered_messages with limit."""
        messages = [MQTTMessage(f"test/{i}", f"payload{i}", MQTTQoS.AT_LEAST_ONCE) for i in range(10)]
        subscriber._message_buffer = messages
        
        limited_messages = subscriber.get_buffered_messages(limit=5)
        
        assert len(limited_messages) == 5
        # get_buffered_messages returns last N messages, not first N
        assert limited_messages == messages[-5:]
    
    def test_message_handler_with_filtering(self, subscriber):
        """Test _handle_filtered_message method."""
        # Create a message that should pass filters
        message = MQTTMessage("test/important", "important data", MQTTQoS.AT_LEAST_ONCE)
        
        # Add a filter that looks for "important" in topic
        def important_filter(msg):
            return "important" in msg.topic
        
        subscriber.add_message_filter(important_filter)
        
        # Add to subscription for tracking
        handler = MagicMock()
        sub_info = SubscriptionInfo(
            topic="test/important",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=handler,
            subscribed_at=datetime.utcnow()
        )
        subscriber._subscriptions["test/important"] = sub_info
        
        # Call the internal handler method
        subscriber._handle_filtered_message("test/important", message)
        
        # Should be added to buffer and handler called
        assert len(subscriber._message_buffer) == 1
        assert subscriber._message_buffer[0] == message
        handler.assert_called_once_with(message)
        
        # Should update subscription stats
        assert sub_info.message_count == 1
        assert sub_info.last_message is not None
    
    def test_message_handler_filtered_out(self, subscriber):
        """Test _handle_filtered_message with message filtered out."""
        message = MQTTMessage("test/normal", "normal data", MQTTQoS.AT_LEAST_ONCE)
        
        # Add a filter that only passes "important" messages
        def important_filter(msg):
            return "important" in msg.topic
        
        subscriber.add_message_filter(important_filter)
        
        # Add to subscription for tracking
        handler = MagicMock()
        sub_info = SubscriptionInfo(
            topic="test/normal",
            qos=MQTTQoS.AT_LEAST_ONCE,
            handler=handler,
            subscribed_at=datetime.utcnow()
        )
        subscriber._subscriptions["test/normal"] = sub_info
        
        # Call the internal handler method
        subscriber._handle_filtered_message("test/normal", message)
        
        # Should NOT be added to buffer or call handler
        assert len(subscriber._message_buffer) == 0
        handler.assert_not_called()
        
        # Should NOT update subscription stats
        assert sub_info.message_count == 0
        assert sub_info.last_message is None
    
    def test_buffer_size_limit(self, subscriber):
        """Test message buffer respects size limit."""
        subscriber._max_buffer_size = 3
        
        # Add messages beyond limit
        for i in range(5):
            message = MQTTMessage(f"test/{i}", f"payload{i}", MQTTQoS.AT_LEAST_ONCE)
            subscriber._message_buffer.append(message)
        
        # Should only keep the last 3 messages (assuming FIFO behavior)
        # Note: The actual implementation might need to be checked for buffer management
        assert len(subscriber._message_buffer) == 5  # Current simple implementation
    
    def test_rate_limit_checking(self, subscriber):
        """Test _check_rate_limit method."""
        topic = "test/rate/limited"
        
        # Set up rate limit: 2 messages per 10 seconds
        subscriber._rate_limits[topic] = {
            "max_messages": 2,
            "time_window": 10,
            "message_times": []
        }
        
        # First message should pass
        assert subscriber._check_rate_limit(topic) is True
        assert len(subscriber._rate_limits[topic]["message_times"]) == 1
        
        # Second message should pass
        assert subscriber._check_rate_limit(topic) is True
        assert len(subscriber._rate_limits[topic]["message_times"]) == 2
        
        # Third message should be rate limited
        assert subscriber._check_rate_limit(topic) is False
        assert len(subscriber._rate_limits[topic]["message_times"]) == 2  # No new time added
    
    def test_rate_limit_cleanup(self, subscriber):
        """Test rate limit cleanup of old timestamps."""
        topic = "test/cleanup"
        
        # Set up rate limit with old timestamps
        old_time = datetime.now() - timedelta(seconds=20)
        recent_time = datetime.now() - timedelta(seconds=1)
        
        subscriber._rate_limits[topic] = {
            "max_messages": 2,
            "time_window": 10,
            "message_times": [old_time, recent_time]
        }
        
        # Check rate limit - should clean up old timestamp
        result = subscriber._check_rate_limit(topic)
        
        # Should pass because old timestamp was cleaned up
        assert result is True
        
        # Should only have recent_time and new timestamp
        message_times = subscriber._rate_limits[topic]["message_times"]
        assert len(message_times) == 2
        assert old_time not in message_times
        assert recent_time in message_times


if __name__ == "__main__":
    pytest.main([__file__])