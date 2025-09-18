"""Unit tests for MQTT Publisher functionality."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from mcmqtt.mqtt.publisher import MQTTPublisher
from mcmqtt.mqtt.client import MQTTClient
from mcmqtt.mqtt.types import MQTTQoS, MQTTMessage


class TestMQTTPublisher:
    """Test cases for MQTTPublisher class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MQTT client."""
        client = MagicMock(spec=MQTTClient)
        client.config = MagicMock()
        client.config.qos = MQTTQoS.AT_LEAST_ONCE
        
        # Mock async methods
        client.publish = AsyncMock(return_value=True)
        client.publish_json = AsyncMock(return_value=True)
        client.subscribe = AsyncMock(return_value=True)
        client.unsubscribe = AsyncMock(return_value=True)
        client.wait_for_message = AsyncMock(return_value=True)
        
        return client

    @pytest.fixture
    def publisher(self, mock_client):
        """Create a publisher instance."""
        return MQTTPublisher(mock_client)

    def test_publisher_initialization(self, mock_client):
        """Test publisher initialization."""
        publisher = MQTTPublisher(mock_client)
        
        assert publisher.client == mock_client
        assert publisher._published_messages == []
        assert publisher._max_history == 1000

    @pytest.mark.asyncio
    async def test_publish_with_retry_success_first_attempt(self, publisher, mock_client):
        """Test successful publish on first attempt."""
        mock_client.publish.return_value = True
        
        result = await publisher.publish_with_retry(
            topic="test/topic",
            payload="test message",
            qos=MQTTQoS.AT_LEAST_ONCE,
            retain=False
        )
        
        assert result is True
        mock_client.publish.assert_called_once_with(
            "test/topic", "test message", MQTTQoS.AT_LEAST_ONCE, False
        )
        assert len(publisher._published_messages) == 1

    @pytest.mark.asyncio
    async def test_publish_with_retry_failure_then_success(self, publisher, mock_client):
        """Test publish succeeding after initial failures."""
        # First call fails, second succeeds
        mock_client.publish.side_effect = [False, True]
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await publisher.publish_with_retry(
                topic="test/topic",
                payload="test message",
                max_retries=3,
                retry_delay=0.1
            )
        
        assert result is True
        assert mock_client.publish.call_count == 2
        mock_sleep.assert_called_once_with(0.1)

    @pytest.mark.asyncio
    async def test_publish_with_retry_max_retries_exceeded(self, publisher, mock_client):
        """Test publish failing after max retries."""
        mock_client.publish.return_value = False
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await publisher.publish_with_retry(
                topic="test/topic",
                payload="test message",
                max_retries=2,
                retry_delay=0.1
            )
        
        assert result is False
        assert mock_client.publish.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_publish_batch_all_success(self, publisher, mock_client):
        """Test batch publishing with all messages succeeding."""
        mock_client.publish.return_value = True
        
        messages = [
            {"topic": "test/1", "payload": "msg1", "qos": MQTTQoS.AT_MOST_ONCE},
            {"topic": "test/2", "payload": "msg2", "retain": True},
            {"topic": "test/3", "payload": "msg3"}
        ]
        
        results = await publisher.publish_batch(messages, default_qos=MQTTQoS.AT_LEAST_ONCE)
        
        assert len(results) == 3
        assert all(results.values())
        assert mock_client.publish.call_count == 3

    @pytest.mark.asyncio
    async def test_publish_batch_partial_failure(self, publisher, mock_client):
        """Test batch publishing with some failures."""
        # First succeeds, second fails, third succeeds
        mock_client.publish.side_effect = [True, False, True]
        
        messages = [
            {"topic": "test/1", "payload": "msg1"},
            {"topic": "test/2", "payload": "msg2"},
            {"topic": "test/3", "payload": "msg3"}
        ]
        
        results = await publisher.publish_batch(messages)
        
        assert results["test/1"] is True
        assert results["test/2"] is False
        assert results["test/3"] is True

    @pytest.mark.asyncio
    async def test_publish_batch_exception_handling(self, publisher, mock_client):
        """Test batch publishing with exceptions."""
        async def failing_publish(*args, **kwargs):
            if args[0] == "test/error":
                raise Exception("Network error")
            return True
        
        mock_client.publish.side_effect = failing_publish
        
        messages = [
            {"topic": "test/success", "payload": "msg1"},
            {"topic": "test/error", "payload": "msg2"}
        ]
        
        results = await publisher.publish_batch(messages)
        
        assert results["test/success"] is True
        assert results["test/error"] is False

    @pytest.mark.asyncio
    async def test_publish_scheduled(self, publisher, mock_client):
        """Test scheduled publishing."""
        mock_client.publish.return_value = True
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await publisher.publish_scheduled(
                topic="test/scheduled",
                payload="delayed message",
                delay=2.0
            )
        
        assert result is True
        mock_sleep.assert_called_once_with(2.0)
        mock_client.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_periodic_limited_iterations(self, publisher, mock_client):
        """Test periodic publishing with limited iterations."""
        mock_client.publish.return_value = True
        
        call_count = 0
        def payload_generator():
            nonlocal call_count
            call_count += 1
            return f"message_{call_count}"
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await publisher.publish_periodic(
                topic="test/periodic",
                payload_generator=payload_generator,
                interval=0.1,
                max_iterations=3
            )
        
        assert mock_client.publish.call_count == 3
        assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_publish_periodic_exception_stops_loop(self, publisher, mock_client):
        """Test periodic publishing stops on exception."""
        mock_client.publish.return_value = True
        
        call_count = 0
        def failing_generator():
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Generator error")
            return f"message_{call_count}"
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await publisher.publish_periodic(
                topic="test/periodic",
                payload_generator=failing_generator,
                interval=0.1,
                max_iterations=5
            )
        
        # Should stop after first successful publish due to generator exception
        assert mock_client.publish.call_count == 1

    @pytest.mark.asyncio
    async def test_publish_with_confirmation_success(self, publisher, mock_client):
        """Test publish with confirmation - success case."""
        mock_client.publish.return_value = True
        mock_client.wait_for_message.return_value = True
        
        result = await publisher.publish_with_confirmation(
            topic="test/request",
            payload="request data",
            confirmation_topic="test/response",
            timeout=10.0
        )
        
        assert result is True
        mock_client.subscribe.assert_called_once_with("test/response")
        mock_client.publish.assert_called_once()
        mock_client.wait_for_message.assert_called_once_with("test/response", 10.0)
        mock_client.unsubscribe.assert_called_once_with("test/response")

    @pytest.mark.asyncio
    async def test_publish_with_confirmation_no_confirmation(self, publisher, mock_client):
        """Test publish with confirmation - no confirmation received."""
        mock_client.publish.return_value = True
        mock_client.wait_for_message.return_value = False
        
        result = await publisher.publish_with_confirmation(
            topic="test/request",
            payload="request data",
            confirmation_topic="test/response"
        )
        
        assert result is False
        mock_client.unsubscribe.assert_called_once_with("test/response")

    @pytest.mark.asyncio
    async def test_publish_with_confirmation_publish_fails(self, publisher, mock_client):
        """Test publish with confirmation - initial publish fails."""
        mock_client.publish.return_value = False
        
        result = await publisher.publish_with_confirmation(
            topic="test/request",
            payload="request data",
            confirmation_topic="test/response"
        )
        
        assert result is False
        mock_client.subscribe.assert_called_once_with("test/response")
        mock_client.unsubscribe.assert_called_once_with("test/response")
        mock_client.wait_for_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_json_schema_valid_data(self, publisher, mock_client):
        """Test JSON schema publishing with valid data."""
        mock_client.publish_json.return_value = True
        
        data = {"name": "John", "age": 30}
        schema = {
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        result = await publisher.publish_json_schema(
            topic="test/json",
            data=data,
            schema=schema
        )
        
        assert result is True
        mock_client.publish_json.assert_called_once_with(
            "test/json", data, None, False
        )

    @pytest.mark.asyncio
    async def test_publish_json_schema_invalid_data(self, publisher, mock_client):
        """Test JSON schema publishing with invalid data."""
        data = {"name": "John"}  # Missing required 'age' field
        schema = {
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        result = await publisher.publish_json_schema(
            topic="test/json",
            data=data,
            schema=schema
        )
        
        assert result is False
        mock_client.publish_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_compressed_gzip(self, publisher, mock_client):
        """Test compressed publishing with gzip."""
        mock_client.publish.return_value = True
        
        result = await publisher.publish_compressed(
            topic="test/compressed",
            payload="This is a test message for compression",
            compression="gzip"
        )
        
        assert result is True
        mock_client.publish.assert_called_once()
        
        # Verify the payload was compressed
        call_args = mock_client.publish.call_args[0]
        compressed_payload = call_args[1]
        assert isinstance(compressed_payload, bytes)
        assert compressed_payload.startswith(b"compression:gzip:")

    @pytest.mark.asyncio
    async def test_publish_compressed_zlib(self, publisher, mock_client):
        """Test compressed publishing with zlib."""
        mock_client.publish.return_value = True
        
        result = await publisher.publish_compressed(
            topic="test/compressed",
            payload=b"Binary test data",
            compression="zlib"
        )
        
        assert result is True
        call_args = mock_client.publish.call_args[0]
        compressed_payload = call_args[1]
        assert compressed_payload.startswith(b"compression:zlib:")

    @pytest.mark.asyncio
    async def test_publish_compressed_unsupported_compression(self, publisher, mock_client):
        """Test compressed publishing with unsupported compression."""
        result = await publisher.publish_compressed(
            topic="test/compressed",
            payload="test data",
            compression="unsupported"
        )
        
        assert result is False
        mock_client.publish.assert_not_called()

    def test_get_publish_history(self, publisher):
        """Test getting publish history."""
        # Add some messages to history
        publisher._published_messages = [
            MagicMock(topic="test/1"),
            MagicMock(topic="test/2"),
            MagicMock(topic="test/3")
        ]
        
        # Get all history
        history = publisher.get_publish_history()
        assert len(history) == 3
        
        # Get limited history
        limited = publisher.get_publish_history(limit=2)
        assert len(limited) == 2

    def test_clear_history(self, publisher):
        """Test clearing publish history."""
        publisher._published_messages = [MagicMock(), MagicMock()]
        
        publisher.clear_history()
        assert len(publisher._published_messages) == 0

    def test_add_to_history_with_limit(self, publisher, mock_client):
        """Test adding messages to history respects max limit."""
        publisher._max_history = 2
        
        # Add 3 messages (should keep only last 2)
        for i in range(3):
            publisher._add_to_history(f"test/{i}", f"msg{i}", MQTTQoS.AT_MOST_ONCE, False)
        
        assert len(publisher._published_messages) == 2
        assert publisher._published_messages[0].topic == "test/1"
        assert publisher._published_messages[1].topic == "test/2"

    def test_validate_json_schema_required_fields(self, publisher):
        """Test JSON schema validation for required fields."""
        schema = {"required": ["name", "email"]}
        
        # Valid data
        valid_data = {"name": "John", "email": "john@example.com", "extra": "field"}
        assert publisher._validate_json_schema(valid_data, schema) is True
        
        # Missing required field
        invalid_data = {"name": "John"}
        assert publisher._validate_json_schema(invalid_data, schema) is False

    def test_validate_json_schema_type_validation(self, publisher):
        """Test JSON schema type validation."""
        schema = {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "active": {"type": "boolean"},
                "tags": {"type": "array"},
                "metadata": {"type": "object"}
            }
        }
        
        # Valid types
        valid_data = {
            "name": "John",
            "age": 30,
            "active": True,
            "tags": ["tag1", "tag2"],
            "metadata": {"key": "value"}
        }
        assert publisher._validate_json_schema(valid_data, schema) is True
        
        # Invalid string type
        invalid_data = {"name": 123}
        assert publisher._validate_json_schema(invalid_data, schema) is False
        
        # Invalid number type
        invalid_data = {"age": "thirty"}
        assert publisher._validate_json_schema(invalid_data, schema) is False

    def test_validate_json_schema_exception_handling(self, publisher):
        """Test JSON schema validation exception handling."""
        # Malformed schema should not crash
        malformed_schema = {"properties": "invalid"}
        data = {"field": "value"}
        
        result = publisher._validate_json_schema(data, malformed_schema)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])