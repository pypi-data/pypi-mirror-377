# MCP Minder 文档

欢迎使用 MCP Minder！这是一个用于管理和监控 MCP (Model Context Protocol) 服务器的框架。

## 目录

- [快速开始](quickstart.md)
- [API 参考](api.md)
- [开发指南](development.md)
- [贡献指南](contributing.md)

## 主要功能

- 🚀 **MCP 服务器生成器**: 快速生成基于模板的 MCP 服务器
- 🎯 **服务启动器**: 管理和监控 MCP 服务进程
- 📝 **模板系统**: 基于 example.py 的灵活模板
- 🔧 **命令行工具**: 简单易用的 CLI 接口
- 💻 **Python API**: 完整的编程接口

## 安装

```bash
pip install mcp-minder
```

## 快速开始

### 生成 MCP 服务器

```bash
mcp-generator my_server.py --service-name "my_service" --tool-name "my_tool"
```

### 启动服务

```bash
mcp-launcher start my_server.py --port 8080
```

### Python API

```python
from minder import MCPGenerator, MCPLauncher

# 生成服务器
generator = MCPGenerator()
generator.generate("my_server.py", service_name="my_service")

# 启动服务
launcher = MCPLauncher()
launcher.start_service("my_server.py", port=8080)
```

## 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件。
