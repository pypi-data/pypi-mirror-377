"""
Embedded MQTT broker management using AMQTT.

Provides on-the-fly MQTT broker spawning capabilities for low-volume queues.
"""

import asyncio
import logging
import socket
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

try:
    from amqtt.broker import Broker
    from amqtt.client import MQTTClient
    AMQTT_AVAILABLE = True
except ImportError:
    AMQTT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BrokerConfig:
    """Configuration for an embedded MQTT broker."""
    port: int = 1883
    host: str = "127.0.0.1"
    name: str = "embedded-broker"
    max_connections: int = 100
    auth_required: bool = False
    username: Optional[str] = None
    password: Optional[str] = None
    persistence: bool = False
    data_dir: Optional[str] = None
    websocket_port: Optional[int] = None
    ssl_enabled: bool = False
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None


@dataclass 
class BrokerInfo:
    """Information about a running broker."""
    config: BrokerConfig
    broker_id: str
    started_at: datetime
    status: str = "running"
    client_count: int = 0
    message_count: int = 0
    topics: List[str] = field(default_factory=list)
    url: str = ""
    
    def __post_init__(self):
        if not self.url:
            self.url = f"mqtt://{self.config.host}:{self.config.port}"


class BrokerManager:
    """Manages embedded MQTT brokers using AMQTT."""
    
    def __init__(self):
        self._brokers: Dict[str, Broker] = {}
        self._broker_infos: Dict[str, BrokerInfo] = {}
        self._broker_tasks: Dict[str, asyncio.Task] = {}
        self._next_broker_id = 1
    
    def is_available(self) -> bool:
        """Check if AMQTT is available for broker creation."""
        return AMQTT_AVAILABLE
    
    def _find_free_port(self, start_port: int = 1883) -> int:
        """Find a free port starting from the given port."""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports available for MQTT broker")
    
    def _create_amqtt_config(self, config: BrokerConfig) -> Dict[str, Any]:
        """Create AMQTT configuration dictionary."""
        amqtt_config = {
            'listeners': {
                'default': {
                    'type': 'tcp',
                    'bind': f"{config.host}:{config.port}",
                    'max_connections': config.max_connections
                }
            },
            'sys_interval': 10,
            'auth': {
                'allow-anonymous': not config.auth_required,
                'password-file': None
            },
            'topic-check': {
                'enabled': False
            }
        }
        
        # Add WebSocket listener if specified
        if config.websocket_port:
            amqtt_config['listeners']['websocket'] = {
                'type': 'ws',
                'bind': f"{config.host}:{config.websocket_port}",
                'max_connections': config.max_connections
            }
        
        # Add SSL/TLS if enabled
        if config.ssl_enabled and config.ssl_cert and config.ssl_key:
            amqtt_config['listeners']['ssl'] = {
                'type': 'tcp',
                'bind': f"{config.host}:{config.port + 1}",  # SSL on port+1
                'ssl': True,
                'certfile': config.ssl_cert,
                'keyfile': config.ssl_key
            }
        
        # Configure authentication
        if config.auth_required and config.username and config.password:
            # Create temporary password file
            password_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.passwd')
            password_file.write(f"{config.username}:{config.password}\n")
            password_file.close()
            
            amqtt_config['auth']['allow-anonymous'] = False
            amqtt_config['auth']['password-file'] = password_file.name
        
        # Configure persistence
        if config.persistence:
            data_dir = config.data_dir or tempfile.mkdtemp(prefix="mqtt_broker_")
            amqtt_config['persistence'] = {
                'enabled': True,
                'store-dir': data_dir,
                'retain-store': 'memory',  # or 'disk'
                'subscription-store': 'memory'
            }
        
        return amqtt_config
    
    async def spawn_broker(self, config: Optional[BrokerConfig] = None) -> str:
        """
        Spawn a new embedded MQTT broker.
        
        Returns:
            str: Unique broker ID for managing the broker
        """
        if not self.is_available():
            raise RuntimeError("AMQTT library not available. Install with: pip install amqtt")
        
        if config is None:
            config = BrokerConfig()
        
        # Find a free port if the requested one is taken or auto-assign requested
        if config.port == 0 or config.port == 1883:  # Auto-assign or default port
            config.port = self._find_free_port(1883)
        else:
            # Check if requested port is available
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((config.host, config.port))
            except OSError:
                # Port is taken, find alternative
                config.port = self._find_free_port(config.port)
        
        # Generate unique broker ID
        broker_id = f"{config.name}-{self._next_broker_id}"
        self._next_broker_id += 1
        
        # Create AMQTT configuration
        amqtt_config = self._create_amqtt_config(config)
        
        try:
            # Create and start the broker
            broker = Broker(amqtt_config)
            
            # Start broker in background task
            broker_task = asyncio.create_task(broker.start())
            
            # Wait a moment for broker to initialize
            await asyncio.sleep(0.1)
            
            # Store broker references
            self._brokers[broker_id] = broker
            self._broker_tasks[broker_id] = broker_task
            self._broker_infos[broker_id] = BrokerInfo(
                config=config,
                broker_id=broker_id,
                started_at=datetime.now(),
                status="running"
            )
            
            logger.info(f"MQTT broker '{broker_id}' started on {config.host}:{config.port}")
            return broker_id
            
        except Exception as e:
            logger.error(f"Failed to start MQTT broker: {e}")
            raise RuntimeError(f"Failed to start MQTT broker: {e}")
    
    async def stop_broker(self, broker_id: str) -> bool:
        """Stop a running broker."""
        if broker_id not in self._brokers:
            return False
        
        try:
            broker = self._brokers[broker_id]
            broker_task = self._broker_tasks.get(broker_id)
            
            # Stop the broker
            await broker.shutdown()
            
            # Cancel the task if it exists
            if broker_task and not broker_task.done():
                broker_task.cancel()
                try:
                    await broker_task
                except asyncio.CancelledError:
                    pass
            
            # Update status
            if broker_id in self._broker_infos:
                self._broker_infos[broker_id].status = "stopped"
            
            # Clean up references
            del self._brokers[broker_id]
            if broker_id in self._broker_tasks:
                del self._broker_tasks[broker_id]
            
            logger.info(f"MQTT broker '{broker_id}' stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping broker {broker_id}: {e}")
            return False
    
    async def get_broker_status(self, broker_id: str) -> Optional[BrokerInfo]:
        """Get status information for a broker."""
        if broker_id not in self._broker_infos:
            return None
        
        info = self._broker_infos[broker_id]
        
        # Update runtime information if broker is still running
        if broker_id in self._brokers:
            broker = self._brokers[broker_id]
            
            # Get client count from broker session manager
            try:
                if hasattr(broker, 'session_manager') and broker.session_manager:
                    info.client_count = len(broker.session_manager.sessions)
            except:
                pass  # Ignore errors accessing internal broker state
                
            # Check if broker task is still running
            broker_task = self._broker_tasks.get(broker_id)
            if broker_task and broker_task.done():
                info.status = "stopped"
        else:
            info.status = "stopped"
        
        return info
    
    def list_brokers(self) -> List[BrokerInfo]:
        """List all broker instances (running and stopped)."""
        return list(self._broker_infos.values())
    
    def get_running_brokers(self) -> List[BrokerInfo]:
        """Get list of currently running brokers."""
        return [info for info in self._broker_infos.values() 
                if info.status == "running" and info.broker_id in self._brokers]
    
    async def stop_all_brokers(self) -> int:
        """Stop all running brokers. Returns count of stopped brokers."""
        running_brokers = list(self._brokers.keys())
        stopped_count = 0
        
        for broker_id in running_brokers:
            if await self.stop_broker(broker_id):
                stopped_count += 1
        
        return stopped_count
    
    async def test_broker_connection(self, broker_id: str) -> bool:
        """Test if a broker is accepting connections."""
        if broker_id not in self._broker_infos:
            return False
        
        info = self._broker_infos[broker_id]
        
        try:
            # Create a test client
            client = MQTTClient()
            
            # Try to connect
            await client.connect(f"mqtt://{info.config.host}:{info.config.port}")
            
            # Disconnect immediately
            await client.disconnect()
            
            return True
            
        except Exception as e:
            logger.debug(f"Broker connection test failed for {broker_id}: {e}")
            return False
    
    def __del__(self):
        """Cleanup on deletion."""
        # Note: In practice, you should call stop_all_brokers() before deletion
        # This is just a safety net
        if hasattr(self, '_broker_tasks'):
            for task in self._broker_tasks.values():
                if not task.done():
                    task.cancel()