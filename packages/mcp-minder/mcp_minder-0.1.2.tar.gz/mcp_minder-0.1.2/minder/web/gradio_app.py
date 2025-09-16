"""
MCP Minder Gradio Web界面

提供友好的Web界面用于管理MCP服务
"""

import gradio as gr
import tempfile
import time
import json
import httpx
from pathlib import Path
from typing import List, Tuple, Optional
from minder import MCPGenerator


class APIClient:
    """API客户端，用于与MCP Minder API服务通信"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def get_services(self) -> dict:
        """获取服务列表"""
        response = self.client.get(f"{self.base_url}/api/services")
        return response.json()
    
    def create_service(self, service_data: dict) -> dict:
        """创建服务"""
        response = self.client.post(f"{self.base_url}/api/services", json=service_data)
        return response.json()
    
    def start_service(self, service_id: str, port: Optional[int] = None) -> dict:
        """启动服务"""
        data = {}
        if port is not None:
            data["port"] = port
        response = self.client.post(f"{self.base_url}/api/services/{service_id}/start", json=data)
        return response.json()
    
    def start_service_by_name(self, service_name: str, port: Optional[int] = None) -> dict:
        """根据名称启动服务"""
        data = {}
        if port is not None:
            data["port"] = port
        response = self.client.post(f"{self.base_url}/api/services/by-name/{service_name}/start", json=data)
        return response.json()
    
    def stop_service(self, service_id: str) -> dict:
        """停止服务"""
        response = self.client.post(f"{self.base_url}/api/services/{service_id}/stop")
        return response.json()
    
    def stop_service_by_name(self, service_name: str) -> dict:
        """根据名称停止服务"""
        response = self.client.post(f"{self.base_url}/api/services/by-name/{service_name}/stop")
        return response.json()
    
    def delete_service(self, service_id: str) -> dict:
        """删除服务"""
        response = self.client.delete(f"{self.base_url}/api/services/{service_id}")
        return response.json()
    
    def delete_service_by_name(self, service_name: str) -> dict:
        """根据名称删除服务"""
        response = self.client.delete(f"{self.base_url}/api/services/by-name/{service_name}")
        return response.json()
    
    def get_service_logs(self, service_id: str, lines: int = 50) -> dict:
        """获取服务日志"""
        response = self.client.get(f"{self.base_url}/api/services/{service_id}/logs?lines={lines}")
        return response.json()
    
    def get_service_logs_by_name(self, service_name: str, lines: int = 50) -> dict:
        """根据名称获取服务日志"""
        response = self.client.get(f"{self.base_url}/api/services/by-name/{service_name}/logs?lines={lines}")
        return response.json()
    
    def sync_services(self) -> dict:
        """同步服务"""
        response = self.client.post(f"{self.base_url}/api/services/sync")
        return response.json()
    
    def close(self):
        """关闭客户端"""
        self.client.close()


class MCPMinderWebApp:
    """MCP Minder Web应用"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.generator = MCPGenerator()
        self.api_client = APIClient(api_base_url)
        self.temp_files = []
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for file_path in self.temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception:
                pass
        self.temp_files.clear()
    
    def preview_mcp_server(
        self,
        service_name: str,
        tool_name: str,
        tool_param_name: str,
        tool_param_type: str,
        tool_return_type: str,
        tool_description: str,
        tool_code: str,
        service_port: Optional[int],
        author: str
    ) -> Tuple[str, str]:
        """预览MCP服务器代码"""
        try:
            # 直接生成代码内容，不创建文件
            content = self.generator.generate_content(
                service_name=service_name,
                tool_name=tool_name,
                tool_param_name=tool_param_name,
                tool_param_type=tool_param_type,
                tool_return_type=tool_return_type,
                tool_description=tool_description,
                tool_code=tool_code,
                service_port=service_port,
                author=author
            )
            
            if content:
                return "✅ MCP服务器代码预览生成成功！", content
            else:
                return "❌ MCP服务器代码预览生成失败！", ""
                
        except Exception as e:
            return f"❌ 预览过程中出现错误: {str(e)}", ""

    def save_mcp_server(
        self,
        service_name: str,
        tool_name: str,
        tool_param_name: str,
        tool_param_type: str,
        tool_return_type: str,
        tool_description: str,
        tool_code: str,
        service_port: Optional[int],
        author: str,
        filename: str
    ) -> str:
        """保存MCP服务器到mcpserver目录"""
        try:
            # 确保mcpserver目录存在
            import os
            os.makedirs("mcpserver", exist_ok=True)
            
            # 处理文件名
            if not filename.endswith('.py'):
                filename += '.py'
            
            output_path = f"mcpserver/{filename}"
            
            # 生成服务器
            success = self.generator.generate(
                output_path=output_path,
                service_name=service_name,
                tool_name=tool_name,
                tool_param_name=tool_param_name,
                tool_param_type=tool_param_type,
                tool_return_type=tool_return_type,
                tool_description=tool_description,
                tool_code=tool_code,
                service_port=service_port,
                author=author
            )
            
            if success:
                return f"✅ MCP服务器已保存到: {output_path}"
            else:
                return "❌ MCP服务器保存失败！"
                
        except Exception as e:
            return f"❌ 保存过程中出现错误: {str(e)}"
    
    def register_service(
        self,
        name: str,
        file_name: str,
        description: str,
        author: str
    ) -> str:
        """注册服务"""
        try:
            if not file_name:
                return "❌ 请选择MCP服务器文件"
            
            # 构建完整的文件路径
            file_path = f"mcpserver/{file_name}"
            
            if not Path(file_path).exists():
                return f"❌ 文件不存在: {file_path}"
            
            result = self.api_client.create_service({
                "name": name,
                "file_path": file_path,
                "host": "127.0.0.1",  # 使用默认主机地址
                "description": description,
                "author": author
            })
            
            if not result.get("success"):
                return f"❌ 创建服务失败: {result.get('error', '未知错误')}"
            
            service_id = result.get("service_id")
            
            return f"✅ 服务注册成功！\n服务名称: {name}\n服务ID: {service_id}\n文件路径: {file_path}"
            
        except Exception as e:
            return f"❌ 注册服务失败: {e}"
    
    def list_services(self) -> Tuple[str, List[List[str]], gr.Dropdown]:
        """列出所有服务"""
        try:
            result = self.api_client.get_services()
            
            if not result.get("success"):
                return f"❌ 获取服务列表失败: {result.get('error', '未知错误')}"
            
            services = result.get("services", [])
            
            if not services:
                return "📋 暂无服务", [], gr.Dropdown(choices=[], value=None)
            
            # 准备表格数据
            table_data = []
            service_choices = []
            for service in services:
                # 添加操作按钮列
                status = service.get('status', 'unknown')
                status_display = f"🟢 {status}" if status == "running" else f"🔴 {status}"
                table_data.append([
                    service.get('id', '')[:8] + "...",  # 显示前8位ID
                    service.get('name', ''),
                    status_display,
                    str(service.get('port', '')) if service.get('port') else "随机",
                    service.get('host', ''),
                    service.get('created_at', '')[:19],  # 只显示日期时间部分
                    service.get('description') or "无"
                ])
                service_choices.append(service.get('name', ''))
            
            return f"📋 共找到 {len(services)} 个服务", table_data, gr.Dropdown(choices=service_choices, value=None)
            
        except Exception as e:
            return f"❌ 获取服务列表失败: {e}", [], gr.Dropdown(choices=[], value=None)
    
    def sync_services(self) -> str:
        """同步mcpserver目录中的服务"""
        try:
            result = self.api_client.sync_services()
            if result.get("success"):
                return "✅ 服务同步完成！"
            else:
                return f"❌ 同步失败: {result.get('error', '未知错误')}"
        except Exception as e:
            return f"❌ 同步失败: {str(e)}"
    
    def get_mcpserver_files(self) -> List[str]:
        """获取mcpserver目录中的Python文件列表"""
        try:
            mcpserver_dir = Path("mcpserver")
            if not mcpserver_dir.exists():
                return []
            
            # 获取所有.py文件
            py_files = []
            for file_path in mcpserver_dir.glob("*.py"):
                py_files.append(file_path.name)
            
            return sorted(py_files)
        except Exception as e:
            print(f"获取mcpserver文件列表失败: {e}")
            return []
    
    def refresh_files_with_feedback(self) -> Tuple[List[str], str]:
        """刷新文件列表并提供反馈信息"""
        try:
            files = self.get_mcpserver_files()
            if files:
                feedback_html = f'<div style="color: #059669; font-size: 0.9em; margin-top: -10px;">✅ 成功刷新，找到 {len(files)} 个文件</div>'
                return files, feedback_html
            else:
                feedback_html = '<div style="color: #f59e0b; font-size: 0.9em; margin-top: -10px;">⚠️ 未找到任何.py文件，请检查mcpserver目录</div>'
                return files, feedback_html
        except Exception as e:
            feedback_html = f'<div style="color: #ef4444; font-size: 0.9em; margin-top: -10px;">❌ 刷新失败: {str(e)}</div>'
            return [], feedback_html
    
    def start_service(self, service_id: str) -> str:
        """启动服务"""
        try:
            result = self.api_client.start_service(service_id)
            
            if result.get('success'):
                return f"✅ {result.get('message', '服务启动成功')}"
            else:
                return f"❌ {result.get('error', '未知错误')}"
                
        except Exception as e:
            return f"❌ 启动服务失败: {e}"
    
    def stop_service(self, service_id: str) -> str:
        """停止服务"""
        try:
            result = self.api_client.stop_service(service_id)
            
            if result.get('success'):
                return f"✅ {result.get('message', '服务停止成功')}"
            else:
                return f"❌ {result.get('error', '未知错误')}"
                
        except Exception as e:
            return f"❌ 停止服务失败: {e}"
    
    def get_service_logs(self, service_id: str, lines: int = 50) -> str:
        """获取服务日志"""
        try:
            result = self.api_client.get_service_logs(service_id, lines)
            
            if result.get('success'):
                total_lines = result.get('total_lines', 0)
                returned_lines = result.get('returned_lines', 0)
                logs = result.get('logs', '无日志内容')
                return f"📄 日志 (共{total_lines}行，显示最近{returned_lines}行):\n\n{logs}"
            else:
                return f"❌ {result.get('error', '未知错误')}"
                
        except Exception as e:
            return f"❌ 获取日志失败: {e}"
    
    def delete_service(self, service_id: str) -> str:
        """删除服务"""
        try:
            result = self.api_client.delete_service(service_id)
            
            if result['success']:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['error']}"
                
        except Exception as e:
            return f"❌ 删除服务失败: {e}"
    
    def start_service_by_name(self, service_name: str, port: Optional[int] = None) -> str:
        """按名称启动服务"""
        try:
            result = self.api_client.start_service_by_name(service_name, port)
            
            if result.get('success'):
                return f"✅ {result.get('message', '服务启动成功')}"
            else:
                return f"❌ {result.get('error', '未知错误')}"
                
        except Exception as e:
            return f"❌ 启动服务失败: {e}"
    
    def stop_service_by_name(self, service_name: str) -> str:
        """按名称停止服务"""
        try:
            result = self.api_client.stop_service_by_name(service_name)
            
            if result['success']:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['error']}"
                
        except Exception as e:
            return f"❌ 停止服务失败: {e}"
    
    def restart_service_by_name(self, service_name: str) -> str:
        """按名称重启服务"""
        try:
            # 先停止服务
            stop_result = self.api_client.stop_service_by_name(service_name)
            if not stop_result['success']:
                return f"❌ 停止服务失败: {stop_result['error']}"
            
            # 等待一秒
            time.sleep(1)
            
            # 再启动服务
            start_result = self.api_client.start_service_by_name(service_name)
            if start_result['success']:
                return f"✅ 服务 {service_name} 重启成功"
            else:
                return f"❌ 启动服务失败: {start_result['error']}"
                
        except Exception as e:
            return f"❌ 重启服务失败: {e}"
    
    def delete_service_by_name(self, service_name: str) -> str:
        """按名称删除服务"""
        try:
            result = self.api_client.delete_service_by_name(service_name)
            
            if result['success']:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['error']}"
                
        except Exception as e:
            return f"❌ 删除服务失败: {e}"
    
    def get_service_logs_by_name(self, service_name: str, lines: int = 50) -> str:
        """按名称获取服务日志"""
        try:
            result = self.api_client.get_service_logs_by_name(service_name, lines)
            
            if result.get('success'):
                total_lines = result.get('total_lines', 0)
                returned_lines = result.get('returned_lines', 0)
                logs = result.get('logs', '无日志内容')
                return f"📄 日志 (共{total_lines}行，显示最近{returned_lines}行):\n\n{logs}"
            else:
                return f"❌ {result.get('error', '未知错误')}"
                
        except Exception as e:
            return f"❌ 获取日志失败: {e}"
    
    def get_service_info(self, service_id: str) -> str:
        """获取服务详细信息"""
        try:
            result = self.api_client.get_services()
            
            if not result.get("success"):
                return f"❌ 获取服务信息失败: {result.get('error', '未知错误')}"
            
            services = result.get("services", [])
            service_info = None
            
            for service in services:
                if service.get("id") == service_id:
                    service_info = service
                    break
            
            if not service_info:
                return "❌ 服务不存在"
            
            info = f"""
📋 服务详细信息:

🆔 ID: {service_info.get('id')}
📛 名称: {service_info.get('name')}
📁 文件路径: {service_info.get('file_path')}
🌐 主机: {service_info.get('host')}
🔌 端口: {service_info.get('port') or '随机'}
📊 状态: {service_info.get('status')}
👤 作者: {service_info.get('author') or '未设置'}
📝 描述: {service_info.get('description') or '无'}
🆔 进程ID: {service_info.get('pid') or '未运行'}
📄 日志文件: {service_info.get('log_file') or '无'}
📅 创建时间: {service_info.get('created_at')}
🔄 更新时间: {service_info.get('updated_at')}
"""
            return info
            
        except Exception as e:
            return f"❌ 获取服务信息失败: {e}"
    
    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        
        with gr.Blocks(
            title="MCP Generator - MCP服务器管理平台",
            theme=gr.themes.Soft(
                primary_hue="blue",
                secondary_hue="gray",
                neutral_hue="slate"
            ),
            css="""
            .gradio-container {
                max-width: 1400px !important;
                margin: 0 auto !important;
                width: 100% !important;
            }
            .gradio-container > div {
                width: 100% !important;
                max-width: 100% !important;
            }
            .main-header {
                text-align: center;
                padding: 20px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .main-header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .main-header p {
                margin: 10px 0 0 0;
                font-size: 1.1em;
                opacity: 0.9;
            }
            .tab-section {
                background: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                min-height: 600px;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box;
            }
            .tab-section > div {
                width: 100% !important;
                max-width: 100% !important;
            }
            .tab-content {
                width: 100%;
                max-width: 100%;
                display: flex;
                flex-direction: column;
            }
            .tab-main-row {
                width: 100%;
                max-width: 100%;
                display: flex;
                gap: 20px;
                box-sizing: border-box;
            }
            .tab-main-column {
                flex: 1 1 50% !important;
                min-width: 0;
                max-width: calc(50% - 10px) !important;
                width: calc(50% - 10px) !important;
                box-sizing: border-box;
            }
            .tab-main-column > div {
                width: 100% !important;
                max-width: 100% !important;
            }
            .tab-full-width {
                width: 100%;
                max-width: 100%;
                box-sizing: border-box;
            }
            .form-section {
                background: #f8fafc;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #3b82f6;
            }
            .form-section h3 {
                margin-top: 0;
                color: #1e40af;
                font-size: 1.2em;
                margin-bottom: 15px;
            }
            .button-group {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 15px;
                justify-content: center;
            }
            .button-group .btn {
                flex: 1;
                min-width: 140px;
                max-width: 200px;
                height: 40px;
                font-weight: 500;
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .button-group .btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .button-row {
                display: flex;
                gap: 12px;
                margin: 10px 0;
                justify-content: center;
            }
            .button-row .btn {
                flex: 1;
                min-width: 120px;
                height: 36px;
                font-weight: 500;
                border-radius: 6px;
            }
            .status-running { 
                color: #22c55e; 
                font-weight: bold; 
                background: #dcfce7;
                padding: 2px 8px;
                border-radius: 4px;
            }
            .status-stopped { 
                color: #ef4444; 
                font-weight: bold; 
                background: #fef2f2;
                padding: 2px 8px;
                border-radius: 4px;
            }
            .status-error { 
                color: #f59e0b; 
                font-weight: bold; 
                background: #fffbeb;
                padding: 2px 8px;
                border-radius: 4px;
            }
            .output-section {
                background: #f1f5f9;
                border-radius: 8px;
                padding: 20px;
                border: 1px solid #e2e8f0;
                margin-bottom: 15px;
            }
            .output-section h3 {
                margin-top: 0;
                color: #1e40af;
                font-size: 1.1em;
                margin-bottom: 15px;
            }
            .service-card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                border-left: 4px solid #3b82f6;
            }
            .uniform-column {
                width: 100%;
                max-width: 100%;
            }
            .form-row {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
            }
            .form-row .form-item {
                flex: 1;
            }
            .action-buttons {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
            }
            .action-buttons .btn {
                min-width: 120px;
                height: 40px;
                font-weight: 500;
                border-radius: 6px;
            }
            
            .refresh-btn {
                min-width: 40px !important;
                height: 40px !important;
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .refresh-btn:hover {
                background-color: #e3f2fd !important;
                transform: rotate(180deg) !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            }
            
            .register-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            }
            
            .register-btn:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
            }
            
            .refresh-files-btn {
                width: 100% !important;
                height: 48px !important;
                font-size: 18px !important;
                font-weight: 500 !important;
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
                background: #f8fafc !important;
                border: 1px solid #e2e8f0 !important;
                color: #475569 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .refresh-files-btn:hover {
                background: #e2e8f0 !important;
                border-color: #cbd5e1 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            }
            """
        ) as interface:
            
            # 页面头部
            with gr.Row(elem_classes="main-header"):
                gr.HTML("""
                <div class="main-header">
                    <h1>🚀 MCP Minder</h1>
                    <p>强大的MCP服务器管理平台 - 生成、部署、管理一体化</p>
                </div>
                """)
            
            with gr.Tabs():
                # 生成器标签页
                with gr.Tab("🔧 MCP服务器生成器", elem_classes="tab-section"):
                    with gr.Column(elem_classes="tab-content"):
                        with gr.Row(elem_classes="tab-main-row"):
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 基本信息配置
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>📋 基本信息配置</h3>")
                                    
                                    with gr.Row():
                                        service_name = gr.Textbox(
                                            label="服务名称",
                                            placeholder="my_service",
                                            value="my_service",
                                            scale=2
                                        )
                                        author = gr.Textbox(
                                            label="作者",
                                            placeholder="开发者",
                                            value="开发者",
                                            scale=1
                                        )
                                    
                                    filename_input = gr.Textbox(
                                        label="文件名 (不含.py扩展名)",
                                        placeholder="my_server",
                                        value="my_server"
                                    )
                                
                                # 工具配置
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>🛠️ 工具配置</h3>")
                                    
                                    with gr.Row():
                                        tool_name = gr.Textbox(
                                            label="工具函数名称",
                                            placeholder="my_tool",
                                            value="my_tool",
                                            scale=1
                                        )
                                        tool_param_name = gr.Textbox(
                                            label="工具参数名称",
                                            placeholder="input_data",
                                            value="input_data",
                                            scale=1
                                        )
                                    
                                    with gr.Row():
                                        tool_param_type = gr.Dropdown(
                                            label="工具参数类型",
                                            choices=["str", "int", "float", "bool", "dict", "list"],
                                            value="str",
                                            scale=1
                                        )
                                        tool_return_type = gr.Dropdown(
                                            label="工具返回类型",
                                            choices=["str", "int", "float", "bool", "dict", "list"],
                                            value="str",
                                            scale=1
                                        )
                                    
                                    tool_description = gr.Textbox(
                                        label="工具描述",
                                        placeholder="这是一个MCP工具",
                                        value="这是一个MCP工具",
                                        lines=2
                                    )
                                
                                # 代码配置
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>💻 代码配置</h3>")
                                    
                                    tool_code = gr.Code(
                                        label="工具函数代码块",
                                        language="python",
                                        value="# 实现您的业务逻辑\n    output = \"处理完成\"",
                                        lines=8
                                    )
                                    
                                    service_port = gr.Number(
                                        label="服务端口 (留空为随机端口)",
                                        value=None,
                                        precision=0
                                    )
                                
                                # 操作按钮
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>⚡ 操作</h3>")
                                    
                                    with gr.Row(elem_classes="button-group"):
                                        preview_btn = gr.Button(
                                            "👁️ 预览代码", 
                                            variant="secondary",
                                            elem_classes="btn"
                                        )
                                        save_btn = gr.Button(
                                            "💾 保存到mcpserver", 
                                            variant="primary",
                                            elem_classes="btn"
                                        )
                        
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 操作结果
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>📊 操作结果</h3>")
                                    generate_output = gr.Textbox(
                                        label="状态信息",
                                        lines=3,
                                        interactive=False
                                    )
                                
                                # 代码预览
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>👀 代码预览</h3>")
                                    generated_code = gr.Code(
                                        label="MCP服务器代码",
                                        language="python",
                                        lines=25,
                                        interactive=False
                                    )
                
                # 服务管理标签页
                with gr.Tab("📋 服务管理", elem_classes="tab-section"):
                    with gr.Column(elem_classes="tab-content"):
                        with gr.Row(elem_classes="tab-main-row"):
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 服务注册
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>📝 注册新服务</h3>")
                                    
                                    # 基本信息
                                    reg_name = gr.Textbox(
                                        label="服务名称", 
                                        placeholder="my_service",
                                        info="为您的服务起一个唯一的名称"
                                    )
                                    
                                    # 文件选择区域
                                    with gr.Row():
                                        with gr.Column(scale=4):
                                            reg_file_dropdown = gr.Dropdown(
                                                label="选择MCP服务器文件",
                                                choices=self.get_mcpserver_files(),
                                                value=None,
                                                interactive=True,
                                                allow_custom_value=False,
                                                info="从mcpserver目录中选择要注册的Python文件"
                                            )
                                        with gr.Column(scale=4):
                                            refresh_files_btn = gr.Button(
                                                "📁",
                                                size="lg",
                                                variant="secondary",
                                                elem_classes="refresh-files-btn"
                                            )
                                    
                                    # 刷新状态提示
                                    refresh_feedback = gr.HTML(
                                        value=f'<div style="color: #059669; font-size: 0.9em; margin-top: -10px;">✅ 已加载 {len(self.get_mcpserver_files())} 个文件</div>',
                                        visible=True
                                    )
                                    
                                    # 描述和作者信息
                                    with gr.Row():
                                        reg_description = gr.Textbox(
                                            label="服务描述", 
                                            placeholder="描述这个服务的功能...",
                                            lines=2,
                                            scale=1
                                        )
                                        reg_author = gr.Textbox(
                                            label="作者", 
                                            placeholder="开发者姓名",
                                            scale=1
                                        )
                                    
                                    # 注册按钮
                                    register_btn = gr.Button(
                                        "📝 注册服务", 
                                        variant="primary",
                                        size="lg",
                                        elem_classes="register-btn"
                                    )
                                    
                                    # 注册结果
                                    register_output = gr.Textbox(
                                        label="注册结果", 
                                        lines=3, 
                                        interactive=False,
                                        visible=True
                                    )
                        
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 服务操作
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>⚙️ 服务操作 (按ID)</h3>")
                                    
                                    service_id = gr.Textbox(
                                        label="服务ID", 
                                        placeholder="输入服务ID"
                                    )
                                    
                                    with gr.Row(elem_classes="button-row"):
                                        start_btn = gr.Button(
                                            "▶️ 启动", 
                                            variant="primary",
                                            elem_classes="btn"
                                        )
                                        stop_btn = gr.Button(
                                            "⏹️ 停止", 
                                            variant="stop",
                                            elem_classes="btn"
                                        )
                                        delete_btn = gr.Button(
                                            "🗑️ 删除", 
                                            variant="stop",
                                            elem_classes="btn"
                                        )
                                    
                                    with gr.Row(elem_classes="button-row"):
                                        info_btn = gr.Button(
                                            "ℹ️ 详细信息",
                                            elem_classes="btn"
                                        )
                                        logs_btn = gr.Button(
                                            "📄 查看日志",
                                            elem_classes="btn"
                                        )
                                    
                                    logs_lines = gr.Number(
                                        label="日志行数", 
                                        value=50, 
                                        precision=0
                                    )
                                    
                                    operation_output = gr.Textbox(
                                        label="操作结果", 
                                        lines=3, 
                                        interactive=False
                                    )
                        
                        # 服务信息显示区域
                        with gr.Row(elem_classes="tab-main-row"):
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>📋 服务详细信息</h3>")
                                    service_info_output = gr.Textbox(
                                        label="服务信息", 
                                        lines=8, 
                                        interactive=False
                                    )
                            
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>📄 服务日志</h3>")
                                    logs_output = gr.Textbox(
                                        label="服务日志", 
                                        lines=12, 
                                        interactive=False
                                    )
                
                # 服务列表标签页
                with gr.Tab("📊 服务列表", elem_classes="tab-section"):
                    with gr.Column(elem_classes="tab-content"):
                        with gr.Row(elem_classes="tab-main-row"):
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 顶部操作区域
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>🔄 服务管理操作</h3>")
                                    
                                    with gr.Row(elem_classes="action-buttons"):
                                        refresh_btn = gr.Button(
                                            "🔄 刷新列表", 
                                            variant="primary",
                                            elem_classes="btn"
                                        )
                                        sync_btn = gr.Button(
                                            "🔄 同步mcpserver目录", 
                                            variant="secondary",
                                            elem_classes="btn"
                                        )
                                    
                                    services_output = gr.Textbox(
                                        label="服务概览", 
                                        lines=2, 
                                        interactive=False
                                    )
                                
                                # 服务操作区域
                                with gr.Group(elem_classes="form-section"):
                                    gr.HTML("<h3>⚡ 快速操作 (按名称)</h3>")
                                    
                                    selected_service_dropdown = gr.Dropdown(
                                        label="选择服务",
                                        choices=[],
                                        value=None,
                                        interactive=True,
                                        allow_custom_value=True
                                    )
                                    
                                    start_port = gr.Number(
                                        label="启动端口 (留空为随机端口)",
                                        value=None,
                                        precision=0,
                                        interactive=True
                                    )
                                    
                                    with gr.Row(elem_classes="button-row"):
                                        start_by_name_btn = gr.Button(
                                            "▶️ 启动服务", 
                                            variant="primary",
                                            elem_classes="btn"
                                        )
                                        stop_by_name_btn = gr.Button(
                                            "⏹️ 停止服务", 
                                            variant="stop",
                                            elem_classes="btn"
                                        )
                                        restart_by_name_btn = gr.Button(
                                            "🔄 重启服务", 
                                            variant="secondary",
                                            elem_classes="btn"
                                        )
                                    
                                    with gr.Row(elem_classes="button-row"):
                                        logs_by_name_btn = gr.Button(
                                            "📄 查看日志",
                                            elem_classes="btn"
                                        )
                                        delete_by_name_btn = gr.Button(
                                            "🗑️ 删除服务", 
                                            variant="stop",
                                            elem_classes="btn"
                                        )
                                    
                                    logs_lines_by_name = gr.Number(
                                        label="日志行数", 
                                        value=50, 
                                        precision=0
                                    )
                            
                            with gr.Column(scale=1, elem_classes="tab-main-column"):
                                # 服务列表表格
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>📋 服务列表</h3>")
                                    services_table = gr.Dataframe(
                                        headers=["ID", "名称", "状态", "端口", "主机", "创建时间", "描述"],
                                        datatype=["str", "str", "str", "str", "str", "str", "str"],
                                        interactive=False,
                                        label="所有服务"
                                    )
                                
                                # 操作结果
                                with gr.Group(elem_classes="output-section"):
                                    gr.HTML("<h3>📊 操作结果</h3>")
                                    service_operation_output = gr.Textbox(
                                        label="操作状态",
                                        lines=8,
                                        interactive=False
                                    )
            
            # 事件绑定
            preview_btn.click(
                fn=self.preview_mcp_server,
                inputs=[
                    service_name, tool_name, tool_param_name, tool_param_type,
                    tool_return_type, tool_description, tool_code, service_port, author
                ],
                outputs=[generate_output, generated_code]
            )
            
            save_btn.click(
                fn=self.save_mcp_server,
                inputs=[
                    service_name, tool_name, tool_param_name, tool_param_type,
                    tool_return_type, tool_description, tool_code, service_port, author, filename_input
                ],
                outputs=[generate_output]
            )
            
            register_btn.click(
                fn=self.register_service,
                inputs=[reg_name, reg_file_dropdown, reg_description, reg_author],
                outputs=[register_output]
            )
            
            refresh_files_btn.click(
                fn=self.refresh_files_with_feedback,
                outputs=[reg_file_dropdown, refresh_feedback]
            )
            
            start_btn.click(
                fn=self.start_service,
                inputs=[service_id],
                outputs=[operation_output]
            )
            
            stop_btn.click(
                fn=self.stop_service,
                inputs=[service_id],
                outputs=[operation_output]
            )
            
            delete_btn.click(
                fn=self.delete_service,
                inputs=[service_id],
                outputs=[operation_output]
            )
            
            info_btn.click(
                fn=self.get_service_info,
                inputs=[service_id],
                outputs=[service_info_output]
            )
            
            logs_btn.click(
                fn=self.get_service_logs,
                inputs=[service_id, logs_lines],
                outputs=[logs_output]
            )
            
            refresh_btn.click(
                fn=self.list_services,
                outputs=[services_output, services_table, selected_service_dropdown]
            )
            
            sync_btn.click(
                fn=self.sync_services,
                outputs=[services_output]
            )
            
            # 按名称操作服务的事件绑定
            start_by_name_btn.click(
                fn=self.start_service_by_name,
                inputs=[selected_service_dropdown, start_port],
                outputs=[service_operation_output]
            )
            
            stop_by_name_btn.click(
                fn=self.stop_service_by_name,
                inputs=[selected_service_dropdown],
                outputs=[service_operation_output]
            )
            
            restart_by_name_btn.click(
                fn=self.restart_service_by_name,
                inputs=[selected_service_dropdown],
                outputs=[service_operation_output]
            )
            
            logs_by_name_btn.click(
                fn=self.get_service_logs_by_name,
                inputs=[selected_service_dropdown, logs_lines_by_name],
                outputs=[service_operation_output]
            )
            
            delete_by_name_btn.click(
                fn=self.delete_service_by_name,
                inputs=[selected_service_dropdown],
                outputs=[service_operation_output]
            )
            
            # 页面加载时自动刷新服务列表
            interface.load(
                fn=self.list_services,
                outputs=[services_output, services_table, selected_service_dropdown]
            )
        
        return interface
    
    def launch(self, **kwargs):
        """启动Gradio应用"""
        interface = self.create_interface()
        
        # 设置默认参数
        default_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": False,
            "show_error": True
        }
        default_kwargs.update(kwargs)
        
        print("🚀 启动MCP Minder Web界面...")
        print(f"📍 访问地址: http://localhost:{default_kwargs['server_port']}")
        
        try:
            interface.launch(**default_kwargs)
        except KeyboardInterrupt:
            print("\n👋 Web界面已关闭")
        finally:
            self.cleanup_temp_files()


def main():
    """主函数"""
    app = MCPMinderWebApp()
    app.launch()


if __name__ == "__main__":
    main()
