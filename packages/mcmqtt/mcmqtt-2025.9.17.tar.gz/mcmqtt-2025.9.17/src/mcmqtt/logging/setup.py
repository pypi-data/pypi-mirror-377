"""Logging setup and configuration for mcmqtt."""

import logging
import sys
from typing import Optional

import structlog


def setup_logging(log_level: str = "WARNING", log_file: Optional[str] = None):
    """Set up logging for MCP server."""
    # For STDIO transport, we need to be careful about logging to avoid interfering
    # with MCP protocol communication over stdout/stdin
    
    handlers = []
    
    if log_file:
        # Log to file when specified
        handlers.append(logging.FileHandler(log_file))
    else:
        # For STDIO mode, log to stderr to avoid protocol interference
        handlers.append(logging.StreamHandler(sys.stderr))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    
    # Configure structlog for clean logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )