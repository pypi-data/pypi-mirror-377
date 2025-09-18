"""
Comprehensive unit tests for server runner modules.

Tests STDIO and HTTP server execution functionality.
"""

import pytest
import sys
from unittest.mock import Mock, AsyncMock, patch

from mcmqtt.server.runners import run_stdio_server, run_http_server


class TestRunStdioServer:
    """Test STDIO server runner functionality."""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock MQTT server."""
        server = Mock()
        server.mqtt_config = None
        server._last_error = None
        server.initialize_mqtt_client = AsyncMock(return_value=True)
        server.connect_mqtt = AsyncMock()
        server.disconnect_mqtt = AsyncMock()
        server.get_mcp_server = Mock()
        
        # Mock the FastMCP instance
        mock_mcp = Mock()
        mock_mcp.run_stdio_async = AsyncMock()
        server.get_mcp_server.return_value = mock_mcp
        
        return server
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_no_auto_connect(self, mock_server):
        """Test STDIO server without auto-connect."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=False)
            
            # Verify no MQTT operations
            mock_server.initialize_mqtt_client.assert_not_called()
            mock_server.connect_mqtt.assert_not_called()
            
            # Verify MCP server started
            mock_server.get_mcp_server.assert_called_once()
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_stdio_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_auto_connect_success(self, mock_server):
        """Test STDIO server with successful auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'localhost'
        mock_config.broker_port = 1883
        mock_server.mqtt_config = mock_config
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            # Verify MQTT operations
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()
            
            # Verify logging
            logger.info.assert_any_call(
                "Auto-connecting to MQTT broker",
                broker="localhost:1883"
            )
            logger.info.assert_any_call("Connected to MQTT broker")
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_auto_connect_failure(self, mock_server):
        """Test STDIO server with failed auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'localhost'
        mock_config.broker_port = 1883
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client = AsyncMock(return_value=False)
        mock_server._last_error = "Connection failed"
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            # Verify MQTT initialization attempted but connect not called
            mock_server.initialize_mqtt_client.assert_called_once()
            mock_server.connect_mqtt.assert_not_called()
            
            # Verify warning logged
            logger.warning.assert_called_once_with(
                "Failed to connect to MQTT broker",
                error="Connection failed"
            )
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_no_mqtt_config(self, mock_server):
        """Test STDIO server with no MQTT config and auto-connect."""
        mock_server.mqtt_config = None
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, auto_connect=True)
            
            # Verify no MQTT operations when no config
            mock_server.initialize_mqtt_client.assert_not_called()
            mock_server.connect_mqtt.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_keyboard_interrupt(self, mock_server):
        """Test STDIO server handling KeyboardInterrupt."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_stdio_async.side_effect = KeyboardInterrupt()
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server)
            
            # Verify cleanup
            mock_server.disconnect_mqtt.assert_called_once()
            logger.info.assert_called_with("Server shutting down...")
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_exception(self, mock_server):
        """Test STDIO server handling general exception."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_stdio_async.side_effect = Exception("Server error")
        
        with patch('structlog.get_logger') as mock_logger, \
             patch('sys.exit') as mock_exit:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server)
            
            # Verify cleanup and exit
            mock_server.disconnect_mqtt.assert_called_once()
            logger.error.assert_called_with("Server error", error="Server error")
            mock_exit.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_run_stdio_server_with_log_file(self, mock_server):
        """Test STDIO server with log file parameter."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_stdio_server(mock_server, log_file="/tmp/test.log")
            
            # Should still run normally (log_file is passed but not used in runner)
            mock_server.get_mcp_server.assert_called_once()
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_stdio_async.assert_called_once()


class TestRunHttpServer:
    """Test HTTP server runner functionality."""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock MQTT server."""
        server = Mock()
        server.mqtt_config = None
        server._last_error = None
        server.initialize_mqtt_client = AsyncMock(return_value=True)
        server.connect_mqtt = AsyncMock()
        server.disconnect_mqtt = AsyncMock()
        server.get_mcp_server = Mock()
        
        # Mock the FastMCP instance
        mock_mcp = Mock()
        mock_mcp.run_http_async = AsyncMock()
        server.get_mcp_server.return_value = mock_mcp
        
        return server
    
    @pytest.mark.asyncio
    async def test_run_http_server_default_params(self, mock_server):
        """Test HTTP server with default parameters."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify MCP server started with defaults
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_http_async.assert_called_once_with(host="0.0.0.0", port=3000)
    
    @pytest.mark.asyncio
    async def test_run_http_server_custom_params(self, mock_server):
        """Test HTTP server with custom parameters."""
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, host="127.0.0.1", port=8080)
            
            # Verify MCP server started with custom params
            mock_mcp = mock_server.get_mcp_server.return_value
            mock_mcp.run_http_async.assert_called_once_with(host="127.0.0.1", port=8080)
    
    @pytest.mark.asyncio
    async def test_run_http_server_auto_connect_success(self, mock_server):
        """Test HTTP server with successful auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'mqtt.example.com'
        mock_config.broker_port = 8883
        mock_server.mqtt_config = mock_config
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, auto_connect=True)
            
            # Verify MQTT connection
            mock_server.initialize_mqtt_client.assert_called_once_with(mock_config)
            mock_server.connect_mqtt.assert_called_once()
            
            # Verify logging
            logger.info.assert_any_call(
                "Auto-connecting to MQTT broker",
                broker="mqtt.example.com:8883"
            )
            logger.info.assert_any_call("Connected to MQTT broker")
    
    @pytest.mark.asyncio
    async def test_run_http_server_auto_connect_failure(self, mock_server):
        """Test HTTP server with failed auto-connect."""
        mock_config = Mock()
        mock_config.broker_host = 'mqtt.example.com'
        mock_config.broker_port = 8883
        mock_server.mqtt_config = mock_config
        mock_server.initialize_mqtt_client = AsyncMock(return_value=False)
        mock_server._last_error = "Connection failed"
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, auto_connect=True)
            
            # Verify MQTT initialization attempted but connect not called
            mock_server.initialize_mqtt_client.assert_called_once()
            mock_server.connect_mqtt.assert_not_called()
            
            # Verify warning logged
            logger.warning.assert_called_once_with(
                "Failed to connect to MQTT broker",
                error="Connection failed"
            )
    
    @pytest.mark.asyncio
    async def test_run_http_server_no_mqtt_config(self, mock_server):
        """Test HTTP server with no MQTT config and auto-connect."""
        mock_server.mqtt_config = None
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server, auto_connect=True)
            
            # Verify no MQTT operations when no config
            mock_server.initialize_mqtt_client.assert_not_called()
            mock_server.connect_mqtt.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_run_http_server_keyboard_interrupt(self, mock_server):
        """Test HTTP server handling KeyboardInterrupt."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_http_async.side_effect = KeyboardInterrupt()
        
        with patch('structlog.get_logger') as mock_logger:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify cleanup
            mock_server.disconnect_mqtt.assert_called_once()
            logger.info.assert_called_with("Server shutting down...")
    
    @pytest.mark.asyncio
    async def test_run_http_server_exception(self, mock_server):
        """Test HTTP server handling general exception."""
        mock_mcp = mock_server.get_mcp_server.return_value
        mock_mcp.run_http_async.side_effect = Exception("HTTP error")
        
        with patch('structlog.get_logger') as mock_logger, \
             patch('sys.exit') as mock_exit:
            logger = Mock()
            mock_logger.return_value = logger
            
            await run_http_server(mock_server)
            
            # Verify cleanup and exit
            mock_server.disconnect_mqtt.assert_called_once()
            logger.error.assert_called_with("Server error", error="HTTP error")
            mock_exit.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_run_http_server_extreme_ports(self, mock_server):
        """Test HTTP server with extreme port values."""
        test_cases = [
            (1, "0.0.0.0"),      # Minimum port
            (65535, "0.0.0.0"),  # Maximum port
            (8080, "127.0.0.1"), # Common development port
            (443, "0.0.0.0"),    # HTTPS port
            (80, "0.0.0.0")      # HTTP port
        ]
        
        for port, host in test_cases:
            with patch('structlog.get_logger') as mock_logger:
                logger = Mock()
                mock_logger.return_value = logger
                
                await run_http_server(mock_server, host=host, port=port)
                
                # Verify MCP server called with correct parameters
                mock_mcp = mock_server.get_mcp_server.return_value
                mock_mcp.run_http_async.assert_called_with(host=host, port=port)
                
                # Reset for next test
                mock_server.reset_mock()
    
    @pytest.mark.asyncio
    async def test_run_http_server_various_hosts(self, mock_server):
        """Test HTTP server with various host configurations."""
        test_hosts = [
            "0.0.0.0",      # All interfaces
            "127.0.0.1",    # Localhost
            "localhost",    # Localhost name
            "192.168.1.1",  # Private IP
            "::"            # IPv6 all interfaces
        ]
        
        for host in test_hosts:
            with patch('structlog.get_logger') as mock_logger:
                logger = Mock()
                mock_logger.return_value = logger
                
                await run_http_server(mock_server, host=host, port=3000)
                
                # Verify MCP server called with correct host
                mock_mcp = mock_server.get_mcp_server.return_value
                mock_mcp.run_http_async.assert_called_with(host=host, port=3000)
                
                # Reset for next test
                mock_server.reset_mock()