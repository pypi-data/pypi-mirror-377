"""
MCP Generator - 基于模板快速生成MCP服务器的工具

一个简单而强大的工具，用于快速生成基于example.py格式的MCP服务器。
"""

from .core.generator import MCPGenerator
from .core.launcher import MCPLauncher
from .core.service_manager import ServiceManager

__version__ = "0.1.0"
__author__ = "MCP Generator Team"

__all__ = ['MCPGenerator', 'MCPLauncher', 'ServiceManager']
