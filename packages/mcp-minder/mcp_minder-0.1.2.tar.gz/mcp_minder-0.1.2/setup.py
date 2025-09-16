#!/usr/bin/env python3
"""
Setup script for MCP Minder package.
"""

from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcp_minder",
    version="0.1.2",
    author="MCP Minder Team",
    author_email="contact@mcpminder.dev",
    description="MCP服务器管理框架 - 用于管理和监控MCP (Model Context Protocol) 服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/mcp-minder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.12",
    install_requires=[
        "pyyaml>=6.0",
        "asyncio-mqtt>=0.16.0",
        "psutil>=5.9.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "starlette>=0.27.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "gradio>=4.0.0",
        "mcp>=1.13.1",
        "httpx>=0.24.0",
        "fastmcp>=2.12.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "minder=minder.cli.main:main",
            "mcp-launcher=minder.cli.launcher_cli:main",
            "mcp-api-server=minder.cli.api_cli:main",
            "mcp-web=minder.cli.web_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "minder": ["templates/*.py", "static/*", "templates/*"],
    },
)
