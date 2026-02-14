import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import sys
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pygame
import io

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from vitae_system import env, cells, metabolism, random_DNA, protein, dor_matrix
    from tools import DNA_Generation, GUI_DNA_Generation
except ImportError as e:
    print(f"导入错误: {e}")
    # 创建空类作为fallback
    class Fallback:
        pass
    env = cells = metabolism = random_DNA = protein = DNA_Generation = GUI_DNA_Generation = Fallback()

class VitaeCanvasTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Vitae Canvas - 生命绘卷")
        self.root.geometry("1200x800")
        
        # 模拟状态
        self.simulation_running = False
        self.simulation_speed = 5  # 帧率
        self.cell_size = 40
        self.view_offset_x = 0
        self.view_offset_y = 0
        
        # 模拟控制器
        self.simulation = None
        self.setup_simulation()
        
        # 创建界面
        self.create_interface()
        
        # 启动模拟循环
        self.simulation_loop()
    
    def setup_simulation(self):
        """初始化模拟环境"""
        try:
            self.simulation = SimulationController()
        except Exception as e:
            print(f"模拟初始化错误: {e}")
            self.simulation = None
    
    def create_interface(self):
        """创建主界面"""
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
        
        # 创建控制面板内容
        self.create_control_panel(control_frame)
        
        # 创建显示区域
        self.create_display_area(display_frame)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 标题
        title_label = ttk.Label(parent, text="Vitae Canvas 控制面板", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 模拟控制区域
        sim_frame = ttk.LabelFrame(parent, text="模拟控制", padding=10)
        sim_frame.pack(fill=tk.X, pady=5)
        
        # 开始/停止按钮
        btn_frame = ttk.Frame(sim_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="开始模拟", 
                                   command=self.toggle_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="重置模拟", 
                  command=self.reset_simulation).pack(side=tk.LEFT)
        
        # 速度控制
        speed_frame = ttk.Frame(sim_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="模拟速度:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=self.simulation_speed)
        speed_scale = ttk.Scale(speed_frame, from_=1, to=20, 
                               variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 细胞管理区域
        cell_frame = ttk.LabelFrame(parent, text="细胞管理", padding=10)
        cell_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(cell_frame, text="添加细胞", 
                  command=self.open_add_cell_dialog).pack(fill=tk.X)
        ttk.Button(cell_frame, text="查看细胞列表", 
                  command=self.show_cell_list).pack(fill=tk.X, pady=5)
        
        # 资源管理区域
        resource_frame = ttk.LabelFrame(parent, text="资源管理", padding=10)
        resource_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(resource_frame, text="添加资源", 
                  command=self.open_add_resource_dialog).pack(fill=tk.X)
        
        # 工具区域
        tools_frame = ttk.LabelFrame(parent, text="工具", padding=10)
        tools_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(tools_frame, text="DNA生成器", 
                  command=self.open_dna_generator).pack(fill=tk.X)
        ttk.Button(tools_frame, text="蛋白质结构查看器", 
                  command=self.open_protein_viewer).pack(fill=tk.X, pady=5)
        
        # 信息显示区域
        info_frame = ttk.LabelFrame(parent, text="模拟信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
    
    def create_display_area(self, parent):
        """创建显示区域"""
        # 创建画布用于显示模拟
        self.canvas = tk.Canvas(parent, bg='#0a1428', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        self.canvas.bind("<Button-4>", self.on_canvas_scroll)  # Linux 向上
        self.canvas.bind("<Button-5>", self.on_canvas_scroll)  # Linux 向下
        
        # 状态栏
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        cell_count_var = tk.StringVar(value="细胞数量: 0")
        ttk.Label(status_frame, textvariable=cell_count_var).pack(side=tk.RIGHT)
        
        # 更新状态函数
        def update_status():
            if self.simulation:
                cell_count_var.set(f"细胞数量: {len(self.simulation.cell_list)}")
            self.root.after(1000, update_status)
        
        update_status()
    
    def toggle_simulation(self):
        """切换模拟状态"""
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.start_btn.config(text="暂停模拟")
            self.status_var.set("模拟运行中")
        else:
            self.start_btn.config(text="继续模拟")
            self.status_var.set("模拟已暂停")
    
    def reset_simulation(self):
        """重置模拟"""
        self.simulation_running = False
        self.setup_simulation()
        self.start_btn.config(text="开始模拟")
        self.status_var.set("模拟已重置")
        self.update_display()
    
    def simulation_loop(self):
        """模拟循环"""
        if self.simulation_running and self.simulation:
            try:
                self.simulation.update()
                self.update_display()
            except Exception as e:
                self.log_message(f"模拟错误: {e}")
        
        # 计算下一帧的延迟
        delay = max(50, 1000 // self.speed_var.get())
        self.root.after(delay, self.simulation_loop)
    
    def update_display(self):
        """更新画布显示"""
        if not self.simulation:
            return
            
        self.canvas.delete("all")
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制细胞
        self.draw_cells()
        
        # 绘制资源
        self.draw_resources()
    
    def draw_grid(self):
        """绘制网格"""
        width = int(self.canvas.winfo_width())
        height = int(self.canvas.winfo_height())
        
        # 计算可见区域
        start_x = -self.view_offset_x // self.cell_size - 1
        end_x = start_x + width // self.cell_size + 2
        start_y = -self.view_offset_y // self.cell_size - 1
        end_y = start_y + height // self.cell_size + 2
        
        # 绘制网格线
        for x in range(int(start_x), int(end_x)):
            screen_x = x * self.cell_size + self.view_offset_x
            self.canvas.create_line(screen_x, 0, screen_x, height, 
                                   fill='#283c5f', width=1)
        
        for y in range(int(start_y), int(end_y)):
            screen_y = y * self.cell_size + self.view_offset_y
            self.canvas.create_line(0, screen_y, width, screen_y, 
                                   fill='#283c5f', width=1)
    
    def draw_cells(self):
        """绘制细胞"""
        for cell in self.simulation.cell_list:
            screen_x = cell.x * self.cell_size + self.view_offset_x
            screen_y = cell.y * self.cell_size + self.view_offset_y
            
            # 检查是否在可见区域内
            if (0 <= screen_x <= self.canvas.winfo_width() and 
                0 <= screen_y <= self.canvas.winfo_height()):
                
                # 绘制细胞圆形
                radius = self.cell_size // 2 - 2
                self.canvas.create_oval(
                    screen_x - radius, screen_y - radius,
                    screen_x + radius, screen_y + radius,
                    fill=self.get_cell_color(cell),
                    outline='white',
                    width=2
                )
                
                # 绘制细胞名称
                self.canvas.create_text(screen_x, screen_y, 
                                       text=cell.name, fill='white', font=('Arial', 8))
    
    def draw_resources(self):
        """绘制资源"""
        # 这里需要根据实际环境数据绘制资源
        # 简化实现：绘制已知的资源点
        resources_positions = [(0, 0), (0, 1)]  # 示例位置
        
        for x, y in resources_positions:
            screen_x = x * self.cell_size + self.view_offset_x
            screen_y = y * self.cell_size + self.view_offset_y
            
            if (0 <= screen_x <= self.canvas.winfo_width() and 
                0 <= screen_y <= self.canvas.winfo_height()):
                
                self.canvas.create_rectangle(
                    screen_x - 5, screen_y - 5,
                    screen_x + 5, screen_y + 5,
                    fill='yellow', outline='orange'
                )
    
    def get_cell_color(self, cell):
        """获取细胞颜色"""
        try:
            # 从cell对象获取颜色属性（应为RGB元组）
            color_tuple = getattr(cell, 'color', (0, 255, 0))
        
            # 将RGB元组转换为十六进制颜色代码
            if isinstance(color_tuple, tuple) and len(color_tuple) == 3:
                r, g, b = [max(0, min(255, x)) for x in color_tuple]  # 确保值在0-255范围
                return f"#{r:02x}{g:02x}{b:02x}"
            else:
                return '#00ff00'  # 默认绿色
        except:
            return '#00ff00'  # 异常时返回默认绿色
    
    def on_canvas_press(self, event):
        """画布鼠标按下事件"""
        self.canvas.scan_mark(event.x, event.y)
    
    def on_canvas_drag(self, event):
        """画布鼠标拖动事件"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.view_offset_x = -self.canvas.canvasx(0)
        self.view_offset_y = -self.canvas.canvasy(0)
    
    def on_canvas_scroll(self, event):
        """画布滚轮缩放事件"""
        if event.delta > 0 or event.num == 4:  # 向上滚轮
            self.cell_size = min(100, self.cell_size + 5)
        else:  # 向下滚轮
            self.cell_size = max(10, self.cell_size - 5)
        self.update_display()
    
    def open_add_cell_dialog(self):
        """打开添加细胞对话框"""
        dialog = AddCellDialog(self.root, self.simulation)
        self.root.wait_window(dialog.top)
        if dialog.result:
            self.log_message(f"添加细胞: {dialog.result}")
    
    def open_add_resource_dialog(self):
        """打开添加资源对话框"""
        dialog = AddResourceDialog(self.root, self.simulation)
        self.root.wait_window(dialog.top)
        if dialog.result:
            self.log_message(f"添加资源: {dialog.result}")
    
    def show_cell_list(self):
        """显示细胞列表"""
        if not self.simulation:
            messagebox.showinfo("细胞列表", "模拟未初始化")
            return
            
        cell_info = "当前细胞列表:\n\n"
        for i, cell in enumerate(self.simulation.cell_list):
            cell_info += f"{i+1}. {cell.name} - 位置: ({cell.x}, {cell.y})\n"
        
        messagebox.showinfo("细胞列表", cell_info)
    
    def open_dna_generator(self):
        """打开DNA生成器"""
        try:
            dna_root = tk.Toplevel(self.root)
            dna_app = GUI_DNA_Generation.AminoAcidApp(dna_root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开DNA生成器: {e}")
    
    def open_protein_viewer(self):
        """打开蛋白质结构查看器"""
        dialog = ProteinViewerDialog(self.root)
        self.root.wait_window(dialog.top)
    
    def log_message(self, message):
        """记录消息到信息框"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)

class AddCellDialog:
    def __init__(self, parent, simulation):
        self.simulation = simulation
        self.result = None
        
        self.top = tk.Toplevel(parent)
        self.top.title("添加细胞")
        self.top.geometry("400x300")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框控件"""
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 细胞名称
        ttk.Label(main_frame, text="细胞名称:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar(value="Cell_" + str(int(time.time())))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 坐标输入
        ttk.Label(main_frame, text="X坐标:").grid(row=1, column=0, sticky='w', pady=5)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(main_frame, textvariable=self.x_var)
        x_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Y坐标:").grid(row=2, column=0, sticky='w', pady=5)
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(main_frame, textvariable=self.y_var)
        y_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # DNA设置
        dna_frame = ttk.LabelFrame(main_frame, text="DNA设置", padding=10)
        dna_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.dna_source = tk.StringVar(value="random")
        ttk.Radiobutton(dna_frame, text="随机生成DNA", variable=self.dna_source, 
                       value="random").pack(anchor='w')
        ttk.Radiobutton(dna_frame, text="手动输入DNA", variable=self.dna_source, 
                       value="manual").pack(anchor='w')
        
        # DNA长度
        ttk.Label(dna_frame, text="DNA长度:").pack(anchor='w', pady=(10, 0))
        self.dna_length_var = tk.StringVar(value="100")
        length_entry = ttk.Entry(dna_frame, textvariable=self.dna_length_var)
        length_entry.pack(fill=tk.X, pady=5)
        
        # DNA序列输入
        self.dna_text = scrolledtext.ScrolledText(dna_frame, height=4)
        self.dna_text.pack(fill=tk.X, pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self.ok).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT)
        
        main_frame.columnconfigure(1, weight=1)
    
    def ok(self):
        """确认添加细胞"""
        try:
            name = self.name_var.get()
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            
            if self.dna_source.get() == "random":
                length = int(self.dna_length_var.get())
                dna_sequence = random_DNA.generate_dna(length)
            else:
                dna_sequence = self.dna_text.get(1.0, tk.END).strip()
            
            # 创建细胞
            dna = cells.DNA(dna_sequence)
            new_cell = cells.Cell(self.simulation.env, x, y, dna=dna, name=name)
            self.simulation.cell_list.append(new_cell)
            
            self.result = f"细胞 {name} 添加成功"
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加细胞失败: {e}")
    
    def cancel(self):
        """取消操作"""
        self.top.destroy()

class AddResourceDialog:
    def __init__(self, parent, simulation):
        self.simulation = simulation
        self.result = None
        
        self.top = tk.Toplevel(parent)
        self.top.title("添加资源")
        self.top.geometry("300x250")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框控件"""
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 资源类型
        ttk.Label(main_frame, text="资源类型:").grid(row=0, column=0, sticky='w', pady=5)
        self.resource_type = tk.StringVar(value="Energy")
        resource_combo = ttk.Combobox(main_frame, textvariable=self.resource_type,
                                     values=["Energy", "O2", "H2O", "Sugar"])
        resource_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 数量
        ttk.Label(main_frame, text="数量:").grid(row=1, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar(value="100")
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var)
        amount_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 坐标
        ttk.Label(main_frame, text="X坐标:").grid(row=2, column=0, sticky='w', pady=5)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(main_frame, textvariable=self.x_var)
        x_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Y坐标:").grid(row=3, column=0, sticky='w', pady=5)
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(main_frame, textvariable=self.y_var)
        y_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self.ok).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT)
        
        main_frame.columnconfigure(1, weight=1)
    
    def ok(self):
        """确认添加资源"""
        try:
            resource_type = self.resource_type.get()
            amount = int(self.amount_var.get())
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            
            # 创建资源对象
            if resource_type == "Energy":
                resource = env.Energy(amount)
            elif resource_type == "O2":
                resource = env.O2(amount)
            elif resource_type == "H2O":
                resource = env.H2O(amount)
            elif resource_type == "Sugar":
                resource = cells.SugarList([cells.Sugar(6, 12, 6)])
            
            self.simulation.env.write(x, y, resource)
            self.result = f"资源 {resource_type} 添加成功"
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加资源失败: {e}")
    
    def cancel(self):
        """取消操作"""
        self.top.destroy()

class ProteinViewerDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("蛋白质结构查看器")
        self.top.geometry("800x600")
        self.top.transient(parent)
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建蛋白质查看器界面"""
        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="蛋白质序列:").pack(side=tk.LEFT)
        self.sequence_var = tk.StringVar(value="GACLICYWSCCMNEEEFGQEGHILKMFPS")
        sequence_entry = ttk.Entry(input_frame, textvariable=self.sequence_var, width=50)
        sequence_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="显示结构", command=self.show_structure).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 显示区域
        self.figure_frame = ttk.Frame(main_frame)
        self.figure_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def show_structure(self):
        """显示蛋白质结构"""
        try:
            sequence = self.sequence_var.get()
            
            # 清除之前的显示
            for widget in self.figure_frame.winfo_children():
                widget.destroy()
            
            # 使用Protein_structure_show模块绘制蛋白质结构
            try:
                from Protein_structure_show import draw_protein
                fig = draw_protein(sequence)
            except ImportError:
                # 如果模块不可用，使用简化版本
                fig = self.draw_simple_protein(sequence)
            
            # 嵌入到Tkinter
            canvas = FigureCanvasTkAgg(fig, self.figure_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示蛋白质结构失败: {e}")
    def draw_simple_protein(self, sequence):
        """简化版蛋白质结构显示（备选方案）"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f"蛋白质结构: {sequence}", 
               ha='center', va='center', fontsize=16)
        ax.set_title("蛋白质结构可视化")
        ax.set_axis_off()
        return fig

class SimulationController:
    """模拟控制器（从原Pygame代码移植）"""
    def __init__(self):
        try:
            self.env = env.Environment(-1, -1)
            self.cell_list = []
            
            # 初始化示例细胞
            dna = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")
            #self.cell_list.append(cells.Cell(self.env, 0, 0, dna=dna, name="Vita"))
            address = dor_matrix.string_to_coordinates("Hello,")
            env1 = env.Environment()
            for i in address:
                self.cell_list.append(cells.Cell(env1, i[0], i[1], dna, ''))
                # 添加初始资源
                resource_list = [
                    env.Energy(100), 
                    env.O2(200), 
                    env.H2O(200), 
                    cells.SugarList([cells.Sugar(6, 12, 6)])
                ]
                for resource in resource_list:
                    self.env.write(i[0], i[1], resource)
            address = dor_matrix.string_to_coordinates("2026!")
            for i in address:
                self.cell_list.append(cells.Cell(env1, i[0], i[1] + 10, dna, ''))
                # 添加初始资源
                resource_list = [
                    env.Energy(100), 
                    env.O2(200), 
                    env.H2O(200), 
                    cells.SugarList([cells.Sugar(6, 12, 6)])
                ]
                for resource in resource_list:
                    self.env.write(i[0], i[1], resource)
            
            self.env.write(0, 1, env.Energy(200))
            
        except Exception as e:
            print(f"模拟控制器初始化错误: {e}")
    
    def update(self):
        """更新模拟状态"""
        try:
            new_cells = []
            for cell in self.cell_list:
                metabolism_system = metabolism.MetabolismSystem(cell, self.env)
                new_cell = metabolism_system.re_info()
                
                if new_cell:
                    new_cells.append(new_cell)
            
            self.cell_list.extend(new_cells)
            self.env.resources_diffusion()
            
        except Exception as e:
            print(f"模拟更新错误: {e}")

def main():
    root = tk.Tk()
    app = VitaeCanvasTkinter(root)
    root.mainloop()

if __name__ == "__main__":
    main()