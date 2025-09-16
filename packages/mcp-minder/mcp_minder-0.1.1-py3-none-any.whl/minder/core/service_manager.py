"""
MCP服务管理器

负责管理MCP服务的生命周期，包括服务的注册、启动、停止和状态维护
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from minder.core.launcher import MCPLauncher


@dataclass
class ServiceInfo:
    """服务信息数据类"""
    id: str
    name: str
    file_path: str
    port: Optional[int]
    host: str
    status: str  # running, stopped, error
    created_at: str
    updated_at: str
    pid: Optional[int] = None
    log_file: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class ServiceManager:
    """MCP服务管理器"""
    
    def __init__(self, data_file: str = "services.json", log_dir: str = "service_logs", mcpserver_dir: str = "mcpserver"):
        """
        初始化服务管理器
        
        Args:
            data_file: 服务数据存储文件路径
            log_dir: 日志目录
            mcpserver_dir: MCP服务器文件目录
        """
        self.data_file = Path(data_file)
        self.log_dir = Path(log_dir)
        self.mcpserver_dir = Path(mcpserver_dir)
        self.launcher = MCPLauncher(str(log_dir))
        self.services: Dict[str, ServiceInfo] = {}
        
        # 确保目录存在
        self.mcpserver_dir.mkdir(exist_ok=True)
        
        self._load_services()
        self._sync_with_mcpserver_dir()
    
    def _load_services(self) -> None:
        """从JSON文件加载服务数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for service_id, service_data in data.items():
                        self.services[service_id] = ServiceInfo(**service_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"警告: 加载服务数据失败: {e}")
                self.services = {}
        else:
            self.services = {}
    
    def _sync_with_mcpserver_dir(self) -> None:
        """与mcpserver目录同步服务信息"""
        try:
            # 扫描mcpserver目录中的Python文件
            mcp_files = list(self.mcpserver_dir.glob("*.py"))
            
            # 获取已存在的服务文件路径集合（用于快速查找）
            existing_file_paths = {
                service_info.file_path 
                for service_info in self.services.values()
            }
            
            # 收集需要添加的服务
            services_to_add = []
            for file_path in mcp_files:
                service_name = file_path.stem
                file_path_str = str(file_path)
                
                # 检查是否已存在指向相同文件的服务（使用集合进行快速查找）
                if file_path_str not in existing_file_paths:
                    services_to_add.append((service_name, file_path_str))
                    print(f"🔄 发现新的MCP服务文件: {file_path_str}")
                else:
                    print(f"ℹ️ 跳过已存在的服务文件: {file_path_str}")
            
            # 添加新服务
            for service_name, file_path_str in services_to_add:
                self.register_service(
                    name=service_name,
                    file_path=file_path_str,
                    host="127.0.0.1",
                    description=f"从mcpserver目录自动发现的MCP服务: {service_name}",
                    author="系统自动发现"
                )
            
            # 检查services.json中是否有不存在的文件
            services_to_remove = []
            for service_id, service_info in self.services.items():
                if not Path(service_info.file_path).exists():
                    print(f"⚠️ 服务文件不存在: {service_info.file_path}")
                    services_to_remove.append(service_id)
            
            # 移除不存在的服务
            for service_id in services_to_remove:
                print(f"🗑️ 移除不存在的服务: {service_id}")
                del self.services[service_id]
            
            # 同步服务状态 - 检查实际运行的服务
            self._sync_service_status()
            
            if services_to_remove:
                self._save_services()
                
        except Exception as e:
            print(f"❌ 同步mcpserver目录失败: {e}")
    
    def _sync_service_status(self) -> None:
        """同步服务状态 - 检查实际运行的服务"""
        try:
            # 获取所有运行中的Python进程
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            running_processes = result.stdout.split('\n')
            
            # 检查每个服务是否实际在运行
            for service_id, service_info in self.services.items():
                if service_info.status == "running" and service_info.pid:
                    # 检查进程是否还在运行
                    pid_running = False
                    for line in running_processes:
                        if f" {service_info.pid} " in line and "python" in line:
                            pid_running = True
                            break
                    
                    if not pid_running:
                        print(f"🔄 更新服务状态: {service_info.name} (PID {service_info.pid} 已停止)")
                        service_info.status = "stopped"
                        service_info.pid = None
                        self._update_service_timestamp(service_id)
                elif service_info.status == "stopped":
                    # 检查是否有新的进程在运行这个服务文件
                    for line in running_processes:
                        if service_info.file_path in line and "python" in line:
                            # 提取PID
                            parts = line.split()
                            if len(parts) > 1:
                                try:
                                    pid = int(parts[1])
                                    print(f"🔄 发现运行中的服务: {service_info.name} (PID {pid})")
                                    service_info.status = "running"
                                    service_info.pid = pid
                                    # 尝试从进程信息中提取端口
                                    if "port" in line:
                                        # 这里可以添加更复杂的端口提取逻辑
                                        pass
                                    self._update_service_timestamp(service_id)
                                    break
                                except (ValueError, IndexError):
                                    continue
        except Exception as e:
            print(f"⚠️ 同步服务状态失败: {e}")
    
    def sync_services(self) -> None:
        """手动同步服务（公开方法）"""
        print("🔄 开始同步mcpserver目录...")
        self._sync_with_mcpserver_dir()
        print("✅ 同步完成")
    
    def _save_services(self) -> None:
        """保存服务数据到JSON文件"""
        try:
            # 确保目录存在
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为可序列化的字典
            data = {
                service_id: asdict(service_info)
                for service_id, service_info in self.services.items()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"错误: 保存服务数据失败: {e}")
    
    def _update_service_timestamp(self, service_id: str) -> None:
        """更新服务时间戳"""
        if service_id in self.services:
            self.services[service_id].updated_at = datetime.now().isoformat()
            self._save_services()
    
    def register_service(
        self,
        name: str,
        file_path: str,
        host: str = "0.0.0.0",
        description: Optional[str] = None,
        author: Optional[str] = None
    ) -> str:
        """
        注册新服务
        
        Args:
            name: 服务名称
            file_path: 服务文件路径
            host: 服务主机
            description: 服务描述
            author: 作者
            
        Returns:
            服务ID
        """
        service_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        service_info = ServiceInfo(
            id=service_id,
            name=name,
            file_path=file_path,
            port=None,  # 端口在启动时动态指定
            host=host,
            status="stopped",
            created_at=now,
            updated_at=now,
            description=description,
            author=author
        )
        
        self.services[service_id] = service_info
        self._save_services()
        
        return service_id
    
    def start_service(self, service_id: str, port: Optional[int] = None) -> Dict[str, Any]:
        """
        启动服务
        
        Args:
            service_id: 服务ID
            port: 服务端口（可选，如果不指定则使用随机端口）
            
        Returns:
            启动结果
        """
        if service_id not in self.services:
            return {
                'success': False,
                'error': f'服务 {service_id} 不存在'
            }
        
        service_info = self.services[service_id]
        
        # 检查服务文件是否存在
        if not Path(service_info.file_path).exists():
            return {
                'success': False,
                'error': f'服务文件不存在: {service_info.file_path}'
            }
        
        # 启动服务，使用指定的端口或服务配置的端口
        start_port = port if port is not None else service_info.port
        
        result = self.launcher.start_service(
            script_path=service_info.file_path,
            use_uv=True,
            host=service_info.host,
            port=start_port,
            background=True
        )
        
        if result['success']:
            # 更新服务状态
            service_info.status = "running"
            service_info.pid = result.get('pid')
            service_info.log_file = result.get('log_file')
            # 更新端口信息
            if start_port is not None:
                service_info.port = start_port
            elif result.get('port') is not None:
                service_info.port = result.get('port')
            self._update_service_timestamp(service_id)
            
            return {
                'success': True,
                'service_id': service_id,
                'pid': result['pid'],
                'message': f'服务 {service_info.name} 启动成功'
            }
        else:
            service_info.status = "error"
            self._update_service_timestamp(service_id)
            
            return {
                'success': False,
                'error': result['error']
            }
    
    def start_service_by_name(self, name: str, port: Optional[int] = None) -> Dict[str, Any]:
        """
        根据服务名称启动服务
        
        Args:
            name: 服务名称
            port: 服务端口（可选，如果不指定则使用随机端口）
            
        Returns:
            启动结果
        """
        service_id = self.get_service_id_by_name(name)
        if not service_id:
            return {
                'success': False,
                'error': f'服务 {name} 不存在'
            }
        
        return self.start_service(service_id, port)
    
    def stop_service(self, service_id: str) -> Dict[str, Any]:
        """
        停止服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            停止结果
        """
        if service_id not in self.services:
            return {
                'success': False,
                'error': f'服务 {service_id} 不存在'
            }
        
        service_info = self.services[service_id]
        
        # 停止服务 - 使用系统命令直接停止进程
        if service_info.pid:
            try:
                import os
                import signal
                # 尝试优雅停止
                os.kill(service_info.pid, signal.SIGTERM)
                
                # 等待进程结束
                import time
                for _ in range(10):  # 等待最多5秒
                    try:
                        os.kill(service_info.pid, 0)  # 检查进程是否存在
                        time.sleep(0.5)
                    except ProcessLookupError:
                        # 进程已结束
                        break
                else:
                    # 如果进程还在运行，强制杀死
                    os.kill(service_info.pid, signal.SIGKILL)
                
                result = {
                    'success': True,
                    'pid': service_info.pid,
                    'message': f'服务 {service_info.name} 已停止'
                }
            except ProcessLookupError:
                # 进程已经不存在
                result = {
                    'success': True,
                    'pid': service_info.pid,
                    'message': f'服务 {service_info.name} 已停止'
                }
            except Exception as e:
                result = {
                    'success': False,
                    'error': f'停止服务时发生错误: {e}'
                }
        else:
            # 如果没有PID，使用启动器
            result = self.launcher.stop_service(service_info.file_path)
        
        if result['success']:
            # 更新服务状态
            service_info.status = "stopped"
            service_info.pid = None
            self._update_service_timestamp(service_id)
            
            return {
                'success': True,
                'service_id': service_id,
                'message': f'服务 {service_info.name} 停止成功'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def stop_service_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据服务名称停止服务
        
        Args:
            name: 服务名称
            
        Returns:
            停止结果
        """
        service_id = self.get_service_id_by_name(name)
        if not service_id:
            return {
                'success': False,
                'error': f'服务 {name} 不存在'
            }
        
        return self.stop_service(service_id)
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """
        获取服务信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            服务信息
        """
        return self.services.get(service_id)
    
    def get_service_by_name(self, name: str) -> Optional[ServiceInfo]:
        """
        根据服务名称获取服务信息
        
        Args:
            name: 服务名称
            
        Returns:
            服务信息
        """
        for service_info in self.services.values():
            if service_info.name == name:
                return service_info
        return None
    
    def get_service_id_by_name(self, name: str) -> Optional[str]:
        """
        根据服务名称获取服务ID
        
        Args:
            name: 服务名称
            
        Returns:
            服务ID
        """
        for service_id, service_info in self.services.items():
            if service_info.name == name:
                return service_id
        return None
    
    def list_services(self, status_filter: Optional[str] = None) -> List[ServiceInfo]:
        """
        列出所有服务
        
        Args:
            status_filter: 状态过滤器 (running, stopped, error)
            
        Returns:
            服务列表
        """
        services = list(self.services.values())
        
        if status_filter:
            services = [s for s in services if s.status == status_filter]
        
        return sorted(services, key=lambda x: x.created_at, reverse=True)
    
    def delete_service(self, service_id: str) -> Dict[str, Any]:
        """
        删除服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            删除结果
        """
        if service_id not in self.services:
            return {
                'success': False,
                'error': f'服务 {service_id} 不存在'
            }
        
        service_info = self.services[service_id]
        
        # 如果服务正在运行，先停止
        if service_info.status == "running":
            stop_result = self.stop_service(service_id)
            if not stop_result['success']:
                return {
                    'success': False,
                    'error': f'无法停止运行中的服务: {stop_result["error"]}'
                }
        
        # 删除服务
        del self.services[service_id]
        self._save_services()
        
        return {
            'success': True,
            'message': f'服务 {service_info.name} 删除成功'
        }
    
    def delete_service_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据服务名称删除服务
        
        Args:
            name: 服务名称
            
        Returns:
            删除结果
        """
        service_id = self.get_service_id_by_name(name)
        if not service_id:
            return {
                'success': False,
                'error': f'服务 {name} 不存在'
            }
        
        return self.delete_service(service_id)
    
    def update_service(
        self,
        service_id: str,
        name: Optional[str] = None,
        port: Optional[int] = None,
        host: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新服务信息
        
        Args:
            service_id: 服务ID
            name: 服务名称
            port: 服务端口
            host: 服务主机
            description: 服务描述
            
        Returns:
            更新结果
        """
        if service_id not in self.services:
            return {
                'success': False,
                'error': f'服务 {service_id} 不存在'
            }
        
        service_info = self.services[service_id]
        
        # 更新字段
        if name is not None:
            service_info.name = name
        if port is not None:
            service_info.port = port
        if host is not None:
            service_info.host = host
        if description is not None:
            service_info.description = description
        
        self._update_service_timestamp(service_id)
        
        return {
            'success': True,
            'message': f'服务 {service_info.name} 更新成功'
        }
    
    def get_service_logs(self, service_id: str, lines: int = 50) -> Dict[str, Any]:
        """
        获取服务日志
        
        Args:
            service_id: 服务ID
            lines: 日志行数
            
        Returns:
            日志内容
        """
        if service_id not in self.services:
            return {
                'success': False,
                'error': f'服务 {service_id} 不存在'
            }
        
        service_info = self.services[service_id]
        
        if not service_info.log_file or not Path(service_info.log_file).exists():
            return {
                'success': False,
                'error': '日志文件不存在'
            }
        
        try:
            with open(service_info.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            return {
                'success': True,
                'logs': ''.join(recent_lines),
                'total_lines': len(all_lines),
                'returned_lines': len(recent_lines)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'读取日志文件失败: {e}'
            }
    
    def get_service_logs_by_name(self, name: str, lines: int = 50) -> Dict[str, Any]:
        """
        根据服务名称获取服务日志
        
        Args:
            name: 服务名称
            lines: 日志行数
            
        Returns:
            日志内容
        """
        service_id = self.get_service_id_by_name(name)
        if not service_id:
            return {
                'success': False,
                'error': f'服务 {name} 不存在'
            }
        
        return self.get_service_logs(service_id, lines)
    
    def sync_service_status(self) -> None:
        """同步服务状态（检查运行中的服务是否还在运行）"""
        for service_id, service_info in self.services.items():
            if service_info.status == "running" and service_info.pid:
                try:
                    # 检查进程是否还在运行
                    import psutil
                    if not psutil.pid_exists(service_info.pid):
                        service_info.status = "stopped"
                        service_info.pid = None
                        self._update_service_timestamp(service_id)
                except ImportError:
                    # 如果没有psutil，跳过检查
                    pass
