.PHONY: help install install-dev test lint format clean build publish

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装项目依赖
	pip install -e .

install-dev: ## 安装开发依赖
	pip install -e ".[dev]"
	pre-commit install

test: ## 运行测试
	pytest tests/ -v --cov=minder --cov-report=html --cov-report=term

lint: ## 运行代码检查
	flake8 minder/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 minder/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy minder/ --ignore-missing-imports

format: ## 格式化代码
	black minder/ tests/
	isort minder/ tests/

format-check: ## 检查代码格式
	black --check minder/ tests/
	isort --check-only minder/ tests/

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

build: ## 构建包
	python -m build

publish: ## 发布到PyPI
	twine upload dist/*

dev: ## 启动开发环境
	mcp-api-server --host 0.0.0.0 --port 8000 --reload

web: ## 启动Web界面
	mcp-web --port 8080

demo: ## 运行演示
	python scripts/start_demo.py

all: clean install-dev format lint test ## 运行完整的质量检查流程
