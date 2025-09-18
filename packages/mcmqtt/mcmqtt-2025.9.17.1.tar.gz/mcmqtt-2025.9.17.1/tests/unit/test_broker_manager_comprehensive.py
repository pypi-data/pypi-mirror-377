"""Comprehensive unit tests for Broker Manager functionality."""

import asyncio
import socket
import tempfile
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from datetime import datetime
from pathlib import Path

from mcmqtt.broker.manager import BrokerManager, BrokerConfig, BrokerInfo, AMQTT_AVAILABLE


class TestBrokerManagerComprehensive:
    """Comprehensive test cases for BrokerManager class."""

    @pytest.fixture
    def broker_config(self):
        """Create a test broker configuration."""
        return BrokerConfig(
            port=1883,
            host="127.0.0.1",
            name="test-broker",
            max_connections=50
        )

    @pytest.fixture
    def manager(self):
        """Create a broker manager instance."""
        return BrokerManager()

    def test_manager_initialization(self, manager):
        """Test broker manager initialization."""
        assert manager._brokers == {}
        assert manager._broker_infos == {}
        assert manager._broker_tasks == {}
        assert manager._next_broker_id == 1

    def test_is_available_when_amqtt_available(self, manager):
        """Test is_available when AMQTT is available."""
        with patch('mcmqtt.broker.manager.AMQTT_AVAILABLE', True):
            assert manager.is_available() is True

    def test_is_available_when_amqtt_not_available(self, manager):
        """Test is_available when AMQTT is not available."""
        with patch('mcmqtt.broker.manager.AMQTT_AVAILABLE', False):
            assert manager.is_available() is False

    def test_find_free_port_success(self, manager):
        """Test finding a free port successfully."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None
            
            port = manager._find_free_port(1883)
            
            assert port == 1883
            mock_sock.bind.assert_called_once_with(('127.0.0.1', 1883))

    def test_find_free_port_first_port_taken(self, manager):
        """Test finding free port when first port is taken."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            
            # First port fails, second succeeds
            mock_sock.bind.side_effect = [OSError("Port in use"), None]
            
            port = manager._find_free_port(1883)
            
            assert port == 1884
            assert mock_sock.bind.call_count == 2

    def test_find_free_port_all_ports_taken(self, manager):
        """Test finding free port when all ports are taken."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.side_effect = OSError("Port in use")
            
            with pytest.raises(RuntimeError, match="No free ports available"):
                manager._find_free_port(1983)  # Start from high port to test range

    def test_create_amqtt_config_basic(self, manager, broker_config):
        """Test creating basic AMQTT configuration."""
        config = manager._create_amqtt_config(broker_config)
        
        assert 'listeners' in config
        assert 'default' in config['listeners']
        assert config['listeners']['default']['bind'] == "127.0.0.1:1883"
        assert config['listeners']['default']['max_connections'] == 50
        assert config['auth']['allow-anonymous'] is True
        assert config['topic-check']['enabled'] is False

    def test_create_amqtt_config_with_websocket(self, manager, broker_config):
        """Test creating AMQTT config with WebSocket listener."""
        broker_config.websocket_port = 9001
        
        config = manager._create_amqtt_config(broker_config)
        
        assert 'websocket' in config['listeners']
        assert config['listeners']['websocket']['type'] == 'ws'
        assert config['listeners']['websocket']['bind'] == "127.0.0.1:9001"

    def test_create_amqtt_config_with_ssl(self, manager, broker_config):
        """Test creating AMQTT config with SSL."""
        broker_config.ssl_enabled = True
        broker_config.ssl_cert = "/path/to/cert.pem"
        broker_config.ssl_key = "/path/to/key.pem"
        
        config = manager._create_amqtt_config(broker_config)
        
        assert 'ssl' in config['listeners']
        assert config['listeners']['ssl']['ssl'] is True
        assert config['listeners']['ssl']['certfile'] == "/path/to/cert.pem"
        assert config['listeners']['ssl']['keyfile'] == "/path/to/key.pem"

    def test_create_amqtt_config_with_auth(self, manager, broker_config):
        """Test creating AMQTT config with authentication."""
        broker_config.auth_required = True
        broker_config.username = "testuser"
        broker_config.password = "testpass"
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_passwd"
            mock_temp.return_value = mock_file
            
            config = manager._create_amqtt_config(broker_config)
            
            assert config['auth']['allow-anonymous'] is False
            assert config['auth']['password-file'] == "/tmp/test_passwd"
            mock_file.write.assert_called_once_with("testuser:testpass\n")
            mock_file.close.assert_called_once()

    def test_create_amqtt_config_with_persistence(self, manager, broker_config):
        """Test creating AMQTT config with persistence."""
        broker_config.persistence = True
        broker_config.data_dir = "/custom/data/dir"
        
        config = manager._create_amqtt_config(broker_config)
        
        assert config['persistence']['enabled'] is True
        assert config['persistence']['store-dir'] == "/custom/data/dir"
        assert config['persistence']['retain-store'] == 'memory'

    def test_create_amqtt_config_with_auto_data_dir(self, manager, broker_config):
        """Test creating AMQTT config with auto-generated data dir."""
        broker_config.persistence = True
        
        with patch('tempfile.mkdtemp') as mock_mkdtemp:
            mock_mkdtemp.return_value = "/tmp/mqtt_broker_abc123"
            
            config = manager._create_amqtt_config(broker_config)
            
            assert config['persistence']['store-dir'] == "/tmp/mqtt_broker_abc123"
            mock_mkdtemp.assert_called_once_with(prefix="mqtt_broker_")

    @pytest.mark.asyncio
    async def test_spawn_broker_amqtt_not_available(self, manager):
        """Test spawning broker when AMQTT is not available."""
        with patch.object(manager, 'is_available', return_value=False):
            with pytest.raises(RuntimeError, match="AMQTT library not available"):
                await manager.spawn_broker()

    @pytest.mark.asyncio
    async def test_spawn_broker_with_default_config(self, manager):
        """Test spawning broker with default configuration."""
        with patch.object(manager, 'is_available', return_value=True), \
             patch.object(manager, '_find_free_port', return_value=1883), \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class, \
             patch('asyncio.create_task') as mock_create_task, \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            mock_broker = MagicMock()
            mock_broker_class.return_value = mock_broker
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task
            
            broker_id = await manager.spawn_broker()
            
            assert broker_id == "embedded-broker-1"
            assert manager._next_broker_id == 2
            assert broker_id in manager._brokers
            assert broker_id in manager._broker_tasks
            assert broker_id in manager._broker_infos
            
            broker_info = manager._broker_infos[broker_id]
            assert broker_info.broker_id == broker_id
            assert broker_info.status == "running"

    @pytest.mark.asyncio
    async def test_spawn_broker_with_custom_config(self, manager, broker_config):
        """Test spawning broker with custom configuration."""
        with patch.object(manager, 'is_available', return_value=True), \
             patch('socket.socket') as mock_socket, \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class, \
             patch('asyncio.create_task') as mock_create_task, \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            # Mock port availability check
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None
            
            mock_broker = MagicMock()
            mock_broker_class.return_value = mock_broker
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task
            
            broker_id = await manager.spawn_broker(broker_config)
            
            assert broker_id == "test-broker-1"
            mock_sock.bind.assert_called_once_with(("127.0.0.1", 1883))

    @pytest.mark.asyncio
    async def test_spawn_broker_port_taken_fallback(self, manager, broker_config):
        """Test spawning broker when requested port is taken."""
        with patch.object(manager, 'is_available', return_value=True), \
             patch.object(manager, '_find_free_port', return_value=1884) as mock_find_port, \
             patch('socket.socket') as mock_socket, \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class, \
             patch('asyncio.create_task'), \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            # Mock port in use
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.side_effect = OSError("Port in use")
            
            mock_broker_class.return_value = MagicMock()
            
            await manager.spawn_broker(broker_config)
            
            mock_find_port.assert_called_once_with(1883)

    @pytest.mark.asyncio
    async def test_spawn_broker_auto_port_assignment(self, manager):
        """Test spawning broker with auto port assignment."""
        config = BrokerConfig(port=0)  # Auto-assign
        
        with patch.object(manager, 'is_available', return_value=True), \
             patch.object(manager, '_find_free_port', return_value=1884) as mock_find_port, \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class, \
             patch('asyncio.create_task'), \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            mock_broker_class.return_value = MagicMock()
            
            await manager.spawn_broker(config)
            
            mock_find_port.assert_called_once_with(1883)

    @pytest.mark.asyncio
    async def test_spawn_broker_creation_failure(self, manager, broker_config):
        """Test spawning broker when creation fails."""
        with patch.object(manager, 'is_available', return_value=True), \
             patch('socket.socket') as mock_socket, \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class:
            
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None
            
            mock_broker_class.side_effect = Exception("Broker creation failed")
            
            with pytest.raises(RuntimeError, match="Failed to start MQTT broker"):
                await manager.spawn_broker(broker_config)

    @pytest.mark.asyncio
    async def test_stop_broker_nonexistent(self, manager):
        """Test stopping a nonexistent broker."""
        result = await manager.stop_broker("nonexistent-broker")
        assert result is False

    @pytest.mark.asyncio
    async def test_stop_broker_success(self, manager):
        """Test stopping a broker successfully."""
        # Set up a running broker
        mock_broker = MagicMock()
        mock_broker.shutdown = AsyncMock()
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        
        broker_id = "test-broker-1"
        manager._brokers[broker_id] = mock_broker
        manager._broker_tasks[broker_id] = mock_task
        manager._broker_infos[broker_id] = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        # Mock task cancellation
        async def mock_task_await():
            raise asyncio.CancelledError()
        mock_task.__await__ = lambda: mock_task_await().__await__()
        
        result = await manager.stop_broker(broker_id)
        
        assert result is True
        mock_broker.shutdown.assert_called_once()
        mock_task.cancel.assert_called_once()
        assert broker_id not in manager._brokers
        assert broker_id not in manager._broker_tasks
        assert manager._broker_infos[broker_id].status == "stopped"

    @pytest.mark.asyncio
    async def test_stop_broker_with_completed_task(self, manager):
        """Test stopping broker with already completed task."""
        mock_broker = MagicMock()
        mock_broker.shutdown = AsyncMock()
        mock_task = MagicMock()
        mock_task.done.return_value = True  # Task already done
        
        broker_id = "test-broker-1"
        manager._brokers[broker_id] = mock_broker
        manager._broker_tasks[broker_id] = mock_task
        manager._broker_infos[broker_id] = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        result = await manager.stop_broker(broker_id)
        
        assert result is True
        mock_task.cancel.assert_not_called()  # Should not cancel completed task

    @pytest.mark.asyncio
    async def test_stop_broker_without_task(self, manager):
        """Test stopping broker without associated task."""
        mock_broker = MagicMock()
        mock_broker.shutdown = AsyncMock()
        
        broker_id = "test-broker-1"
        manager._brokers[broker_id] = mock_broker
        manager._broker_infos[broker_id] = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        result = await manager.stop_broker(broker_id)
        
        assert result is True
        mock_broker.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_broker_shutdown_failure(self, manager):
        """Test stopping broker when shutdown fails."""
        mock_broker = MagicMock()
        mock_broker.shutdown = AsyncMock(side_effect=Exception("Shutdown failed"))
        
        broker_id = "test-broker-1"
        manager._brokers[broker_id] = mock_broker
        manager._broker_infos[broker_id] = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        result = await manager.stop_broker(broker_id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_broker_status_nonexistent(self, manager):
        """Test getting status for nonexistent broker."""
        result = await manager.get_broker_status("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_broker_status_running_broker(self, manager):
        """Test getting status for running broker."""
        mock_broker = MagicMock()
        mock_session_manager = MagicMock()
        mock_session_manager.sessions = {"client1": {}, "client2": {}}
        mock_broker.session_manager = mock_session_manager
        
        mock_task = MagicMock()
        mock_task.done.return_value = False
        
        broker_id = "test-broker-1"
        config = BrokerConfig()
        broker_info = BrokerInfo(
            config=config,
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        manager._brokers[broker_id] = mock_broker
        manager._broker_tasks[broker_id] = mock_task
        manager._broker_infos[broker_id] = broker_info
        
        result = await manager.get_broker_status(broker_id)
        
        assert result is not None
        assert result.client_count == 2
        assert result.status == "running"

    @pytest.mark.asyncio
    async def test_get_broker_status_stopped_broker(self, manager):
        """Test getting status for stopped broker."""
        broker_id = "test-broker-1"
        broker_info = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now(),
            status="running"
        )
        
        manager._broker_infos[broker_id] = broker_info
        
        result = await manager.get_broker_status(broker_id)
        
        assert result is not None
        assert result.status == "stopped"

    @pytest.mark.asyncio
    async def test_get_broker_status_with_completed_task(self, manager):
        """Test getting status for broker with completed task."""
        mock_broker = MagicMock()
        mock_task = MagicMock()
        mock_task.done.return_value = True  # Task completed
        
        broker_id = "test-broker-1"
        broker_info = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        manager._brokers[broker_id] = mock_broker
        manager._broker_tasks[broker_id] = mock_task
        manager._broker_infos[broker_id] = broker_info
        
        result = await manager.get_broker_status(broker_id)
        
        assert result.status == "stopped"

    @pytest.mark.asyncio
    async def test_get_broker_status_session_manager_error(self, manager):
        """Test getting status when session manager access fails."""
        mock_broker = MagicMock()
        # Simulate error accessing session manager
        type(mock_broker).session_manager = PropertyMock(side_effect=Exception("Access error"))
        
        broker_id = "test-broker-1"
        broker_info = BrokerInfo(
            config=BrokerConfig(),
            broker_id=broker_id,
            started_at=datetime.now()
        )
        
        manager._brokers[broker_id] = mock_broker
        manager._broker_infos[broker_id] = broker_info
        
        # Should not raise exception
        result = await manager.get_broker_status(broker_id)
        
        assert result is not None
        assert result.client_count == 0  # Should remain unchanged

    def test_list_brokers_empty(self, manager):
        """Test listing brokers when none exist."""
        result = manager.list_brokers()
        assert result == []

    def test_list_brokers_with_data(self, manager):
        """Test listing brokers with data."""
        broker_info1 = BrokerInfo(
            config=BrokerConfig(),
            broker_id="broker-1",
            started_at=datetime.now()
        )
        broker_info2 = BrokerInfo(
            config=BrokerConfig(),
            broker_id="broker-2",
            started_at=datetime.now()
        )
        
        manager._broker_infos["broker-1"] = broker_info1
        manager._broker_infos["broker-2"] = broker_info2
        
        result = manager.list_brokers()
        
        assert len(result) == 2
        assert broker_info1 in result
        assert broker_info2 in result

    def test_get_running_brokers_empty(self, manager):
        """Test getting running brokers when none are running."""
        result = manager.get_running_brokers()
        assert result == []

    def test_get_running_brokers_with_running_and_stopped(self, manager):
        """Test getting running brokers with mixed states."""
        running_info = BrokerInfo(
            config=BrokerConfig(),
            broker_id="running-broker",
            started_at=datetime.now(),
            status="running"
        )
        stopped_info = BrokerInfo(
            config=BrokerConfig(),
            broker_id="stopped-broker",
            started_at=datetime.now(),
            status="stopped"
        )
        
        manager._broker_infos["running-broker"] = running_info
        manager._broker_infos["stopped-broker"] = stopped_info
        manager._brokers["running-broker"] = MagicMock()  # Only running broker has broker instance
        
        result = manager.get_running_brokers()
        
        assert len(result) == 1
        assert result[0].broker_id == "running-broker"

    @pytest.mark.asyncio
    async def test_stop_all_brokers_empty(self, manager):
        """Test stopping all brokers when none are running."""
        result = await manager.stop_all_brokers()
        assert result == 0

    @pytest.mark.asyncio
    async def test_stop_all_brokers_with_brokers(self, manager):
        """Test stopping all brokers with multiple running."""
        # Set up multiple brokers
        for i in range(3):
            broker_id = f"broker-{i}"
            mock_broker = MagicMock()
            mock_broker.shutdown = AsyncMock()
            manager._brokers[broker_id] = mock_broker
            manager._broker_infos[broker_id] = BrokerInfo(
                config=BrokerConfig(),
                broker_id=broker_id,
                started_at=datetime.now()
            )
        
        result = await manager.stop_all_brokers()
        
        assert result == 3
        assert len(manager._brokers) == 0

    @pytest.mark.asyncio
    async def test_stop_all_brokers_partial_failure(self, manager):
        """Test stopping all brokers when some fail to stop."""
        # Set up brokers with one failing
        for i in range(2):
            broker_id = f"broker-{i}"
            mock_broker = MagicMock()
            if i == 0:
                mock_broker.shutdown = AsyncMock()  # Success
            else:
                mock_broker.shutdown = AsyncMock(side_effect=Exception("Stop failed"))  # Failure
            
            manager._brokers[broker_id] = mock_broker
            manager._broker_infos[broker_id] = BrokerInfo(
                config=BrokerConfig(),
                broker_id=broker_id,
                started_at=datetime.now()
            )
        
        result = await manager.stop_all_brokers()
        
        assert result == 1  # Only one stopped successfully

    @pytest.mark.asyncio
    async def test_test_broker_connection_nonexistent(self, manager):
        """Test connection test for nonexistent broker."""
        result = await manager.test_broker_connection("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_test_broker_connection_success(self, manager):
        """Test successful broker connection test."""
        broker_info = BrokerInfo(
            config=BrokerConfig(host="localhost", port=1883),
            broker_id="test-broker",
            started_at=datetime.now()
        )
        manager._broker_infos["test-broker"] = broker_info
        
        with patch('mcmqtt.broker.manager.MQTTClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            result = await manager.test_broker_connection("test-broker")
            
            assert result is True
            mock_client.connect.assert_called_once_with("mqtt://localhost:1883")
            mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_broker_connection_failure(self, manager):
        """Test broker connection test failure."""
        broker_info = BrokerInfo(
            config=BrokerConfig(host="localhost", port=1883),
            broker_id="test-broker",
            started_at=datetime.now()
        )
        manager._broker_infos["test-broker"] = broker_info
        
        with patch('mcmqtt.broker.manager.MQTTClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))
            mock_client_class.return_value = mock_client
            
            result = await manager.test_broker_connection("test-broker")
            
            assert result is False

    def test_broker_manager_destructor(self, manager):
        """Test broker manager destructor cleanup."""
        # Set up some tasks
        mock_task1 = MagicMock()
        mock_task1.done.return_value = False
        mock_task2 = MagicMock()
        mock_task2.done.return_value = True
        
        manager._broker_tasks = {
            "broker-1": mock_task1,
            "broker-2": mock_task2
        }
        
        # Call destructor
        manager.__del__()
        
        # Only running task should be cancelled
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_not_called()

    def test_broker_manager_destructor_no_tasks(self, manager):
        """Test broker manager destructor with no tasks."""
        # Should not raise exception
        manager.__del__()

    def test_broker_config_defaults(self):
        """Test BrokerConfig default values."""
        config = BrokerConfig()
        
        assert config.port == 1883
        assert config.host == "127.0.0.1"
        assert config.name == "embedded-broker"
        assert config.max_connections == 100
        assert config.auth_required is False
        assert config.username is None
        assert config.password is None
        assert config.persistence is False
        assert config.data_dir is None
        assert config.websocket_port is None
        assert config.ssl_enabled is False
        assert config.ssl_cert is None
        assert config.ssl_key is None

    def test_broker_info_url_generation(self):
        """Test BrokerInfo URL generation."""
        config = BrokerConfig(host="192.168.1.100", port=1884)
        info = BrokerInfo(
            config=config,
            broker_id="test-broker",
            started_at=datetime.now()
        )
        
        assert info.url == "mqtt://192.168.1.100:1884"

    def test_broker_info_custom_url(self):
        """Test BrokerInfo with custom URL."""
        config = BrokerConfig()
        info = BrokerInfo(
            config=config,
            broker_id="test-broker",
            started_at=datetime.now(),
            url="mqtts://custom.host:8883"
        )
        
        assert info.url == "mqtts://custom.host:8883"


# Additional edge case and integration-style tests
class TestBrokerManagerEdgeCases:
    """Edge case tests for broker manager."""

    @pytest.fixture
    def manager(self):
        """Create a broker manager instance."""
        return BrokerManager()

    def test_broker_config_with_all_options(self):
        """Test broker config with all options set."""
        config = BrokerConfig(
            port=8883,
            host="0.0.0.0",
            name="full-featured-broker",
            max_connections=200,
            auth_required=True,
            username="admin",
            password="secret",
            persistence=True,
            data_dir="/var/mqtt/data",
            websocket_port=9001,
            ssl_enabled=True,
            ssl_cert="/etc/ssl/mqtt.crt",
            ssl_key="/etc/ssl/mqtt.key"
        )
        
        assert config.port == 8883
        assert config.host == "0.0.0.0"
        assert config.name == "full-featured-broker"
        assert config.auth_required is True
        assert config.persistence is True
        assert config.websocket_port == 9001
        assert config.ssl_enabled is True

    def test_broker_info_default_fields(self):
        """Test BrokerInfo default field values."""
        config = BrokerConfig()
        info = BrokerInfo(
            config=config,
            broker_id="test",
            started_at=datetime.now()
        )
        
        assert info.status == "running"
        assert info.client_count == 0
        assert info.message_count == 0
        assert info.topics == []

    @pytest.mark.asyncio
    async def test_complex_broker_lifecycle(self, manager):
        """Test complete broker lifecycle."""
        with patch.object(manager, 'is_available', return_value=True), \
             patch('socket.socket') as mock_socket, \
             patch('mcmqtt.broker.manager.Broker') as mock_broker_class, \
             patch('asyncio.create_task') as mock_create_task, \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            # Mock successful port binding
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None
            
            # Mock broker creation
            mock_broker = MagicMock()
            mock_broker.shutdown = AsyncMock()
            mock_broker_class.return_value = mock_broker
            
            mock_task = MagicMock()
            mock_task.done.return_value = False
            mock_create_task.return_value = mock_task
            
            # Spawn broker
            broker_id = await manager.spawn_broker()
            
            # Check it's listed as running
            running_brokers = manager.get_running_brokers()
            assert len(running_brokers) == 1
            assert running_brokers[0].broker_id == broker_id
            
            # Stop broker
            async def mock_task_await():
                raise asyncio.CancelledError()
            mock_task.__await__ = lambda: mock_task_await().__await__()
            
            stopped = await manager.stop_broker(broker_id)
            assert stopped is True
            
            # Check it's no longer running
            running_brokers = manager.get_running_brokers()
            assert len(running_brokers) == 0


if __name__ == "__main__":
    pytest.main([__file__])