"""
MCP Minder FastAPI 应用

提供 RESTful API 接口用于远程管理 MCP 服务
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from minder.core.service_manager import ServiceManager
from minder.core.generator import MCPGenerator
from minder.core.mcp_proxy import MCPProxyManager
from minder.api.models import (
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceStartRequest,
    ServiceListResponse,
    ServiceResponse,
    ServiceActionResponse,
    LogsResponse,
    MCPGenerateRequest,
    MCPGenerateResponse,
    HealthResponse,
    ServiceInfo,
    # MCP 代理相关模型
    MCPProxyRequest,
    MCPProxyResponse,
    MCPAvailableServicesResponse,
    MCPHealthCheckRequest,
    MCPHealthCheckResponse
)

# 创建 FastAPI 应用
app = FastAPI(
    title="MCP Minder API",
    description="MCP服务器管理框架的RESTful API接口",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务管理器和生成器
service_manager = ServiceManager()
generator = MCPGenerator()
mcp_proxy_manager = MCPProxyManager(service_manager)


@app.get("/", response_model=HealthResponse)
async def root():
    """根路径健康检查"""
    services = service_manager.list_services()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0",
        services_count=len(services)
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    services = service_manager.list_services()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0",
        services_count=len(services)
    )


# ==================== 服务管理 API ====================

@app.post("/api/services", response_model=ServiceResponse)
async def create_service(request: ServiceCreateRequest):
    """创建新服务"""
    try:
        service_id = service_manager.register_service(
            name=request.name,
            file_path=request.file_path,
            host=request.host,
            description=request.description,
            author=request.author
        )
        
        service_info = service_manager.get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=f"服务 {request.name} 创建成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services", response_model=ServiceListResponse)
async def list_services(status: Optional[str] = Query(None, description="状态过滤器")):
    """获取服务列表"""
    try:
        services = service_manager.list_services(status_filter=status)
        service_infos = [ServiceInfo(**service.__dict__) for service in services]
        
        return ServiceListResponse(
            success=True,
            services=service_infos,
            total=len(service_infos)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str):
    """获取特定服务信息"""
    try:
        service_info = service_manager.get_service(service_id)
        if not service_info:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/by-name/{service_name}", response_model=ServiceResponse)
async def get_service_by_name(service_name: str):
    """根据服务名称获取服务信息"""
    try:
        service_info = service_manager.get_service_by_name(service_name)
        if not service_info:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
        
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/services/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, request: ServiceUpdateRequest):
    """更新服务信息"""
    try:
        result = service_manager.update_service(
            service_id=service_id,
            name=request.name,
            port=request.port,
            host=request.host,
            description=request.description
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        service_info = service_manager.get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/services/by-name/{service_name}", response_model=ServiceResponse)
async def update_service_by_name(service_name: str, request: ServiceUpdateRequest):
    """根据服务名称更新服务信息"""
    try:
        # 先获取服务ID
        service_id = service_manager.get_service_id_by_name(service_name)
        if not service_id:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
        
        result = service_manager.update_service(
            service_id=service_id,
            name=request.name,
            port=request.port,
            host=request.host,
            description=request.description
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        service_info = service_manager.get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/services/{service_id}", response_model=ServiceActionResponse)
async def delete_service(service_id: str):
    """删除服务"""
    try:
        result = service_manager.delete_service(service_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/services/by-name/{service_name}", response_model=ServiceActionResponse)
async def delete_service_by_name(service_name: str):
    """根据服务名称删除服务"""
    try:
        result = service_manager.delete_service_by_name(service_name)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/{service_id}/start", response_model=ServiceActionResponse)
async def start_service(service_id: str, request: ServiceStartRequest = ServiceStartRequest()):
    """启动服务"""
    try:
        result = service_manager.start_service(service_id, request.port)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message'],
            pid=result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/by-name/{service_name}/start", response_model=ServiceActionResponse)
async def start_service_by_name(service_name: str, request: ServiceStartRequest = ServiceStartRequest()):
    """根据服务名称启动服务"""
    try:
        result = service_manager.start_service_by_name(service_name, request.port)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message'],
            pid=result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/{service_id}/stop", response_model=ServiceActionResponse)
async def stop_service(service_id: str):
    """停止服务"""
    try:
        result = service_manager.stop_service(service_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/by-name/{service_name}/stop", response_model=ServiceActionResponse)
async def stop_service_by_name(service_name: str):
    """根据服务名称停止服务"""
    try:
        result = service_manager.stop_service_by_name(service_name)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/by-name/{service_name}/restart", response_model=ServiceActionResponse)
async def restart_service_by_name(service_name: str):
    """根据服务名称重启服务"""
    try:
        # 先停止服务
        stop_result = service_manager.stop_service_by_name(service_name)
        if not stop_result['success']:
            raise HTTPException(status_code=400, detail=f"停止服务失败: {stop_result['error']}")
        
        # 等待一秒
        import asyncio
        await asyncio.sleep(1)
        
        # 再启动服务
        start_result = service_manager.start_service_by_name(service_name)
        if not start_result['success']:
            raise HTTPException(status_code=400, detail=f"启动服务失败: {start_result['error']}")
        
        return ServiceActionResponse(
            success=True,
            service_id=start_result.get('service_id'),
            message=f"服务 {service_name} 重启成功",
            pid=start_result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/{service_id}/logs", response_model=LogsResponse)
async def get_service_logs(
    service_id: str,
    lines: int = Query(50, description="返回的日志行数")
):
    """获取服务日志"""
    try:
        result = service_manager.get_service_logs(service_id, lines)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return LogsResponse(
            success=True,
            logs=result['logs'],
            total_lines=result['total_lines'],
            returned_lines=result['returned_lines']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/by-name/{service_name}/logs", response_model=LogsResponse)
async def get_service_logs_by_name(
    service_name: str,
    lines: int = Query(50, description="返回的日志行数")
):
    """根据服务名称获取服务日志"""
    try:
        result = service_manager.get_service_logs_by_name(service_name, lines)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return LogsResponse(
            success=True,
            logs=result['logs'],
            total_lines=result['total_lines'],
            returned_lines=result['returned_lines']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/sync", response_model=ServiceActionResponse)
async def sync_service_status():
    """同步服务状态"""
    try:
        service_manager.sync_service_status()
        return ServiceActionResponse(
            success=True,
            message="服务状态同步完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/sync-services", response_model=ServiceActionResponse)
async def sync_services():
    """同步服务列表（重新扫描mcpserver目录）"""
    try:
        service_manager.sync_services()
        return ServiceActionResponse(
            success=True,
            message="服务列表同步完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MCP 生成器 API ====================

@app.post("/api/generate", response_model=MCPGenerateResponse)
async def generate_mcp_server(request: MCPGenerateRequest):
    """生成 MCP 服务器文件"""
    try:
        success = generator.generate(
            output_path=request.output_path,
            service_name=request.service_name,
            tool_name=request.tool_name,
            tool_param_name=request.tool_param_name,
            tool_param_type=request.tool_param_type,
            tool_return_type=request.tool_return_type,
            tool_description=request.tool_description,
            tool_code=request.tool_code,
            service_port=request.service_port,
            author=request.author
        )
        
        if success:
            return MCPGenerateResponse(
                success=True,
                output_path=request.output_path,
                message=f"MCP服务器文件生成成功: {request.output_path}"
            )
        else:
            raise HTTPException(status_code=500, detail="MCP服务器文件生成失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preview")
async def preview_mcp_server(request: MCPGenerateRequest):
    """预览MCP服务器代码（不生成文件）"""
    try:
        content = generator.generate_content(
            service_name=request.service_name,
            tool_name=request.tool_name,
            tool_param_name=request.tool_param_name,
            tool_param_type=request.tool_param_type,
            tool_return_type=request.tool_return_type,
            tool_description=request.tool_description,
            tool_code=request.tool_code,
            service_port=request.service_port,
            author=request.author
        )
        
        return {
            "success": True,
            "content": content,
            "message": "MCP服务器代码预览生成成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 批量操作 API ====================

@app.post("/api/services/start-all", response_model=ServiceActionResponse)
async def start_all_services():
    """启动所有停止的服务"""
    try:
        services = service_manager.list_services(status_filter="stopped")
        started_count = 0
        failed_count = 0
        
        for service in services:
            result = service_manager.start_service(service.id)
            if result['success']:
                started_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量启动完成: 成功 {started_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/stop-all", response_model=ServiceActionResponse)
async def stop_all_services():
    """停止所有运行中的服务"""
    try:
        services = service_manager.list_services(status_filter="running")
        stopped_count = 0
        failed_count = 0
        
        for service in services:
            result = service_manager.stop_service(service.id)
            if result['success']:
                stopped_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量停止完成: 成功 {stopped_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/restart-all", response_model=ServiceActionResponse)
async def restart_all_services():
    """重启所有运行中的服务"""
    try:
        services = service_manager.list_services(status_filter="running")
        restarted_count = 0
        failed_count = 0
        
        for service in services:
            # 先停止
            stop_result = service_manager.stop_service(service.id)
            if stop_result['success']:
                # 等待一秒
                import asyncio
                await asyncio.sleep(1)
                # 再启动
                start_result = service_manager.start_service(service.id)
                if start_result['success']:
                    restarted_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量重启完成: 成功 {restarted_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 错误处理 ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "资源不存在"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "内部服务器错误"}
    )


# ==================== MCP 代理 API 端点 ====================

@app.post("/api/mcp/proxy", response_model=MCPProxyResponse)
async def proxy_mcp_request(request: MCPProxyRequest):
    """
    代理 MCP 请求到指定服务
    
    AI 可以使用此端点将 MCP 请求代理到对应的 MCP 服务端口
    支持会话管理，自动处理MCP协议初始化
    """
    try:
        # 代理请求，返回响应和会话ID
        response_data, session_id = await mcp_proxy_manager.proxy_mcp_request(
            request.service_name, 
            request.mcp_request.model_dump(),
            request.session_id 
        )
        
        return MCPProxyResponse(
            success=True,
            service_name=request.service_name,
            session_id=session_id,
            response=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        return MCPProxyResponse(
            success=False,
            service_name=request.service_name,
            session_id=request.session_id,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )


@app.get("/api/mcp/services", response_model=MCPAvailableServicesResponse)
async def list_mcp_services():
    """
    获取可用的 MCP 服务列表
    
    返回所有正在运行且可用的 MCP 服务信息
    """
    try:
        services = await mcp_proxy_manager.get_available_services()
        
        return MCPAvailableServicesResponse(
            success=True,
            services=services,
            count=len(services),
            message=f"找到 {len(services)} 个可用的 MCP 服务"
        )
        
    except Exception as e:
        return MCPAvailableServicesResponse(
            success=False,
            services=[],
            count=0,
            message=f"获取服务列表失败: {str(e)}"
        )


@app.post("/api/mcp/health", response_model=MCPHealthCheckResponse)
async def check_mcp_service_health(request: MCPHealthCheckRequest):
    """
    检查 MCP 服务健康状态
    
    检查指定 MCP 服务的健康状态和连接性
    """
    try:
        health_info = await mcp_proxy_manager.health_check(request.service_name)
        
        return MCPHealthCheckResponse(
            success=health_info["status"] != "error",
            service_name=request.service_name,
            status=health_info["status"],
            port=health_info.get("port"),
            host=health_info.get("host"),
            message=health_info.get("message")
        )
        
    except Exception as e:
        return MCPHealthCheckResponse(
            success=False,
            service_name=request.service_name,
            status="error",
            message=f"健康检查失败: {str(e)}"
        )


@app.get("/api/mcp/services/{service_name}/health", response_model=MCPHealthCheckResponse)
async def check_mcp_service_health_by_name(service_name: str):
    """
    通过服务名检查 MCP 服务健康状态
    
    检查指定 MCP 服务的健康状态和连接性
    """
    try:
        health_info = await mcp_proxy_manager.health_check(service_name)
        
        return MCPHealthCheckResponse(
            success=health_info["status"] != "error",
            service_name=service_name,
            status=health_info["status"],
            port=health_info.get("port"),
            host=health_info.get("host"),
            message=health_info.get("message")
        )
        
    except Exception as e:
        return MCPHealthCheckResponse(
            success=False,
            service_name=service_name,
            status="error",
            message=f"健康检查失败: {str(e)}"
        )


# ==================== MCP 中间件代理端点 ====================

@app.post("/mcp/{service_name}")
async def mcp_middleware_proxy_by_name(service_name: str, request: Request):
    """
    MCP 中间件代理 - 通过 URL 路径指定服务名
    
    这个端点作为 MCP 中间件，可以：
    1. 接收标准的 MCP JSON-RPC 2.0 请求
    2. 根据 URL 路径中的服务名路由到对应的 MCP 服务
    3. 透明地转发请求并返回标准 MCP 响应
    
    用法: POST /mcp/{service_name}
    请求体: 标准的 MCP JSON-RPC 2.0 请求
    """
    try:
        # 读取原始请求体
        request_body = await request.body()
        
        # 解析MCP请求
        try:
            mcp_request = json.loads(request_body)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": f"Invalid JSON: {str(e)}"
                    }
                }
            )
        
        # 验证MCP请求格式
        if not isinstance(mcp_request, dict):
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id") if isinstance(mcp_request, dict) else None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Request must be a JSON object"
                    }
                }
            )
        
        if "method" not in mcp_request:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Missing 'method' field"
                    }
                }
            )
        
        # 代理请求到目标服务
        try:
            response_data, session_id = await mcp_proxy_manager.proxy_mcp_request(
                service_name,
                mcp_request,
                request.headers.get("X-Session-ID")  # 使用现有的会话ID
            )
            
            # 返回标准 MCP 响应格式
            headers = {}
            if session_id:
                headers["X-Session-ID"] = session_id
            headers["X-Target-Service"] = service_name
            
            return JSONResponse(
                content=response_data,
                headers=headers
            )
            
        except Exception as proxy_error:
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": f"Proxy error: {str(proxy_error)}"
                    }
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Unexpected error: {str(e)}"
                }
            }
        )


@app.post("/mcp")
async def mcp_middleware_proxy(request: Request):
    """
    MCP 中间件代理 - 自动服务发现模式
    
    这个端点作为 MCP 中间件，可以：
    1. 接收标准的 MCP JSON-RPC 2.0 请求
    2. 根据请求内容自动发现目标服务
    3. 透明地转发请求并返回标准 MCP 响应
    
    支持的请求格式：
    - 标准 MCP JSON-RPC 2.0 请求
    - 通过 X-Service-Name 头部指定目标服务
    - 通过请求参数中的 service_name 字段指定目标服务
    - 自动根据工具名推断服务
    """
    try:
        # 读取原始请求体
        request_body = await request.body()
        
        # 解析MCP请求
        try:
            mcp_request = json.loads(request_body)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": f"Invalid JSON: {str(e)}"
                    }
                }
            )
        
        # 验证MCP请求格式
        if not isinstance(mcp_request, dict):
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id") if isinstance(mcp_request, dict) else None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Request must be a JSON object"
                    }
                }
            )
        
        if "method" not in mcp_request:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Missing 'method' field"
                    }
                }
            )
        
        # 确定目标服务名称
        service_name = None
        
        # 方法1: 从请求头获取
        service_name = request.headers.get("X-Service-Name")
        
        # 方法2: 从请求参数获取
        if not service_name and "params" in mcp_request:
            params = mcp_request["params"]
            if isinstance(params, dict):
                service_name = params.get("service_name")
        
        # 方法3: 从方法名推断（如果是 tools/call 且有工具名）
        if not service_name and mcp_request.get("method") == "tools/call":
            params = mcp_request.get("params", {})
            if isinstance(params, dict) and "name" in params:
                tool_name = params["name"]
                # 尝试根据工具名找到对应的服务
                services = service_manager.list_services(status_filter="running")
                for service in services:
                    # 这里可以添加更复杂的匹配逻辑
                    # 暂时使用简单的名称匹配
                    if tool_name.lower() in service.name.lower():
                        service_name = service.name
                        break
        
        # 方法4: 如果只有一个运行中的服务，使用它
        if not service_name:
            services = service_manager.list_services(status_filter="running")
            if len(services) == 1:
                service_name = services[0].name
        
        if not service_name:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": "No target service specified. Please provide service name via X-Service-Name header or params.service_name"
                    }
                }
            )
        
        # 代理请求到目标服务
        try:
            response_data, session_id = await mcp_proxy_manager.proxy_mcp_request(
                service_name,
                mcp_request,
                request.headers.get("X-Session-ID")  # 使用现有的会话ID
            )
            
            # 返回标准 MCP 响应格式
            headers = {}
            if session_id:
                headers["X-Session-ID"] = session_id
            if service_name:
                headers["X-Target-Service"] = service_name
            
            return JSONResponse(
                content=response_data,
                headers=headers
            )
            
        except Exception as proxy_error:
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": f"Proxy error: {str(proxy_error)}"
                    }
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Unexpected error: {str(e)}"
                }
            }
        )


@app.post("/mcp/register")
async def register_mcp_service(request: Request):
    """
    MCP 服务注册端点
    
    允许其他 MCP 服务向代理注册自己，以便代理能够路由请求到它们。
    
    请求格式：
    {
        "service_name": "服务名称",
        "port": 端口号,
        "host": "主机地址",
        "description": "服务描述",
        "capabilities": {...}
    }
    """
    try:
        # 读取请求体
        request_body = await request.body()
        
        try:
            register_data = json.loads(request_body)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": f"Invalid JSON: {str(e)}"
                    }
                }
            )
        
        # 验证必需字段
        required_fields = ["service_name", "port"]
        for field in required_fields:
            if field not in register_data:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "id": register_data.get("id"),
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": f"Missing required field: {field}"
                        }
                    }
                )
        
        service_name = register_data["service_name"]
        port = register_data["port"]
        host = register_data.get("host", "127.0.0.1")
        description = register_data.get("description", f"Registered MCP service: {service_name}")
        
        # 检查服务是否已存在
        existing_service = service_manager.get_service_by_name(service_name)
        if existing_service:
            # 更新现有服务信息
            service_manager.update_service(
                service_id=existing_service.id,
                port=port,
                host=host,
                description=description
            )
            message = f"Service '{service_name}' updated successfully"
        else:
            # 注册新服务
            service_id = service_manager.register_service(
                name=service_name,
                file_path=f"registered/{service_name}",  # 虚拟路径
                host=host,
                description=description,
                author="MCP Proxy Registration"
            )
            message = f"Service '{service_name}' registered successfully"
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": register_data.get("id"),
                "result": {
                    "success": True,
                    "service_name": service_name,
                    "port": port,
                    "host": host,
                    "message": message
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Registration error: {str(e)}"
                }
            }
        )


@app.get("/mcp/services")
async def list_registered_mcp_services():
    """
    列出所有已注册的 MCP 服务
    
    返回所有可用的 MCP 服务列表，包括运行状态和基本信息。
    """
    try:
        services = service_manager.list_services()
        service_list = []
        
        for service in services:
            service_list.append({
                "name": service.name,
                "port": service.port,
                "host": service.host,
                "status": service.status,
                "description": service.description,
                "created_at": service.created_at
            })
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "services": service_list,
                    "count": len(service_list)
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Failed to list services: {str(e)}"
                }
            }
        )


@app.post("/api/mcp/{service_name}")
async def proxy_mcp_by_service_name(service_name: str, request: Request):
    """
    通过服务名直接代理MCP请求 - 类似nginx的location代理
    
    用法: POST /api/mcp/{service_name}
    请求体: 原始的MCP JSON请求
    
    这个端点提供了最接近nginx代理的体验：
    1. 根据URL路径中的服务名自动路由
    2. 直接转发原始请求体到目标MCP服务
    3. 自动处理会话管理和协议初始化
    """
    try:
        # 读取原始请求体
        request_body = await request.body()
        
        # 解析MCP请求
        try:
            mcp_request = json.loads(request_body)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": f"Invalid JSON: {str(e)}"
                    }
                }
            )
        
        # 验证MCP请求格式
        if not isinstance(mcp_request, dict) or "method" not in mcp_request:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id") if isinstance(mcp_request, dict) else None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Invalid MCP request format"
                    }
                }
            )
        
        # 代理请求
        response_data, session_id = await mcp_proxy_manager.proxy_mcp_request(
            service_name,
            mcp_request,
            request.headers.get("X-Session-ID")  # 使用现有的会话ID
        )
        
        # 返回原始MCP响应格式
        headers = {}
        if session_id:
            headers["X-Session-ID"] = session_id
        headers["X-Target-Service"] = service_name
        
        return JSONResponse(
            content=response_data,
            headers=headers
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": mcp_request.get("id") if 'mcp_request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
