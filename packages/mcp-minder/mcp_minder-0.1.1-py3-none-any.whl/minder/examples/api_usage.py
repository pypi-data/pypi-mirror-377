"""
MCP Minder API 使用示例

演示如何使用 FastAPI 接口管理 MCP 服务
"""

import asyncio
import httpx
import json
from pathlib import Path


class MCPMinderAPIClient:
    """MCP Minder API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
    
    async def health_check(self):
        """健康检查"""
        response = await self.client.get("/health")
        return response.json()
    
    async def create_service(self, service_data: dict):
        """创建服务"""
        response = await self.client.post("/api/services", json=service_data)
        return response.json()
    
    async def list_services(self, status: str = None):
        """获取服务列表"""
        params = {"status": status} if status else {}
        response = await self.client.get("/api/services", params=params)
        return response.json()
    
    async def get_service(self, service_id: str):
        """获取服务信息"""
        response = await self.client.get(f"/api/services/{service_id}")
        return response.json()
    
    async def update_service(self, service_id: str, update_data: dict):
        """更新服务"""
        response = await self.client.put(f"/api/services/{service_id}", json=update_data)
        return response.json()
    
    async def delete_service(self, service_id: str):
        """删除服务"""
        response = await self.client.delete(f"/api/services/{service_id}")
        return response.json()
    
    async def start_service(self, service_id: str):
        """启动服务"""
        response = await self.client.post(f"/api/services/{service_id}/start")
        return response.json()
    
    async def stop_service(self, service_id: str):
        """停止服务"""
        response = await self.client.post(f"/api/services/{service_id}/stop")
        return response.json()
    
    async def get_service_logs(self, service_id: str, lines: int = 50):
        """获取服务日志"""
        response = await self.client.get(f"/api/services/{service_id}/logs", params={"lines": lines})
        return response.json()
    
    async def generate_mcp_server(self, generate_data: dict):
        """生成MCP服务器"""
        response = await self.client.post("/api/generate", json=generate_data)
        return response.json()
    
    async def sync_service_status(self):
        """同步服务状态"""
        response = await self.client.post("/api/services/sync")
        return response.json()
    
    async def start_all_services(self):
        """启动所有服务"""
        response = await self.client.post("/api/services/start-all")
        return response.json()
    
    async def stop_all_services(self):
        """停止所有服务"""
        response = await self.client.post("/api/services/stop-all")
        return response.json()


async def main():
    """主函数 - 演示API使用"""
    print("🚀 MCP Minder API 使用示例")
    print("=" * 50)
    
    # 创建API客户端
    api_client = MCPMinderAPIClient()
    
    try:
        # 1. 健康检查
        print("\n📋 步骤1: 健康检查")
        health = await api_client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"📊 服务数量: {health['services_count']}")
        
        # 2. 生成MCP服务器
        print("\n🔧 步骤2: 生成MCP服务器")
        generate_data = {
            "output_path": "example_mcp_server.py",
            "service_name": "example_service",
            "tool_name": "example_tool",
            "tool_description": "示例MCP工具",
            "tool_code": "# 示例代码\n    output = f\"处理输入: {input_data}\"",
            "author": "API示例"
        }
        
        generate_result = await api_client.generate_mcp_server(generate_data)
        if generate_result['success']:
            print(f"✅ {generate_result['message']}")
        else:
            print(f"❌ 生成失败: {generate_result['error']}")
            return
        
        # 3. 创建服务
        print("\n📦 步骤3: 创建服务")
        service_data = {
            "name": "example_service",
            "file_path": "example_mcp_server.py",
            "port": 8080,
            "host": "127.0.0.1",
            "description": "通过API创建的示例服务",
            "author": "API示例"
        }
        
        create_result = await api_client.create_service(service_data)
        if create_result['success']:
            service_id = create_result['service']['id']
            print(f"✅ 服务创建成功，ID: {service_id}")
        else:
            print(f"❌ 服务创建失败: {create_result['error']}")
            return
        
        # 4. 获取服务列表
        print("\n📋 步骤4: 获取服务列表")
        services = await api_client.list_services()
        if services['success']:
            print(f"✅ 共有 {services['total']} 个服务")
            for service in services['services']:
                print(f"  - {service['name']} ({service['status']})")
        
        # 5. 获取特定服务信息
        print("\n🔍 步骤5: 获取服务信息")
        service_info = await api_client.get_service(service_id)
        if service_info['success']:
            service = service_info['service']
            print(f"✅ 服务名称: {service['name']}")
            print(f"📁 文件路径: {service['file_path']}")
            print(f"🌐 端口: {service['port']}")
            print(f"📊 状态: {service['status']}")
        
        # 6. 更新服务信息
        print("\n✏️ 步骤6: 更新服务信息")
        update_data = {
            "description": "更新后的服务描述",
            "port": 9000
        }
        
        update_result = await api_client.update_service(service_id, update_data)
        if update_result['success']:
            print(f"✅ {update_result['message']}")
        else:
            print(f"❌ 更新失败: {update_result['error']}")
        
        # 7. 启动服务（注意：这里只是演示，实际启动需要服务文件存在）
        print("\n🚀 步骤7: 启动服务")
        start_result = await api_client.start_service(service_id)
        if start_result['success']:
            print(f"✅ {start_result['message']}")
            if start_result.get('pid'):
                print(f"🆔 进程ID: {start_result['pid']}")
        else:
            print(f"❌ 启动失败: {start_result['error']}")
        
        # 8. 获取服务日志
        print("\n📄 步骤8: 获取服务日志")
        logs_result = await api_client.get_service_logs(service_id, lines=10)
        if logs_result['success']:
            print(f"✅ 日志获取成功，共 {logs_result['total_lines']} 行")
            if logs_result['logs']:
                print("📝 最近日志:")
                print(logs_result['logs'][-200:])  # 显示最后200个字符
        else:
            print(f"❌ 日志获取失败: {logs_result['error']}")
        
        # 9. 停止服务
        print("\n⏹️ 步骤9: 停止服务")
        stop_result = await api_client.stop_service(service_id)
        if stop_result['success']:
            print(f"✅ {stop_result['message']}")
        else:
            print(f"❌ 停止失败: {stop_result['error']}")
        
        # 10. 同步服务状态
        print("\n🔄 步骤10: 同步服务状态")
        sync_result = await api_client.sync_service_status()
        if sync_result['success']:
            print(f"✅ {sync_result['message']}")
        
        # 11. 删除服务
        print("\n🗑️ 步骤11: 删除服务")
        delete_result = await api_client.delete_service(service_id)
        if delete_result['success']:
            print(f"✅ {delete_result['message']}")
        else:
            print(f"❌ 删除失败: {delete_result['error']}")
        
        print("\n🎉 API使用示例完成！")
        
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
    
    finally:
        # 清理生成的示例文件
        example_file = Path("example_mcp_server.py")
        if example_file.exists():
            example_file.unlink()
            print("🗑️ 已清理示例文件")
        
        # 关闭API客户端
        await api_client.close()


if __name__ == "__main__":
    print("💡 提示: 请确保MCP Minder API服务器正在运行")
    print("   启动命令: mcp-api-server")
    print("   或者: python -m minder.cli.api_cli")
    print()
    
    asyncio.run(main())
