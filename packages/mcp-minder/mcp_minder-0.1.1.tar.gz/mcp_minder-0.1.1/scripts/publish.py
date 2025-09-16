#!/usr/bin/env python3
"""
PyPI发布脚本

使用方法:
    python scripts/publish.py --test    # 发布到测试PyPI
    python scripts/publish.py --prod    # 发布到正式PyPI
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令并返回结果"""
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result


def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        run_command(f"rm -rf {pattern}", check=False)


def build_package():
    """构建包"""
    print("📦 构建包...")
    run_command("python -m build")


def check_package():
    """检查包"""
    print("🔍 检查包...")
    run_command("python -m twine check dist/*")


def upload_to_testpypi():
    """上传到测试PyPI"""
    print("🚀 上传到测试PyPI...")
    run_command("python -m twine upload --repository testpypi dist/*")


def upload_to_pypi():
    """上传到正式PyPI"""
    print("🚀 上传到正式PyPI...")
    run_command("python -m twine upload dist/*")


def main():
    parser = argparse.ArgumentParser(description="PyPI发布脚本")
    parser.add_argument("--test", action="store_true", help="发布到测试PyPI")
    parser.add_argument("--prod", action="store_true", help="发布到正式PyPI")
    parser.add_argument("--build-only", action="store_true", help="仅构建包，不上传")
    
    args = parser.parse_args()
    
    if not any([args.test, args.prod, args.build_only]):
        parser.print_help()
        sys.exit(1)
    
    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        # 清理构建文件
        clean_build()
        
        # 构建包
        build_package()
        
        # 检查包
        check_package()
        
        if args.build_only:
            print("✅ 包构建完成，未上传")
            return
        
        # 上传到PyPI
        if args.test:
            upload_to_testpypi()
            print("✅ 已上传到测试PyPI")
            print("📝 测试安装命令: pip install --index-url https://test.pypi.org/simple/ mcp-minder")
        elif args.prod:
            upload_to_pypi()
            print("✅ 已上传到正式PyPI")
            print("📝 安装命令: pip install mcp-minder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
