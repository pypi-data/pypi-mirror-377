# 开发指南

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd mcp-minder
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装开发依赖

```bash
make install-dev
```

或者手动安装：

```bash
pip install -e ".[dev]"
pre-commit install
```

## 开发工作流

### 代码质量检查

```bash
# 运行所有检查
make all

# 单独运行各项检查
make lint      # 代码风格检查
make format    # 代码格式化
make test      # 运行测试
```

### 代码格式化

项目使用以下工具进行代码格式化：

- **Black**: Python代码格式化
- **isort**: 导入语句排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查

### 提交代码

1. 确保所有检查通过：`make all`
2. 提交代码：`git commit -m "描述你的更改"`
3. 推送代码：`git push`

## 项目结构

```
mcp-minder/
├── minder/                # 主包
│   ├── core/              # 核心功能
│   ├── cli/               # 命令行接口
│   ├── api/               # FastAPI接口
│   ├── web/               # Web界面
│   ├── client/            # 客户端库
│   └── examples/          # 使用示例
├── tests/                 # 测试文件
├── docs/                  # 文档
├── scripts/               # 脚本工具
└── mcpserver/             # 生成的MCP服务器
```

## 添加新功能

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 实现功能

- 在相应的模块中添加代码
- 添加适当的测试
- 更新文档

### 3. 运行测试

```bash
make test
```

### 4. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

## 测试

### 运行所有测试

```bash
make test
```

### 运行特定测试

```bash
pytest tests/test_generator.py -v
```

### 测试覆盖率

```bash
pytest --cov=minder --cov-report=html
```

## 发布

### 构建包

```bash
make build
```

### 发布到PyPI

```bash
make publish
```

## 故障排除

### 常见问题

1. **导入错误**: 确保虚拟环境已激活
2. **测试失败**: 检查依赖是否正确安装
3. **格式化失败**: 运行 `make format` 自动修复

### 获取帮助

- 查看项目文档
- 提交Issue
- 参与讨论
