"""Environment and configuration management for mcmqtt."""

import os
import logging
from typing import Optional
from argparse import Namespace

from ..mqtt.types import MQTTConfig, MQTTQoS


def _parse_bool(value: str) -> bool:
    """Parse a string value to boolean, supporting various formats."""
    if not value:
        return False
    return value.lower() in ("true", "1", "yes", "on")


def create_mqtt_config_from_env() -> Optional[MQTTConfig]:
    """Create MQTT configuration from environment variables."""
    try:
        broker_host = os.getenv("MQTT_BROKER_HOST")
        if not broker_host:
            return None
            
        return MQTTConfig(
            broker_host=broker_host,
            broker_port=int(os.getenv("MQTT_BROKER_PORT", "1883")),
            client_id=os.getenv("MQTT_CLIENT_ID", f"mcmqtt-{os.getpid()}"),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            keepalive=int(os.getenv("MQTT_KEEPALIVE", "60")),
            qos=MQTTQoS(int(os.getenv("MQTT_QOS", "1"))),
            use_tls=_parse_bool(os.getenv("MQTT_USE_TLS", "false")),
            clean_session=_parse_bool(os.getenv("MQTT_CLEAN_SESSION", "true")),
            reconnect_interval=int(os.getenv("MQTT_RECONNECT_INTERVAL", "5")),
            max_reconnect_attempts=int(os.getenv("MQTT_MAX_RECONNECT_ATTEMPTS", "10"))
        )
    except Exception as e:
        logging.error(f"Error creating MQTT config from environment: {e}")
        return None


def create_mqtt_config_from_args(args: Namespace) -> Optional[MQTTConfig]:
    """Create MQTT configuration from command-line arguments."""
    if not args.mqtt_host:
        return None
        
    try:
        return MQTTConfig(
            broker_host=args.mqtt_host,
            broker_port=args.mqtt_port,
            client_id=args.mqtt_client_id or f"mcmqtt-{os.getpid()}",
            username=args.mqtt_username,
            password=args.mqtt_password
        )
    except Exception as e:
        logging.error(f"Error creating MQTT config from arguments: {e}")
        return None