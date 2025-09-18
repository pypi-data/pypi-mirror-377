"""Command-line argument parsing for mcmqtt."""

import argparse
from argparse import Namespace


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for mcmqtt."""
    parser = argparse.ArgumentParser(
        description="mcmqtt - FastMCP MQTT Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcmqtt                                    # Run with STDIO transport (default)
  mcmqtt --transport http --port 3000      # Run with HTTP transport
  mcmqtt --auto-connect                     # Auto-connect to MQTT broker
  mcmqtt --log-level INFO --log-file mcp.log  # Enable logging to file
  
Environment Variables:
  MQTT_BROKER_HOST     MQTT broker hostname
  MQTT_BROKER_PORT     MQTT broker port (default: 1883)
  MQTT_CLIENT_ID       MQTT client ID
  MQTT_USERNAME        MQTT username
  MQTT_PASSWORD        MQTT password
  MQTT_USE_TLS         Enable TLS (true/false)
  MQTT_QOS             QoS level (0, 1, 2)
        """
    )
    
    # Transport options
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    
    # HTTP transport options
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP transport (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=3000,
        help="Port for HTTP transport (default: 3000)"
    )
    
    # MQTT configuration
    parser.add_argument(
        "--mqtt-host",
        help="MQTT broker hostname (overrides MQTT_BROKER_HOST)"
    )
    
    parser.add_argument(
        "--mqtt-port",
        type=int,
        default=1883,
        help="MQTT broker port (default: 1883)"
    )
    
    parser.add_argument(
        "--mqtt-client-id",
        help="MQTT client ID"
    )
    
    parser.add_argument(
        "--mqtt-username",
        help="MQTT username"
    )
    
    parser.add_argument(
        "--mqtt-password",
        help="MQTT password"
    )
    
    parser.add_argument(
        "--auto-connect",
        action="store_true",
        help="Automatically connect to MQTT broker on startup"
    )
    
    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="Log level (default: WARNING)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path (logs to stderr if not specified)"
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    
    return parser


def parse_arguments(args=None) -> Namespace:
    """Parse command-line arguments."""
    parser = create_argument_parser()
    return parser.parse_args(args)