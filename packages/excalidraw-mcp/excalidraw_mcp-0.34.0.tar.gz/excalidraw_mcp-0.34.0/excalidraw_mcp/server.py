#!/usr/bin/env python3
"""Excalidraw MCP Server - Python FastMCP Implementation
Provides MCP tools for creating and managing Excalidraw diagrams with canvas sync.
"""

import asyncio
import atexit
import logging
from typing import Any

from fastmcp import FastMCP

from .monitoring.supervisor import MonitoringSupervisor

# Initialize FastMCP server
mcp = FastMCP("Excalidraw MCP Server")

# Register MCP tools
from .mcp_tools import MCPToolsManager

tools_manager = MCPToolsManager(mcp)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
process_manager: Any = None
monitoring_supervisor: Any = None


def get_process_manager() -> Any:
    """Get or create the global process manager instance."""
    global process_manager
    if process_manager is None:
        from .process_manager import CanvasProcessManager

        process_manager = CanvasProcessManager()
        # Register cleanup function
        atexit.register(process_manager.cleanup)
    return process_manager


def get_monitoring_supervisor() -> Any:
    """Get or create the global monitoring supervisor instance."""
    global monitoring_supervisor
    if monitoring_supervisor is None:
        from .monitoring.supervisor import MonitoringSupervisor

        monitoring_supervisor = MonitoringSupervisor()
    return monitoring_supervisor


# Initialize monitoring supervisor
monitoring_supervisor = MonitoringSupervisor()


def cleanup_monitoring() -> None:
    if monitoring_supervisor.is_running:
        from contextlib import suppress

        with suppress(RuntimeError):
            asyncio.create_task(monitoring_supervisor.stop())


def main() -> None:
    """Main entry point for the CLI"""
    try:
        logger.info("Starting Excalidraw MCP Server...")

        # Initialize services first using a simple approach
        init_background_services()

        # Run the FastMCP server in HTTP mode
        mcp.run(transport="http", host="localhost", port=3032)

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def init_background_services() -> None:
    """Initialize background services without asyncio conflicts."""
    import subprocess
    import time

    # Start canvas server directly via subprocess if not running
    try:
        import requests

        # Check if canvas server is already running
        requests.get("http://localhost:3031/health", timeout=1)
        logger.info("Canvas server already running")
    except (requests.RequestException, ConnectionError, OSError):
        logger.info("Starting canvas server...")
        # Start canvas server in background
        subprocess.Popen(
            ["npm", "run", "canvas"],
            cwd="/Users/les/Projects/excalidraw-mcp",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for it to be ready
        for i in range(30):
            try:
                requests.get("http://localhost:3031/health", timeout=1)
                logger.info("Canvas server is ready")
                break
            except (requests.RequestException, ConnectionError, OSError):
                time.sleep(1)
        else:
            logger.warning("Canvas server may not be ready")

    logger.info("Background services initialized")


if __name__ == "__main__":
    main()
