"""
MCP Minder API 服务器命令行启动器

用于启动 FastAPI 服务器
"""

import argparse
import uvicorn
from minder.api.main import app


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='启动 MCP Minder API 服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动API服务器（默认配置）
  mcp-api-server
  
  # 指定主机和端口
  mcp-api-server --host 127.0.0.1 --port 8080
  
  # 启用调试模式
  mcp-api-server --debug
  
  # 指定工作目录
  mcp-api-server --work-dir /path/to/workspace
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API服务器绑定主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API服务器绑定端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载（开发模式）"
    )
    
    parser.add_argument(
        "--work-dir",
        default=".",
        help="工作目录路径 (默认: 当前目录)"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="日志级别 (默认: info)"
    )
    
    args = parser.parse_args()
    
    print("🚀 启动 MCP Minder API 服务器")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"📚 API文档: http://{args.host}:{args.port}/docs")
    print(f"🔧 工作目录: {args.work_dir}")
    print(f"🐛 调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 API服务器已停止")
    except Exception as e:
        print(f"❌ 启动API服务器失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()
