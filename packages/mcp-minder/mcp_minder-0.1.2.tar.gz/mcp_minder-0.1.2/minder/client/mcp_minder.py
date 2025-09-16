"""
MCP Minder Client

A client library for interacting with MCP Minder API services.
"""

import httpx
import asyncio
from typing import Optional, Dict, List, Any, Union
from urllib.parse import urljoin
import json

from .exceptions import (
    McpMinderError, 
    McpMinderConnectionError, 
    McpMinderAPIError,
    McpMinderServiceError
)


class ServiceInfo:
    """Represents information about an MCP service."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.name = data.get("name")
        self.file_path = data.get("file_path")
        self.host = data.get("host")
        self.port = data.get("port")
        self.status = data.get("status")
        self.pid = data.get("pid")
        self.description = data.get("description")
        self.author = data.get("author")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
    
    def __repr__(self):
        return f"ServiceInfo(name='{self.name}', status='{self.status}', port={self.port})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "pid": self.pid,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class McpMinder:
    """
    MCP Minder Client
    
    A client for interacting with MCP Minder API services.
    
    Example:
        >>> minder = McpMinder.get_service(url="http://localhost:8000", servername="my_server")
        >>> minder.start(port=8080)
        >>> minder.stop()
    """
    
    def __init__(self, base_url: str, service_name: str, timeout: int = 30):
        """
        Initialize MCP Minder client.
        
        Args:
            base_url: Base URL of the MCP Minder API server
            service_name: Name of the MCP service to manage
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.timeout = timeout
        self._client = None
    
    @classmethod
    def get_service(cls, url: str, servername: str, timeout: int = 30) -> 'McpMinder':
        """
        Create a new MCP Minder client instance.
        
        Args:
            url: Base URL of the MCP Minder API server
            servername: Name of the MCP service to manage
            timeout: Request timeout in seconds
            
        Returns:
            McpMinder client instance
            
        Example:
            >>> minder = McpMinder.get_service(url="http://localhost:8000", servername="my_server")
        """
        return cls(url, servername, timeout)
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
        return self._client
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API."""
        client = self._get_client()
        # 确保 URL 正确编码
        from urllib.parse import quote
        # 对路径中的中文字符进行编码
        encoded_endpoint = '/'.join(quote(part, safe='') for part in endpoint.lstrip('/').split('/'))
        url = urljoin(self.base_url + "/", encoded_endpoint)
        
        try:
            response = await client.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                
                raise McpMinderAPIError(
                    error_msg, 
                    status_code=response.status_code,
                    response_data=error_data if 'error_data' in locals() else None
                )
            
            if response.content:
                return response.json()
            return {}
            
        except httpx.RequestError as e:
            raise McpMinderConnectionError(f"Connection error: {e}")
        except json.JSONDecodeError as e:
            raise McpMinderAPIError(f"Invalid JSON response: {e}")
    
    async def _close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.create_task(self._close())
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close()
    
    # Service Management Methods
    
    async def get_info(self) -> ServiceInfo:
        """
        Get service information.
        
        Returns:
            ServiceInfo object containing service details
            
        Raises:
            McpMinderAPIError: If service not found or API error
        """
        try:
            response = await self._request("GET", f"/api/services/by-name/{self.service_name}")
            # API 返回格式: {"success": true, "service": {...}}
            if response.get("success") and "service" in response:
                return ServiceInfo(response["service"])
            else:
                raise McpMinderAPIError("Invalid API response format")
        except McpMinderAPIError as e:
            if e.status_code == 404:
                raise McpMinderServiceError(f"Service '{self.service_name}' not found")
            raise
    
    async def start(self, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Start the service.
        
        Args:
            port: Optional port number to start the service on
            
        Returns:
            Dictionary containing start result
            
        Raises:
            McpMinderServiceError: If service start fails
        """
        payload = {}
        if port is not None:
            payload["port"] = port
        
        try:
            return await self._request(
                "POST", 
                f"/api/services/by-name/{self.service_name}/start",
                json=payload
            )
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to start service: {e}")
    
    async def stop(self) -> Dict[str, Any]:
        """
        Stop the service.
        
        Returns:
            Dictionary containing stop result
            
        Raises:
            McpMinderServiceError: If service stop fails
        """
        try:
            return await self._request(
                "POST", 
                f"/api/services/by-name/{self.service_name}/stop"
            )
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to stop service: {e}")
    
    async def restart(self, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Restart the service.
        
        Args:
            port: Optional port number to restart the service on
            
        Returns:
            Dictionary containing restart result
            
        Raises:
            McpMinderServiceError: If service restart fails
        """
        payload = {}
        if port is not None:
            payload["port"] = port
        
        try:
            return await self._request(
                "POST", 
                f"/api/services/by-name/{self.service_name}/restart",
                json=payload
            )
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to restart service: {e}")
    
    async def delete(self) -> Dict[str, Any]:
        """
        Delete the service.
        
        Returns:
            Dictionary containing delete result
            
        Raises:
            McpMinderServiceError: If service deletion fails
        """
        try:
            return await self._request(
                "DELETE", 
                f"/api/services/by-name/{self.service_name}"
            )
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to delete service: {e}")
    
    async def get_logs(self, lines: int = 50) -> str:
        """
        Get service logs.
        
        Args:
            lines: Number of log lines to retrieve
            
        Returns:
            Service logs as string
            
        Raises:
            McpMinderServiceError: If log retrieval fails
        """
        try:
            response = await self._request(
                "GET", 
                f"/api/services/by-name/{self.service_name}/logs",
                params={"lines": lines}
            )
            return response.get("logs", "")
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to get logs: {e}")
    
    async def get_status(self) -> str:
        """
        Get service status.
        
        Returns:
            Service status string
            
        Raises:
            McpMinderServiceError: If status retrieval fails
        """
        try:
            info = await self.get_info()
            return info.status
        except McpMinderServiceError:
            return "unknown"
    
    # Synchronous wrapper methods
    
    def start_sync(self, port: Optional[int] = None) -> Dict[str, Any]:
        """Synchronous version of start()."""
        return asyncio.run(self.start(port))
    
    def stop_sync(self) -> Dict[str, Any]:
        """Synchronous version of stop()."""
        return asyncio.run(self.stop())
    
    def restart_sync(self, port: Optional[int] = None) -> Dict[str, Any]:
        """Synchronous version of restart()."""
        return asyncio.run(self.restart(port))
    
    def delete_sync(self) -> Dict[str, Any]:
        """Synchronous version of delete()."""
        return asyncio.run(self.delete())
    
    def get_info_sync(self) -> ServiceInfo:
        """Synchronous version of get_info()."""
        return asyncio.run(self.get_info())
    
    def get_logs_sync(self, lines: int = 50) -> str:
        """Synchronous version of get_logs()."""
        return asyncio.run(self.get_logs(lines))
    
    def get_status_sync(self) -> str:
        """Synchronous version of get_status()."""
        return asyncio.run(self.get_status())
    
    # Utility methods
    
    async def health_check(self) -> bool:
        """
        Check if the MCP Minder API server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            await self._request("GET", "/health")
            return True
        except:
            return False
    
    def health_check_sync(self) -> bool:
        """Synchronous version of health_check()."""
        return asyncio.run(self.health_check())
    
    async def list_all_services(self) -> List[ServiceInfo]:
        """
        List all services on the MCP Minder server.
        
        Returns:
            List of ServiceInfo objects
        """
        try:
            data = await self._request("GET", "/api/services")
            return [ServiceInfo(service) for service in data.get("services", [])]
        except McpMinderAPIError as e:
            raise McpMinderServiceError(f"Failed to list services: {e}")
    
    def list_all_services_sync(self) -> List[ServiceInfo]:
        """Synchronous version of list_all_services()."""
        return asyncio.run(self.list_all_services())
    
    # ==================== MCP 代理功能 ====================
    
    async def proxy_mcp_request(self, service_name: str, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proxy MCP request to specified service.
        
        Args:
            service_name: Target MCP service name
            mcp_request: MCP request data
            
        Returns:
            MCP response data
            
        Raises:
            McpMinderAPIError: If proxy request fails
        """
        try:
            request_data = {
                "service_name": service_name,
                "mcp_request": mcp_request
            }
            response = await self._request("POST", "/api/mcp/proxy", json=request_data)
            
            if not response.get("success"):
                raise McpMinderAPIError(f"Proxy request failed: {response.get('error', 'Unknown error')}")
            
            return response.get("response", {})
            
        except McpMinderAPIError as e:
            raise
        except Exception as e:
            raise McpMinderAPIError(f"Failed to proxy MCP request: {e}")
    
    async def list_mcp_services(self) -> List[Dict[str, Any]]:
        """
        List available MCP services.
        
        Returns:
            List of available MCP services
        """
        try:
            response = await self._request("GET", "/api/mcp/services")
            
            if not response.get("success"):
                raise McpMinderAPIError(f"Failed to list MCP services: {response.get('message', 'Unknown error')}")
            
            return response.get("services", [])
            
        except McpMinderAPIError as e:
            raise
        except Exception as e:
            raise McpMinderAPIError(f"Failed to list MCP services: {e}")
    
    async def check_mcp_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Check MCP service health.
        
        Args:
            service_name: Service name to check
            
        Returns:
            Health check result
        """
        try:
            response = await self._request("GET", f"/api/mcp/services/{service_name}/health")
            
            return {
                "success": response.get("success", False),
                "service_name": response.get("service_name"),
                "status": response.get("status"),
                "port": response.get("port"),
                "host": response.get("host"),
                "message": response.get("message")
            }
            
        except McpMinderAPIError as e:
            raise
        except Exception as e:
            raise McpMinderAPIError(f"Failed to check MCP service health: {e}")
    
    # 同步版本的 MCP 代理方法
    def proxy_mcp_request_sync(self, service_name: str, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """同步版本的 MCP 请求代理"""
        return asyncio.run(self.proxy_mcp_request(service_name, mcp_request))
    
    def list_mcp_services_sync(self) -> List[Dict[str, Any]]:
        """同步版本的 MCP 服务列表"""
        return asyncio.run(self.list_mcp_services())
    
    def check_mcp_service_health_sync(self, service_name: str) -> Dict[str, Any]:
        """同步版本的 MCP 服务健康检查"""
        return asyncio.run(self.check_mcp_service_health(service_name))
