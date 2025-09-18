"""Pytest configuration and fixtures for mcmqtt tests."""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# MQTT fixtures removed to avoid heavy imports during test discovery
# Individual test files can import and create their own configs as needed


@pytest.fixture
def mock_paho_client():
    """Create a mock paho MQTT client."""
    mock_client = MagicMock()
    mock_client.connect.return_value = 0  # MQTT_ERR_SUCCESS
    mock_client.disconnect.return_value = 0
    mock_client.publish.return_value = MagicMock(rc=0)
    mock_client.subscribe.return_value = (0, 1)
    mock_client.unsubscribe.return_value = (0, None)
    mock_client.loop_start.return_value = None
    mock_client.loop_stop.return_value = None
    return mock_client


# MQTT client fixtures removed to avoid heavy imports during test discovery


# Test data fixtures
@pytest.fixture
def sample_mqtt_message() -> Dict[str, Any]:
    """Sample MQTT message data."""
    return {
        "topic": "test/topic",
        "payload": "test message",
        "qos": 1,
        "retain": False
    }


@pytest.fixture
def sample_json_message() -> Dict[str, Any]:
    """Sample JSON MQTT message data."""
    return {
        "topic": "test/json",
        "payload": {
            "temperature": 25.5,
            "humidity": 60,
            "timestamp": "2025-09-16T01:48:00Z"
        },
        "qos": 1,
        "retain": False
    }


@pytest.fixture
def batch_messages() -> list:
    """Sample batch of MQTT messages."""
    return [
        {
            "topic": "sensor/temp/1",
            "payload": {"value": 20.1, "unit": "C"},
            "qos": 1
        },
        {
            "topic": "sensor/temp/2", 
            "payload": {"value": 22.3, "unit": "C"},
            "qos": 1
        },
        {
            "topic": "sensor/humidity/1",
            "payload": {"value": 45.0, "unit": "%"},
            "qos": 0
        }
    ]


# Mock external dependencies
@pytest.fixture
def mock_mosquitto_broker():
    """Mock mosquitto broker for integration tests."""
    mock_broker = MagicMock()
    mock_broker.start.return_value = True
    mock_broker.stop.return_value = True
    mock_broker.is_running = True
    return mock_broker


@pytest.fixture
def temporary_directory():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    original_env = dict(os.environ)
    
    # Set test environment variables
    test_env = {
        "MQTT_BROKER_HOST": "localhost",
        "MQTT_BROKER_PORT": "1883",
        "MQTT_CLIENT_ID": "test-client",
        "LOG_LEVEL": "DEBUG"
    }
    
    os.environ.update(test_env)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# JSON Schema fixtures for validation tests
@pytest.fixture
def sensor_data_schema() -> Dict[str, Any]:
    """JSON schema for sensor data validation."""
    return {
        "type": "object",
        "required": ["value", "unit", "timestamp"],
        "properties": {
            "value": {"type": "number"},
            "unit": {"type": "string"},
            "timestamp": {"type": "string"},
            "sensor_id": {"type": "string"}
        }
    }


@pytest.fixture
def valid_sensor_data() -> Dict[str, Any]:
    """Valid sensor data matching the schema."""
    return {
        "value": 25.5,
        "unit": "C",
        "timestamp": "2025-09-16T01:48:00Z",
        "sensor_id": "temp_01"
    }


@pytest.fixture
def invalid_sensor_data() -> Dict[str, Any]:
    """Invalid sensor data not matching the schema."""
    return {
        "value": "invalid",  # Should be number
        "unit": 123,        # Should be string
        # Missing required timestamp
    }


# Performance test fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        "message_count": 1000,
        "concurrent_connections": 10,
        "message_size_bytes": 1024,
        "test_duration_seconds": 30
    }


# Error simulation fixtures
@pytest.fixture
def connection_error_scenarios():
    """Different connection error scenarios for testing."""
    return [
        {"error_type": "timeout", "description": "Connection timeout"},
        {"error_type": "refused", "description": "Connection refused"},
        {"error_type": "auth_failed", "description": "Authentication failed"},
        {"error_type": "network_error", "description": "Network unreachable"}
    ]


# Cleanup utilities
@pytest.fixture
def cleanup_subscriptions():
    """Utility to cleanup test subscriptions."""
    subscriptions_to_clean = []
    
    def add_subscription(topic: str):
        subscriptions_to_clean.append(topic)
    
    yield add_subscription
    
    # Cleanup logic would go here in a real implementation
    # For now, just track what needs cleaning
    if subscriptions_to_clean:
        print(f"Cleaning up {len(subscriptions_to_clean)} test subscriptions")


# Integration test utilities
@pytest.fixture
def integration_test_broker():
    """Integration test broker setup."""
    # In a real scenario, this would start a test MQTT broker
    # For now, return configuration for testing
    return {
        "host": "localhost",
        "port": 1883,
        "test_topics": [
            "test/integration/basic",
            "test/integration/json",
            "test/integration/wildcard/+",
            "test/integration/multilevel/#"
        ]
    }