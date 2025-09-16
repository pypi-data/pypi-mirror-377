"""
MCP服务器模板 - 基于HTTP Stream的MCP服务器
作者: 张三
服务名称: user_service
"""

import logging
import random
from fastmcp import FastMCP

mcp = FastMCP("user_service")

logger = logging.getLogger(__name__)

# 确保 mcp 工具装饰器能正确处理异步函数
@mcp.tool()
async def get_user_info(user_id: int) -> dict:
    """
    获取用户信息,
    :param user_id: input user_id
    :return: output result
    """
    # 实现您的业务逻辑
    output = "处理完成"

    return output

if __name__ == "__main__":
    default_port = 8080
    mcp.run(transport="streamable-http", host="0.0.0.0", port=default_port, path="/mcp")
