"""
MCP服务启动器命令行接口

提供启动、停止、管理MCP服务的命令行工具
"""

import argparse
import sys
import json
from pathlib import Path
from ..core.launcher import MCPLauncher
from ..core.service_manager import ServiceManager


def start_command(args):
    """启动服务命令"""
    launcher = MCPLauncher(log_dir=args.log_dir)
    
    result = launcher.start_service(
        script_path=args.script,
        use_uv=not args.no_uv,
        host=args.host,
        port=args.port,
        background=not args.foreground
    )
    
    if result['success']:
        print(f"✅ 服务启动成功!")
        print(f"📁 脚本: {args.script}")
        if result.get('background'):
            print(f"🆔 PID: {result['pid']}")
            print(f"📝 日志: {result['log_file']}")
        print(f"🔧 命令: {result['command']}")
    else:
        print(f"❌ 服务启动失败: {result['error']}")
        sys.exit(1)


def stop_command(args):
    """停止服务命令"""
    launcher = MCPLauncher(log_dir=args.log_dir)
    
    result = launcher.stop_service(args.script)
    
    if result['success']:
        print(f"✅ 服务已停止!")
        print(f"📁 脚本: {args.script}")
        print(f"🆔 PID: {result['pid']}")
    else:
        print(f"❌ 停止服务失败: {result['error']}")
        sys.exit(1)


def list_command(args):
    """列出运行中的服务命令"""
    launcher = MCPLauncher(log_dir=args.log_dir)
    
    result = launcher.list_running_services()
    
    if result['success']:
        services = result['services']
        if services:
            print(f"📋 运行中的服务 ({result['count']} 个):")
            print("-" * 60)
            for service in services:
                print(f"📁 脚本: {service['script_path']}")
                print(f"🆔 PID: {service['pid']}")
                print(f"📊 状态: {service['status']}")
                print("-" * 60)
        else:
            print("📋 没有运行中的服务")
    else:
        print(f"❌ 获取服务列表失败: {result['error']}")
        sys.exit(1)


def stop_all_command(args):
    """停止所有服务命令"""
    launcher = MCPLauncher(log_dir=args.log_dir)
    
    result = launcher.stop_all_services()
    
    if result['success']:
        print(f"✅ 所有服务已停止!")
        print(f"📊 停止的服务数量: {result['total_stopped']}")
        if result['stopped_services']:
            print("📁 已停止的服务:")
            for service in result['stopped_services']:
                print(f"  - {service}")
    else:
        print(f"⚠️ 部分服务停止失败:")
        for failed in result['failed_services']:
            print(f"  - {failed['script_path']}: {failed['error']}")
        sys.exit(1)


def logs_command(args):
    """查看日志命令"""
    launcher = MCPLauncher(log_dir=args.log_dir)
    
    result = launcher.get_service_logs(
        script_path=args.script,
        lines=args.lines
    )
    
    if result['success']:
        print(f"📝 服务日志 ({args.script}):")
        print(f"📊 总行数: {result['total_lines']}, 显示行数: {result['returned_lines']}")
        print("-" * 60)
        print(result['logs'])
    else:
        print(f"❌ 获取日志失败: {result['error']}")
        sys.exit(1)


def start_by_name_command(args):
    """根据服务名称启动服务命令"""
    service_manager = ServiceManager()
    
    result = service_manager.start_service_by_name(args.name, args.port)
    
    if result['success']:
        print(f"✅ 服务 {args.name} 启动成功!")
        print(f"🆔 PID: {result['pid']}")
        print(f"📝 消息: {result['message']}")
    else:
        print(f"❌ 启动服务失败: {result['error']}")
        sys.exit(1)


def stop_by_name_command(args):
    """根据服务名称停止服务命令"""
    service_manager = ServiceManager()
    
    result = service_manager.stop_service_by_name(args.name)
    
    if result['success']:
        print(f"✅ 服务 {args.name} 停止成功!")
        print(f"📝 消息: {result['message']}")
    else:
        print(f"❌ 停止服务失败: {result['error']}")
        sys.exit(1)


def delete_by_name_command(args):
    """根据服务名称删除服务命令"""
    service_manager = ServiceManager()
    
    result = service_manager.delete_service_by_name(args.name)
    
    if result['success']:
        print(f"✅ 服务 {args.name} 删除成功!")
        print(f"📝 消息: {result['message']}")
    else:
        print(f"❌ 删除服务失败: {result['error']}")
        sys.exit(1)


def logs_by_name_command(args):
    """根据服务名称查看日志命令"""
    service_manager = ServiceManager()
    
    result = service_manager.get_service_logs_by_name(args.name, args.lines)
    
    if result['success']:
        print(f"📝 服务日志 ({args.name}):")
        print(f"📊 总行数: {result['total_lines']}, 显示行数: {result['returned_lines']}")
        print("-" * 60)
        print(result['logs'])
    else:
        print(f"❌ 获取日志失败: {result['error']}")
        sys.exit(1)


def list_services_command(args):
    """列出所有服务命令"""
    service_manager = ServiceManager()
    
    services = service_manager.list_services(status_filter=args.status)
    
    if services:
        print(f"📋 服务列表 ({len(services)} 个):")
        print("-" * 80)
        for service in services:
            print(f"📝 名称: {service.name}")
            print(f"🆔 ID: {service.id}")
            print(f"📁 文件: {service.file_path}")
            print(f"🌐 地址: {service.host}:{service.port}")
            print(f"📊 状态: {service.status}")
            if service.pid:
                print(f"🆔 PID: {service.pid}")
            print(f"📅 创建时间: {service.created_at}")
            print("-" * 80)
    else:
        print("📋 没有找到服务")


def sync_services_command(args):
    """同步服务命令"""
    service_manager = ServiceManager()
    
    print("🔄 正在同步服务...")
    service_manager.sync_services()
    print("✅ 服务同步完成!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MCP服务启动器 - 管理MCP服务器进程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动服务 (按文件路径)
  mcp-launcher start my_server.py
  mcp-launcher start my_server.py --port 8080 --host 127.0.0.1
  
  # 停止服务 (按文件路径)
  mcp-launcher stop my_server.py
  
  # 列出运行中的服务
  mcp-launcher list
  
  # 停止所有服务
  mcp-launcher stop-all
  
  # 查看服务日志 (按文件路径)
  mcp-launcher logs my_server.py
  mcp-launcher logs my_server.py --lines 100
  
  # 按服务名称操作
  mcp-launcher start-by-name my_service
  mcp-launcher start-by-name my_service --port 8080
  mcp-launcher stop-by-name my_service
  mcp-launcher delete-by-name my_service
  mcp-launcher logs-by-name my_service --lines 100
  
  # 服务管理
  mcp-launcher list-services
  mcp-launcher list-services --status running
  mcp-launcher sync-services
        """
    )
    
    parser.add_argument(
        '--log-dir',
        default='service_logs',
        help='日志目录 (默认: service_logs)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 启动命令
    start_parser = subparsers.add_parser('start', help='启动MCP服务')
    start_parser.add_argument('script', help='Python脚本路径')
    start_parser.add_argument('--host', default='0.0.0.0', help='主机地址 (默认: 0.0.0.0)')
    start_parser.add_argument('--port', type=int, help='端口号')
    start_parser.add_argument('--no-uv', action='store_true', help='不使用uv运行')
    start_parser.add_argument('--foreground', action='store_true', help='前台运行')
    start_parser.set_defaults(func=start_command)
    
    # 停止命令
    stop_parser = subparsers.add_parser('stop', help='停止MCP服务')
    stop_parser.add_argument('script', help='Python脚本路径')
    stop_parser.set_defaults(func=stop_command)
    
    # 列出命令
    list_parser = subparsers.add_parser('list', help='列出运行中的服务')
    list_parser.set_defaults(func=list_command)
    
    # 停止所有命令
    stop_all_parser = subparsers.add_parser('stop-all', help='停止所有运行中的服务')
    stop_all_parser.set_defaults(func=stop_all_command)
    
    # 日志命令
    logs_parser = subparsers.add_parser('logs', help='查看服务日志')
    logs_parser.add_argument('script', help='Python脚本路径')
    logs_parser.add_argument('--lines', type=int, default=50, help='显示的行数 (默认: 50)')
    logs_parser.set_defaults(func=logs_command)
    
    # 按名称启动服务命令
    start_by_name_parser = subparsers.add_parser('start-by-name', help='根据服务名称启动服务')
    start_by_name_parser.add_argument('name', help='服务名称')
    start_by_name_parser.add_argument('--port', type=int, help='端口号（可选，如果不指定则使用随机端口）')
    start_by_name_parser.set_defaults(func=start_by_name_command)
    
    # 按名称停止服务命令
    stop_by_name_parser = subparsers.add_parser('stop-by-name', help='根据服务名称停止服务')
    stop_by_name_parser.add_argument('name', help='服务名称')
    stop_by_name_parser.set_defaults(func=stop_by_name_command)
    
    # 按名称删除服务命令
    delete_by_name_parser = subparsers.add_parser('delete-by-name', help='根据服务名称删除服务')
    delete_by_name_parser.add_argument('name', help='服务名称')
    delete_by_name_parser.set_defaults(func=delete_by_name_command)
    
    # 按名称查看日志命令
    logs_by_name_parser = subparsers.add_parser('logs-by-name', help='根据服务名称查看日志')
    logs_by_name_parser.add_argument('name', help='服务名称')
    logs_by_name_parser.add_argument('--lines', type=int, default=50, help='显示的行数 (默认: 50)')
    logs_by_name_parser.set_defaults(func=logs_by_name_command)
    
    # 列出所有服务命令
    list_services_parser = subparsers.add_parser('list-services', help='列出所有服务')
    list_services_parser.add_argument('--status', help='状态过滤器 (running, stopped, error)')
    list_services_parser.set_defaults(func=list_services_command)
    
    # 同步服务命令
    sync_services_parser = subparsers.add_parser('sync-services', help='同步服务状态')
    sync_services_parser.set_defaults(func=sync_services_command)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行命令时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
