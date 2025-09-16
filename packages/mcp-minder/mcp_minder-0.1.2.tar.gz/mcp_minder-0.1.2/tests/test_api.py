"""
MCP Minder API 测试

测试 FastAPI 接口的功能
"""

import pytest
import tempfile
import json
from pathlib import Path
from fastapi.testclient import TestClient
from minder.api.main import app
from minder.core.service_manager import ServiceManager


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_service_file():
    """创建临时服务文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestHealthAPI:
    """健康检查API测试"""
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services_count" in data
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestServiceAPI:
    """服务管理API测试"""
    
    def test_create_service(self, client, temp_service_file):
        """测试创建服务"""
        service_data = {
            "name": "test_service",
            "file_path": temp_service_file,
            "port": 8080,
            "host": "127.0.0.1",
            "description": "测试服务",
            "author": "测试作者"
        }
        
        response = client.post("/api/services", json=service_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"]["name"] == "test_service"
        assert data["service"]["port"] == 8080
        assert data["service"]["status"] == "stopped"
    
    def test_list_services(self, client, temp_service_file):
        """测试获取服务列表"""
        # 先创建一个服务
        service_data = {
            "name": "test_service",
            "file_path": temp_service_file,
            "port": 8080
        }
        client.post("/api/services", json=service_data)
        
        # 获取服务列表
        response = client.get("/api/services")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] >= 1
        assert len(data["services"]) >= 1
    
    def test_get_service(self, client, temp_service_file):
        """测试获取特定服务"""
        # 先创建一个服务
        service_data = {
            "name": "test_service",
            "file_path": temp_service_file,
            "port": 8080
        }
        create_response = client.post("/api/services", json=service_data)
        service_id = create_response.json()["service"]["id"]
        
        # 获取服务信息
        response = client.get(f"/api/services/{service_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"]["id"] == service_id
        assert data["service"]["name"] == "test_service"
    
    def test_update_service(self, client, temp_service_file):
        """测试更新服务"""
        # 先创建一个服务
        service_data = {
            "name": "test_service",
            "file_path": temp_service_file,
            "port": 8080
        }
        create_response = client.post("/api/services", json=service_data)
        service_id = create_response.json()["service"]["id"]
        
        # 更新服务
        update_data = {
            "name": "updated_service",
            "port": 9000,
            "description": "更新后的服务"
        }
        response = client.put(f"/api/services/{service_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"]["name"] == "updated_service"
        assert data["service"]["port"] == 9000
    
    def test_delete_service(self, client, temp_service_file):
        """测试删除服务"""
        # 先创建一个服务
        service_data = {
            "name": "test_service",
            "file_path": temp_service_file,
            "port": 8080
        }
        create_response = client.post("/api/services", json=service_data)
        service_id = create_response.json()["service"]["id"]
        
        # 删除服务
        response = client.delete(f"/api/services/{service_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证服务已被删除
        get_response = client.get(f"/api/services/{service_id}")
        assert get_response.status_code == 404
    
    def test_service_not_found(self, client):
        """测试服务不存在的情况"""
        response = client.get("/api/services/non-existent-id")
        assert response.status_code == 404


class TestMCPGenerateAPI:
    """MCP生成器API测试"""
    
    def test_generate_mcp_server(self, client):
        """测试生成MCP服务器"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_path = f.name
        
        try:
            generate_data = {
                "output_path": output_path,
                "service_name": "test_mcp_service",
                "tool_name": "test_tool",
                "tool_description": "测试MCP工具",
                "author": "测试作者"
            }
            
            response = client.post("/api/generate", json=generate_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["output_path"] == output_path
            
            # 验证文件是否生成
            assert Path(output_path).exists()
            
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_generate_mcp_server_custom_params(self, client):
        """测试使用自定义参数生成MCP服务器"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_path = f.name
        
        try:
            generate_data = {
                "output_path": output_path,
                "service_name": "custom_service",
                "tool_name": "custom_tool",
                "tool_param_name": "user_id",
                "tool_param_type": "int",
                "tool_return_type": "dict",
                "tool_description": "自定义MCP工具",
                "service_port": 9000,
                "author": "自定义作者"
            }
            
            response = client.post("/api/generate", json=generate_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 验证生成的文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "custom_service" in content
                assert "custom_tool" in content
                assert "user_id: int" in content
                assert "-> dict" in content
                assert "9000" in content
                
        finally:
            Path(output_path).unlink(missing_ok=True)


class TestBatchOperationsAPI:
    """批量操作API测试"""
    
    def test_sync_service_status(self, client):
        """测试同步服务状态"""
        response = client.post("/api/services/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "同步完成" in data["message"]
