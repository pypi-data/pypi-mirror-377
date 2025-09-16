"""
MCP Minder Client Library

A client library for interacting with MCP Minder API services.
"""

from .mcp_minder import McpMinder
from .exceptions import McpMinderError, McpMinderConnectionError, McpMinderAPIError

__version__ = "0.1.0"
__all__ = ["McpMinder", "McpMinderError", "McpMinderConnectionError", "McpMinderAPIError"]
