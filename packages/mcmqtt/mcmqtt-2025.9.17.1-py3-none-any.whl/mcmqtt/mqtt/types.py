"""Type definitions for MQTT functionality."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator


class MQTTConnectionState(str, Enum):
    """MQTT connection states."""
    
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"  
    CONNECTED = "connected"
    CONFIGURED = "configured"  # Client initialized but not connected
    RECONNECTING = "reconnecting"
    ERROR = "error"


class MQTTQoS(int, Enum):
    """MQTT Quality of Service levels."""
    
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


@dataclass
class MQTTMessage:
    """Represents an MQTT message."""
    
    topic: str
    payload: Union[str, bytes, Dict[str, Any]]
    qos: MQTTQoS = MQTTQoS.AT_LEAST_ONCE
    retain: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @property
    def payload_str(self) -> str:
        """Get payload as string."""
        if isinstance(self.payload, str):
            return self.payload
        elif isinstance(self.payload, bytes):
            return self.payload.decode('utf-8')
        elif isinstance(self.payload, dict):
            import json
            return json.dumps(self.payload)
        else:
            return str(self.payload)
    
    @property
    def payload_bytes(self) -> bytes:
        """Get payload as bytes."""
        if isinstance(self.payload, bytes):
            return self.payload
        elif isinstance(self.payload, str):
            return self.payload.encode('utf-8')
        elif isinstance(self.payload, dict):
            import json
            return json.dumps(self.payload).encode('utf-8')
        else:
            return str(self.payload).encode('utf-8')
    
    @property
    def payload_dict(self) -> Dict[str, Any]:
        """Get payload as dictionary (if JSON)."""
        if isinstance(self.payload, dict):
            return self.payload
        elif isinstance(self.payload, (str, bytes)):
            try:
                import json
                return json.loads(self.payload_str)
            except (json.JSONDecodeError, ValueError):
                return {"raw": self.payload_str}
        else:
            return {"raw": str(self.payload)}


class MQTTConfig(BaseModel):
    """MQTT client configuration."""
    
    broker_host: str = Field(..., description="MQTT broker hostname")
    broker_port: int = Field(1883, description="MQTT broker port")
    client_id: str = Field(..., description="MQTT client ID")
    username: Optional[str] = Field(None, description="MQTT username")
    password: Optional[str] = Field(None, description="MQTT password") 
    keepalive: int = Field(60, description="Keep alive interval in seconds")
    qos: MQTTQoS = Field(MQTTQoS.AT_LEAST_ONCE, description="Default QoS level")
    clean_session: bool = Field(True, description="Clean session flag")
    will_topic: Optional[str] = Field(None, description="Last will topic")
    will_payload: Optional[str] = Field(None, description="Last will payload")
    will_qos: MQTTQoS = Field(MQTTQoS.AT_LEAST_ONCE, description="Last will QoS")
    will_retain: bool = Field(False, description="Last will retain flag")
    reconnect_interval: int = Field(5, description="Reconnect interval in seconds")
    max_reconnect_attempts: int = Field(10, description="Maximum reconnection attempts")
    use_tls: bool = Field(False, description="Enable TLS/SSL")
    ca_cert_path: Optional[str] = Field(None, description="Path to CA certificate")
    cert_path: Optional[str] = Field(None, description="Path to client certificate")
    key_path: Optional[str] = Field(None, description="Path to client private key")
    
    @validator('broker_port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('keepalive')
    def validate_keepalive(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Keepalive must be between 1 and 65535 seconds')
        return v
    
    @validator('reconnect_interval')
    def validate_reconnect_interval(cls, v):
        if v < 1:
            raise ValueError('Reconnect interval must be at least 1 second')
        return v


class MQTTConnectionInfo(BaseModel):
    """Information about MQTT connection."""
    
    state: MQTTConnectionState
    broker_host: str
    broker_port: int
    client_id: str
    connected_at: Optional[datetime] = None
    last_ping: Optional[datetime] = None
    reconnect_attempts: int = 0
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MQTTStats(BaseModel):
    """MQTT client statistics."""
    
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    topics_subscribed: int = 0
    connection_uptime: Optional[float] = None
    last_message_time: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }