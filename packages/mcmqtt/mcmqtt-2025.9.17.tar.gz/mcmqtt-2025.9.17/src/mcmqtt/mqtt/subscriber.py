"""MQTT subscriber functionality."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass

from .client import MQTTClient
from .types import MQTTMessage, MQTTQoS

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionInfo:
    """Information about a subscription."""
    topic: str
    qos: MQTTQoS
    handler: Optional[Callable]
    subscribed_at: datetime
    message_count: int = 0
    last_message: Optional[datetime] = None


class MQTTSubscriber:
    """Enhanced MQTT subscriber with advanced features."""
    
    def __init__(self, client: MQTTClient):
        self.client = client
        self._subscriptions: Dict[str, SubscriptionInfo] = {}
        self._message_filters: List[Callable] = []
        self._message_buffer: List[MQTTMessage] = []
        self._max_buffer_size = 10000
        
        # Pattern matching for dynamic subscriptions
        self._pattern_subscriptions: Dict[str, SubscriptionInfo] = {}
        
        # Rate limiting
        self._rate_limits: Dict[str, Dict] = {}
    
    def add_handler(self, topic: str, handler: Callable):
        """TEMPORARY WORKAROUND: Redirect to client's add_message_handler method."""
        logger.warning(f"DEPRECATED: add_handler called, redirecting to add_message_handler for topic: {topic}")
        return self.client.add_message_handler(topic, handler)
        
    async def subscribe_with_filter(self, 
                                    topic: str,
                                    message_filter: Callable[[MQTTMessage], bool],
                                    handler: Optional[Callable] = None,
                                    qos: MQTTQoS = None) -> bool:
        """Subscribe to topic with message filtering."""
        def filtered_handler(message: MQTTMessage):
            try:
                if message_filter(message):
                    if handler:
                        if asyncio.iscoroutinefunction(handler):
                            asyncio.create_task(handler(message))
                        else:
                            handler(message)
                    self._add_to_buffer(message)
                    self._update_subscription_stats(topic, message)
            except Exception as e:
                logger.error(f"Error in filtered handler for {topic}: {e}")
        
        success = await self.client.subscribe(topic, qos, filtered_handler)
        if success:
            self._subscriptions[topic] = SubscriptionInfo(
                topic=topic,
                qos=qos or self.client.config.qos,
                handler=filtered_handler,
                subscribed_at=datetime.utcnow()
            )
        return success
    
    async def subscribe_with_rate_limit(self, 
                                        topic: str,
                                        max_messages_per_second: int,
                                        handler: Optional[Callable] = None,
                                        qos: MQTTQoS = None) -> bool:
        """Subscribe to topic with rate limiting."""
        rate_limit_info = {
            'max_rate': max_messages_per_second,
            'messages': [],
            'dropped': 0
        }
        self._rate_limits[topic] = rate_limit_info
        
        def rate_limited_handler(message: MQTTMessage):
            try:
                now = datetime.utcnow()
                
                # Clean old messages
                cutoff = now - timedelta(seconds=1)
                rate_limit_info['messages'] = [
                    ts for ts in rate_limit_info['messages'] if ts > cutoff
                ]
                
                # Check rate limit
                if len(rate_limit_info['messages']) >= max_messages_per_second:
                    rate_limit_info['dropped'] += 1
                    logger.debug(f"Rate limit exceeded for {topic}, dropping message")
                    return
                
                # Accept message
                rate_limit_info['messages'].append(now)
                
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(message))
                    else:
                        handler(message)
                
                self._add_to_buffer(message)
                self._update_subscription_stats(topic, message)
                
            except Exception as e:
                logger.error(f"Error in rate limited handler for {topic}: {e}")
        
        success = await self.client.subscribe(topic, qos, rate_limited_handler)
        if success:
            self._subscriptions[topic] = SubscriptionInfo(
                topic=topic,
                qos=qos or self.client.config.qos,
                handler=rate_limited_handler,
                subscribed_at=datetime.utcnow()
            )
        return success
    
    async def subscribe_json_schema(self, 
                                    topic: str,
                                    schema: Dict[str, Any],
                                    handler: Optional[Callable] = None,
                                    qos: MQTTQoS = None) -> bool:
        """Subscribe to topic with JSON schema validation."""
        def schema_handler(message: MQTTMessage):
            try:
                # Try to parse as JSON
                try:
                    data = message.payload_dict
                except Exception:
                    logger.debug(f"Message on {topic} is not valid JSON")
                    return
                
                # Validate against schema
                if self._validate_json_schema(data, schema):
                    if handler:
                        if asyncio.iscoroutinefunction(handler):
                            asyncio.create_task(handler(message))
                        else:
                            handler(message)
                    self._add_to_buffer(message)
                    self._update_subscription_stats(topic, message)
                else:
                    logger.debug(f"Message on {topic} failed schema validation")
                    
            except Exception as e:
                logger.error(f"Error in schema handler for {topic}: {e}")
        
        success = await self.client.subscribe(topic, qos, schema_handler)
        if success:
            self._subscriptions[topic] = SubscriptionInfo(
                topic=topic,
                qos=qos or self.client.config.qos,
                handler=schema_handler,
                subscribed_at=datetime.utcnow()
            )
        return success
    
    async def subscribe_compressed(self, 
                                   topic: str,
                                   handler: Optional[Callable] = None,
                                   qos: MQTTQoS = None) -> bool:
        """Subscribe to topic expecting compressed messages."""
        def decompression_handler(message: MQTTMessage):
            try:
                payload = message.payload_bytes
                
                # Check for compression header
                if payload.startswith(b'compression:'):
                    header_end = payload.find(b':', 12)  # After 'compression:'
                    if header_end != -1:
                        compression_type = payload[12:header_end].decode()
                        compressed_data = payload[header_end + 1:]
                        
                        # Decompress
                        if compression_type == 'gzip':
                            import gzip
                            decompressed = gzip.decompress(compressed_data)
                        elif compression_type == 'zlib':
                            import zlib
                            decompressed = zlib.decompress(compressed_data)
                        else:
                            logger.warning(f"Unknown compression type: {compression_type}")
                            return
                        
                        # Create new message with decompressed payload
                        decompressed_message = MQTTMessage(
                            topic=message.topic,
                            payload=decompressed,
                            qos=message.qos,
                            retain=message.retain,
                            timestamp=message.timestamp
                        )
                        
                        if handler:
                            if asyncio.iscoroutinefunction(handler):
                                asyncio.create_task(handler(decompressed_message))
                            else:
                                handler(decompressed_message)
                        
                        self._add_to_buffer(decompressed_message)
                        self._update_subscription_stats(topic, decompressed_message)
                    else:
                        logger.warning("Invalid compression header format")
                else:
                    # Not compressed, handle normally
                    if handler:
                        if asyncio.iscoroutinefunction(handler):
                            asyncio.create_task(handler(message))
                        else:
                            handler(message)
                    self._add_to_buffer(message)
                    self._update_subscription_stats(topic, message)
                    
            except Exception as e:
                logger.error(f"Error in decompression handler for {topic}: {e}")
        
        success = await self.client.subscribe(topic, qos, decompression_handler)
        if success:
            self._subscriptions[topic] = SubscriptionInfo(
                topic=topic,
                qos=qos or self.client.config.qos,
                handler=decompression_handler,
                subscribed_at=datetime.utcnow()
            )
        return success
    
    async def subscribe_pattern(self, 
                                pattern: str,
                                handler: Optional[Callable] = None,
                                qos: MQTTQoS = None) -> bool:
        """Subscribe to topic pattern with wildcards."""
        success = await self.client.subscribe(pattern, qos, handler)
        if success:
            self._pattern_subscriptions[pattern] = SubscriptionInfo(
                topic=pattern,
                qos=qos or self.client.config.qos,
                handler=handler,
                subscribed_at=datetime.utcnow()
            )
        return success
    
    def add_global_filter(self, message_filter: Callable[[MQTTMessage], bool]):
        """Add a global message filter that applies to all subscriptions."""
        self._message_filters.append(message_filter)
    
    def remove_global_filter(self, message_filter: Callable[[MQTTMessage], bool]):
        """Remove a global message filter."""
        try:
            self._message_filters.remove(message_filter)
        except ValueError:
            pass
    
    def get_buffered_messages(self, 
                              topic: Optional[str] = None,
                              since: Optional[datetime] = None,
                              limit: Optional[int] = None) -> List[MQTTMessage]:
        """Get buffered messages with optional filtering."""
        messages = self._message_buffer
        
        # Filter by topic
        if topic:
            messages = [msg for msg in messages if msg.topic == topic]
        
        # Filter by time
        if since:
            messages = [msg for msg in messages if msg.timestamp >= since]
        
        # Limit results
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_buffer(self, topic: Optional[str] = None):
        """Clear message buffer."""
        if topic:
            self._message_buffer = [
                msg for msg in self._message_buffer if msg.topic != topic
            ]
        else:
            self._message_buffer.clear()
    
    def get_subscription_info(self, topic: str) -> Optional[SubscriptionInfo]:
        """Get information about a subscription."""
        return self._subscriptions.get(topic) or self._pattern_subscriptions.get(topic)
    
    def get_all_subscriptions(self) -> Dict[str, SubscriptionInfo]:
        """Get all subscription information."""
        result = self._subscriptions.copy()
        result.update(self._pattern_subscriptions)
        return result
    
    def get_rate_limit_stats(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get rate limiting statistics for a topic."""
        return self._rate_limits.get(topic)
    
    async def wait_for_messages(self, 
                                topic: str,
                                count: int,
                                timeout: float = 30.0) -> List[MQTTMessage]:
        """Wait for a specific number of messages on a topic."""
        messages = []
        message_future = asyncio.Future()
        
        def collector(message: MQTTMessage):
            messages.append(message)
            if len(messages) >= count and not message_future.done():
                message_future.set_result(messages)
        
        # Subscribe temporarily if not already subscribed
        was_subscribed = topic in self._subscriptions
        if not was_subscribed:
            await self.client.subscribe(topic)
        
        # Add temporary handler
        self.client.add_message_handler(topic, collector)
        
        try:
            # Wait for messages with timeout
            result = await asyncio.wait_for(message_future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for {count} messages on topic: {topic}")
            return messages  # Return partial results
        finally:
            # Cleanup
            self.client.remove_message_handler(topic, collector)
            if not was_subscribed:
                await self.client.unsubscribe(topic)
    
    def _add_to_buffer(self, message: MQTTMessage):
        """Add message to buffer."""
        # Apply global filters
        for filter_func in self._message_filters:
            try:
                if not filter_func(message):
                    return  # Message filtered out
            except Exception as e:
                logger.error(f"Error in global filter: {e}")
        
        self._message_buffer.append(message)
        
        # Limit buffer size
        if len(self._message_buffer) > self._max_buffer_size:
            self._message_buffer = self._message_buffer[-self._max_buffer_size:]
    
    def _update_subscription_stats(self, topic: str, message: MQTTMessage):
        """Update subscription statistics."""
        if topic in self._subscriptions:
            sub_info = self._subscriptions[topic]
            sub_info.message_count += 1
            sub_info.last_message = message.timestamp
    
    def _validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Basic JSON schema validation (simplified)."""
        # This is a simplified validation - in production, use jsonschema library
        try:
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    return False
            
            properties = schema.get('properties', {})
            for field, field_schema in properties.items():
                if field in data:
                    expected_type = field_schema.get('type')
                    if expected_type == 'string' and not isinstance(data[field], str):
                        return False
                    elif expected_type == 'number' and not isinstance(data[field], (int, float)):
                        return False
                    elif expected_type == 'boolean' and not isinstance(data[field], bool):
                        return False
                    elif expected_type == 'array' and not isinstance(data[field], list):
                        return False
                    elif expected_type == 'object' and not isinstance(data[field], dict):
                        return False
            
            return True
            
        except Exception:
            return False