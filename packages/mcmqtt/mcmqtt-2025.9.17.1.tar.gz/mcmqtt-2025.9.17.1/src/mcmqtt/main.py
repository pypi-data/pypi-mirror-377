"""FastMCP MQTT Server - Main entry point following FastMCP conventions."""

import asyncio
import os
import sys
from typing import Optional

import typer
from rich.console import Console

from .mqtt.types import MQTTConfig
from .mcp.server import MCMQTTServer


# Setup rich console
console = Console()


def get_version() -> str:
    """Get package version."""
    try:
        from importlib.metadata import version
        return version("mcmqtt")
    except Exception:
        return "0.1.0"


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
            use_tls=os.getenv("MQTT_USE_TLS", "false").lower() == "true",
            clean_session=os.getenv("MQTT_CLEAN_SESSION", "true").lower() == "true",
            reconnect_interval=int(os.getenv("MQTT_RECONNECT_INTERVAL", "5")),
            max_reconnect_attempts=int(os.getenv("MQTT_MAX_RECONNECT_ATTEMPTS", "10"))
        )
    except Exception as e:
        console.print(f"[red]Error creating MQTT config from environment: {e}[/red]")
        return None


def show_startup_banner():
    """Display the mcmqtt startup banner with version and contributor info."""
    version = get_version()
    
    banner = f"""
╭─────────────────────────────────────────────────────────────────╮
│                    🚀 mcmqtt FastMCP MQTT Server                │
│                                                                 │
│  Version: {version:<20} Transport: FastMCP Protocol     │
│                                                                 │
│  📡 Features:                                                   │
│    • Instant MQTT broker spawning                              │
│    • Real-time agent coordination                              │  
│    • Production-ready infrastructure                           │
│    • Global ecosystem connectivity                             │
│                                                                 │
│  👥 Created by:                                                 │
│    • Ryan Malloy <ryan@malloys.us>                             │
│    • Claude (Anthropic)                                        │
│                                                                 │
│  🌍 Repository: https://git.supported.systems/MCP/mcmqtt       │
│  📦 PyPI: https://pypi.org/project/mcmqtt/                     │
│                                                                 │
│  Built with ❤️ for the AI developer community                  │
╰─────────────────────────────────────────────────────────────────╯
"""
    console.print(banner, style="cyan")


def main_server(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport mode: stdio (default) or http"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind the server to (HTTP mode only)"),
    port: int = typer.Option(3000, "--port", "-p", help="Port to bind the server to (HTTP mode only)"),
    mqtt_broker_host: Optional[str] = typer.Option(None, "--mqtt-host", help="MQTT broker hostname"),
    mqtt_broker_port: int = typer.Option(1883, "--mqtt-port", help="MQTT broker port"),
    mqtt_client_id: Optional[str] = typer.Option(None, "--mqtt-client-id", help="MQTT client ID"),
    mqtt_username: Optional[str] = typer.Option(None, "--mqtt-username", help="MQTT username"),
    mqtt_password: Optional[str] = typer.Option(None, "--mqtt-password", help="MQTT password"),
    auto_connect: bool = typer.Option(False, "--auto-connect", help="Automatically connect to MQTT broker on startup")
):
    """mcmqtt FastMCP MQTT Server - Enabling MQTT integration for MCP clients."""
    
    # Show startup banner
    show_startup_banner()
    
    # Create MQTT configuration
    mqtt_config = None
    
    if mqtt_broker_host:
        # Use CLI arguments
        mqtt_config = MQTTConfig(
            broker_host=mqtt_broker_host,
            broker_port=mqtt_broker_port,
            client_id=mqtt_client_id or f"mcmqtt-{os.getpid()}",
            username=mqtt_username,
            password=mqtt_password
        )
    else:
        # Try environment variables
        mqtt_config = create_mqtt_config_from_env()
    
    # Create and configure server
    server = MCMQTTServer(mqtt_config)
    
    # Handle MQTT auto-connect if needed
    if auto_connect and mqtt_config:
        async def connect_mqtt():
            success = await server.initialize_mqtt_client(mqtt_config)
            if success:
                await server.connect_mqtt()
        
        try:
            asyncio.run(connect_mqtt())
        except Exception as e:
            console.print(f"[red]MQTT connection failed: {e}[/red]")
    
    # Start FastMCP server based on transport
    try:
        if transport.lower() == "http":
            # HTTP mode uses async
            async def run_http():
                await server.run_server(host, port)
            asyncio.run(run_http())
        else:
            # STDIO mode is synchronous and handles its own event loop
            server.run_stdio()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point following FastMCP conventions."""
    typer.run(main_server)


if __name__ == "__main__":
    main()