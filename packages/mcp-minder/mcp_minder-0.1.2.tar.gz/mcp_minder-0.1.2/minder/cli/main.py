"""
MCP生成器命令行接口

提供完整的命令行参数支持和帮助信息
"""

import argparse
import sys
from ..core.generator import MCPGenerator


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description='MCP服务器生成器 - 快速生成基于example.py格式的MCP服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本用法
  mcp-generator my_server.py
  
  # 完整自定义
  mcp-generator my_server.py \\
    -s "user_service" \\
    -t "get_user_info" \\
    -p "user_id" \\
    --param-type "int" \\
    --return-type "dict" \\
    -d "获取用户信息" \\
    --port 8080 \\
    -a "张三"
  
  # 文件处理工具
  mcp-generator file_processor.py \\
    -s "file_processor" \\
    -t "process_file" \\
    -p "file_path" \\
    --return-type "bool" \\
    -d "处理文件" \\
    --port 8081
        """
    )
    
    parser.add_argument('output', help='输出文件路径')
    parser.add_argument('-s', '--service-name', help='服务名称（默认从文件名提取）')
    parser.add_argument('-t', '--tool-name', help='工具函数名称（默认从服务名生成）')
    parser.add_argument('-p', '--param-name', default='path', help='工具参数名称')
    parser.add_argument('--param-type', default='str', help='工具参数类型')
    parser.add_argument('--return-type', default='str', help='工具返回类型')
    parser.add_argument('-d', '--description', default='MCP工具', help='工具描述')
    parser.add_argument('-c', '--code', help='工具函数代码块（可选）')
    parser.add_argument('--port', type=int, help='服务端口（默认随机）')
    parser.add_argument('-a', '--author', default='开发者', help='作者')
    
    args = parser.parse_args()
    
    # 创建生成器实例
    generator = MCPGenerator()
    
    # 处理输出路径，如果只是文件名则放在mcpserver目录
    output_path = args.output
    if not output_path.startswith('/') and '/' not in output_path:
        output_path = f"mcpserver/{output_path}"
    
    # 设置默认代码块
    tool_code = args.code if args.code else "# 实现您的业务逻辑\n    output = \"处理完成\""
    
    # 生成MCP服务器
    success = generator.generate(
        output_path=output_path,
        service_name=args.service_name,
        tool_name=args.tool_name,
        tool_param_name=args.param_name,
        tool_param_type=args.param_type,
        tool_return_type=args.return_type,
        tool_description=args.description,
        tool_code=tool_code,
        service_port=args.port,
        author=args.author
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
