"""
API 数据模型

定义 FastAPI 请求和响应的数据模型
"""

from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceCreateRequest(BaseModel):
    """创建服务请求模型"""
    name: str = Field(..., description="服务名称")
    file_path: str = Field(..., description="服务文件路径")
    port: Optional[int] = Field(None, description="服务端口")
    host: str = Field("0.0.0.0", description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")
    author: Optional[str] = Field(None, description="作者")


class ServiceUpdateRequest(BaseModel):
    """更新服务请求模型"""
    name: Optional[str] = Field(None, description="服务名称")
    port: Optional[int] = Field(None, description="服务端口")
    host: Optional[str] = Field(None, description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")


class ServiceInfo(BaseModel):
    """服务信息响应模型"""
    id: str
    name: str
    file_path: str
    port: Optional[int]
    host: str
    status: str
    created_at: str
    updated_at: str
    pid: Optional[int] = None
    log_file: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class ServiceListResponse(BaseModel):
    """服务列表响应模型"""
    success: bool
    services: List[ServiceInfo]
    total: int


class ServiceResponse(BaseModel):
    """单个服务响应模型"""
    success: bool
    service: Optional[ServiceInfo] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ServiceStartRequest(BaseModel):
    """启动服务请求模型"""
    port: Optional[int] = Field(None, description="服务端口（可选，如果不指定则使用随机端口）")


class ServiceActionResponse(BaseModel):
    """服务操作响应模型"""
    success: bool
    service_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    pid: Optional[int] = None


class LogsResponse(BaseModel):
    """日志响应模型"""
    success: bool
    logs: Optional[str] = None
    total_lines: Optional[int] = None
    returned_lines: Optional[int] = None
    error: Optional[str] = None


class MCPGenerateRequest(BaseModel):
    """MCP服务器生成请求模型"""
    output_path: str = Field(..., description="输出文件路径")
    service_name: Optional[str] = Field(None, description="服务名称")
    tool_name: Optional[str] = Field(None, description="工具函数名称")
    tool_param_name: str = Field("path", description="工具参数名称")
    tool_param_type: str = Field("str", description="工具参数类型")
    tool_return_type: str = Field("str", description="工具返回类型")
    tool_description: str = Field("MCP工具", description="工具描述")
    tool_code: str = Field("# 实现您的业务逻辑\n    output = \"处理完成\"", description="工具函数代码块")
    service_port: Optional[int] = Field(None, description="服务端口")
    author: str = Field("开发者", description="作者")


class MCPGenerateResponse(BaseModel):
    """MCP服务器生成响应模型"""
    success: bool
    output_path: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: str
    version: str
    services_count: int


# MCP 代理相关模型

class MCPRequest(BaseModel):
    """MCP 请求模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Union[str, int] = Field(..., description="请求ID")
    method: str = Field(..., description="MCP 方法名")
    params: Optional[Dict[str, Any]] = Field(None, description="方法参数")


class MCPResponse(BaseModel):
    """MCP 响应模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Union[str, int] = Field(..., description="请求ID")
    result: Optional[Any] = Field(None, description="方法结果")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")


class MCPProxyRequest(BaseModel):
    """MCP 代理请求模型"""
    service_name: str = Field(..., description="目标服务名称")
    mcp_request: MCPRequest = Field(..., description="MCP 请求数据")
    session_id: Optional[str] = Field(None, description="会话ID，如果不提供则创建新会话")


class MCPProxyResponse(BaseModel):
    """MCP 代理响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_name: str = Field(..., description="目标服务名称")
    session_id: Optional[str] = Field(None, description="会话ID")
    response: Optional[MCPResponse] = Field(None, description="MCP 响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: str = Field(..., description="响应时间戳")


class MCPServiceInfo(BaseModel):
    """MCP 服务信息模型"""
    name: str = Field(..., description="服务名称")
    port: int = Field(..., description="服务端口")
    host: str = Field(..., description="服务主机")
    status: str = Field(..., description="服务状态")
    description: Optional[str] = Field(None, description="服务描述")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="服务能力")


class MCPAvailableServicesResponse(BaseModel):
    """可用 MCP 服务列表响应模型"""
    success: bool = Field(..., description="请求是否成功")
    services: List[MCPServiceInfo] = Field(..., description="可用服务列表")
    count: int = Field(..., description="服务数量")
    message: Optional[str] = Field(None, description="响应消息")


class MCPHealthCheckRequest(BaseModel):
    """MCP 健康检查请求模型"""
    service_name: str = Field(..., description="服务名称")


class MCPHealthCheckResponse(BaseModel):
    """MCP 健康检查响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="健康状态")
    port: Optional[int] = Field(None, description="服务端口")
    host: Optional[str] = Field(None, description="服务主机")
    message: Optional[str] = Field(None, description="状态消息")
