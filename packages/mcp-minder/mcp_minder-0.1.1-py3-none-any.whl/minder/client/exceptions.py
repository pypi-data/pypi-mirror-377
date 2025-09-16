"""
MCP Minder Client Exceptions
"""


class McpMinderError(Exception):
    """Base exception for MCP Minder client errors."""
    pass


class McpMinderConnectionError(McpMinderError):
    """Raised when connection to MCP Minder API fails."""
    pass


class McpMinderAPIError(McpMinderError):
    """Raised when API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class McpMinderServiceError(McpMinderError):
    """Raised when service operation fails."""
    pass
