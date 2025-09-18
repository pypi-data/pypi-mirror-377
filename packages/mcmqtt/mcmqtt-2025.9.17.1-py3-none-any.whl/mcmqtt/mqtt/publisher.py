"""MQTT publisher functionality."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .client import MQTTClient
from .types import MQTTMessage, MQTTQoS

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Enhanced MQTT publisher with advanced features."""
    
    def __init__(self, client: MQTTClient):
        self.client = client
        self._published_messages: List[MQTTMessage] = []
        self._max_history = 1000
        
    async def publish_with_retry(self, 
                                 topic: str,
                                 payload: Union[str, bytes, Dict[str, Any]],
                                 qos: MQTTQoS = None,
                                 retain: bool = False,
                                 max_retries: int = 3,
                                 retry_delay: float = 1.0) -> bool:
        """Publish message with retry logic."""
        for attempt in range(max_retries + 1):
            success = await self.client.publish(topic, payload, qos, retain)
            if success:
                self._add_to_history(topic, payload, qos, retain)
                return True
                
            if attempt < max_retries:
                logger.warning(f"Publish attempt {attempt + 1} failed, retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            
        logger.error(f"Failed to publish after {max_retries + 1} attempts")
        return False
    
    async def publish_batch(self, 
                            messages: List[Dict[str, Any]],
                            default_qos: MQTTQoS = None) -> Dict[str, bool]:
        """Publish multiple messages in batch."""
        results = {}
        
        tasks = []
        for msg_data in messages:
            topic = msg_data['topic']
            payload = msg_data['payload']
            qos = msg_data.get('qos', default_qos)
            retain = msg_data.get('retain', False)
            
            task = self.client.publish(topic, payload, qos, retain)
            tasks.append((topic, task))
        
        # Execute all publishes concurrently
        for topic, task in tasks:
            try:
                success = await task
                results[topic] = success
                if success:
                    self._add_to_history(topic, payload, qos, retain)
            except Exception as e:
                logger.error(f"Batch publish error for {topic}: {e}")
                results[topic] = False
        
        return results
    
    async def publish_scheduled(self, 
                                topic: str,
                                payload: Union[str, bytes, Dict[str, Any]],
                                delay: float,
                                qos: MQTTQoS = None,
                                retain: bool = False) -> bool:
        """Publish message after a delay."""
        await asyncio.sleep(delay)
        success = await self.client.publish(topic, payload, qos, retain)
        if success:
            self._add_to_history(topic, payload, qos, retain)
        return success
    
    async def publish_periodic(self, 
                               topic: str,
                               payload_generator: callable,
                               interval: float,
                               max_iterations: Optional[int] = None,
                               qos: MQTTQoS = None,
                               retain: bool = False) -> None:
        """Publish messages periodically."""
        iteration = 0
        
        while max_iterations is None or iteration < max_iterations:
            try:
                payload = payload_generator()
                success = await self.client.publish(topic, payload, qos, retain)
                if success:
                    self._add_to_history(topic, payload, qos, retain)
                    
                iteration += 1
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Periodic publish error: {e}")
                break
    
    async def publish_with_confirmation(self, 
                                        topic: str,
                                        payload: Union[str, bytes, Dict[str, Any]],
                                        confirmation_topic: str,
                                        timeout: float = 30.0,
                                        qos: MQTTQoS = None,
                                        retain: bool = False) -> bool:
        """Publish message and wait for confirmation on another topic."""
        # Subscribe to confirmation topic
        await self.client.subscribe(confirmation_topic)
        
        # Publish message
        success = await self.client.publish(topic, payload, qos, retain)
        if not success:
            await self.client.unsubscribe(confirmation_topic)
            return False
        
        # Wait for confirmation
        confirmation = await self.client.wait_for_message(confirmation_topic, timeout)
        
        # Cleanup
        await self.client.unsubscribe(confirmation_topic)
        
        if confirmation:
            self._add_to_history(topic, payload, qos, retain)
            return True
        else:
            logger.warning(f"No confirmation received for message on {topic}")
            return False
    
    async def publish_json_schema(self, 
                                  topic: str,
                                  data: Dict[str, Any],
                                  schema: Dict[str, Any],
                                  qos: MQTTQoS = None,
                                  retain: bool = False) -> bool:
        """Publish JSON data with schema validation."""
        try:
            # Basic schema validation (simplified)
            if not self._validate_json_schema(data, schema):
                logger.error("Data does not match schema")
                return False
                
            success = await self.client.publish_json(topic, data, qos, retain)
            if success:
                self._add_to_history(topic, data, qos, retain)
            return success
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    async def publish_compressed(self, 
                                 topic: str,
                                 payload: Union[str, bytes],
                                 compression: str = 'gzip',
                                 qos: MQTTQoS = None,
                                 retain: bool = False) -> bool:
        """Publish compressed message."""
        try:
            import gzip
            import zlib
            
            if isinstance(payload, str):
                payload = payload.encode('utf-8')
            
            if compression == 'gzip':
                compressed = gzip.compress(payload)
            elif compression == 'zlib':
                compressed = zlib.compress(payload)
            else:
                raise ValueError(f"Unsupported compression: {compression}")
            
            # Add compression header
            compressed_payload = f"compression:{compression}:".encode() + compressed
            
            success = await self.client.publish(topic, compressed_payload, qos, retain)
            if success:
                self._add_to_history(topic, payload, qos, retain)
            return success
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return False
    
    def get_publish_history(self, limit: Optional[int] = None) -> List[MQTTMessage]:
        """Get history of published messages."""
        if limit:
            return self._published_messages[-limit:]
        return self._published_messages.copy()
    
    def clear_history(self):
        """Clear publish history."""
        self._published_messages.clear()
    
    def _add_to_history(self, topic: str, payload: Any, qos: MQTTQoS, retain: bool):
        """Add message to publish history."""
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=qos or self.client.config.qos,
            retain=retain,
            timestamp=datetime.utcnow()
        )
        
        self._published_messages.append(message)
        
        # Limit history size
        if len(self._published_messages) > self._max_history:
            self._published_messages = self._published_messages[-self._max_history:]
    
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