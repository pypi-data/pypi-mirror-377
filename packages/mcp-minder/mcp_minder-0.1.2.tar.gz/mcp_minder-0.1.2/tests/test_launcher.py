"""
MCP启动器测试
"""

import pytest
import tempfile
from pathlib import Path
from minder.core.launcher import MCPLauncher


class TestMCPLauncher:
    """MCP启动器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.launcher = MCPLauncher()
    
    def test_launcher_initialization(self):
        """测试启动器初始化"""
        assert self.launcher.log_dir == Path("service_logs")
        assert isinstance(self.launcher.running_processes, dict)
        assert len(self.launcher.running_processes) == 0
    
    def test_list_running_services_empty(self):
        """测试空服务列表"""
        result = self.launcher.list_running_services()
        assert result['success'] is True
        assert result['services'] == []
        assert result['count'] == 0
    
    def test_stop_all_services_empty(self):
        """测试停止所有服务（空列表）"""
        result = self.launcher.stop_all_services()
        assert result['success'] is True
        assert result['stopped_services'] == []
        assert result['failed_services'] == []
        assert result['total_stopped'] == 0
    
    def test_get_service_logs_nonexistent(self):
        """测试获取不存在的服务日志"""
        result = self.launcher.get_service_logs("nonexistent.py")
        assert result['success'] is False
        assert "日志文件不存在" in result['error']
