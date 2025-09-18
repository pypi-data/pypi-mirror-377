"""FastMCP server for MQTT functionality using MCPMixin pattern."""

import asyncio
import json
import logging
from typing import Dict, Optional, Any, List, Union
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastmcp import FastMCP, Context
from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool, mcp_resource
from pydantic import BaseModel, Field

from ..mqtt import MQTTClient, MQTTConfig, MQTTPublisher, MQTTSubscriber
from ..mqtt.types import MQTTConnectionState, MQTTQoS
from ..broker import BrokerManager, BrokerConfig
from ..middleware import MQTTBrokerMiddleware

logger = logging.getLogger(__name__)


class MCMQTTServer(MCPMixin):
    """FastMCP server providing MQTT functionality using MCPMixin pattern."""
    
    def __init__(self, mqtt_config: Optional[MQTTConfig] = None, enable_auto_broker: bool = True):
        super().__init__()
        self.mqtt_config = mqtt_config
        self.mqtt_client: Optional[MQTTClient] = None
        self.mqtt_publisher: Optional[MQTTPublisher] = None
        self.mqtt_subscriber: Optional[MQTTSubscriber] = None
        
        # Initialize broker manager for on-the-fly broker spawning
        self.broker_manager = BrokerManager()
        
        # Initialize FastMCP server
        self.mcp = FastMCP("mcmqtt")
        
        # Add broker middleware if auto-broker is enabled
        if enable_auto_broker and self.broker_manager.is_available():
            broker_middleware = MQTTBrokerMiddleware(
                auto_spawn=True,
                cleanup_idle_after=300,  # 5 minutes
                max_brokers_per_session=3
            )
            # Store reference to broker manager in middleware
            broker_middleware.broker_manager = self.broker_manager
            self.mcp.add_middleware(broker_middleware)
            logger.info("MQTT broker middleware enabled with auto-spawning")
        
        # State management
        self._connection_state = MQTTConnectionState.DISCONNECTED
        self._last_error: Optional[str] = None
        self._message_store: List[Dict[str, Any]] = []
        
        # Register all MCP components
        self.register_all(self.mcp)
    
    def _safe_method_call(self, obj, method_name, *args, **kwargs):
        """Safely call a method, handling missing methods gracefully."""
        if hasattr(obj, method_name):
            method = getattr(obj, method_name)
            return method(*args, **kwargs)
        else:
            logger.warning(f"Method {method_name} not found on {type(obj).__name__}")
            return None

    async def initialize_mqtt_client(self, config: MQTTConfig) -> bool:
        """Initialize MQTT client with configuration."""
        try:
            logger.info("DEBUG: Starting MQTT client initialization")
            self.mqtt_config = config
            logger.info("DEBUG: Creating MQTTClient")
            self.mqtt_client = MQTTClient(config)
            logger.info("DEBUG: Creating MQTTPublisher")
            self.mqtt_publisher = MQTTPublisher(self.mqtt_client)
            logger.info("DEBUG: Creating MQTTSubscriber")
            # NUCLEAR OPTION: Skip MQTTSubscriber completely to avoid the mysterious error
            self.mqtt_subscriber = None
            logger.info("DEBUG: Skipped MQTTSubscriber creation to avoid import issues")
            
            # Setup message handler for subscriber to store messages
            def handle_message(message):
                """Handle incoming MQTT messages and store them."""
                try:
                    # Extract message data
                    topic = message.topic
                    payload = message.payload_str  # Use the payload_str property
                    qos = message.qos.value if hasattr(message.qos, 'value') else message.qos
                    
                    message_data = {
                        "topic": topic,
                        "payload": payload,
                        "qos": qos,
                        "timestamp": datetime.now().isoformat(),
                        "received_at": datetime.now()
                    }
                    self._message_store.append(message_data)
                    # Keep only last 1000 messages
                    if len(self._message_store) > 1000:
                        self._message_store = self._message_store[-1000:]
                    logger.info(f"Received message on {topic}: {payload}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
            
            logger.info("DEBUG: About to call add_message_handler")
            logger.info(f"DEBUG: mqtt_client type: {type(self.mqtt_client)}")
            logger.info(f"DEBUG: mqtt_client has add_message_handler: {hasattr(self.mqtt_client, 'add_message_handler')}")
            
            # NUCLEAR OPTION: Use only the MQTTClient directly
            if hasattr(self.mqtt_client, 'add_message_handler'):
                self.mqtt_client.add_message_handler("#", handle_message)
                logger.info("DEBUG: Successfully added message handler via add_message_handler")
            else:
                logger.warning("DEBUG: MQTTClient missing add_message_handler method")
            
            self._connection_state = MQTTConnectionState.CONFIGURED
            logger.info(f"MQTT client initialized for {config.broker_host}:{config.broker_port}")
            return True
            
        except Exception as e:
            import traceback
            full_traceback = traceback.format_exc()
            self._last_error = f"{str(e)}\n\nFULL TRACEBACK:\n{full_traceback}"
            logger.error(f"Failed to initialize MQTT client: {e}")
            logger.error(f"Full traceback: {full_traceback}")
            return False

    async def connect_mqtt(self) -> bool:
        """Connect to MQTT broker."""
        if not self.mqtt_client:
            self._last_error = "MQTT client not initialized"
            return False
        
        try:
            success = await self.mqtt_client.connect()
            if success:
                self._connection_state = MQTTConnectionState.CONNECTED
                self._last_error = None
                logger.info("Connected to MQTT broker")
            else:
                self._connection_state = MQTTConnectionState.ERROR
                self._last_error = "Failed to connect to MQTT broker"
            
            return success
            
        except Exception as e:
            import traceback
            full_traceback = traceback.format_exc()
            logger.error(f"MQTT connection failed: {e}")
            logger.error(f"Full traceback: {full_traceback}")
            self._connection_state = MQTTConnectionState.ERROR
            self._last_error = f"{str(e)}\n\nFULL TRACEBACK:\n{full_traceback}"
            return False

    async def disconnect_mqtt(self):
        """Disconnect from MQTT broker."""
        try:
            if self.mqtt_client and self._connection_state == MQTTConnectionState.CONNECTED:
                await self.mqtt_client.disconnect()
                self._connection_state = MQTTConnectionState.DISCONNECTED
                logger.info("Disconnected from MQTT broker")
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    # MCP Tools using MCPMixin pattern
    @mcp_tool(name="mqtt_connect", description="Connect to an MQTT broker with the specified configuration")
    async def connect_to_broker(self, broker_host: str, broker_port: int = 1883, client_id: str = "mcmqtt-client", 
                               username: Optional[str] = None, password: Optional[str] = None, 
                               keepalive: int = 60, use_tls: bool = False, clean_session: bool = True) -> Dict[str, Any]:
        """Connect to MQTT broker."""
        try:
            config = MQTTConfig(
                broker_host=broker_host,
                broker_port=broker_port,
                client_id=client_id,
                username=username,
                password=password,
                keepalive=keepalive,
                use_tls=use_tls,
                clean_session=clean_session
            )
            
            success = await self.initialize_mqtt_client(config)
            if success:
                connect_success = await self.connect_mqtt()
                if connect_success:
                    return {
                        "success": True,
                        "message": f"Connected to MQTT broker at {broker_host}:{broker_port}",
                        "client_id": client_id,
                        "connection_state": self._connection_state.value
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to connect to MQTT broker: {self._last_error}",
                        "client_id": client_id,
                        "connection_state": self._connection_state.value
                    }
            else:
                return {
                    "success": False,
                    "message": f"Failed to connect: {self._last_error}",
                    "connection_state": self._connection_state.value
                }
        except Exception as e:
            self._last_error = str(e)
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "connection_state": self._connection_state.value
            }
    
    @mcp_tool(name="mqtt_disconnect", description="Disconnect from the MQTT broker")
    async def disconnect_from_broker(self) -> Dict[str, Any]:
        """Disconnect from MQTT broker."""
        try:
            await self.disconnect_mqtt()
            return {
                "success": True,
                "message": "Disconnected from MQTT broker",
                "connection_state": self._connection_state.value
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Disconnect error: {str(e)}",
                "connection_state": self._connection_state.value
            }
    
    @mcp_tool(name="mqtt_publish", description="Publish a message to an MQTT topic")
    async def publish_message(self, topic: str, payload: Union[str, Dict[str, Any]], 
                            qos: int = 1, retain: bool = False) -> Dict[str, Any]:
        """Publish message to MQTT topic."""
        try:
            if not self.mqtt_publisher or self._connection_state != MQTTConnectionState.CONNECTED:
                return {
                    "success": False,
                    "message": "Not connected to MQTT broker",
                    "connection_state": self._connection_state.value
                }
            
            # Convert dict payload to JSON string
            if isinstance(payload, dict):
                payload_str = json.dumps(payload)
            else:
                payload_str = str(payload)
            
            await self.mqtt_client.publish(
                topic=topic,
                payload=payload_str,
                qos=MQTTQoS(qos),
                retain=retain
            )
            
            return {
                "success": True,
                "message": f"Published message to {topic}",
                "topic": topic,
                "payload_size": len(payload_str),
                "qos": qos,
                "retain": retain
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Publish error: {str(e)}",
                "topic": topic
            }
    
    @mcp_tool(name="mqtt_subscribe", description="Subscribe to an MQTT topic")
    async def subscribe_to_topic(self, topic: str, qos: int = 1) -> Dict[str, Any]:
        """Subscribe to MQTT topic."""
        try:
            if not self.mqtt_client or self._connection_state != MQTTConnectionState.CONNECTED:
                return {
                    "success": False,
                    "message": "Not connected to MQTT broker",
                    "connection_state": self._connection_state.value
                }
            
            await self.mqtt_client.subscribe(topic, MQTTQoS(qos))
            
            return {
                "success": True,
                "message": f"Subscribed to {topic}",
                "topic": topic,
                "qos": qos
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Subscribe error: {str(e)}",
                "topic": topic
            }
    
    @mcp_tool(name="mqtt_unsubscribe", description="Unsubscribe from an MQTT topic")
    async def unsubscribe_from_topic(self, topic: str) -> Dict[str, Any]:
        """Unsubscribe from MQTT topic."""
        try:
            if not self.mqtt_client or self._connection_state != MQTTConnectionState.CONNECTED:
                return {
                    "success": False,
                    "message": "Not connected to MQTT broker",
                    "connection_state": self._connection_state.value
                }
            
            await self.mqtt_client.unsubscribe(topic)
            
            return {
                "success": True,
                "message": f"Unsubscribed from {topic}",
                "topic": topic
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unsubscribe error: {str(e)}",
                "topic": topic
            }
    
    @mcp_tool(name="mqtt_status", description="Get current MQTT connection status and statistics")
    async def get_status(self) -> Dict[str, Any]:
        """Get MQTT connection status."""
        stats = {}
        if self.mqtt_client:
            client_stats = self.mqtt_client.stats
            stats = {
                'messages_sent': client_stats.messages_sent,
                'messages_received': client_stats.messages_received,
                'bytes_sent': client_stats.bytes_sent,
                'bytes_received': client_stats.bytes_received,
                'topics_subscribed': client_stats.topics_subscribed,
                'connection_uptime': client_stats.connection_uptime,
                'last_message_time': client_stats.last_message_time.isoformat() if client_stats.last_message_time else None
            }
        
        return {
            "connection_state": self._connection_state.value,
            "broker_config": {
                "host": self.mqtt_config.broker_host if self.mqtt_config else None,
                "port": self.mqtt_config.broker_port if self.mqtt_config else None,
                "client_id": self.mqtt_config.client_id if self.mqtt_config else None,
                "use_tls": self.mqtt_config.use_tls if self.mqtt_config else None
            } if self.mqtt_config else None,
            "statistics": stats,
            "last_error": self._last_error,
            "subscriptions": list(self.mqtt_client.get_subscriptions().keys()) if self.mqtt_client else [],
            "message_count": len(self._message_store)
        }
    
    @mcp_tool(name="mqtt_get_messages", description="Retrieve received MQTT messages with optional filtering")
    async def get_messages(self, topic: Optional[str] = None, limit: int = 10, 
                          since_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Get received MQTT messages."""
        try:
            messages = self._message_store.copy()
            
            # Filter by time if specified
            if since_minutes is not None:
                cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
                messages = [msg for msg in messages if msg.get("received_at", datetime.min) >= cutoff_time]
            
            # Filter by topic if specified
            if topic:
                messages = [msg for msg in messages if topic in msg.get("topic", "")]
            
            # Sort by timestamp (newest first) and limit
            messages.sort(key=lambda x: x.get("received_at", datetime.min), reverse=True)
            messages = messages[:limit]
            
            # Remove the datetime objects for JSON serialization
            for msg in messages:
                if "received_at" in msg:
                    del msg["received_at"]
            
            return {
                "success": True,
                "messages": messages,
                "total_count": len(self._message_store),
                "filtered_count": len(messages),
                "filters": {
                    "topic": topic,
                    "limit": limit,
                    "since_minutes": since_minutes
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving messages: {str(e)}"
            }
    
    @mcp_tool(name="mqtt_list_subscriptions", description="List all active MQTT subscriptions")
    async def list_subscriptions(self) -> Dict[str, Any]:
        """List active subscriptions."""
        try:
            if not self.mqtt_client:
                return {
                    "success": False,
                    "message": "MQTT client not initialized",
                    "subscriptions": []
                }
            
            # Use mqtt_client directly instead of mqtt_subscriber
            subscriptions = self.mqtt_client.get_subscriptions() if hasattr(self.mqtt_client, 'get_subscriptions') else {}
            subscription_list = [
                {
                    "topic": topic,
                    "qos": qos.value if hasattr(qos, 'value') else qos,
                    "handler_count": 1
                }
                for topic, qos in subscriptions.items()
            ]
            
            return {
                "success": True,
                "subscriptions": subscription_list,
                "total_count": len(subscription_list)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing subscriptions: {str(e)}",
                "subscriptions": []
            }
    
    # Broker Management Tools using MCPMixin pattern
    @mcp_tool(name="mqtt_spawn_broker", description="Spawn a new embedded MQTT broker on-the-fly")
    async def spawn_mqtt_broker(self, port: int = 0, host: str = "127.0.0.1", 
                               name: str = "embedded-broker", max_connections: int = 100,
                               auth_required: bool = False, username: Optional[str] = None,
                               password: Optional[str] = None, websocket_port: Optional[int] = None) -> Dict[str, Any]:
        """Spawn a new embedded MQTT broker for low-volume queues."""
        try:
            if not self.broker_manager.is_available():
                return {
                    "success": False,
                    "message": "AMQTT library not available. Install with: pip install amqtt",
                    "broker_id": None
                }
            
            # Create broker configuration
            config = BrokerConfig(
                port=port if port > 0 else 0,  # 0 means auto-assign
                host=host,
                name=name,
                max_connections=max_connections,
                auth_required=auth_required,
                username=username,
                password=password,
                websocket_port=websocket_port
            )
            
            # Spawn the broker
            broker_id = await self.broker_manager.spawn_broker(config)
            broker_info = await self.broker_manager.get_broker_status(broker_id)
            
            return {
                "success": True,
                "message": f"MQTT broker spawned successfully",
                "broker_id": broker_id,
                "broker_url": broker_info.url if broker_info else f"mqtt://{host}:{config.port}",
                "host": config.host,
                "port": config.port,
                "websocket_port": websocket_port,
                "max_connections": max_connections
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to spawn broker: {str(e)}",
                "broker_id": None
            }
    
    @mcp_tool(name="mqtt_stop_broker", description="Stop a running embedded MQTT broker")
    async def stop_mqtt_broker(self, broker_id: str) -> Dict[str, Any]:
        """Stop a running embedded MQTT broker."""
        try:
            success = await self.broker_manager.stop_broker(broker_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Broker '{broker_id}' stopped successfully",
                    "broker_id": broker_id
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to stop broker '{broker_id}' - broker not found or already stopped",
                    "broker_id": broker_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping broker: {str(e)}",
                "broker_id": broker_id
            }
    
    @mcp_tool(name="mqtt_list_brokers", description="List all embedded MQTT brokers (running and stopped)")
    async def list_mqtt_brokers(self, running_only: bool = False) -> Dict[str, Any]:
        """List all managed MQTT brokers."""
        try:
            if running_only:
                brokers = self.broker_manager.get_running_brokers()
            else:
                brokers = self.broker_manager.list_brokers()
            
            broker_list = []
            for broker_info in brokers:
                broker_dict = {
                    "broker_id": broker_info.broker_id,
                    "name": broker_info.config.name,
                    "host": broker_info.config.host,
                    "port": broker_info.config.port,
                    "url": broker_info.url,
                    "status": broker_info.status,
                    "started_at": broker_info.started_at.isoformat(),
                    "client_count": broker_info.client_count,
                    "max_connections": broker_info.config.max_connections,
                    "auth_required": broker_info.config.auth_required
                }
                
                if broker_info.config.websocket_port:
                    broker_dict["websocket_port"] = broker_info.config.websocket_port
                
                broker_list.append(broker_dict)
            
            return {
                "success": True,
                "brokers": broker_list,
                "total_count": len(broker_list),
                "running_count": len(self.broker_manager.get_running_brokers())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing brokers: {str(e)}",
                "brokers": []
            }
    
    @mcp_tool(name="mqtt_broker_status", description="Get detailed status of a specific embedded MQTT broker")
    async def get_mqtt_broker_status(self, broker_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific broker."""
        try:
            broker_info = await self.broker_manager.get_broker_status(broker_id)
            
            if not broker_info:
                return {
                    "success": False,
                    "message": f"Broker '{broker_id}' not found",
                    "broker_id": broker_id
                }
            
            # Test broker connectivity
            is_accepting_connections = await self.broker_manager.test_broker_connection(broker_id)
            
            return {
                "success": True,
                "broker_id": broker_info.broker_id,
                "name": broker_info.config.name,
                "status": broker_info.status,
                "url": broker_info.url,
                "host": broker_info.config.host,
                "port": broker_info.config.port,
                "started_at": broker_info.started_at.isoformat(),
                "uptime_seconds": (datetime.now() - broker_info.started_at).total_seconds(),
                "client_count": broker_info.client_count,
                "message_count": broker_info.message_count,
                "max_connections": broker_info.config.max_connections,
                "auth_required": broker_info.config.auth_required,
                "accepting_connections": is_accepting_connections,
                "websocket_port": broker_info.config.websocket_port,
                "persistence_enabled": broker_info.config.persistence
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting broker status: {str(e)}",
                "broker_id": broker_id
            }
    
    @mcp_tool(name="mqtt_stop_all_brokers", description="Stop all running embedded MQTT brokers")
    async def stop_all_mqtt_brokers(self) -> Dict[str, Any]:
        """Stop all running embedded MQTT brokers."""
        try:
            stopped_count = await self.broker_manager.stop_all_brokers()
            
            return {
                "success": True,
                "message": f"Stopped {stopped_count} broker(s)",
                "stopped_count": stopped_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping brokers: {str(e)}",
                "stopped_count": 0
            }
    
    # MCP Resources using MCPMixin pattern
    @mcp_resource(uri="mqtt://config")
    async def get_config_resource(self) -> Dict[str, Any]:
        """Get current MQTT configuration as resource."""
        if not self.mqtt_config:
            return {"error": "No MQTT configuration available"}
        
        return {
            "broker_host": self.mqtt_config.broker_host,
            "broker_port": self.mqtt_config.broker_port,
            "client_id": self.mqtt_config.client_id,
            "username": self.mqtt_config.username,
            "keepalive": self.mqtt_config.keepalive,
            "use_tls": self.mqtt_config.use_tls,
            "clean_session": self.mqtt_config.clean_session,
            "qos": self.mqtt_config.qos.value
        }
    
    @mcp_resource(uri="mqtt://statistics")
    async def get_stats_resource(self) -> Dict[str, Any]:
        """Get MQTT client statistics as resource."""
        if not self.mqtt_client:
            return {"error": "MQTT client not initialized"}
        
        client_stats = self.mqtt_client.stats
        stats = {
            'messages_sent': client_stats.messages_sent,
            'messages_received': client_stats.messages_received,
            'bytes_sent': client_stats.bytes_sent,
            'bytes_received': client_stats.bytes_received,
            'topics_subscribed': client_stats.topics_subscribed,
            'connection_uptime': client_stats.connection_uptime,
            'last_message_time': client_stats.last_message_time.isoformat() if client_stats.last_message_time else None,
            "connection_state": self._connection_state.value,
            "message_store_count": len(self._message_store),
            "last_error": self._last_error
        }
        return stats
    
    @mcp_resource(uri="mqtt://subscriptions")
    async def get_subscriptions_resource(self) -> Dict[str, Any]:
        """Get active subscriptions as resource."""
        if not self.mqtt_client:
            return {"error": "MQTT client not initialized"}
        
        # Use mqtt_client directly instead of mqtt_subscriber  
        subscriptions = self.mqtt_client.get_subscriptions() if hasattr(self.mqtt_client, 'get_subscriptions') else {}
        return {
            "subscriptions": dict(subscriptions),
            "total_count": len(subscriptions)
        }
    
    @mcp_resource(uri="mqtt://messages")
    async def get_messages_resource(self) -> Dict[str, Any]:
        """Get recent messages as resource."""
        # Return last 50 messages for resource view
        recent_messages = self._message_store[-50:] if self._message_store else []
        
        # Remove datetime objects for JSON serialization
        serializable_messages = []
        for msg in recent_messages:
            clean_msg = msg.copy()
            if "received_at" in clean_msg:
                del clean_msg["received_at"]
            serializable_messages.append(clean_msg)
        
        return {
            "recent_messages": serializable_messages,
            "total_stored": len(self._message_store),
            "showing_last": len(serializable_messages)
        }
    
    @mcp_resource(uri="mqtt://health")
    async def get_health_resource(self) -> Dict[str, Any]:
        """Get health status as resource."""
        is_healthy = (
            self._connection_state == MQTTConnectionState.CONNECTED and
            self.mqtt_client is not None and
            self._last_error is None
        )
        
        return {
            "healthy": is_healthy,
            "connection_state": self._connection_state.value,
            "components": {
                "mqtt_client": self.mqtt_client is not None,
                "mqtt_publisher": self.mqtt_publisher is not None,
                "mqtt_subscriber": self.mqtt_subscriber is not None
            },
            "last_error": self._last_error,
            "uptime_info": {
                "config_set": self.mqtt_config is not None,
                "message_store_size": len(self._message_store)
            }
        }
    
    @mcp_resource(uri="mqtt://brokers")
    async def get_brokers_resource(self) -> Dict[str, Any]:
        """Get embedded brokers status as resource."""
        try:
            running_brokers = self.broker_manager.get_running_brokers()
            all_brokers = self.broker_manager.list_brokers()
            
            brokers_info = []
            for broker_info in all_brokers:
                brokers_info.append({
                    "broker_id": broker_info.broker_id,
                    "name": broker_info.config.name,
                    "url": broker_info.url,
                    "status": broker_info.status,
                    "host": broker_info.config.host,
                    "port": broker_info.config.port,
                    "client_count": broker_info.client_count,
                    "started_at": broker_info.started_at.isoformat(),
                    "max_connections": broker_info.config.max_connections
                })
            
            return {
                "embedded_brokers": brokers_info,
                "total_brokers": len(all_brokers),
                "running_brokers": len(running_brokers),
                "amqtt_available": self.broker_manager.is_available()
            }
            
        except Exception as e:
            return {
                "error": f"Error accessing broker information: {str(e)}",
                "embedded_brokers": [],
                "total_brokers": 0,
                "running_brokers": 0,
                "amqtt_available": self.broker_manager.is_available()
            }

    async def run_server(self, host: str = "0.0.0.0", port: int = 3000):
        """Run the FastMCP server with HTTP transport."""
        try:
            # Use FastMCP's built-in run_http_async method
            await self.mcp.run_http_async(host=host, port=port)
            
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    
    def run_stdio(self):
        """Run the FastMCP server with STDIO transport (default for MCP clients)."""
        try:
            # FastMCP's run() method is synchronous and handles its own event loop
            self.mcp.run()
            
        except Exception as e:
            logger.error(f"STDIO server error: {e}")
            raise
    
    def get_mcp_server(self) -> FastMCP:
        """Get the FastMCP server instance."""
        return self.mcp