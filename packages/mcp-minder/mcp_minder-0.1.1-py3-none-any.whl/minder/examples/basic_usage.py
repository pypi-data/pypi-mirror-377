#!/usr/bin/env python3
"""
MCP生成器基本使用示例

演示如何使用MCPGenerator生成不同类型的MCP服务器
"""

from minder import MCPGenerator


def main():
    """主函数"""
    print("🚀 MCP生成器使用示例")
    print("=" * 50)
    
    # 创建生成器实例
    generator = MCPGenerator()
    
    # 示例1: 用户服务
    print("\n📝 示例1: 用户服务")
    success = generator.generate(
        output_path="examples_output/user_service.py",
        service_name="user_service",
        tool_name="get_user_info",
        tool_param_name="user_id",
        tool_param_type="int",
        tool_return_type="dict",
        tool_description="获取用户信息",
        service_port=8080,
        author="张三"
    )
    
    if success:
        print("✅ 用户服务生成完成！")
    else:
        print("❌ 用户服务生成失败！")
    
    # 示例2: 文件处理工具
    print("\n📝 示例2: 文件处理工具")
    success = generator.generate(
        output_path="examples_output/file_processor.py",
        service_name="file_processor",
        tool_name="process_file",
        tool_param_name="file_path",
        tool_param_type="str",
        tool_return_type="bool",
        tool_description="处理文件",
        service_port=8081,
        author="李四"
    )
    
    if success:
        print("✅ 文件处理工具生成完成！")
    else:
        print("❌ 文件处理工具生成失败！")
    
    # 示例3: 数据分析服务
    print("\n📝 示例3: 数据分析服务")
    success = generator.generate(
        output_path="examples_output/data_analyzer.py",
        service_name="data_analyzer",
        tool_name="analyze_data",
        tool_param_name="data_source",
        tool_param_type="str",
        tool_return_type="dict",
        tool_description="分析数据",
        service_port=8082,
        author="王五"
    )
    
    if success:
        print("✅ 数据分析服务生成完成！")
    else:
        print("❌ 数据分析服务生成失败！")
    
    print("\n🎉 所有示例生成完成！")
    print("📁 生成的文件位于 'examples_output' 目录中")


if __name__ == "__main__":
    main()
