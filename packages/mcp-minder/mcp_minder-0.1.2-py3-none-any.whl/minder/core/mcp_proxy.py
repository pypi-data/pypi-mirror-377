"""
MCP 代理服务模块

提供 MCP 协议代理功能，允许 AI 根据服务名将 MCP 请求代理到对应的 MCP 端口。
"""

import asyncio
import json
import logging
import httpx
import uuid
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import subprocess
import socket
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@dataclass
class MCPProxyConfig:
    """MCP 代理配置"""
    service_name: str
    port: int
    host: str = "127.0.0.1"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    mcp_path: str = "/mcp"  # MCP服务的路径


@dataclass
class MCPSession:
    """MCP会话信息"""
    session_id: str
    service_name: str
    initialized: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class MCPProtocolError(Exception):
    """MCP 协议错误"""
    pass


class MCPConnectionError(Exception):
    """MCP 连接错误"""
    pass


class MCPProxy:
    """MCP 代理服务 - 类似nginx的透明代理"""
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.active_connections: Dict[str, MCPProxyConfig] = {}
        self.connection_pool: Dict[str, httpx.AsyncClient] = {}
        self.sessions: Dict[str, MCPSession] = {}  # 会话管理
        self.logger = logging.getLogger(__name__)
    
    async def get_service_config(self, service_name: str) -> Optional[MCPProxyConfig]:
        """获取服务的代理配置"""
        try:
            service_info = self.service_manager.get_service_by_name(service_name)
            if not service_info:
                return None
            
            # 检查服务是否正在运行
            if service_info.status != "running":
                raise MCPConnectionError(f"Service '{service_name}' is not running")
            
            # 检查端口是否可用
            if not service_info.port:
                raise MCPConnectionError(f"Service '{service_name}' has no port assigned")
            
            return MCPProxyConfig(
                service_name=service_name,
                port=service_info.port,
                host=service_info.host or "127.0.0.1",
                timeout=30,
                max_retries=3,
                retry_delay=1.0,
                mcp_path="/mcp"  # 标准的MCP端点路径
            )
        except Exception as e:
            self.logger.error(f"Failed to get service config for '{service_name}': {e}")
            return None
    
    async def _get_connection(self, config: MCPProxyConfig) -> httpx.AsyncClient:
        """获取或创建连接"""
        connection_key = f"{config.host}:{config.port}"
        
        if connection_key not in self.connection_pool:
            self.connection_pool[connection_key] = httpx.AsyncClient(
                base_url=f"http://{config.host}:{config.port}",
                timeout=config.timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
        
        return self.connection_pool[connection_key]
    
    def _create_session(self, service_name: str) -> MCPSession:
        """创建新的MCP会话"""
        session_id = str(uuid.uuid4())
        session = MCPSession(
            session_id=session_id,
            service_name=service_name,
            initialized=False
        )
        self.sessions[session_id] = session
        self.logger.info(f"Created new MCP session {session_id} for service '{service_name}'")
        return session
    
    def _get_or_create_session(self, service_name: str, session_id: Optional[str] = None) -> MCPSession:
        """获取或创建MCP会话"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        return self._create_session(service_name)
    
    async def _ensure_session_initialized(self, session: MCPSession, config: MCPProxyConfig) -> bool:
        """确保会话已初始化"""
        if session.initialized:
            return True
        
        try:
            connection = await self._get_connection(config)
            
            # 发送初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "mcp-proxy",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await connection.post(config.mcp_path, json=init_request)
            if response.status_code != 200:
                return False
            
            # 解析响应
            response_text = response.text.strip()
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    json_data = line[6:]
                    try:
                        mcp_response = json.loads(json_data)
                        if mcp_response.get("result"):
                            # 发送initialized通知
                            initialized_notification = {
                                "jsonrpc": "2.0",
                                "method": "notifications/initialized",
                                "params": {}
                            }
                            
                            # 发送通知（不需要等待响应）
                            await connection.post(config.mcp_path, json=initialized_notification)
                            
                            session.initialized = True
                            self.logger.info(f"Session {session.session_id} initialized successfully")
                            return True
                    except json.JSONDecodeError:
                        continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session {session.session_id}: {e}")
            return False
    
    async def _check_service_health(self, config: MCPProxyConfig) -> bool:
        """检查服务健康状态"""
        try:
            connection = await self._get_connection(config)
            # 尝试连接到 MCP 服务的 /health 端点
            try:
                response = await connection.get("/health", timeout=5)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            
            # 如果 /health 端点不可用，尝试根路径
            try:
                response = await connection.get("/", timeout=5)
                return response.status_code in [200, 404]  # 404 也是正常的，说明服务在运行
            except Exception:
                pass
            
            # 如果都不可用，尝试 /mcp 端点的 OPTIONS 请求
            try:
                response = await connection.request("OPTIONS", "/mcp", timeout=5)
                return response.status_code in [200, 404, 405]  # 405 Method Not Allowed 也是正常的
            except Exception:
                pass
            
            return False
        except Exception as e:
            self.logger.warning(f"Health check failed for {config.service_name}: {e}")
            return False
    
    async def proxy_request(self, service_name: str, mcp_request: Dict[str, Any], session_id: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
        """
        透明代理 MCP 请求到指定服务 - 类似nginx的代理功能
        
        Args:
            service_name: MCP 服务名称
            mcp_request: MCP 请求数据
            session_id: 可选的会话ID，如果不提供则创建新会话
            
        Returns:
            Tuple[MCP响应数据, 会话ID]
            
        Raises:
            MCPConnectionError: 连接错误
            MCPProtocolError: 协议错误
        """
        try:
            # 获取服务配置
            config = await self.get_service_config(service_name)
            if not config:
                raise MCPConnectionError(f"Service '{service_name}' not found or not running")
            
            # 检查服务健康状态
            if not await self._check_service_health(config):
                raise MCPConnectionError(f"Service '{service_name}' is not healthy")
            
            # 获取或创建会话
            session = self._get_or_create_session(service_name, session_id)
            
            # 确保会话已初始化
            if not await self._ensure_session_initialized(session, config):
                raise MCPConnectionError(f"Failed to initialize session for service '{service_name}'")
            
            # 获取连接
            connection = await self._get_connection(config)
            
            # 构建 MCP 请求（保持原始请求格式）
            mcp_request_data = {
                "jsonrpc": "2.0",
                "id": mcp_request.get("id", 1),
                "method": mcp_request.get("method"),
                "params": mcp_request.get("params", {})
            }
            
            # 添加session ID到请求参数中（FastMCP可能期望这种方式）
            if session.session_id:
                mcp_request_data["session_id"] = session.session_id
            
            # 发送请求到MCP服务的标准路径
            # 同时尝试在请求头中添加session ID
            headers = {"X-Session-ID": session.session_id} if session.session_id else {}
            response = await connection.post(config.mcp_path, json=mcp_request_data, headers=headers)
            
            if response.status_code != 200:
                raise MCPProtocolError(f"HTTP {response.status_code}: {response.text}")
            
            # 处理Server-Sent Events响应格式
            response_text = response.text.strip()
            mcp_response = None
            
            # 查找JSON数据行（以 "data: " 开头）
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    json_data = line[6:]  # 移除 "data: " 前缀
                    try:
                        mcp_response = json.loads(json_data)
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not mcp_response:
                raise MCPProtocolError("No valid JSON data found in SSE response")
            
            # 验证 MCP 协议格式
            if "jsonrpc" not in mcp_response:
                raise MCPProtocolError("Invalid MCP response: missing jsonrpc field")
            
            if mcp_response.get("jsonrpc") != "2.0":
                raise MCPProtocolError("Invalid MCP response: unsupported jsonrpc version")
            
            # 记录代理日志
            self.logger.info(f"Proxied MCP request to '{service_name}' (session: {session.session_id}): {mcp_request.get('method', 'unknown')}")
            
            return mcp_response, session.session_id
            
        except httpx.TimeoutException:
            raise MCPConnectionError(f"Timeout connecting to service '{service_name}'")
        except httpx.ConnectError:
            raise MCPConnectionError(f"Failed to connect to service '{service_name}'")
        except json.JSONDecodeError as e:
            raise MCPProtocolError(f"Invalid JSON response from service '{service_name}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error proxying request to '{service_name}': {e}")
            raise MCPConnectionError(f"Unexpected error: {e}")
    
    async def list_available_services(self) -> List[Dict[str, Any]]:
        """列出可用的 MCP 服务"""
        try:
            services = self.service_manager.list_services()
            available_services = []
            
            for service in services:
                if service.status == "running" and service.port:
                    config = await self.get_service_config(service.name)
                    if config and await self._check_service_health(config):
                        available_services.append({
                            "name": service.name,
                            "port": service.port,
                            "host": service.host,
                            "status": service.status,
                            "description": service.description,
                            "capabilities": await self._get_service_capabilities(config)
                        })
            
            return available_services
            
        except Exception as e:
            self.logger.error(f"Failed to list available services: {e}")
            return []
    
    async def _get_service_capabilities(self, config: MCPProxyConfig) -> Dict[str, Any]:
        """获取服务能力信息"""
        try:
            connection = await self._get_connection(config)
            response = await connection.get("/capabilities", timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception:
            return {}
    
    async def close_connections(self):
        """关闭所有连接"""
        for connection in self.connection_pool.values():
            await connection.aclose()
        self.connection_pool.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connections()


class MCPProxyManager:
    """MCP 代理管理器"""
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.proxy = MCPProxy(service_manager)
        self.logger = logging.getLogger(__name__)
    
    async def proxy_mcp_request(self, service_name: str, request_data: Dict[str, Any], session_id: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
        """代理 MCP 请求 - 返回响应和会话ID"""
        return await self.proxy.proxy_request(service_name, request_data, session_id)
    
    async def get_available_services(self) -> List[Dict[str, Any]]:
        """获取可用的 MCP 服务列表"""
        return await self.proxy.list_available_services()
    
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """健康检查"""
        try:
            config = await self.proxy.get_service_config(service_name)
            if not config:
                return {"status": "error", "message": f"Service '{service_name}' not found"}
            
            is_healthy = await self.proxy._check_service_health(config)
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "service": service_name,
                "port": config.port,
                "host": config.host
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def close(self):
        """关闭代理管理器"""
        await self.proxy.close_connections()
