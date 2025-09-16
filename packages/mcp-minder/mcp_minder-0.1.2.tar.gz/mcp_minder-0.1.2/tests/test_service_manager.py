"""
服务管理器测试

测试 ServiceManager 类的功能
"""

import pytest
import tempfile
import json
from pathlib import Path
from minder.core.service_manager import ServiceManager, ServiceInfo


class TestServiceManager:
    """服务管理器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建临时数据文件
        self.temp_data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_data_file.close()
        
        # 创建临时日志目录
        self.temp_log_dir = tempfile.mkdtemp()
        
        # 创建服务管理器实例
        self.manager = ServiceManager(
            data_file=self.temp_data_file.name,
            log_dir=self.temp_log_dir
        )
    
    def teardown_method(self):
        """测试后清理"""
        # 清理临时文件
        Path(self.temp_data_file.name).unlink(missing_ok=True)
        import shutil
        shutil.rmtree(self.temp_log_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.manager.data_file == Path(self.temp_data_file.name)
        assert self.manager.log_dir == Path(self.temp_log_dir)
        assert isinstance(self.manager.services, dict)
        assert len(self.manager.services) == 0
    
    def test_register_service(self):
        """测试注册服务"""
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py",
            port=8080,
            host="127.0.0.1",
            description="测试服务",
            author="测试作者"
        )
        
        assert service_id is not None
        assert service_id in self.manager.services
        
        service_info = self.manager.services[service_id]
        assert service_info.name == "test_service"
        assert service_info.file_path == "/path/to/test.py"
        assert service_info.port == 8080
        assert service_info.host == "127.0.0.1"
        assert service_info.status == "stopped"
        assert service_info.description == "测试服务"
        assert service_info.author == "测试作者"
    
    def test_get_service(self):
        """测试获取服务"""
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py"
        )
        
        service_info = self.manager.get_service(service_id)
        assert service_info is not None
        assert service_info.name == "test_service"
        
        # 测试获取不存在的服务
        non_existent = self.manager.get_service("non-existent-id")
        assert non_existent is None
    
    def test_list_services(self):
        """测试列出服务"""
        # 注册多个服务
        service1_id = self.manager.register_service("service1", "/path/to/service1.py")
        service2_id = self.manager.register_service("service2", "/path/to/service2.py")
        
        # 列出所有服务
        services = self.manager.list_services()
        assert len(services) == 2
        
        # 按状态过滤
        stopped_services = self.manager.list_services(status_filter="stopped")
        assert len(stopped_services) == 2
        
        running_services = self.manager.list_services(status_filter="running")
        assert len(running_services) == 0
    
    def test_update_service(self):
        """测试更新服务"""
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py",
            port=8080
        )
        
        # 更新服务信息
        result = self.manager.update_service(
            service_id=service_id,
            name="updated_service",
            port=9000,
            description="更新后的服务"
        )
        
        assert result['success'] is True
        
        service_info = self.manager.get_service(service_id)
        assert service_info.name == "updated_service"
        assert service_info.port == 9000
        assert service_info.description == "更新后的服务"
    
    def test_delete_service(self):
        """测试删除服务"""
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py"
        )
        
        # 删除服务
        result = self.manager.delete_service(service_id)
        assert result['success'] is True
        
        # 验证服务已被删除
        service_info = self.manager.get_service(service_id)
        assert service_info is None
    
    def test_delete_nonexistent_service(self):
        """测试删除不存在的服务"""
        result = self.manager.delete_service("non-existent-id")
        assert result['success'] is False
        assert "不存在" in result['error']
    
    def test_persistence(self):
        """测试数据持久化"""
        # 注册服务
        service_id = self.manager.register_service(
            name="persistent_service",
            file_path="/path/to/persistent.py",
            port=8080
        )
        
        # 创建新的管理器实例（模拟重启）
        new_manager = ServiceManager(
            data_file=self.temp_data_file.name,
            log_dir=self.temp_log_dir
        )
        
        # 验证数据是否被正确加载
        service_info = new_manager.get_service(service_id)
        assert service_info is not None
        assert service_info.name == "persistent_service"
        assert service_info.port == 8080
    
    def test_get_service_logs_nonexistent(self):
        """测试获取不存在服务的日志"""
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py"
        )
        
        result = self.manager.get_service_logs(service_id)
        assert result['success'] is False
        assert "日志文件不存在" in result['error']
    
    def test_sync_service_status(self):
        """测试同步服务状态"""
        # 注册一个服务并设置为运行状态
        service_id = self.manager.register_service(
            name="test_service",
            file_path="/path/to/test.py"
        )
        self.manager.services[service_id].status = "running"
        self.manager.services[service_id].pid = 99999  # 不存在的PID
        
        # 同步状态
        self.manager.sync_service_status()
        
        # 验证状态是否被更新
        service_info = self.manager.get_service(service_id)
        assert service_info.status == "stopped"
        assert service_info.pid is None
