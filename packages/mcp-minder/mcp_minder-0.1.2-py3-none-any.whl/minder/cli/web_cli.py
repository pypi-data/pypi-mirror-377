"""
MCP Minder Web界面命令行启动器

用于启动Gradio Web界面
"""

import argparse
from minder.web.gradio_app import MCPMinderWebApp


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='启动 MCP Minder Web界面',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动Web界面（默认配置）
  mcp-web
  
  # 指定端口
  mcp-web --port 8080
  
  # 启用分享链接
  mcp-web --share
  
  # 启用调试模式
  mcp-web --debug
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Web服务器绑定主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Web服务器绑定端口 (默认: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="启用公共分享链接"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--show-error",
        action="store_true",
        default=True,
        help="显示详细错误信息"
    )
    
    args = parser.parse_args()
    
    print("🌐 启动 MCP Minder Web界面")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"🔗 分享: {'启用' if args.share else '禁用'}")
    print(f"🐛 调试: {'启用' if args.debug else '禁用'}")
    print("=" * 50)
    
    try:
        app = MCPMinderWebApp()
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug,
            show_error=args.show_error
        )
    except KeyboardInterrupt:
        print("\n👋 Web界面已关闭")
    except Exception as e:
        print(f"❌ 启动Web界面失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()
