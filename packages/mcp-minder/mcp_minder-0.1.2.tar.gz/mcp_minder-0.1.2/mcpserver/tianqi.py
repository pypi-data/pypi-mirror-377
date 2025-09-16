"""
MCP服务器模板 - 基于HTTP Stream的MCP服务器
作者: 开发者
服务名称: 天气查询
"""

import logging
import random
import sys
from fastmcp import FastMCP

mcp = FastMCP("天气查询")

logger = logging.getLogger(__name__)

# 确保 mcp 工具装饰器能正确处理异步函数
@mcp.tool()
async def query_tianqi(input: str) -> str:
    """
    天气查询工具,
    :param input: input input
    :return: output result
    """
    # 实现天气查询逻辑
    output = "天气是阴天"

    return output

if __name__ == "__main__":
    # 检查命令行参数中的端口
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # 如果没有指定端口，使用随机端口
    if port is None:
        port = random.randint(10001, 18000)
    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp", stateless_http=True)