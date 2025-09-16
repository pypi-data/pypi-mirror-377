"""
MCP服务启动器

用于启动模板生成的Python MCP服务器文件
"""

import os
import asyncio
import logging
import subprocess
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class MCPLauncher:
    """MCP服务启动器类"""
    
    def __init__(self, log_dir: str = "service_logs"):
        """
        初始化启动器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = Path(log_dir)
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start_service(
        self,
        script_path: str,
        use_uv: bool = True,
        host: str = "0.0.0.0",
        port: Optional[int] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        启动MCP服务
        
        Args:
            script_path: Python脚本路径
            use_uv: 是否使用uv运行
            host: 主机地址
            port: 端口号
            background: 是否在后台运行
            
        Returns:
            启动结果信息
        """
        script_path = Path(script_path).resolve()
        
        # 验证脚本是否存在
        if not script_path.exists():
            error_msg = f"错误: 脚本未在 {script_path} 找到"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        
        # 确保日志目录存在
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            error_msg = f"错误: 无法创建日志目录 {self.log_dir}: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        
        # 构建命令
        if use_uv:
            command = ["uv", "run", str(script_path)]
        else:
            command = [sys.executable, str(script_path)]
        
        # 添加端口参数
        if port:
            command.extend(["--port", str(port)])
        
        # 添加主机参数
        if host != "0.0.0.0":
            command.extend(["--host", host])
        
        # 设置日志文件路径
        log_file_path = self.log_dir / f"{script_path.stem}.log"
        
        try:
            self.logger.info(f"启动服务: {' '.join(command)}")
            self.logger.info(f"日志文件: {log_file_path}")
            
            if background:
                # 后台运行
                with open(log_file_path, 'ab') as log_file:
                    process = subprocess.Popen(
                        command,
                        stdout=log_file,
                        stderr=log_file,
                        cwd=script_path.parent,
                        start_new_session=True  # 创建新的进程组
                    )
                
                # 记录运行中的进程
                self.running_processes[str(script_path)] = process
                
                return {
                    'success': True,
                    'pid': process.pid,
                    'port': port,
                    'log_file': str(log_file_path),
                    'command': ' '.join(command),
                    'background': True
                }
            else:
                # 前台运行
                process = subprocess.run(
                    command,
                    cwd=script_path.parent
                )
                
                return {
                    'success': process.returncode == 0,
                    'return_code': process.returncode,
                    'command': ' '.join(command),
                    'background': False
                }
                
        except FileNotFoundError as e:
            error_msg = f"错误: 命令未找到 - {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"启动服务时发生错误: {e}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg
            }
    
    def stop_service(self, script_path: str) -> Dict[str, Any]:
        """
        停止MCP服务
        
        Args:
            script_path: Python脚本路径
            
        Returns:
            停止结果信息
        """
        # 确保路径格式与存储时一致
        script_path = str(Path(script_path).resolve())
        
        # 首先尝试通过脚本路径查找
        if script_path in self.running_processes:
            process = self.running_processes[script_path]
        else:
            # 如果通过路径找不到，尝试通过进程ID查找
            # 这里我们需要从服务管理器获取PID
            return {
                'success': False,
                'error': f'服务 {script_path} 未在运行'
            }
    
    def stop_service_by_pid(self, pid: int) -> Dict[str, Any]:
        """
        通过进程ID停止MCP服务
        
        Args:
            pid: 进程ID
            
        Returns:
            停止结果信息
        """
        # 查找对应的进程
        target_process = None
        target_script_path = None
        
        for script_path, process in self.running_processes.items():
            if process.pid == pid:
                target_process = process
                target_script_path = script_path
                break
        
        if target_process is None:
            return {
                'success': False,
                'error': f'进程 {pid} 未在运行'
            }
        
        try:
            # 尝试优雅关闭
            target_process.terminate()
            
            # 等待进程结束
            try:
                target_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果进程没有在5秒内结束，强制杀死
                self.logger.warning(f"进程 {pid} 未在超时时间内结束，强制终止")
                target_process.kill()
                target_process.wait()
            
            # 从运行列表中移除
            del self.running_processes[target_script_path]
            
            self.logger.info(f"服务已停止: {target_script_path} (PID: {pid})")
            
            return {
                'success': True,
                'pid': pid,
                'message': f'服务 {target_script_path} 已停止'
            }
            
        except Exception as e:
            error_msg = f"停止服务时发生错误: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def list_running_services(self) -> Dict[str, Any]:
        """
        列出所有运行中的服务
        
        Returns:
            运行中的服务列表
        """
        services = []
        for script_path, process in self.running_processes.items():
            try:
                # 检查进程是否还在运行
                if process.poll() is None:
                    services.append({
                        'script_path': script_path,
                        'pid': process.pid,
                        'status': 'running'
                    })
                else:
                    # 进程已结束，从列表中移除
                    del self.running_processes[script_path]
            except Exception:
                # 进程可能已经结束，从列表中移除
                del self.running_processes[script_path]
        
        return {
            'success': True,
            'services': services,
            'count': len(services)
        }
    
    def stop_all_services(self) -> Dict[str, Any]:
        """
        停止所有运行中的服务
        
        Returns:
            停止结果信息
        """
        stopped_services = []
        failed_services = []
        
        for script_path in list(self.running_processes.keys()):
            result = self.stop_service(script_path)
            if result['success']:
                stopped_services.append(script_path)
            else:
                failed_services.append({
                    'script_path': script_path,
                    'error': result['error']
                })
        
        return {
            'success': len(failed_services) == 0,
            'stopped_services': stopped_services,
            'failed_services': failed_services,
            'total_stopped': len(stopped_services)
        }
    
    def get_service_logs(self, script_path: str, lines: int = 50) -> Dict[str, Any]:
        """
        获取服务日志
        
        Args:
            script_path: Python脚本路径
            lines: 返回的日志行数
            
        Returns:
            日志内容
        """
        script_path = Path(script_path).resolve()
        log_file_path = self.log_dir / f"{script_path.stem}.log"
        
        if not log_file_path.exists():
            return {
                'success': False,
                'error': f'日志文件不存在: {log_file_path}'
            }
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
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
