"""Server runner implementations for STDIO and HTTP transports."""

import sys
from typing import Optional

import structlog

from ..mcp.server import MCMQTTServer


async def run_stdio_server(
    server: MCMQTTServer,
    auto_connect: bool = False,
    log_file: Optional[str] = None
):
    """Run FastMCP server with STDIO transport."""
    logger = structlog.get_logger()
    
    try:
        # Auto-connect to MQTT if configured and requested
        if auto_connect and server.mqtt_config:
            logger.info("Auto-connecting to MQTT broker", 
                       broker=f"{server.mqtt_config.broker_host}:{server.mqtt_config.broker_port}")
            success = await server.initialize_mqtt_client(server.mqtt_config)
            if success:
                await server.connect_mqtt()
                logger.info("Connected to MQTT broker")
            else:
                logger.warning("Failed to connect to MQTT broker", error=server._last_error)
        
        # Get FastMCP instance and run with STDIO transport
        mcp = server.get_mcp_server()
        
        # Run server with STDIO transport (default for MCP)
        await mcp.run_stdio_async()
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        await server.disconnect_mqtt()
    except Exception as e:
        logger.error("Server error", error=str(e))
        await server.disconnect_mqtt()
        sys.exit(1)


async def run_http_server(
    server: MCMQTTServer,
    host: str = "0.0.0.0",
    port: int = 3000,
    auto_connect: bool = False
):
    """Run FastMCP server with HTTP transport."""
    logger = structlog.get_logger()
    
    try:
        # Auto-connect to MQTT if configured and requested
        if auto_connect and server.mqtt_config:
            logger.info("Auto-connecting to MQTT broker",
                       broker=f"{server.mqtt_config.broker_host}:{server.mqtt_config.broker_port}")
            success = await server.initialize_mqtt_client(server.mqtt_config)
            if success:
                await server.connect_mqtt()
                logger.info("Connected to MQTT broker")
            else:
                logger.warning("Failed to connect to MQTT broker", error=server._last_error)
        
        # Get FastMCP instance and run with HTTP transport
        mcp = server.get_mcp_server()
        
        # Run server with HTTP transport
        await mcp.run_http_async(host=host, port=port)
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        await server.disconnect_mqtt()
    except Exception as e:
        logger.error("Server error", error=str(e))
        await server.disconnect_mqtt()
        sys.exit(1)