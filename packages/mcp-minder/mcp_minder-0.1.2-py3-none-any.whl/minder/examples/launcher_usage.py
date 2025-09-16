#!/usr/bin/env python3
"""
MCP启动器使用示例

演示如何使用MCPLauncher启动和管理MCP服务
"""

import time
from minder import MCPGenerator, MCPLauncher


def main():
    """主函数"""
    print("🚀 MCP启动器使用示例")
    print("=" * 50)
    
    # 1. 生成一个MCP服务器文件
    print("\n📝 步骤1: 生成MCP服务器文件")
    generator = MCPGenerator()
    
    success = generator.generate(
        output_path="demo_server.py",
        service_name="demo_service",
        tool_name="demo_tool",
        tool_param_name="input_data",
        tool_param_type="str",
        tool_return_type="str",
        tool_description="演示工具",
        service_port=8080,
        author="演示者"
    )
    
    if not success:
        print("❌ 生成MCP服务器失败")
        return
    
    print("✅ MCP服务器文件生成成功: demo_server.py")
    
    # 2. 使用启动器启动服务
    print("\n🚀 步骤2: 启动MCP服务")
    launcher = MCPLauncher()
    
    # 启动服务
    result = launcher.start_service(
        script_path="demo_server.py",
        use_uv=True,
        host="127.0.0.1",
        port=8080,
        background=True
    )
    
    if result['success']:
        print("✅ 服务启动成功!")
        print(f"🆔 PID: {result['pid']}")
        print(f"📝 日志: {result['log_file']}")
        print(f"🔧 命令: {result['command']}")
        
        # 3. 列出运行中的服务
        print("\n📋 步骤3: 列出运行中的服务")
        services_result = launcher.list_running_services()
        
        if services_result['success']:
            services = services_result['services']
            print(f"📊 运行中的服务数量: {services_result['count']}")
            for service in services:
                print(f"  - {service['script_path']} (PID: {service['pid']})")
        
        # 4. 查看服务日志
        print("\n📝 步骤4: 查看服务日志")
        time.sleep(2)  # 等待服务启动
        
        logs_result = launcher.get_service_logs("demo_server.py", lines=10)
        
        if logs_result['success']:
            print(f"📊 日志总行数: {logs_result['total_lines']}")
            print("📄 最近日志:")
            print("-" * 40)
            print(logs_result['logs'])
        else:
            print(f"❌ 获取日志失败: {logs_result['error']}")
        
        # 5. 停止服务
        print("\n🛑 步骤5: 停止服务")
        time.sleep(1)
        
        stop_result = launcher.stop_service("demo_server.py")
        
        if stop_result['success']:
            print("✅ 服务已停止!")
            print(f"🆔 PID: {stop_result['pid']}")
        else:
            print(f"❌ 停止服务失败: {stop_result['error']}")
        
        # 6. 再次列出服务
        print("\n📋 步骤6: 再次列出运行中的服务")
        services_result = launcher.list_running_services()
        
        if services_result['success']:
            print(f"📊 运行中的服务数量: {services_result['count']}")
            if services_result['count'] == 0:
                print("✅ 所有服务已停止")
        
    else:
        print(f"❌ 服务启动失败: {result['error']}")
    
    print("\n🎉 演示完成!")
    print("💡 提示: 您可以使用以下命令管理MCP服务:")
    print("  - mcp-launcher start <script.py>")
    print("  - mcp-launcher stop <script.py>")
    print("  - mcp-launcher list")
    print("  - mcp-launcher logs <script.py>")


if __name__ == "__main__":
    main()
