"""
MCP生成器测试
"""

import pytest
import tempfile
from pathlib import Path
from minder.core.generator import MCPGenerator


class TestMCPGenerator:
    """MCP生成器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.generator = MCPGenerator()
    
    def test_generate_basic(self):
        """测试基本生成功能"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_path = f.name
        
        try:
            result = self.generator.generate(
                output_path=output_path,
                service_name="test_service",
                tool_name="test_tool",
                tool_description="测试工具"
            )
            
            assert result is True
            assert Path(output_path).exists()
            
            # 检查生成的文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "test_service" in content
                assert "test_tool" in content
                assert "测试工具" in content
                
        finally:
            # 清理临时文件
            Path(output_path).unlink(missing_ok=True)
    
    def test_generate_with_custom_params(self):
        """测试自定义参数生成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_path = f.name
        
        try:
            result = self.generator.generate(
                output_path=output_path,
                service_name="custom_service",
                tool_name="custom_tool",
                tool_param_name="user_id",
                tool_param_type="int",
                tool_return_type="dict",
                tool_description="自定义工具",
                service_port=8080,
                author="测试作者"
            )
            
            assert result is True
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "custom_service" in content
                assert "custom_tool" in content
                assert "user_id: int" in content
                assert "-> dict" in content
                assert "自定义工具" in content
                assert "测试作者" in content
                assert "8080" in content
                
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_to_class_name(self):
        """测试类名转换"""
        assert MCPGenerator.to_class_name("test_service") == "TestService"
        assert MCPGenerator.to_class_name("my-custom-tool") == "MyCustomTool"
        assert MCPGenerator.to_class_name("simple") == "Simple"
