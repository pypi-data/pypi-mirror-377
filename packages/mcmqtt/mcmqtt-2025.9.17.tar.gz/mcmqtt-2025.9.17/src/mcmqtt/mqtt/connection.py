"""MQTT connection management."""

import asyncio
import logging
import ssl
from datetime import datetime
from typing import Optional, Callable, Dict, Any

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage as PahoMessage

from .types import MQTTConfig, MQTTConnectionState, MQTTConnectionInfo, MQTTQoS

logger = logging.getLogger(__name__)


class MQTTConnectionManager:
    """Manages MQTT connection lifecycle and events."""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self._client: Optional[mqtt.Client] = None
        self._state = MQTTConnectionState.DISCONNECTED
        self._connection_info = MQTTConnectionInfo(
            state=self._state,
            broker_host=config.broker_host,
            broker_port=config.broker_port,
            client_id=config.client_id
        )
        self._reconnect_task: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Event callbacks
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_message: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        
        # Connection state
        self._reconnect_attempts = 0
        self._connected_at: Optional[datetime] = None
        
    @property
    def state(self) -> MQTTConnectionState:
        """Current connection state."""
        return self._state
    
    @property
    def connection_info(self) -> MQTTConnectionInfo:
        """Get current connection information."""
        self._connection_info.state = self._state
        self._connection_info.connected_at = self._connected_at
        self._connection_info.reconnect_attempts = self._reconnect_attempts
        return self._connection_info
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._state == MQTTConnectionState.CONNECTED
    
    def set_callbacks(self, 
                      on_connect: Optional[Callable] = None,
                      on_disconnect: Optional[Callable] = None,
                      on_message: Optional[Callable] = None,
                      on_error: Optional[Callable] = None):
        """Set event callbacks."""
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_message = on_message
        self._on_error = on_error
    
    async def connect(self) -> bool:
        """Connect to MQTT broker."""
        if self._state == MQTTConnectionState.CONNECTED:
            logger.warning("Already connected")
            return True
            
        self._loop = asyncio.get_event_loop()
        self._set_state(MQTTConnectionState.CONNECTING)
        
        try:
            # Create MQTT client
            self._client = mqtt.Client(
                client_id=self.config.client_id,
                clean_session=self.config.clean_session,
                protocol=mqtt.MQTTv311
            )
            
            # Set callbacks
            self._client.on_connect = self._on_paho_connect
            self._client.on_disconnect = self._on_paho_disconnect
            self._client.on_message = self._on_paho_message
            self._client.on_log = self._on_paho_log
            
            # Configure authentication
            if self.config.username and self.config.password:
                self._client.username_pw_set(
                    self.config.username, 
                    self.config.password
                )
            
            # Configure TLS
            if self.config.use_tls:
                context = ssl.create_default_context()
                if self.config.ca_cert_path:
                    context.load_verify_locations(self.config.ca_cert_path)
                if self.config.cert_path and self.config.key_path:
                    context.load_cert_chain(self.config.cert_path, self.config.key_path)
                self._client.tls_set_context(context)
            
            # Configure last will
            if self.config.will_topic and self.config.will_payload:
                self._client.will_set(
                    self.config.will_topic,
                    self.config.will_payload,
                    qos=self.config.will_qos.value,
                    retain=self.config.will_retain
                )
            
            # Connect to broker
            logger.info(f"Connecting to MQTT broker {self.config.broker_host}:{self.config.broker_port}")
            result = self._client.connect(
                self.config.broker_host,
                self.config.broker_port,
                self.config.keepalive
            )
            
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise ConnectionError(f"Failed to connect: {mqtt.error_string(result)}")
            
            # Start network loop
            self._client.loop_start()
            
            # Wait for connection to be established
            connection_timeout = 10.0
            start_time = asyncio.get_event_loop().time()
            
            while (self._state == MQTTConnectionState.CONNECTING and 
                   asyncio.get_event_loop().time() - start_time < connection_timeout):
                await asyncio.sleep(0.1)
            
            if self._state == MQTTConnectionState.CONNECTED:
                logger.info("Successfully connected to MQTT broker")
                self._reconnect_attempts = 0
                return True
            else:
                raise ConnectionError("Connection timeout")
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._set_state(MQTTConnectionState.ERROR, str(e))
            if self._client:
                self._client.loop_stop()
                self._client = None
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MQTT broker."""
        if self._state == MQTTConnectionState.DISCONNECTED:
            return True
            
        try:
            if self._reconnect_task:
                self._reconnect_task.cancel()
                self._reconnect_task = None
                
            if self._client:
                self._client.disconnect()
                self._client.loop_stop()
                self._client = None
                
            self._set_state(MQTTConnectionState.DISCONNECTED)
            logger.info("Disconnected from MQTT broker")
            return True
            
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return False
    
    async def publish(self, topic: str, payload: str | bytes, 
                      qos: MQTTQoS = None, retain: bool = False) -> bool:
        """Publish message to topic."""
        if not self.is_connected:
            logger.error("Cannot publish: not connected")
            return False
            
        try:
            if qos is None:
                qos = self.config.qos
                
            result = self._client.publish(
                topic, 
                payload, 
                qos=qos.value, 
                retain=retain
            )
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Publish failed: {mqtt.error_string(result.rc)}")
                return False
                
            logger.debug(f"Published to {topic}: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False
    
    async def subscribe(self, topic: str, qos: MQTTQoS = None) -> bool:
        """Subscribe to topic."""
        if not self.is_connected:
            logger.error("Cannot subscribe: not connected")
            return False
            
        try:
            if qos is None:
                qos = self.config.qos
                
            result = self._client.subscribe(topic, qos=qos.value)
            
            if result[0] != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Subscribe failed: {mqtt.error_string(result[0])}")
                return False
                
            logger.info(f"Subscribed to {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Subscribe error: {e}")
            return False
    
    async def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from topic."""
        if not self.is_connected:
            logger.error("Cannot unsubscribe: not connected")
            return False
            
        try:
            result = self._client.unsubscribe(topic)
            
            if result[0] != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Unsubscribe failed: {mqtt.error_string(result[0])}")
                return False
                
            logger.info(f"Unsubscribed from {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Unsubscribe error: {e}")
            return False
    
    def _set_state(self, new_state: MQTTConnectionState, error_msg: Optional[str] = None):
        """Update connection state."""
        old_state = self._state
        self._state = new_state
        self._connection_info.state = new_state
        self._connection_info.error_message = error_msg
        
        if new_state == MQTTConnectionState.CONNECTED:
            self._connected_at = datetime.utcnow()
        elif new_state == MQTTConnectionState.DISCONNECTED:
            self._connected_at = None
            
        logger.debug(f"State changed: {old_state} -> {new_state}")
    
    def _on_paho_connect(self, client, userdata, flags, rc):
        """Handle paho MQTT connect callback."""
        if rc == 0:
            self._set_state(MQTTConnectionState.CONNECTED)
            if self._on_connect and self._loop:
                self._loop.create_task(self._on_connect())
        else:
            error_msg = f"Connection failed with code {rc}: {mqtt.connack_string(rc)}"
            self._set_state(MQTTConnectionState.ERROR, error_msg)
            if self._on_error and self._loop:
                self._loop.create_task(self._on_error(error_msg))
    
    def _on_paho_disconnect(self, client, userdata, rc):
        """Handle paho MQTT disconnect callback."""
        if rc == 0:
            # Clean disconnect
            self._set_state(MQTTConnectionState.DISCONNECTED)
        else:
            # Unexpected disconnect
            self._set_state(MQTTConnectionState.ERROR, f"Unexpected disconnect: {rc}")
            self._start_reconnect()
            
        if self._on_disconnect and self._loop:
            self._loop.create_task(self._on_disconnect(rc))
    
    def _on_paho_message(self, client, userdata, msg: PahoMessage):
        """Handle paho MQTT message callback."""
        if self._on_message and self._loop:
            self._loop.create_task(self._on_message(msg.topic, msg.payload, msg.qos, msg.retain))
    
    def _on_paho_log(self, client, userdata, level, buf):
        """Handle paho MQTT log callback."""
        logger.debug(f"MQTT Log [{level}]: {buf}")
    
    def _start_reconnect(self):
        """Start reconnection process."""
        if (self._reconnect_attempts < self.config.max_reconnect_attempts and 
            not self._reconnect_task):
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
        """Reconnection loop."""
        while (self._reconnect_attempts < self.config.max_reconnect_attempts and 
               self._state != MQTTConnectionState.CONNECTED):
            
            self._reconnect_attempts += 1
            self._set_state(MQTTConnectionState.RECONNECTING)
            
            logger.info(f"Reconnection attempt {self._reconnect_attempts}/{self.config.max_reconnect_attempts}")
            
            await asyncio.sleep(self.config.reconnect_interval)
            
            success = await self.connect()
            if success:
                break
        
        if self._state != MQTTConnectionState.CONNECTED:
            logger.error("Max reconnection attempts reached")
            self._set_state(MQTTConnectionState.ERROR, "Max reconnection attempts reached")
        
        self._reconnect_task = None