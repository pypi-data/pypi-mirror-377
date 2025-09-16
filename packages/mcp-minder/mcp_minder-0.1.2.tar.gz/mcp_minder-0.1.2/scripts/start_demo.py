#!/usr/bin/env python3
"""
MCP Minder 演示启动脚本

展示如何使用新的服务管理和API功能
"""

import asyncio
import tempfile
import time
from pathlib import Path
from minder.core.generator import MCPGenerator
from minder.core.service_manager import ServiceManager


async def demo_service_management():
    """演示服务管理功能"""
    print("🚀 MCP Minder 服务管理演示")
    print("=" * 50)
    
    # 1. 生成MCP服务器
    print("\n📝 步骤1: 生成MCP服务器")
    generator = MCPGenerator()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        output_path = f.name
    
    success = generator.generate(
        output_path=output_path,
        service_name="demo_service",
        tool_name="demo_tool",
        tool_description="演示MCP工具",
        author="演示脚本"
    )
    
    if success:
        print(f"✅ MCP服务器生成成功: {output_path}")
    else:
        print("❌ MCP服务器生成失败")
        return
    
    # 2. 创建服务管理器
    print("\n🔧 步骤2: 创建服务管理器")
    service_manager = ServiceManager()
    
    # 3. 注册服务
    print("\n📦 步骤3: 注册服务")
    service_id = service_manager.register_service(
        name="demo_service",
        file_path=output_path,
        port=8080,
        host="127.0.0.1",
        description="演示服务",
        author="演示脚本"
    )
    print(f"✅ 服务注册成功，ID: {service_id}")
    
    # 4. 获取服务信息
    print("\n🔍 步骤4: 获取服务信息")
    service_info = service_manager.get_service(service_id)
    if service_info:
        print(f"✅ 服务名称: {service_info.name}")
        print(f"📁 文件路径: {service_info.file_path}")
        print(f"🌐 端口: {service_info.port}")
        print(f"📊 状态: {service_info.status}")
    
    # 5. 列出所有服务
    print("\n📋 步骤5: 列出所有服务")
    services = service_manager.list_services()
    print(f"✅ 共有 {len(services)} 个服务:")
    for service in services:
        print(f"  - {service.name} ({service.status})")
    
    # 6. 启动服务
    print("\n🚀 步骤6: 启动服务")
    start_result = service_manager.start_service(service_id)
    if start_result['success']:
        print(f"✅ {start_result['message']}")
        if start_result.get('pid'):
            print(f"🆔 进程ID: {start_result['pid']}")
    else:
        print(f"❌ 启动失败: {start_result['error']}")
    
    # 7. 等待一段时间
    print("\n⏳ 步骤7: 等待服务运行...")
    time.sleep(2)
    
    # 8. 获取服务日志
    print("\n📄 步骤8: 获取服务日志")
    logs_result = service_manager.get_service_logs(service_id, lines=10)
    if logs_result['success']:
        print(f"✅ 日志获取成功，共 {logs_result['total_lines']} 行")
        if logs_result['logs']:
            print("📝 最近日志:")
            print(logs_result['logs'][-200:])  # 显示最后200个字符
    else:
        print(f"❌ 日志获取失败: {logs_result['error']}")
    
    # 9. 停止服务
    print("\n⏹️ 步骤9: 停止服务")
    stop_result = service_manager.stop_service(service_id)
    if stop_result['success']:
        print(f"✅ {stop_result['message']}")
    else:
        print(f"❌ 停止失败: {stop_result['error']}")
    
    # 10. 删除服务
    print("\n🗑️ 步骤10: 删除服务")
    delete_result = service_manager.delete_service(service_id)
    if delete_result['success']:
        print(f"✅ {delete_result['message']}")
    else:
        print(f"❌ 删除失败: {delete_result['error']}")
    
    # 清理临时文件
    Path(output_path).unlink(missing_ok=True)
    print(f"🗑️ 已清理临时文件: {output_path}")
    
    print("\n🎉 服务管理演示完成！")
    print("\n💡 提示:")
    print("  - 启动API服务器: mcp-api-server")
    print("  - 查看API文档: http://localhost:8000/docs")
    print("  - 运行API示例: python -m minder.examples.api_usage")


if __name__ == "__main__":
    asyncio.run(demo_service_management())
