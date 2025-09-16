# 快速开始指南

本指南将帮助您快速上手 MCP Minder。

## 安装

### 使用 pip 安装

```bash
pip install mcp-minder
```

### 从源码安装

```bash
git clone https://github.com/your-org/mcp-minder.git
cd mcp-minder
pip install -e .
```

## 基本使用

### 1. 生成 MCP 服务器

使用命令行工具生成一个基本的 MCP 服务器：

```bash
mcp-generator hello_server.py
```

这将创建一个名为 `hello_server.py` 的 MCP 服务器文件。

### 2. 自定义生成

您可以通过参数自定义生成的服务器：

```bash
mcp-generator user_service.py \
  --service-name "user_service" \
  --tool-name "get_user_info" \
  --param-name "user_id" \
  --param-type "int" \
  --return-type "dict" \
  --description "获取用户信息" \
  --port 8080 \
  --author "您的名字"
```

### 3. 启动服务

使用启动器启动生成的服务器：

```bash
mcp-launcher start user_service.py
```

### 4. 管理服务

```bash
# 列出运行中的服务
mcp-launcher list

# 停止特定服务
mcp-launcher stop user_service.py

# 停止所有服务
mcp-launcher stop-all

# 查看服务日志
mcp-launcher logs user_service.py
```

## Python API 使用

### 生成器 API

```python
from minder import MCPGenerator

generator = MCPGenerator()

# 基本生成
success = generator.generate("my_server.py")

# 自定义生成
success = generator.generate(
    output_path="custom_server.py",
    service_name="custom_service",
    tool_name="custom_tool",
    tool_param_name="input_data",
    tool_param_type="str",
    tool_return_type="dict",
    tool_description="自定义工具描述",
    service_port=9000,
    author="开发者"
)
```

### 启动器 API

```python
from minder import MCPLauncher

launcher = MCPLauncher()

# 启动服务
result = launcher.start_service(
    script_path="my_server.py",
    use_uv=True,
    host="127.0.0.1",
    port=8080,
    background=True
)

if result['success']:
    print(f"服务已启动，PID: {result['pid']}")
    print(f"日志文件: {result['log_file']}")

# 列出运行中的服务
services = launcher.list_running_services()
print(f"运行中的服务数量: {services['count']}")

# 停止服务
stop_result = launcher.stop_service("my_server.py")
if stop_result['success']:
    print("服务已停止")
```

## 下一步

- 查看 [API 参考](api.md) 了解详细的 API 文档
- 阅读 [开发指南](development.md) 了解如何扩展功能
- 查看 [贡献指南](contributing.md) 了解如何参与项目开发
