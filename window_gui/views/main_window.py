"""
主窗口视图
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

from views.control_panel import ControlPanel
from views.canvas_view import CanvasView
from utils.logging_utils import LogWidget

class MainWindow:
    """主窗口"""
    
    def __init__(self, root, simulation_thread, event_queue):
        """
        初始化主窗口
        
        Args:
            root: tkinter根窗口
            simulation_thread: 模拟线程
            event_queue: 事件队列
        """
        self.root = root
        self.sim_thread = simulation_thread
        self.event_queue = event_queue
        self.simulation_running = False
        
        # 创建界面
        self._create_interface()
        
        # 启动事件处理循环
        self._process_events()
    
    def _create_interface(self):
        """创建界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 右侧显示区域
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建控制面板
        self.control_panel = ControlPanel(control_frame, self)
        
        # 创建画布视图
        self.canvas_view = CanvasView(display_frame, self.sim_thread)
        
        # 创建日志区域
        self._create_log_area(display_frame)
        
        # 创建状态栏
        self._create_status_bar(display_frame)
    
    def _create_log_area(self, parent):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(parent, text="模拟信息", padding=5)
        log_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.log_widget = LogWidget(log_frame, height=8)
        self.log_widget.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # 细胞数量
        self.cell_count_var = tk.StringVar(value="细胞数量: 0")
        ttk.Label(self.status_frame, textvariable=self.cell_count_var).pack(side=tk.RIGHT)
        
        # FPS显示
        self.fps_var = tk.StringVar(value="FPS: 0")
        ttk.Label(self.status_frame, textvariable=self.fps_var).pack(side=tk.RIGHT, padx=(0, 20))
    
    def _process_events(self):
        """处理事件队列中的事件"""
        try:
            while True:
                try:
                    event = self.event_queue.get_nowait()
                    self._handle_event(event)
                except:
                    break
        finally:
            # 定期检查事件
            self.root.after(100, self._process_events)
    
    def _handle_event(self, event):
        """处理事件"""
        event_type = event.get('type')
        
        if event_type == 'simulation_info':
            info = event.get('data', {})
            self.cell_count_var.set(f"细胞数量: {info.get('cell_count', 0)}")
            self.fps_var.set(f"FPS: {info.get('fps', 0)}")
            
        elif event_type == 'simulation_log':
            message = event.get('data', '')
            self.log_widget.log_message(message)
            
        elif event_type == 'simulation_error':
            error = event.get('data', '未知错误')
            self.log_widget.log_message(f"错误: {error}", 'error')
            messagebox.showerror("模拟错误", str(error))
    
    def toggle_simulation(self):
        """切换模拟状态"""
        self.simulation_running = not self.simulation_running
        
        if self.simulation_running:
            self.sim_thread.resume()
            self.status_var.set("模拟运行中")
            self.log_widget.log_message("模拟已开始")
        else:
            self.sim_thread.pause()
            self.status_var.set("模拟已暂停")
            self.log_widget.log_message("模拟已暂停")
    
    def reset_simulation(self):
        """重置模拟"""
        self.simulation_running = False
        self.sim_thread.reset()
        self.status_var.set("模拟已重置")
        self.log_widget.log_message("模拟已重置")
        self.canvas_view.update_display()
    
    def open_dna_generator(self):
        """打开DNA生成器"""
        try:
            from tools import GUI_DNA_Generation
            dna_root = tk.Toplevel(self.root)
            dna_app = GUI_DNA_Generation.AminoAcidApp(dna_root)
        except Exception as e:
            self.log_widget.log_message(f"无法打开DNA生成器: {e}", 'error')
            messagebox.showerror("错误", f"无法打开DNA生成器: {e}")
    
    def open_protein_viewer(self):
        """打开蛋白质结构查看器"""
        from views.dialogs.protein_viewer_dialog import ProteinViewerDialog
        dialog = ProteinViewerDialog(self.root)
    
    def add_cell(self, cell_info):
        """添加细胞"""
        success = self.sim_thread.add_cell(**cell_info)
        if success:
            self.log_widget.log_message(f"添加细胞: {cell_info.get('name', '未知')}")
        return success
    
    def add_resource(self, resource_info):
        """添加资源"""
        success = self.sim_thread.add_resource(**resource_info)
        if success:
            self.log_widget.log_message(f"添加资源: {resource_info.get('type', '未知')}")
        return success