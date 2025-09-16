"""
命令行接口模块

提供MCP生成器的命令行接口
"""

from .main import main
from .launcher_cli import main as launcher_main

__all__ = ['main', 'launcher_main']
