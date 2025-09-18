"""Unit tests for MQTT Broker Middleware functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from mcmqtt.middleware.broker_middleware import MQTTBrokerMiddleware
from mcmqtt.broker import BrokerManager, BrokerConfig, BrokerInfo


class TestMQTTBrokerMiddleware:
    """Test cases for MQTTBrokerMiddleware class."""

    @pytest.fixture
    def middleware(self):
        """Create a middleware instance."""
        middleware = MQTTBrokerMiddleware(
            auto_spawn=True,
            cleanup_idle_after=300,
            max_brokers_per_session=5
        )
        yield middleware
        # Cleanup after test
        if middleware._cleanup_task and not middleware._cleanup_task.done():
            middleware._cleanup_task.cancel()

    @pytest.fixture
    def mock_context(self):
        """Create a mock middleware context."""
        context = MagicMock()
        context.session_id = "test_session"
        context.source = "test_source"
        context.message = MagicMock()
        context.fastmcp_context = MagicMock()
        return context

    @pytest.fixture
    def mock_broker_manager(self):
        """Create a mock broker manager."""
        manager = MagicMock(spec=BrokerManager)
        manager.spawn_broker = AsyncMock()
        manager.get_broker_status = AsyncMock()
        manager.stop_broker = AsyncMock()
        return manager

    @pytest.fixture
    def sample_broker_info(self):
        """Create a sample broker info."""
        return BrokerInfo(
            config=BrokerConfig(name="test", host="127.0.0.1", port=1883),
            broker_id="test_broker",
            started_at=datetime.now(),
            status="running",
            client_count=0,
            message_count=0,
            url="mqtt://127.0.0.1:1883"
        )

    def test_middleware_initialization(self):
        """Test middleware initialization with default values."""
        middleware = MQTTBrokerMiddleware()
        
        assert middleware.auto_spawn is True
        assert middleware.cleanup_idle_after == 300
        assert middleware.max_brokers_per_session == 5
        assert middleware.broker_manager is None
        assert middleware._session_brokers == {}
        assert middleware._session_last_activity == {}
        assert middleware._cleanup_task is None
        assert middleware._cleanup_started is False

    def test_middleware_initialization_custom_values(self):
        """Test middleware initialization with custom values."""
        middleware = MQTTBrokerMiddleware(
            auto_spawn=False,
            cleanup_idle_after=600,
            max_brokers_per_session=10
        )
        
        assert middleware.auto_spawn is False
        assert middleware.cleanup_idle_after == 600
        assert middleware.max_brokers_per_session == 10

    def test_get_session_id_from_session_id(self, middleware, mock_context):
        """Test getting session ID from context session_id."""
        mock_context.session_id = "custom_session"
        
        session_id = middleware._get_session_id(mock_context)
        assert session_id == "custom_session"

    def test_get_session_id_from_source(self, middleware, mock_context):
        """Test getting session ID from context source."""
        mock_context.session_id = None
        mock_context.source = "test_source"
        
        session_id = middleware._get_session_id(mock_context)
        assert session_id.startswith("session_")
        assert isinstance(session_id, str)

    def test_get_session_id_default(self, middleware, mock_context):
        """Test getting default session ID."""
        mock_context.session_id = None
        mock_context.source = None
        
        session_id = middleware._get_session_id(mock_context)
        assert session_id == "default"

    def test_start_cleanup_task_no_event_loop(self, middleware):
        """Test starting cleanup task when no event loop is running."""
        # Should not raise an exception
        middleware._start_cleanup_task()
        
        # Task should not be created without event loop
        assert middleware._cleanup_task is None
        assert middleware._cleanup_started is False

    @pytest.mark.asyncio
    async def test_start_cleanup_task_with_event_loop(self, middleware):
        """Test starting cleanup task with active event loop."""
        with patch('asyncio.create_task') as mock_create_task:
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task
            
            middleware._start_cleanup_task()
            
            mock_create_task.assert_called_once()
            assert middleware._cleanup_task == mock_task
            assert middleware._cleanup_started is True

    @pytest.mark.asyncio
    async def test_cleanup_idle_brokers_basic(self, middleware):
        """Test basic cleanup of idle brokers."""
        # Add an old session
        old_time = datetime.now() - timedelta(seconds=400)  # Older than cleanup_idle_after
        middleware._session_last_activity["old_session"] = old_time
        middleware._session_brokers["old_session"] = [{"broker_id": "old_broker"}]
        
        # Mock the cleanup method
        middleware._cleanup_session_brokers = AsyncMock()
        
        # Run one iteration of cleanup
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = [None, asyncio.CancelledError()]  # Run once then stop
            
            await middleware._cleanup_idle_brokers()
            
            middleware._cleanup_session_brokers.assert_called_once_with("old_session")

    @pytest.mark.asyncio
    async def test_cleanup_idle_brokers_exception_handling(self, middleware):
        """Test cleanup task handles exceptions gracefully."""
        # Set up middleware with old session data to trigger cleanup
        old_time = datetime.now() - timedelta(seconds=400)  # Older than cleanup_idle_after (300s)
        middleware._session_last_activity["old_session"] = old_time
        middleware._cleanup_session_brokers = AsyncMock(side_effect=Exception("Test error"))
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with patch('mcmqtt.middleware.broker_middleware.logger') as mock_logger:
                mock_sleep.side_effect = [None, asyncio.CancelledError()]
                
                await middleware._cleanup_idle_brokers()
                
                mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_session_brokers(self, middleware):
        """Test cleaning up brokers for a specific session."""
        # Setup session with brokers
        middleware._session_brokers["test_session"] = [
            {"broker_id": "broker1"},
            {"broker_id": "broker2"}
        ]
        middleware._session_last_activity["test_session"] = datetime.now()
        
        await middleware._cleanup_session_brokers("test_session")
        
        assert "test_session" not in middleware._session_brokers
        assert "test_session" not in middleware._session_last_activity

    @pytest.mark.asyncio
    async def test_cleanup_session_brokers_nonexistent(self, middleware):
        """Test cleaning up non-existent session doesn't crash."""
        # Should not raise an exception
        await middleware._cleanup_session_brokers("nonexistent_session")

    def test_is_mqtt_tool(self, middleware):
        """Test MQTT tool detection."""
        # MQTT tools
        assert middleware._is_mqtt_tool("mqtt_connect") is True
        assert middleware._is_mqtt_tool("mqtt_publish") is True
        assert middleware._is_mqtt_tool("mqtt_subscribe") is True
        assert middleware._is_mqtt_tool("tools/call") is True
        
        # Non-MQTT tools
        assert middleware._is_mqtt_tool("some_other_tool") is False
        assert middleware._is_mqtt_tool("") is False

    def test_needs_broker(self, middleware):
        """Test broker requirement detection."""
        # Tools that need brokers
        assert middleware._needs_broker("mqtt_connect") is True
        assert middleware._needs_broker("mqtt_publish") is True
        assert middleware._needs_broker("mqtt_subscribe") is True
        
        # Tools that don't need brokers
        assert middleware._needs_broker("mqtt_status") is False
        assert middleware._needs_broker("mqtt_disconnect") is False
        assert middleware._needs_broker("other_tool") is False

    @pytest.mark.asyncio
    async def test_ensure_broker_available_existing_broker(self, middleware, mock_context, mock_broker_manager, sample_broker_info):
        """Test ensuring broker availability when one already exists."""
        # Setup existing broker
        middleware._session_brokers["test_session"] = [
            {"broker_id": "existing_broker", "url": "mqtt://127.0.0.1:1883"}
        ]
        
        mock_broker_manager.get_broker_status.return_value = sample_broker_info
        
        broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
        
        assert broker_id == "existing_broker"
        assert "test_session" in middleware._session_last_activity

    @pytest.mark.asyncio
    async def test_ensure_broker_available_spawn_new(self, middleware, mock_context, mock_broker_manager, sample_broker_info):
        """Test spawning new broker when none exists."""
        mock_broker_manager.spawn_broker.return_value = "new_broker"
        mock_broker_manager.get_broker_status.return_value = sample_broker_info
        
        broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
        
        assert broker_id == "new_broker"
        mock_broker_manager.spawn_broker.assert_called_once()
        
        # Check broker was tracked
        assert "test_session" in middleware._session_brokers
        assert len(middleware._session_brokers["test_session"]) == 1
        assert middleware._session_brokers["test_session"][0]["broker_id"] == "new_broker"

    @pytest.mark.asyncio
    async def test_ensure_broker_available_auto_spawn_disabled(self, middleware, mock_context, mock_broker_manager):
        """Test broker availability when auto_spawn is disabled."""
        middleware.auto_spawn = False
        
        broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
        
        assert broker_id is None
        mock_broker_manager.spawn_broker.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_broker_available_max_brokers_exceeded(self, middleware, mock_context, mock_broker_manager):
        """Test broker availability when max brokers limit is reached."""
        middleware.max_brokers_per_session = 2
        
        # Setup session with max brokers
        middleware._session_brokers["test_session"] = [
            {"broker_id": "broker1"},
            {"broker_id": "broker2"}
        ]
        
        broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
        
        assert broker_id is None
        mock_broker_manager.spawn_broker.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_broker_available_spawn_failure(self, middleware, mock_context, mock_broker_manager):
        """Test handling broker spawn failure."""
        mock_broker_manager.spawn_broker.side_effect = Exception("Spawn failed")
        
        with patch('mcmqtt.middleware.broker_middleware.logger') as mock_logger:
            broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
            
            assert broker_id is None
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_tool_call_mqtt_connect_injection(self, middleware, mock_context, mock_broker_manager, sample_broker_info):
        """Test automatic broker injection for mqtt_connect."""
        # Setup context for mqtt_connect tool
        mock_context.message.params = {
            "name": "mqtt_connect",
            "arguments": {}  # Empty arguments, should be injected
        }
        
        # Mock server with broker manager
        mock_server = MagicMock()
        mock_server.broker_manager = mock_broker_manager
        mock_context.fastmcp_context.server = mock_server
        
        # Mock broker availability
        mock_broker_manager.spawn_broker.return_value = "auto_broker"
        mock_broker_manager.get_broker_status.return_value = sample_broker_info
        
        # Mock call_next
        call_next = AsyncMock(return_value={"status": "success"})
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        # Check that broker details were injected
        arguments = mock_context.message.params["arguments"]
        assert arguments["broker_host"] == "127.0.0.1"
        assert arguments["broker_port"] == 1883
        
        call_next.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_on_tool_call_no_injection_when_provided(self, middleware, mock_context, mock_broker_manager):
        """Test no injection when broker details already provided."""
        # Setup context with existing broker details
        mock_context.message.params = {
            "name": "mqtt_connect",
            "arguments": {
                "broker_host": "existing.broker.com",
                "broker_port": 8883
            }
        }
        
        # Mock server with broker manager
        mock_server = MagicMock()
        mock_server.broker_manager = mock_broker_manager
        mock_context.fastmcp_context.server = mock_server
        
        call_next = AsyncMock(return_value={"status": "success"})
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        # Check that existing details weren't overridden
        arguments = mock_context.message.params["arguments"]
        assert arguments["broker_host"] == "existing.broker.com"
        assert arguments["broker_port"] == 8883

    @pytest.mark.asyncio
    async def test_on_tool_call_non_mqtt_tool(self, middleware, mock_context):
        """Test tool call handling for non-MQTT tools."""
        mock_context.message.params = {
            "name": "some_other_tool",
            "arguments": {}
        }
        
        call_next = AsyncMock(return_value={"status": "success"})
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        assert result == {"status": "success"}
        call_next.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_on_tool_call_response_enhancement(self, middleware, mock_context):
        """Test enhancing tool responses with broker information."""
        # Setup session with brokers
        middleware._session_brokers["test_session"] = [
            {"broker_id": "broker1"},
            {"broker_id": "broker2"}
        ]
        
        mock_context.message.params = {"name": "mqtt_status"}
        
        # Mock server
        mock_server = MagicMock()
        mock_context.fastmcp_context.server = mock_server
        mock_server.broker_manager = MagicMock()
        
        # Mock response content
        mock_content = MagicMock()
        mock_content.text = "{'status': 'connected'}"
        
        call_next = AsyncMock(return_value={
            "content": [mock_content]
        })
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        # Verify broker info was attempted to be added
        call_next.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_on_tool_call_no_server_context(self, middleware, mock_context):
        """Test tool call when no server context is available."""
        mock_context.fastmcp_context = None
        mock_context.message.params = {"name": "mqtt_connect", "arguments": {}}
        
        call_next = AsyncMock(return_value={"status": "success"})
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        assert result == {"status": "success"}
        call_next.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_on_tool_call_no_broker_manager(self, middleware, mock_context):
        """Test tool call when server has no broker manager."""
        mock_server = MagicMock()
        # No broker_manager attribute
        mock_context.fastmcp_context.server = mock_server
        mock_context.message.params = {"name": "mqtt_connect", "arguments": {}}
        
        call_next = AsyncMock(return_value={"status": "success"})
        
        result = await middleware.on_tool_call(mock_context, call_next)
        
        assert result == {"status": "success"}
        call_next.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_on_session_end(self, middleware, mock_context):
        """Test session end cleanup."""
        # Setup session with brokers
        middleware._session_brokers["test_session"] = [{"broker_id": "broker1"}]
        middleware._session_last_activity["test_session"] = datetime.now()
        
        call_next = AsyncMock(return_value={"status": "session_ended"})
        
        result = await middleware.on_session_end(mock_context, call_next)
        
        # Verify session was cleaned up
        assert "test_session" not in middleware._session_brokers
        assert "test_session" not in middleware._session_last_activity
        
        call_next.assert_called_once_with(mock_context)
        assert result == {"status": "session_ended"}

    def test_middleware_deletion(self, middleware):
        """Test middleware cleanup on deletion."""
        # Create a mock task
        mock_task = MagicMock()
        mock_task.done.return_value = False
        middleware._cleanup_task = mock_task
        
        # Trigger deletion
        middleware.__del__()
        
        mock_task.cancel.assert_called_once()

    def test_middleware_deletion_no_task(self, middleware):
        """Test middleware deletion when no cleanup task exists."""
        middleware._cleanup_task = None
        
        # Should not raise an exception
        middleware.__del__()

    def test_middleware_deletion_task_done(self, middleware):
        """Test middleware deletion when cleanup task is already done."""
        mock_task = MagicMock()
        mock_task.done.return_value = True
        middleware._cleanup_task = mock_task
        
        middleware.__del__()
        
        # Should not try to cancel finished task
        mock_task.cancel.assert_not_called()

    @pytest.mark.asyncio
    async def test_complex_scenario_multiple_sessions(self, middleware, mock_broker_manager, sample_broker_info):
        """Test complex scenario with multiple sessions and brokers."""
        mock_broker_manager.spawn_broker.return_value = "new_broker"
        mock_broker_manager.get_broker_status.return_value = sample_broker_info
        
        # Create contexts for different sessions
        context1 = MagicMock()
        context1.session_id = "session1"
        context1.source = "source1"
        
        context2 = MagicMock()
        context2.session_id = "session2"
        context2.source = "source2"
        
        # Ensure brokers for both sessions
        broker1 = await middleware._ensure_broker_available(context1, mock_broker_manager)
        broker2 = await middleware._ensure_broker_available(context2, mock_broker_manager)
        
        assert broker1 == "new_broker"
        assert broker2 == "new_broker"
        assert len(middleware._session_brokers) == 2
        assert "session1" in middleware._session_brokers
        assert "session2" in middleware._session_brokers

    @pytest.mark.asyncio
    async def test_broker_status_check_failure(self, middleware, mock_context, mock_broker_manager):
        """Test handling broker status check failure."""
        # Setup existing broker
        middleware._session_brokers["test_session"] = [
            {"broker_id": "existing_broker"}
        ]
        
        # Mock status check failure
        mock_broker_manager.get_broker_status.return_value = None
        mock_broker_manager.spawn_broker.return_value = "new_broker"
        
        # Create a new broker info for spawn
        new_broker_info = BrokerInfo(
            config=BrokerConfig(name="new", host="127.0.0.1", port=1884),
            broker_id="new_broker",
            started_at=datetime.now(),
            status="running",
            client_count=0,
            message_count=0,
            url="mqtt://127.0.0.1:1884"
        )
        mock_broker_manager.get_broker_status.side_effect = [None, new_broker_info]
        
        broker_id = await middleware._ensure_broker_available(mock_context, mock_broker_manager)
        
        assert broker_id == "new_broker"
        mock_broker_manager.spawn_broker.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])