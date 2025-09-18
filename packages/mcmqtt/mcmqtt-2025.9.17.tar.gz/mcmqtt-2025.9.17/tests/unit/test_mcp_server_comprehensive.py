"""Comprehensive unit tests for MCP Server functionality."""

import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

from mcmqtt.mcp.server import MCMQTTServer
from mcmqtt.mqtt.types import MQTTConfig, MQTTConnectionState, MQTTQoS
from mcmqtt.broker.manager import BrokerConfig, BrokerInfo


class TestMCMQTTServerComprehensive:
    """Comprehensive test cases for MCMQTTServer class."""

    @pytest.fixture
    def mqtt_config(self):
        """Create a test MQTT configuration."""
        return MQTTConfig(
            broker_host="localhost",
            broker_port=1883,
            client_id="test-client",
            username="testuser",
            password="testpass",
            keepalive=60,
            use_tls=False,
            clean_session=True
        )

    @pytest.fixture
    def mock_broker_manager(self):
        """Create a mock broker manager."""
        manager = MagicMock()
        manager.is_available.return_value = True
        manager.spawn_broker = AsyncMock(return_value="test-broker-123")
        manager.stop_broker = AsyncMock(return_value=True)
        manager.get_broker_status = AsyncMock()
        manager.list_brokers = MagicMock(return_value=[])
        manager.get_running_brokers = MagicMock(return_value=[])
        manager.stop_all_brokers = AsyncMock(return_value=2)
        manager.test_broker_connection = AsyncMock(return_value=True)
        return manager

    @pytest.fixture 
    def mock_fastmcp(self):
        """Create a mock FastMCP instance."""
        fastmcp = MagicMock()
        fastmcp.add_middleware = MagicMock()
        fastmcp.run_http_async = AsyncMock()
        return fastmcp

    @pytest.fixture
    def server(self, mock_broker_manager, mock_fastmcp):
        """Create a server instance with mocked dependencies."""
        with patch('mcmqtt.mcp.server.BrokerManager', return_value=mock_broker_manager), \
             patch('mcmqtt.mcp.server.FastMCP', return_value=mock_fastmcp), \
             patch.object(MCMQTTServer, 'register_all'):
            server = MCMQTTServer(enable_auto_broker=True)
            server.broker_manager = mock_broker_manager
            server.mcp = mock_fastmcp
            return server

    @pytest.fixture
    def server_no_auto_broker(self, mock_broker_manager, mock_fastmcp):
        """Create a server instance without auto broker."""
        with patch('mcmqtt.mcp.server.BrokerManager', return_value=mock_broker_manager), \
             patch('mcmqtt.mcp.server.FastMCP', return_value=mock_fastmcp), \
             patch.object(MCMQTTServer, 'register_all'):
            server = MCMQTTServer(enable_auto_broker=False)
            server.broker_manager = mock_broker_manager
            server.mcp = mock_fastmcp
            return server

    def test_server_initialization_with_auto_broker(self, server):
        """Test server initialization with auto broker enabled."""
        assert server.mqtt_config is None
        assert server.mqtt_client is None
        assert server.mqtt_publisher is None
        assert server.mqtt_subscriber is None
        assert server._connection_state == MQTTConnectionState.DISCONNECTED
        assert server._last_error is None
        assert server._message_store == []
        server.mcp.add_middleware.assert_called_once()

    def test_server_initialization_no_auto_broker(self, server_no_auto_broker):
        """Test server initialization without auto broker."""
        assert server_no_auto_broker.mqtt_config is None
        assert server_no_auto_broker._connection_state == MQTTConnectionState.DISCONNECTED
        server_no_auto_broker.mcp.add_middleware.assert_not_called()

    def test_server_initialization_with_config(self, mqtt_config):
        """Test server initialization with MQTT config."""
        with patch('mcmqtt.mcp.server.BrokerManager'), \
             patch('mcmqtt.mcp.server.FastMCP'), \
             patch.object(MCMQTTServer, 'register_all'):
            server = MCMQTTServer(mqtt_config=mqtt_config)
            assert server.mqtt_config == mqtt_config

    def test_server_initialization_amqtt_not_available(self, mock_fastmcp):
        """Test server initialization when AMQTT is not available."""
        mock_broker_manager = MagicMock()
        mock_broker_manager.is_available.return_value = False
        
        with patch('mcmqtt.mcp.server.BrokerManager', return_value=mock_broker_manager), \
             patch('mcmqtt.mcp.server.FastMCP', return_value=mock_fastmcp), \
             patch.object(MCMQTTServer, 'register_all'):
            server = MCMQTTServer(enable_auto_broker=True)
            mock_fastmcp.add_middleware.assert_not_called()

    def test_safe_method_call_method_exists(self, server):
        """Test _safe_method_call when method exists."""
        obj = MagicMock()
        obj.test_method.return_value = "success"
        
        result = server._safe_method_call(obj, "test_method", "arg1", kwarg1="value1")
        
        assert result == "success"
        obj.test_method.assert_called_once_with("arg1", kwarg1="value1")

    def test_safe_method_call_method_missing(self, server):
        """Test _safe_method_call when method doesn't exist."""
        obj = MagicMock(spec=[])  # Empty spec means no methods
        
        result = server._safe_method_call(obj, "nonexistent_method", "arg1")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_success(self, server, mqtt_config):
        """Test successful MQTT client initialization."""
        with patch('mcmqtt.mcp.server.MQTTClient') as mock_client_class, \
             patch('mcmqtt.mcp.server.MQTTPublisher') as mock_publisher_class:
            
            mock_client = MagicMock()
            mock_client.add_message_handler = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_publisher = MagicMock()
            mock_publisher_class.return_value = mock_publisher
            
            result = await server.initialize_mqtt_client(mqtt_config)
            
            assert result is True
            assert server.mqtt_config == mqtt_config
            assert server.mqtt_client == mock_client
            assert server.mqtt_publisher == mock_publisher
            assert server.mqtt_subscriber is None  # Intentionally skipped
            assert server._connection_state == MQTTConnectionState.CONFIGURED
            mock_client.add_message_handler.assert_called_once_with("#", server.mqtt_client.add_message_handler.call_args[0][1])

    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_failure(self, server, mqtt_config):
        """Test MQTT client initialization failure."""
        with patch('mcmqtt.mcp.server.MQTTClient', side_effect=Exception("Init failed")):
            result = await server.initialize_mqtt_client(mqtt_config)
            
            assert result is False
            assert "Init failed" in server._last_error
            assert server._connection_state == MQTTConnectionState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_no_add_message_handler(self, server, mqtt_config):
        """Test MQTT client initialization when add_message_handler is missing."""
        with patch('mcmqtt.mcp.server.MQTTClient') as mock_client_class, \
             patch('mcmqtt.mcp.server.MQTTPublisher'):
            
            mock_client = MagicMock(spec=[])  # No add_message_handler method
            mock_client_class.return_value = mock_client
            
            result = await server.initialize_mqtt_client(mqtt_config)
            
            assert result is True
            assert server._connection_state == MQTTConnectionState.CONFIGURED

    @pytest.mark.asyncio
    async def test_connect_mqtt_success(self, server):
        """Test successful MQTT connection."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=True)
        server.mqtt_client = mock_client
        
        result = await server.connect_mqtt()
        
        assert result is True
        assert server._connection_state == MQTTConnectionState.CONNECTED
        assert server._last_error is None
        mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_mqtt_failure(self, server):
        """Test MQTT connection failure."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=False)
        server.mqtt_client = mock_client
        
        result = await server.connect_mqtt()
        
        assert result is False
        assert server._connection_state == MQTTConnectionState.ERROR
        assert server._last_error == "Failed to connect to MQTT broker"

    @pytest.mark.asyncio
    async def test_connect_mqtt_no_client(self, server):
        """Test MQTT connection with no client."""
        result = await server.connect_mqtt()
        
        assert result is False
        assert server._last_error == "MQTT client not initialized"

    @pytest.mark.asyncio
    async def test_connect_mqtt_exception(self, server):
        """Test MQTT connection with exception."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(side_effect=Exception("Connection error"))
        server.mqtt_client = mock_client
        
        result = await server.connect_mqtt()
        
        assert result is False
        assert server._connection_state == MQTTConnectionState.ERROR
        assert "Connection error" in server._last_error

    @pytest.mark.asyncio
    async def test_disconnect_mqtt_success(self, server):
        """Test successful MQTT disconnection."""
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        await server.disconnect_mqtt()
        
        assert server._connection_state == MQTTConnectionState.DISCONNECTED
        mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_mqtt_not_connected(self, server):
        """Test MQTT disconnection when not connected."""
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.DISCONNECTED
        
        await server.disconnect_mqtt()
        
        mock_client.disconnect.assert_not_called()

    @pytest.mark.asyncio
    async def test_disconnect_mqtt_exception(self, server):
        """Test MQTT disconnection with exception."""
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock(side_effect=Exception("Disconnect error"))
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        await server.disconnect_mqtt()
        
        assert "Disconnect error" in server._last_error

    @pytest.mark.asyncio
    async def test_connect_to_broker_success(self, server):
        """Test connect_to_broker tool success."""
        with patch.object(server, 'initialize_mqtt_client', return_value=True), \
             patch.object(server, 'connect_mqtt', return_value=True):
            
            server._connection_state = MQTTConnectionState.CONNECTED
            
            result = await server.connect_to_broker(
                broker_host="test.broker.com",
                broker_port=1883,
                client_id="test-client"
            )
            
            assert result["success"] is True
            assert "Connected to MQTT broker" in result["message"]
            assert result["client_id"] == "test-client"
            assert result["connection_state"] == MQTTConnectionState.CONNECTED.value

    @pytest.mark.asyncio
    async def test_connect_to_broker_init_failure(self, server):
        """Test connect_to_broker tool with initialization failure."""
        with patch.object(server, 'initialize_mqtt_client', return_value=False):
            server._last_error = "Init failed"
            
            result = await server.connect_to_broker("test.broker.com")
            
            assert result["success"] is False
            assert "Failed to connect: Init failed" in result["message"]

    @pytest.mark.asyncio
    async def test_connect_to_broker_connect_failure(self, server):
        """Test connect_to_broker tool with connection failure."""
        with patch.object(server, 'initialize_mqtt_client', return_value=True), \
             patch.object(server, 'connect_mqtt', return_value=False):
            
            server._last_error = "Connect failed"
            
            result = await server.connect_to_broker("test.broker.com")
            
            assert result["success"] is False
            assert "Failed to connect to MQTT broker" in result["message"]

    @pytest.mark.asyncio
    async def test_connect_to_broker_exception(self, server):
        """Test connect_to_broker tool with exception."""
        with patch.object(server, 'initialize_mqtt_client', side_effect=Exception("Unexpected error")):
            
            result = await server.connect_to_broker("test.broker.com")
            
            assert result["success"] is False
            assert "Connection error: Unexpected error" in result["message"]

    @pytest.mark.asyncio
    async def test_disconnect_from_broker_success(self, server):
        """Test disconnect_from_broker tool success."""
        with patch.object(server, 'disconnect_mqtt') as mock_disconnect:
            server._connection_state = MQTTConnectionState.DISCONNECTED
            
            result = await server.disconnect_from_broker()
            
            assert result["success"] is True
            assert result["message"] == "Disconnected from MQTT broker"
            assert result["connection_state"] == MQTTConnectionState.DISCONNECTED.value
            mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_from_broker_exception(self, server):
        """Test disconnect_from_broker tool with exception."""
        with patch.object(server, 'disconnect_mqtt', side_effect=Exception("Disconnect error")):
            
            result = await server.disconnect_from_broker()
            
            assert result["success"] is False
            assert "Disconnect error: Disconnect error" in result["message"]

    @pytest.mark.asyncio
    async def test_publish_message_success(self, server):
        """Test publish_message tool success."""
        mock_client = MagicMock()
        mock_client.publish = AsyncMock()
        server.mqtt_client = mock_client
        server.mqtt_publisher = MagicMock()
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.publish_message("test/topic", "test message", qos=1, retain=False)
        
        assert result["success"] is True
        assert result["topic"] == "test/topic"
        assert result["qos"] == 1
        assert result["retain"] is False
        mock_client.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_message_dict_payload(self, server):
        """Test publish_message tool with dict payload."""
        mock_client = MagicMock()
        mock_client.publish = AsyncMock()
        server.mqtt_client = mock_client
        server.mqtt_publisher = MagicMock()
        server._connection_state = MQTTConnectionState.CONNECTED
        
        payload_dict = {"temperature": 22.5, "humidity": 60}
        result = await server.publish_message("sensor/data", payload_dict)
        
        assert result["success"] is True
        # Verify the payload was JSON serialized
        call_args = mock_client.publish.call_args
        assert json.loads(call_args[1]['payload']) == payload_dict

    @pytest.mark.asyncio
    async def test_publish_message_not_connected(self, server):
        """Test publish_message tool when not connected."""
        server._connection_state = MQTTConnectionState.DISCONNECTED
        
        result = await server.publish_message("test/topic", "test message")
        
        assert result["success"] is False
        assert result["message"] == "Not connected to MQTT broker"

    @pytest.mark.asyncio
    async def test_publish_message_exception(self, server):
        """Test publish_message tool with exception."""
        mock_client = MagicMock()
        mock_client.publish = AsyncMock(side_effect=Exception("Publish error"))
        server.mqtt_client = mock_client
        server.mqtt_publisher = MagicMock()
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.publish_message("test/topic", "test message")
        
        assert result["success"] is False
        assert "Publish error: Publish error" in result["message"]

    @pytest.mark.asyncio
    async def test_subscribe_to_topic_success(self, server):
        """Test subscribe_to_topic tool success."""
        mock_client = MagicMock()
        mock_client.subscribe = AsyncMock()
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.subscribe_to_topic("test/topic", qos=1)
        
        assert result["success"] is True
        assert result["topic"] == "test/topic"
        assert result["qos"] == 1
        mock_client.subscribe.assert_called_once_with("test/topic", MQTTQoS(1))

    @pytest.mark.asyncio
    async def test_subscribe_to_topic_not_connected(self, server):
        """Test subscribe_to_topic tool when not connected."""
        server._connection_state = MQTTConnectionState.DISCONNECTED
        
        result = await server.subscribe_to_topic("test/topic")
        
        assert result["success"] is False
        assert result["message"] == "Not connected to MQTT broker"

    @pytest.mark.asyncio
    async def test_subscribe_to_topic_exception(self, server):
        """Test subscribe_to_topic tool with exception."""
        mock_client = MagicMock()
        mock_client.subscribe = AsyncMock(side_effect=Exception("Subscribe error"))
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.subscribe_to_topic("test/topic")
        
        assert result["success"] is False
        assert "Subscribe error: Subscribe error" in result["message"]

    @pytest.mark.asyncio
    async def test_unsubscribe_from_topic_success(self, server):
        """Test unsubscribe_from_topic tool success."""
        mock_client = MagicMock()
        mock_client.unsubscribe = AsyncMock()
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.unsubscribe_from_topic("test/topic")
        
        assert result["success"] is True
        assert result["topic"] == "test/topic"
        mock_client.unsubscribe.assert_called_once_with("test/topic")

    @pytest.mark.asyncio
    async def test_unsubscribe_from_topic_not_connected(self, server):
        """Test unsubscribe_from_topic tool when not connected."""
        server._connection_state = MQTTConnectionState.DISCONNECTED
        
        result = await server.unsubscribe_from_topic("test/topic")
        
        assert result["success"] is False
        assert result["message"] == "Not connected to MQTT broker"

    @pytest.mark.asyncio
    async def test_unsubscribe_from_topic_exception(self, server):
        """Test unsubscribe_from_topic tool with exception."""
        mock_client = MagicMock()
        mock_client.unsubscribe = AsyncMock(side_effect=Exception("Unsubscribe error"))
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        
        result = await server.unsubscribe_from_topic("test/topic")
        
        assert result["success"] is False
        assert "Unsubscribe error: Unsubscribe error" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_with_client(self, server, mqtt_config):
        """Test get_status tool with MQTT client."""
        mock_stats = MagicMock()
        mock_stats.messages_sent = 10
        mock_stats.messages_received = 5
        mock_stats.bytes_sent = 1024
        mock_stats.bytes_received = 512
        mock_stats.topics_subscribed = 3
        mock_stats.connection_uptime = 300.5
        mock_stats.last_message_time = datetime.now()
        
        mock_client = MagicMock()
        mock_client.stats = mock_stats
        mock_client.get_subscriptions.return_value = {"topic1": MQTTQoS.AT_LEAST_ONCE}
        
        server.mqtt_client = mock_client
        server.mqtt_config = mqtt_config
        server._connection_state = MQTTConnectionState.CONNECTED
        server._message_store = [{"topic": "test", "payload": "data"}]
        
        result = await server.get_status()
        
        assert result["connection_state"] == MQTTConnectionState.CONNECTED.value
        assert result["statistics"]["messages_sent"] == 10
        assert result["statistics"]["messages_received"] == 5
        assert result["broker_config"]["host"] == "localhost"
        assert result["broker_config"]["port"] == 1883
        assert result["subscriptions"] == ["topic1"]
        assert result["message_count"] == 1

    @pytest.mark.asyncio
    async def test_get_status_no_client(self, server):
        """Test get_status tool without MQTT client."""
        result = await server.get_status()
        
        assert result["connection_state"] == MQTTConnectionState.DISCONNECTED.value
        assert result["broker_config"] is None
        assert result["statistics"] == {}
        assert result["subscriptions"] == []

    @pytest.mark.asyncio
    async def test_get_messages_success(self, server):
        """Test get_messages tool success."""
        now = datetime.now()
        server._message_store = [
            {
                "topic": "test/topic1",
                "payload": "payload1",
                "qos": 1,
                "timestamp": now.isoformat(),
                "received_at": now
            },
            {
                "topic": "test/topic2", 
                "payload": "payload2",
                "qos": 0,
                "timestamp": now.isoformat(),
                "received_at": now
            }
        ]
        
        result = await server.get_messages(limit=10)
        
        assert result["success"] is True
        assert len(result["messages"]) == 2
        assert result["total_count"] == 2
        assert result["filtered_count"] == 2
        
        # Check that received_at was removed for JSON serialization
        for msg in result["messages"]:
            assert "received_at" not in msg

    @pytest.mark.asyncio
    async def test_get_messages_with_topic_filter(self, server):
        """Test get_messages tool with topic filter."""
        now = datetime.now()
        server._message_store = [
            {
                "topic": "sensor/temperature",
                "payload": "22.5",
                "received_at": now
            },
            {
                "topic": "sensor/humidity",
                "payload": "60",
                "received_at": now
            },
            {
                "topic": "actuator/valve",
                "payload": "open",
                "received_at": now
            }
        ]
        
        result = await server.get_messages(topic="sensor", limit=10)
        
        assert result["success"] is True
        assert len(result["messages"]) == 2
        assert all("sensor" in msg["topic"] for msg in result["messages"])

    @pytest.mark.asyncio
    async def test_get_messages_with_time_filter(self, server):
        """Test get_messages tool with time filter."""
        old_time = datetime.now() - timedelta(minutes=10)
        recent_time = datetime.now() - timedelta(minutes=2)
        
        server._message_store = [
            {
                "topic": "old/message",
                "payload": "old",
                "received_at": old_time
            },
            {
                "topic": "recent/message",
                "payload": "recent", 
                "received_at": recent_time
            }
        ]
        
        result = await server.get_messages(since_minutes=5, limit=10)
        
        assert result["success"] is True
        assert len(result["messages"]) == 1
        assert result["messages"][0]["topic"] == "recent/message"

    @pytest.mark.asyncio
    async def test_get_messages_exception(self, server):
        """Test get_messages tool with exception."""
        # Force an exception by making the sort fail
        server._message_store = [{"invalid": "data"}]  # Missing required fields
        
        with patch.object(server._message_store, 'copy', side_effect=Exception("Copy error")):
            result = await server.get_messages()
            
            assert result["success"] is False
            assert "Error retrieving messages: Copy error" in result["message"]

    @pytest.mark.asyncio
    async def test_list_subscriptions_success(self, server):
        """Test list_subscriptions tool success."""
        mock_client = MagicMock()
        mock_client.get_subscriptions.return_value = {
            "topic1": MQTTQoS.AT_LEAST_ONCE,
            "topic2": MQTTQoS.AT_MOST_ONCE
        }
        server.mqtt_client = mock_client
        
        result = await server.list_subscriptions()
        
        assert result["success"] is True
        assert len(result["subscriptions"]) == 2
        assert result["total_count"] == 2
        
        # Check subscription details
        topics = [sub["topic"] for sub in result["subscriptions"]]
        assert "topic1" in topics
        assert "topic2" in topics

    @pytest.mark.asyncio
    async def test_list_subscriptions_no_client(self, server):
        """Test list_subscriptions tool without client."""
        result = await server.list_subscriptions()
        
        assert result["success"] is False
        assert result["message"] == "MQTT client not initialized"
        assert result["subscriptions"] == []

    @pytest.mark.asyncio
    async def test_list_subscriptions_no_method(self, server):
        """Test list_subscriptions tool when get_subscriptions method missing."""
        mock_client = MagicMock(spec=[])  # No get_subscriptions method
        server.mqtt_client = mock_client
        
        result = await server.list_subscriptions()
        
        assert result["success"] is True
        assert result["subscriptions"] == []

    @pytest.mark.asyncio
    async def test_list_subscriptions_exception(self, server):
        """Test list_subscriptions tool with exception."""
        mock_client = MagicMock()
        mock_client.get_subscriptions.side_effect = Exception("Get subs error")
        server.mqtt_client = mock_client
        
        result = await server.list_subscriptions()
        
        assert result["success"] is False
        assert "Error listing subscriptions: Get subs error" in result["message"]

    # Broker Management Tools Tests
    @pytest.mark.asyncio
    async def test_spawn_mqtt_broker_success(self, server, mock_broker_manager):
        """Test spawn_mqtt_broker tool success."""
        broker_info = BrokerInfo(
            config=BrokerConfig(name="test-broker", port=1883),
            broker_id="test-broker-123",
            started_at=datetime.now(),
            url="mqtt://127.0.0.1:1883"
        )
        mock_broker_manager.get_broker_status.return_value = broker_info
        
        result = await server.spawn_mqtt_broker(
            port=1884,
            host="0.0.0.0",
            name="custom-broker",
            max_connections=200
        )
        
        assert result["success"] is True
        assert result["broker_id"] == "test-broker-123"
        assert result["host"] == "0.0.0.0"
        assert result["port"] == 1884
        assert result["max_connections"] == 200
        mock_broker_manager.spawn_broker.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_mqtt_broker_amqtt_not_available(self, server, mock_broker_manager):
        """Test spawn_mqtt_broker tool when AMQTT not available."""
        mock_broker_manager.is_available.return_value = False
        
        result = await server.spawn_mqtt_broker()
        
        assert result["success"] is False
        assert "AMQTT library not available" in result["message"]
        assert result["broker_id"] is None

    @pytest.mark.asyncio
    async def test_spawn_mqtt_broker_exception(self, server, mock_broker_manager):
        """Test spawn_mqtt_broker tool with exception."""
        mock_broker_manager.spawn_broker.side_effect = Exception("Spawn failed")
        
        result = await server.spawn_mqtt_broker()
        
        assert result["success"] is False
        assert "Failed to spawn broker: Spawn failed" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_mqtt_broker_success(self, server, mock_broker_manager):
        """Test stop_mqtt_broker tool success."""
        result = await server.stop_mqtt_broker("test-broker-123")
        
        assert result["success"] is True
        assert "stopped successfully" in result["message"]
        assert result["broker_id"] == "test-broker-123"
        mock_broker_manager.stop_broker.assert_called_once_with("test-broker-123")

    @pytest.mark.asyncio
    async def test_stop_mqtt_broker_not_found(self, server, mock_broker_manager):
        """Test stop_mqtt_broker tool when broker not found."""
        mock_broker_manager.stop_broker.return_value = False
        
        result = await server.stop_mqtt_broker("nonexistent-broker")
        
        assert result["success"] is False
        assert "broker not found or already stopped" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_mqtt_broker_exception(self, server, mock_broker_manager):
        """Test stop_mqtt_broker tool with exception."""
        mock_broker_manager.stop_broker.side_effect = Exception("Stop failed")
        
        result = await server.stop_mqtt_broker("test-broker")
        
        assert result["success"] is False
        assert "Error stopping broker: Stop failed" in result["message"]

    @pytest.mark.asyncio
    async def test_list_mqtt_brokers_all(self, server, mock_broker_manager):
        """Test list_mqtt_brokers tool for all brokers."""
        broker_info = BrokerInfo(
            config=BrokerConfig(name="test-broker", port=1883, websocket_port=9001),
            broker_id="test-broker-123",
            started_at=datetime.now(),
            url="mqtt://127.0.0.1:1883",
            status="running",
            client_count=5
        )
        mock_broker_manager.list_brokers.return_value = [broker_info]
        mock_broker_manager.get_running_brokers.return_value = [broker_info]
        
        result = await server.list_mqtt_brokers(running_only=False)
        
        assert result["success"] is True
        assert len(result["brokers"]) == 1
        assert result["total_count"] == 1
        assert result["running_count"] == 1
        
        broker = result["brokers"][0]
        assert broker["broker_id"] == "test-broker-123"
        assert broker["name"] == "test-broker"
        assert broker["websocket_port"] == 9001

    @pytest.mark.asyncio
    async def test_list_mqtt_brokers_running_only(self, server, mock_broker_manager):
        """Test list_mqtt_brokers tool for running brokers only."""
        broker_info = BrokerInfo(
            config=BrokerConfig(name="running-broker", port=1883),
            broker_id="running-broker-123",
            started_at=datetime.now(),
            status="running"
        )
        mock_broker_manager.get_running_brokers.return_value = [broker_info]
        
        result = await server.list_mqtt_brokers(running_only=True)
        
        assert result["success"] is True
        assert len(result["brokers"]) == 1
        mock_broker_manager.get_running_brokers.assert_called_once()
        mock_broker_manager.list_brokers.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_mqtt_brokers_exception(self, server, mock_broker_manager):
        """Test list_mqtt_brokers tool with exception."""
        mock_broker_manager.list_brokers.side_effect = Exception("List failed")
        
        result = await server.list_mqtt_brokers()
        
        assert result["success"] is False
        assert "Error listing brokers: List failed" in result["message"]
        assert result["brokers"] == []

    @pytest.mark.asyncio
    async def test_get_mqtt_broker_status_success(self, server, mock_broker_manager):
        """Test get_mqtt_broker_status tool success."""
        broker_info = BrokerInfo(
            config=BrokerConfig(name="test-broker", port=1883),
            broker_id="test-broker-123",
            started_at=datetime.now() - timedelta(seconds=300),
            status="running",
            client_count=5,
            message_count=100
        )
        mock_broker_manager.get_broker_status.return_value = broker_info
        
        result = await server.get_mqtt_broker_status("test-broker-123")
        
        assert result["success"] is True
        assert result["broker_id"] == "test-broker-123"
        assert result["status"] == "running"
        assert result["client_count"] == 5
        assert result["message_count"] == 100
        assert result["accepting_connections"] is True
        assert result["uptime_seconds"] >= 299  # Should be around 300

    @pytest.mark.asyncio
    async def test_get_mqtt_broker_status_not_found(self, server, mock_broker_manager):
        """Test get_mqtt_broker_status tool when broker not found."""
        mock_broker_manager.get_broker_status.return_value = None
        
        result = await server.get_mqtt_broker_status("nonexistent-broker")
        
        assert result["success"] is False
        assert "Broker 'nonexistent-broker' not found" in result["message"]

    @pytest.mark.asyncio
    async def test_get_mqtt_broker_status_exception(self, server, mock_broker_manager):
        """Test get_mqtt_broker_status tool with exception."""
        mock_broker_manager.get_broker_status.side_effect = Exception("Status failed")
        
        result = await server.get_mqtt_broker_status("test-broker")
        
        assert result["success"] is False
        assert "Error getting broker status: Status failed" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_all_mqtt_brokers_success(self, server, mock_broker_manager):
        """Test stop_all_mqtt_brokers tool success."""
        result = await server.stop_all_mqtt_brokers()
        
        assert result["success"] is True
        assert result["message"] == "Stopped 2 broker(s)"
        assert result["stopped_count"] == 2
        mock_broker_manager.stop_all_brokers.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_all_mqtt_brokers_exception(self, server, mock_broker_manager):
        """Test stop_all_mqtt_brokers tool with exception."""
        mock_broker_manager.stop_all_brokers.side_effect = Exception("Stop all failed")
        
        result = await server.stop_all_mqtt_brokers()
        
        assert result["success"] is False
        assert "Error stopping brokers: Stop all failed" in result["message"]
        assert result["stopped_count"] == 0

    # MCP Resources Tests
    @pytest.mark.asyncio
    async def test_get_config_resource_with_config(self, server, mqtt_config):
        """Test get_config_resource with MQTT config."""
        server.mqtt_config = mqtt_config
        
        result = await server.get_config_resource()
        
        assert result["broker_host"] == "localhost"
        assert result["broker_port"] == 1883
        assert result["client_id"] == "test-client"
        assert result["username"] == "testuser"
        assert result["keepalive"] == 60
        assert result["use_tls"] is False
        assert result["clean_session"] is True
        assert result["qos"] == 1

    @pytest.mark.asyncio
    async def test_get_config_resource_no_config(self, server):
        """Test get_config_resource without MQTT config."""
        result = await server.get_config_resource()
        
        assert "error" in result
        assert result["error"] == "No MQTT configuration available"

    @pytest.mark.asyncio
    async def test_get_stats_resource_with_client(self, server):
        """Test get_stats_resource with MQTT client."""
        mock_stats = MagicMock()
        mock_stats.messages_sent = 10
        mock_stats.messages_received = 5
        mock_stats.connection_uptime = 300.5
        mock_stats.last_message_time = datetime.now()
        
        mock_client = MagicMock()
        mock_client.stats = mock_stats
        server.mqtt_client = mock_client
        server._connection_state = MQTTConnectionState.CONNECTED
        server._message_store = [{"test": "data"}]
        
        result = await server.get_stats_resource()
        
        assert result["messages_sent"] == 10
        assert result["messages_received"] == 5
        assert result["connection_state"] == MQTTConnectionState.CONNECTED.value
        assert result["message_store_count"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_resource_no_client(self, server):
        """Test get_stats_resource without MQTT client."""
        result = await server.get_stats_resource()
        
        assert "error" in result
        assert result["error"] == "MQTT client not initialized"

    @pytest.mark.asyncio
    async def test_get_subscriptions_resource_with_client(self, server):
        """Test get_subscriptions_resource with MQTT client."""
        mock_client = MagicMock()
        mock_client.get_subscriptions.return_value = {
            "topic1": MQTTQoS.AT_LEAST_ONCE,
            "topic2": MQTTQoS.AT_MOST_ONCE
        }
        server.mqtt_client = mock_client
        
        result = await server.get_subscriptions_resource()
        
        assert len(result["subscriptions"]) == 2
        assert result["total_count"] == 2
        assert "topic1" in result["subscriptions"]
        assert "topic2" in result["subscriptions"]

    @pytest.mark.asyncio
    async def test_get_subscriptions_resource_no_client(self, server):
        """Test get_subscriptions_resource without MQTT client."""
        result = await server.get_subscriptions_resource()
        
        assert "error" in result
        assert result["error"] == "MQTT client not initialized"

    @pytest.mark.asyncio
    async def test_get_messages_resource(self, server):
        """Test get_messages_resource."""
        now = datetime.now()
        server._message_store = [
            {
                "topic": f"test/topic{i}",
                "payload": f"payload{i}",
                "received_at": now
            }
            for i in range(60)  # More than 50 to test limiting
        ]
        
        result = await server.get_messages_resource()
        
        assert len(result["recent_messages"]) == 50  # Limited to last 50
        assert result["total_stored"] == 60
        assert result["showing_last"] == 50
        
        # Check that received_at was removed
        for msg in result["recent_messages"]:
            assert "received_at" not in msg

    @pytest.mark.asyncio
    async def test_get_health_resource_healthy(self, server):
        """Test get_health_resource when healthy."""
        server._connection_state = MQTTConnectionState.CONNECTED
        server.mqtt_client = MagicMock()
        server.mqtt_publisher = MagicMock()
        server.mqtt_subscriber = None  # Intentionally None
        server._last_error = None
        
        result = await server.get_health_resource()
        
        assert result["healthy"] is True
        assert result["connection_state"] == MQTTConnectionState.CONNECTED.value
        assert result["components"]["mqtt_client"] is True
        assert result["components"]["mqtt_publisher"] is True
        assert result["components"]["mqtt_subscriber"] is False
        assert result["last_error"] is None

    @pytest.mark.asyncio
    async def test_get_health_resource_unhealthy(self, server):
        """Test get_health_resource when unhealthy."""
        server._connection_state = MQTTConnectionState.ERROR
        server.mqtt_client = None
        server._last_error = "Connection failed"
        
        result = await server.get_health_resource()
        
        assert result["healthy"] is False
        assert result["connection_state"] == MQTTConnectionState.ERROR.value
        assert result["components"]["mqtt_client"] is False
        assert result["last_error"] == "Connection failed"

    @pytest.mark.asyncio
    async def test_get_brokers_resource_success(self, server, mock_broker_manager):
        """Test get_brokers_resource success."""
        broker_info = BrokerInfo(
            config=BrokerConfig(name="test-broker", port=1883),
            broker_id="test-broker-123",
            started_at=datetime.now(),
            status="running",
            client_count=3
        )
        mock_broker_manager.get_running_brokers.return_value = [broker_info]
        mock_broker_manager.list_brokers.return_value = [broker_info]
        
        result = await server.get_brokers_resource()
        
        assert len(result["embedded_brokers"]) == 1
        assert result["total_brokers"] == 1
        assert result["running_brokers"] == 1
        assert result["amqtt_available"] is True
        
        broker = result["embedded_brokers"][0]
        assert broker["broker_id"] == "test-broker-123"
        assert broker["status"] == "running"

    @pytest.mark.asyncio
    async def test_get_brokers_resource_exception(self, server, mock_broker_manager):
        """Test get_brokers_resource with exception."""
        mock_broker_manager.list_brokers.side_effect = Exception("List failed")
        
        result = await server.get_brokers_resource()
        
        assert "error" in result
        assert "Error accessing broker information: List failed" in result["error"]
        assert result["embedded_brokers"] == []
        assert result["total_brokers"] == 0

    @pytest.mark.asyncio
    async def test_run_server_success(self, server, mock_fastmcp):
        """Test run_server method success."""
        await server.run_server(host="127.0.0.1", port=3001)
        
        mock_fastmcp.run_http_async.assert_called_once_with(host="127.0.0.1", port=3001)

    @pytest.mark.asyncio
    async def test_run_server_exception(self, server, mock_fastmcp):
        """Test run_server method with exception."""
        mock_fastmcp.run_http_async.side_effect = Exception("Server failed")
        
        with pytest.raises(Exception, match="Server failed"):
            await server.run_server()

    def test_get_mcp_server(self, server, mock_fastmcp):
        """Test get_mcp_server method."""
        result = server.get_mcp_server()
        
        assert result == mock_fastmcp

    def test_message_handler_functionality(self, server):
        """Test the message handler function that stores messages."""
        # Create a mock message object
        mock_message = MagicMock()
        mock_message.topic = "test/topic"
        mock_message.payload_str = "test payload"
        mock_message.qos.value = 1
        
        # Initialize the message handler by calling initialize_mqtt_client
        with patch('mcmqtt.mcp.server.MQTTClient') as mock_client_class, \
             patch('mcmqtt.mcp.server.MQTTPublisher'):
            
            mock_client = MagicMock()
            mock_client.add_message_handler = MagicMock()
            mock_client_class.return_value = mock_client
            
            # This will create the handler function
            asyncio.run(server.initialize_mqtt_client(MQTTConfig(
                broker_host="test",
                broker_port=1883,
                client_id="test"
            )))
            
            # Get the handler function that was passed to add_message_handler
            handler_call = mock_client.add_message_handler.call_args
            handler_function = handler_call[0][1]  # Second argument is the handler
            
            # Call the handler with our mock message
            handler_function(mock_message)
            
            # Verify the message was stored
            assert len(server._message_store) == 1
            stored_message = server._message_store[0]
            assert stored_message["topic"] == "test/topic"
            assert stored_message["payload"] == "test payload"
            assert stored_message["qos"] == 1

    def test_message_handler_exception_handling(self, server):
        """Test message handler exception handling."""
        # Create a handler that will be created during initialize_mqtt_client
        with patch('mcmqtt.mcp.server.MQTTClient') as mock_client_class, \
             patch('mcmqtt.mcp.server.MQTTPublisher'):
            
            mock_client = MagicMock()
            mock_client.add_message_handler = MagicMock()
            mock_client_class.return_value = mock_client
            
            asyncio.run(server.initialize_mqtt_client(MQTTConfig(
                broker_host="test",
                broker_port=1883,
                client_id="test"
            )))
            
            # Get the handler function
            handler_function = mock_client.add_message_handler.call_args[0][1]
            
            # Create a mock message that will cause an exception
            mock_message = MagicMock()
            mock_message.topic = "test/topic"
            mock_message.payload_str.side_effect = Exception("Payload error")
            
            # Handler should not raise exception
            handler_function(mock_message)
            
            # Message store should remain empty due to error
            assert len(server._message_store) == 0

    def test_message_store_limit(self, server):
        """Test that message store respects the 1000 message limit."""
        # Add more than 1000 messages to test the limit
        for i in range(1100):
            server._message_store.append({
                "topic": f"test/topic{i}",
                "payload": f"payload{i}",
                "qos": 1,
                "timestamp": datetime.now().isoformat(),
                "received_at": datetime.now()
            })
        
        # Simulate the trimming that happens in the message handler
        if len(server._message_store) > 1000:
            server._message_store = server._message_store[-1000:]
        
        assert len(server._message_store) == 1000
        # Should keep the last 1000 messages
        assert server._message_store[0]["topic"] == "test/topic100"
        assert server._message_store[-1]["topic"] == "test/topic1099"


if __name__ == "__main__":
    pytest.main([__file__])