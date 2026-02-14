"""
控制面板视图
"""

import tkinter as tk
from tkinter import ttk
from views.dialogs.add_cell_dialog import AddCellDialog
from views.dialogs.add_resource_dialog import AddResourceDialog

class ControlPanel:
    """控制面板"""
    
    def __init__(self, parent, main_window):
        """
        初始化控制面板
        
        Args:
            parent: 父容器
            main_window: 主窗口实例
        """
        self.parent = parent
        self.main_window = main_window
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        # 标题
        title_label = ttk.Label(self.parent, text="Vitae Canvas 控制面板", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 模拟控制区域
        self._create_simulation_controls()
        
        # 细胞管理区域
        self._create_cell_controls()
        
        # 资源管理区域
        self._create_resource_controls()
        
        # 工具区域
        self._create_tools_controls()
    
    def _create_simulation_controls(self):
        """创建模拟控制区域"""
        sim_frame = ttk.LabelFrame(self.parent, text="模拟控制", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始/停止按钮
        btn_frame = ttk.Frame(sim_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(
            btn_frame, 
            text="开始模拟", 
            command=self.main_window.toggle_simulation,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame, 
            text="重置模拟", 
            command=self.main_window.reset_simulation,
            width=15
        ).pack(side=tk.LEFT)
        
        # 速度控制
        speed_frame = ttk.Frame(sim_frame)
        speed_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(speed_frame, text="模拟速度:").pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=5)
        speed_scale = ttk.Scale(
            speed_frame, 
            from_=1, 
            to=20, 
            variable=self.speed_var, 
            orient=tk.HORIZONTAL
        )
        speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 显示当前速度值
        speed_value_label = ttk.Label(sim_frame, textvariable=self.speed_var)
        speed_value_label.pack(anchor=tk.E)
        
        # 绑定速度变化事件
        def on_speed_change(*args):
            self.main_window.sim_thread.update_rate = self.speed_var.get()
        
        self.speed_var.trace_add('write', on_speed_change)
    
    def _create_cell_controls(self):
        """创建细胞管理区域"""
        cell_frame = ttk.LabelFrame(self.parent, text="细胞管理", padding=10)
        cell_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加细胞按钮
        ttk.Button(
            cell_frame, 
            text="添加细胞", 
            command=self._open_add_cell_dialog,
            width=20
        ).pack(fill=tk.X)
        
        # 查看细胞列表按钮
        ttk.Button(
            cell_frame, 
            text="查看细胞列表", 
            command=self._show_cell_list,
            width=20
        ).pack(fill=tk.X, pady=(5, 0))
        
        # 批量操作
        batch_frame = ttk.Frame(cell_frame)
        batch_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(batch_frame, text="批量操作:").pack(side=tk.LEFT)
        
        ttk.Button(
            batch_frame, 
            text="添加5个随机细胞", 
            command=self._add_random_cells,
            width=15
        ).pack(side=tk.RIGHT)
    
    def _create_resource_controls(self):
        """创建资源管理区域"""
        resource_frame = ttk.LabelFrame(self.parent, text="资源管理", padding=10)
        resource_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加资源按钮
        ttk.Button(
            resource_frame, 
            text="添加资源", 
            command=self._open_add_resource_dialog,
            width=20
        ).pack(fill=tk.X)
        
        # 资源类型快速添加
        quick_frame = ttk.Frame(resource_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quick_frame, text="快速添加:").pack(side=tk.LEFT)
        
        # 快速添加按钮
        quick_buttons = [
            ("能量", "Energy"),
            ("氧气", "O2"),
            ("水", "H2O"),
            ("糖", "Sugar")
        ]
        
        btn_container = ttk.Frame(quick_frame)
        btn_container.pack(side=tk.RIGHT)
        
        for text, r_type in quick_buttons:
            ttk.Button(
                btn_container, 
                text=text, 
                command=lambda rt=r_type: self._quick_add_resource(rt),
                width=6
            ).pack(side=tk.LEFT, padx=(2, 0))
    
    def _create_tools_controls(self):
        """创建工具区域"""
        tools_frame = ttk.LabelFrame(self.parent, text="工具", padding=10)
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        # DNA生成器按钮
        ttk.Button(
            tools_frame, 
            text="DNA生成器", 
            command=self.main_window.open_dna_generator,
            width=20
        ).pack(fill=tk.X)
        
        # 蛋白质结构查看器按钮
        ttk.Button(
            tools_frame, 
            text="蛋白质结构查看器", 
            command=self.main_window.open_protein_viewer,
            width=20
        ).pack(fill=tk.X, pady=(5, 0))
        
        # 高级工具
        advanced_frame = ttk.Frame(tools_frame)
        advanced_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(advanced_frame, text="高级工具:").pack(side=tk.LEFT)
        
        ttk.Button(
            advanced_frame, 
            text="代谢分析", 
            command=self._open_metabolism_analyzer,
            width=12
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            advanced_frame, 
            text="环境编辑器", 
            command=self._open_environment_editor,
            width=12
        ).pack(side=tk.RIGHT)
    
    def _open_add_cell_dialog(self):
        """打开添加细胞对话框"""
        def on_cell_confirm(cell_info):
            success = self.main_window.add_cell(cell_info)
            if success:
                self._update_simulation_controls()
        
        dialog = AddCellDialog(self.parent.winfo_toplevel(), on_cell_confirm)
    
    def _open_add_resource_dialog(self):
        """打开添加资源对话框"""
        def on_resource_confirm(resource_info):
            success = self.main_window.add_resource(resource_info)
            if success:
                self._update_simulation_controls()
        
        dialog = AddResourceDialog(self.parent.winfo_toplevel(), on_resource_confirm)
    
    def _show_cell_list(self):
        """显示细胞列表"""
        import tkinter.messagebox as messagebox
        
        state = self.main_window.sim_thread.get_state()
        if not state or not state.get('cells'):
            messagebox.showinfo("细胞列表", "当前没有细胞")
            return
        
        cells = state['cells']
        cell_info = f"当前细胞列表 ({len(cells)} 个):\n\n"
        
        for i, cell in enumerate(cells[:20]):  # 只显示前20个
            cell_info += f"{i+1}. {cell.get('name', '未知')} - 位置: ({cell.get('x', 0)}, {cell.get('y', 0)})\n"
        
        if len(cells) > 20:
            cell_info += f"\n... 还有 {len(cells) - 20} 个细胞未显示"
        
        messagebox.showinfo("细胞列表", cell_info)
    
    def _add_random_cells(self):
        """添加随机细胞"""
        import random
        
        for i in range(5):
            x = random.randint(-10, 10)
            y = random.randint(-10, 10)
            name = f"Random_Cell_{i+1}"
            
            # 生成随机DNA
            import random as rand
            bases = ['A', 'T', 'C', 'G']
            dna_length = random.randint(50, 200)
            dna_sequence = ''.join(rand.choice(bases) for _ in range(dna_length))
            
            self.main_window.add_cell({
                'name': name,
                'x': x,
                'y': y,
                'dna_sequence': dna_sequence
            })
    
    def _quick_add_resource(self, resource_type):
        """快速添加资源"""
        import random
        
        # 随机位置
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
        amount = random.randint(50, 200)
        
        self.main_window.add_resource({
            'x': x,
            'y': y,
            'resource_type': resource_type,
            'amount': amount
        })
    
    def _open_metabolism_analyzer(self):
        """打开代谢分析器"""
        from tkinter import messagebox
        messagebox.showinfo("提示", "代谢分析器功能开发中...")
    
    def _open_environment_editor(self):
        """打开环境编辑器"""
        from tkinter import messagebox
        messagebox.showinfo("提示", "环境编辑器功能开发中...")
    
    def _update_simulation_controls(self):
        """更新模拟控制状态"""
        # 可以在这里更新按钮状态等
        pass
    
    def update_start_button(self, is_running):
        """更新开始按钮文本"""
        if is_running:
            self.start_btn.config(text="暂停模拟")
        else:
            self.start_btn.config(text="开始模拟")