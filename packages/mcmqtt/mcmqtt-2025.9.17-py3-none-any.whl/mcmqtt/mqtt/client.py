"""Main MQTT client implementation."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union

from .connection import MQTTConnectionManager
from .types import MQTTConfig, MQTTMessage, MQTTQoS, MQTTStats, MQTTConnectionState

logger = logging.getLogger(__name__)


class MQTTClient:
    """High-level MQTT client with pub/sub functionality."""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self._connection_manager = MQTTConnectionManager(config)
        self._stats = MQTTStats()
        
        # Message handling
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._pattern_handlers: Dict[str, List[Callable]] = {}
        self._subscriptions: Dict[str, MQTTQoS] = {}
        
        # Message queue for offline storage
        self._offline_queue: List[MQTTMessage] = []
        self._max_offline_queue = 1000
        
        # Set up connection callbacks
        self._connection_manager.set_callbacks(
            on_connect=self._on_connect,
            on_disconnect=self._on_disconnect,
            on_message=self._on_message,
            on_error=self._on_error
        )
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connection_manager.is_connected
    
    @property
    def connection_info(self):
        """Get connection information."""
        return self._connection_manager.connection_info
    
    @property
    def stats(self) -> MQTTStats:
        """Get client statistics."""
        if self._connection_manager.is_connected and self._connection_manager._connected_at:
            uptime = (datetime.utcnow() - self._connection_manager._connected_at).total_seconds()
            self._stats.connection_uptime = uptime
        return self._stats
    
    async def connect(self) -> bool:
        """Connect to MQTT broker."""
        success = await self._connection_manager.connect()
        if success:
            logger.info("MQTT client connected successfully")
        return success
    
    async def disconnect(self) -> bool:
        """Disconnect from MQTT broker."""
        success = await self._connection_manager.disconnect()
        if success:
            logger.info("MQTT client disconnected")
        return success
    
    async def publish(self, 
                      topic: str, 
                      payload: Union[str, bytes, Dict[str, Any]], 
                      qos: MQTTQoS = None,
                      retain: bool = False) -> bool:
        """Publish message to topic."""
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=qos or self.config.qos,
            retain=retain
        )
        
        if not self.is_connected:
            # Queue message for later if offline
            if len(self._offline_queue) < self._max_offline_queue:
                self._offline_queue.append(message)
                logger.info(f"Queued message for offline delivery: {topic}")
            else:
                logger.warning(f"Offline queue full, dropping message: {topic}")
            return False
        
        # Convert payload to appropriate format
        if isinstance(payload, dict):
            payload_bytes = json.dumps(payload).encode('utf-8')
        elif isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload
        
        success = await self._connection_manager.publish(
            topic, payload_bytes, message.qos, retain
        )
        
        if success:
            self._stats.messages_sent += 1
            self._stats.bytes_sent += len(payload_bytes)
            self._stats.last_message_time = datetime.utcnow()
        
        return success
    
    async def subscribe(self, 
                        topic: str, 
                        qos: MQTTQoS = None,
                        handler: Optional[Callable] = None) -> bool:
        """Subscribe to topic with optional message handler."""
        if qos is None:
            qos = self.config.qos
            
        success = await self._connection_manager.subscribe(topic, qos)
        
        if success:
            self._subscriptions[topic] = qos
            self._stats.topics_subscribed = len(self._subscriptions)
            
            # Add handler if provided
            if handler:
                self.add_message_handler(topic, handler)
        
        return success
    
    async def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from topic."""
        success = await self._connection_manager.unsubscribe(topic)
        
        if success:
            self._subscriptions.pop(topic, None)
            self._stats.topics_subscribed = len(self._subscriptions)
            
            # Remove handlers for this topic
            self._message_handlers.pop(topic, None)
        
        return success
    
    def add_message_handler(self, topic: str, handler: Callable):
        """Add message handler for specific topic."""
        if topic not in self._message_handlers:
            self._message_handlers[topic] = []
        self._message_handlers[topic].append(handler)
        logger.debug(f"Added message handler for topic: {topic}")
    
    def add_pattern_handler(self, pattern: str, handler: Callable):
        """Add message handler for topic pattern (wildcards)."""
        if pattern not in self._pattern_handlers:
            self._pattern_handlers[pattern] = []
        self._pattern_handlers[pattern].append(handler)
        logger.debug(f"Added pattern handler for: {pattern}")
    
    def remove_message_handler(self, topic: str, handler: Callable):
        """Remove specific message handler."""
        if topic in self._message_handlers:
            try:
                self._message_handlers[topic].remove(handler)
                if not self._message_handlers[topic]:
                    del self._message_handlers[topic]
            except ValueError:
                pass
    
    async def publish_json(self, 
                           topic: str, 
                           data: Dict[str, Any],
                           qos: MQTTQoS = None,
                           retain: bool = False) -> bool:
        """Publish JSON data to topic."""
        return await self.publish(topic, data, qos, retain)
    
    async def wait_for_message(self, 
                               topic: str, 
                               timeout: float = 30.0) -> Optional[MQTTMessage]:
        """Wait for a specific message on a topic."""
        message_future = asyncio.Future()
        
        def handler(received_topic: str, payload: bytes, qos: int, retain: bool):
            if not message_future.done():
                message = MQTTMessage(
                    topic=received_topic,
                    payload=payload,
                    qos=MQTTQoS(qos),
                    retain=retain
                )
                message_future.set_result(message)
        
        # Subscribe temporarily if not already subscribed
        was_subscribed = topic in self._subscriptions
        if not was_subscribed:
            await self.subscribe(topic)
        
        # Add temporary handler
        self.add_message_handler(topic, handler)
        
        try:
            # Wait for message with timeout
            message = await asyncio.wait_for(message_future, timeout=timeout)
            return message
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for message on topic: {topic}")
            return None
        finally:
            # Cleanup
            self.remove_message_handler(topic, handler)
            if not was_subscribed:
                await self.unsubscribe(topic)
    
    async def request_response(self, 
                               request_topic: str,
                               response_topic: str, 
                               payload: Union[str, bytes, Dict[str, Any]],
                               timeout: float = 30.0) -> Optional[MQTTMessage]:
        """Send request and wait for response (request/response pattern)."""
        # Subscribe to response topic
        await self.subscribe(response_topic)
        
        # Send request
        await self.publish(request_topic, payload)
        
        # Wait for response
        response = await self.wait_for_message(response_topic, timeout)
        
        # Cleanup subscription
        await self.unsubscribe(response_topic)
        
        return response
    
    def get_subscriptions(self) -> Dict[str, MQTTQoS]:
        """Get current subscriptions."""
        return self._subscriptions.copy()
    
    async def _on_connect(self):
        """Handle connection established."""
        logger.info("MQTT connection established")
        
        # Resubscribe to all topics
        for topic, qos in self._subscriptions.items():
            await self._connection_manager.subscribe(topic, qos)
        
        # Send queued offline messages
        await self._send_offline_messages()
    
    async def _on_disconnect(self, rc: int):
        """Handle disconnection."""
        if rc == 0:
            logger.info("MQTT disconnected cleanly")
        else:
            logger.warning(f"MQTT disconnected unexpectedly: {rc}")
    
    async def _on_message(self, topic: str, payload: bytes, qos: int, retain: bool):
        """Handle incoming message."""
        self._stats.messages_received += 1
        self._stats.bytes_received += len(payload)
        self._stats.last_message_time = datetime.utcnow()
        
        logger.debug(f"Received message on {topic}: {len(payload)} bytes")
        
        # Create message object
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=MQTTQoS(qos),
            retain=retain
        )
        
        # Call topic-specific handlers
        if topic in self._message_handlers:
            for handler in self._message_handlers[topic]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler for {topic}: {e}")
        
        # Call pattern handlers
        for pattern, handlers in self._pattern_handlers.items():
            if self._topic_matches_pattern(topic, pattern):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        logger.error(f"Error in pattern handler for {pattern}: {e}")
    
    async def _on_error(self, error_msg: str):
        """Handle connection error."""
        logger.error(f"MQTT connection error: {error_msg}")
    
    async def _send_offline_messages(self):
        """Send queued offline messages."""
        if not self._offline_queue:
            return
            
        logger.info(f"Sending {len(self._offline_queue)} queued messages")
        
        # Send all queued messages
        messages_to_send = self._offline_queue.copy()
        self._offline_queue.clear()
        
        for message in messages_to_send:
            success = await self.publish(
                message.topic,
                message.payload,
                message.qos,
                message.retain
            )
            if not success:
                # Re-queue if failed
                self._offline_queue.append(message)
    
    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if topic matches MQTT wildcard pattern."""
        topic_parts = topic.split('/')
        pattern_parts = pattern.split('/')
        
        if len(pattern_parts) > len(topic_parts):
            return False
        
        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == '#':
                return True  # Multi-level wildcard matches rest
            elif pattern_part == '+':
                continue  # Single-level wildcard matches any single level
            elif i >= len(topic_parts) or pattern_part != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)