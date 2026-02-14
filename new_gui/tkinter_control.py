import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import queue

class TkinterControlPanel:
    """Tkinter控制面板"""
    
    def __init__(self, simulation_controller=None):
        self.simulation_controller = simulation_controller
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("VitaeCanvas 控制面板")
        self.root.geometry("500x700")
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_control_tab()
        self.create_cell_tab()
        self.create_info_tab()
        
        # 状态变量
        self.running = True
        
        # 创建线程安全的日志队列和UI更新队列
        self.log_queue = queue.Queue()
        self.ui_update_queue = queue.Queue()
        
        # 设置队列处理器
        self.setup_queue_handlers()
        
        # 启动更新线程
        self.update_thread = threading.Thread(target=self.update_display_thread, daemon=True)
        self.update_thread.start()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

         # 新增：细胞信息查看窗口引用
        self.cell_info_windows = {}  # 存储细胞信息窗口，key为细胞名称
        
        # 新增：蛋白质信息窗口引用
        self.protein_info_windows = {}  # 存储蛋白质信息窗口
        
    def create_control_tab(self):
        """创建控制标签页"""
        control_tab = ttk.Frame(self.notebook)
        self.notebook.add(control_tab, text="控制")
        
        # 模拟控制框架
        control_frame = ttk.LabelFrame(control_tab, text="模拟控制", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # 代谢控制按钮
        self.metabolism_btn = ttk.Button(
            control_frame, text="开启代谢", 
            command=self.toggle_metabolism,
            width=20
        )
        # self.metabolism_btn.pack(pady=5)
        
        # 代谢间隔控制
        interval_frame = ttk.Frame(control_frame)
        interval_frame.pack(fill='x', pady=5)
        
        ttk.Label(interval_frame, text="代谢间隔(秒):").pack(side='left')
        self.interval_var = tk.DoubleVar(value=5.0)
        self.interval_spinbox = ttk.Spinbox(
            interval_frame, from_=0.1, to=60, 
            increment=0.5, textvariable=self.interval_var,
            width=10
        )
        self.interval_spinbox.pack(side='left', padx=5)
        ttk.Button(
            interval_frame, text="设置", 
            command=self.set_metabolism_interval,
            width=10
        ).pack(side='left')
        

        # 蛋白质结构查看器
        coord_frame = ttk.LabelFrame(control_frame, text="蛋白质结构查看", padding=10)
        coord_frame.pack(fill='x', pady=10)
        '''
        # X坐标
        x_frame = ttk.Frame(coord_frame)
        x_frame.pack(fill='x', pady=2)
        ttk.Label(x_frame, text="X:", width=5).pack(side='left')
        self.x_var = tk.DoubleVar(value=2.0)
        self.x_spinbox = ttk.Spinbox(
            x_frame, from_=-1000, to=1000, 
            increment=0.1, textvariable=self.x_var,
            width=15
        )
        self.x_spinbox.pack(side='left', padx=5)
        '''
        # 名称输入
        name_frame = ttk.Frame(coord_frame)
       
        ttk.Label(name_frame, text="氨基酸序列:").pack(side='left')
        self.new_protein_seq = tk.StringVar(value="GACLICYWSCCMNEEEFGQEGHILKMFPS")
        ttk.Entry(name_frame, textvariable=self.new_protein_seq, width=20).pack(side='left', padx=5)
        name_frame.pack(fill='x', pady=5)
        # 坐标设置按钮
        ttk.Button(
            coord_frame, text="查看蛋白质结构", 
            command=self.view_protein_structure,
            width=20
        ).pack(pady=5)

        # 重置模拟按钮
        ttk.Button(
            control_frame, text="重置模拟", 
            command=self.reset_simulation,
            width=20
        ).pack(pady=5)
        
        # 坐标显示
        self.coord_display = ttk.Label(
            control_frame, 
            text="当前坐标: (2.00, 3.00)",
            font=('Arial', 10, 'bold')
        )
        self.coord_display.pack(pady=10)
        
        # 细胞数量显示
        self.cell_count_label = ttk.Label(
            control_frame,
            text="细胞数量: 2",
            font=('Arial', 10)
        )
        self.cell_count_label.pack(pady=5)
    
    def view_protein_structure(self):
        import tools.Protein_structure_show as pss
        pss.draw_protein(self.new_protein_seq.get(),show=True)


    def create_cell_tab(self):
        """创建细胞管理标签页"""
        cell_tab = ttk.Frame(self.notebook)
        self.notebook.add(cell_tab, text="细胞管理")
        
        # 添加细胞框架
        add_frame = ttk.LabelFrame(cell_tab, text="添加细胞", padding=10)
        add_frame.pack(fill='x', padx=10, pady=10)
        
        # 位置输入
        pos_frame = ttk.Frame(add_frame)
        pos_frame.pack(fill='x', pady=5)
        
        ttk.Label(pos_frame, text="X位置:").pack(side='left')
        self.new_cell_x = tk.IntVar(value=0)
        ttk.Entry(pos_frame, textvariable=self.new_cell_x, width=10).pack(side='left', padx=5)
        
        ttk.Label(pos_frame, text="Y位置:").pack(side='left', padx=(10,0))
        self.new_cell_y = tk.IntVar(value=0)
        ttk.Entry(pos_frame, textvariable=self.new_cell_y, width=10).pack(side='left', padx=5)
        
        # 名称输入
        name_frame = ttk.Frame(add_frame)
        name_frame.pack(fill='x', pady=5)
        
        ttk.Label(name_frame, text="名称:").pack(side='left')
        self.new_cell_name = tk.StringVar(value="")
        ttk.Entry(name_frame, textvariable=self.new_cell_name, width=20).pack(side='left', padx=5)
        
        # 添加按钮
        ttk.Button(
            add_frame, text="添加细胞", 
            command=self.add_cell,
            width=20
        ).pack(pady=10)
        
        # 细胞列表框架
        list_frame = ttk.LabelFrame(cell_tab, text="细胞列表", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 细胞列表
        self.cell_listbox = tk.Listbox(list_frame, height=10)
        self.cell_listbox.pack(fill='both', expand=True, pady=5)
        
        # 初始细胞
        self.cell_listbox.insert(tk.END, "Vita1 - 位置: (0, 0)")
        self.cell_listbox.insert(tk.END, "Vita2 - 位置: (1, 0)")
        
        # 操作按钮
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            btn_frame, text="移除选中", 
            command=self.remove_selected_cell,
            width=15
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, text="查看信息", 
            command=self.show_cell_info,
            width=15
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, text="刷新列表", 
            command=self.update_cell_list,
            width=15
        ).pack(side='left', padx=5)
    
    def create_info_tab(self):
        """创建信息标签页"""
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="日志信息")
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(info_tab, height=20, width=50)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 初始日志
        self.add_log("控制面板已启动")
        self.add_log("模拟初始化完成")
        self.add_log("细胞载入完成")
        
        # 操作按钮
        btn_frame = ttk.Frame(info_tab)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            btn_frame, text="清空日志", 
            command=self.clear_log,
            width=15
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, text="保存日志", 
            command=self.save_log,
            width=15
        ).pack(side='left', padx=5)
        
        # 状态栏
        self.status_bar = ttk.Label(
            info_tab, 
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill='x', padx=10, pady=5)
    
    def setup_queue_handlers(self):
        """设置队列处理器"""
        # 每100毫秒检查一次日志队列
        self.root.after(100, self.process_log_queue)
        # 每200毫秒检查一次UI更新队列
        self.root.after(200, self.process_ui_update_queue)
    
    def process_log_queue(self):
        """处理日志队列中的消息（在主线程中调用）"""
        try:
            while True:
                # 非阻塞方式获取队列中的消息
                log_message = self.log_queue.get_nowait()
                self._add_log_thread_safe(log_message)
        except queue.Empty:
            pass
        # 继续定时检查
        self.root.after(100, self.process_log_queue)
    
    def process_ui_update_queue(self):
        """处理UI更新队列中的消息（在主线程中调用）"""
        try:
            while True:
                # 非阻塞方式获取队列中的消息
                update_func, args = self.ui_update_queue.get_nowait()
                if callable(update_func):
                    update_func(*args)
        except queue.Empty:
            pass
        # 继续定时检查
        self.root.after(200, self.process_ui_update_queue)
    
    def add_log_safe(self, message):
        """线程安全的添加日志（从其他线程调用）"""
        if self.running and hasattr(self, 'log_queue'):
            timestamp = time.strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            try:
                self.log_queue.put(log_message)
            except:
                pass  # 如果队列已满，则丢弃消息

    # 在TkinterControlPanel类中添加以下方法

    def set_simulation_controller(self, controller):
        """设置模拟控制器引用"""
        self.simulation_controller = controller
        self.add_log("模拟控制器已连接")
    
        # 更新代谢按钮文本
        if controller and controller.metabolism_enabled:
            self.metabolism_btn.config(text="关闭代谢")
        else:
            self.metabolism_btn.config(text="开启代谢")
    
    def add_log(self, message):
        """添加日志（从主线程调用）"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self._add_log_thread_safe(log_message)
    
    def _add_log_thread_safe(self, log_message):
        """线程安全的日志添加（必须在主线程中调用）"""
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)  # 滚动到底部
    
    def update_display_thread(self):
        """更新显示线程"""
        while self.running:
            try:
                # 更新细胞数量
                if self.simulation_controller:
                    # 使用线程安全的方式获取细胞数量
                    cell_count = 0
                    try:
                        with self.simulation_controller.lock:
                            cell_count = len(self.simulation_controller.cell_list)
                    except:
                        pass
                    
                    # 通过UI更新队列更新显示
                    self.ui_update_queue.put((self._update_cell_count, (cell_count,)))
                
                # 更新细胞列表
                self.ui_update_queue.put((self.update_cell_list_safe, ()))
                
                # 更新状态栏
                current_time = time.strftime("%H:%M:%S")
                self.ui_update_queue.put((self._update_status_bar, (current_time,)))
                
            except Exception as e:
                # 记录错误到日志队列
                self.add_log_safe(f"更新显示时出错: {e}")
            
            time.sleep(1)  # 每秒更新一次
    
    def _update_cell_count(self, cell_count):
        """更新细胞数量显示（在主线程中调用）"""
        try:
            self.cell_count_label.config(text=f"细胞数量: {cell_count}")
        except:
            pass
    
    def _update_status_bar(self, current_time):
        """更新状态栏（在主线程中调用）"""
        try:
            self.status_bar.config(text=f"就绪 | 时间: {current_time}")
        except:
            pass
    
    def update_cell_list_safe(self):
        """安全的更新细胞列表（在主线程中调用）"""
        try:
            if not self.simulation_controller:
                return
                
            # 获取细胞信息
            cell_infos = []
            try:
                with self.simulation_controller.lock:
                    for cell in self.simulation_controller.cell_list:
                        cell_info = f"{cell.name} - 位置: ({cell.x}, {cell.y}) - 能量: {round(cell.energy.value, 2)}"
                        cell_infos.append(cell_info)
            except Exception as e:
                self.add_log_safe(f"获取细胞信息时出错: {e}")
                return
            
            # 更新列表
            self.cell_listbox.delete(0, tk.END)
            for cell_info in cell_infos:
                self.cell_listbox.insert(tk.END, cell_info)
        except Exception as e:
            # 记录错误但不中断程序
            self.add_log_safe(f"更新细胞列表时出错: {e}")
    
    def update_cell_list(self):
        """更新细胞列表（主线程版本）"""
        self.update_cell_list_safe()
    
    def update_coordinate_display(self, x, y):
        """更新坐标显示（线程安全）"""
        # 将更新请求放入UI更新队列
        self.ui_update_queue.put((self._update_coordinate_display, (x, y)))
    
    def _update_coordinate_display(self, x, y):
        """实际更新坐标显示（在主线程中调用）"""
        try:
            self.x_var.set(round(x, 2))
            self.y_var.set(round(y, 2))
            self.coord_display.config(text=f"当前坐标: ({x:.2f}, {y:.2f})")
        except:
            pass
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("日志已清空")
    
    def save_log(self):
        """保存日志"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            with open("simulation_log.txt", "w", encoding="utf-8") as f:
                f.write(log_content)
            self.add_log("日志已保存到 simulation_log.txt")
            messagebox.showinfo("成功", "日志已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存日志时出错: {e}")
    
    def toggle_metabolism(self):
        """切换代谢状态"""
        if self.simulation_controller:
            self.simulation_controller.toggle_metabolism()
            # 更新按钮文本
            if self.simulation_controller.metabolism_enabled:
                self.metabolism_btn.config(text="关闭代谢")
            else:
                self.metabolism_btn.config(text="开启代谢")
    
    def set_metabolism_interval(self):
        """设置代谢间隔"""
        if self.simulation_controller:
            interval = self.interval_var.get()
            if interval <= 0:
                messagebox.showwarning("警告", "代谢间隔必须大于0")
                return
            self.simulation_controller.set_metabolism_interval(interval)
    
    def set_coordinates(self):
        """设置坐标"""
        if self.simulation_controller:
            try:
                x = float(self.x_var.get())
                y = float(self.y_var.get())
                self.simulation_controller.display_pos = [x, y]
                self._update_coordinate_display(x, y)
                self.add_log(f"坐标设置为: ({x:.2f}, {y:.2f})")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的坐标值")
    
    def add_cell(self):
        """添加细胞"""
        if self.simulation_controller:
            try:
                x = self.new_cell_x.get()
                y = self.new_cell_y.get()
                name = self.new_cell_name.get()
                
                if not name:
                    import random
                    name = f"Cell_{random.randint(1000, 9999)}"
                
                self.simulation_controller.add_cell(x, y, name)
                
                # 清空输入框
                self.new_cell_name.set("")
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的坐标值")
    
    def remove_selected_cell(self):
        """移除选中的细胞"""
        if self.simulation_controller:
            selection = self.cell_listbox.curselection()
            if selection:
                index = selection[0]
                self.simulation_controller.remove_cell(index)
    
    def show_cell_info(self):
        """显示选中细胞的详细信息"""
        selection = self.cell_listbox.curselection()
        if selection:
            index = selection[0]
            cell_info = self.cell_listbox.get(index)
            messagebox.showinfo("细胞信息", f"详细信息:\n{cell_info}")
    
    def reset_simulation(self):
        """重置模拟"""
        if self.simulation_controller:
            self.simulation_controller.reset_simulation()
    
    def run(self):
        """运行控制面板"""
        self.root.mainloop()
    
    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.running = False
            if self.simulation_controller:
                self.simulation_controller.stop()
            self.root.destroy()

    def show_cell_info(self):
        """显示选中细胞的详细信息（完整面板）"""
        selection = self.cell_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个细胞")
            return
        
        index = selection[0]
        if not self.simulation_controller:
            return
        
        try:
            with self.simulation_controller.lock:
                if 0 <= index < len(self.simulation_controller.cell_list):
                    cell = self.simulation_controller.cell_list[index]
                    
                    # 如果这个细胞的窗口已经打开，就将其带到前台
                    if cell.name in self.cell_info_windows:
                        window = self.cell_info_windows[cell.name]
                        window.deiconify()  # 显示窗口
                        window.lift()       # 置于顶层
                        return
                    
                    # 创建新的细胞信息窗口
                    self.create_cell_info_window(cell)
        except Exception as e:
            self.add_log(f"获取细胞信息时出错: {e}")
    
    def create_cell_info_window(self, cell):
        """创建细胞详细信息窗口"""
        # 创建顶级窗口
        cell_window = tk.Toplevel(self.root)
        cell_window.title(f"细胞详细信息 - {cell.name}")
        cell_window.geometry("800x600")
        
        # 保存窗口引用
        self.cell_info_windows[cell.name] = cell_window
        
        # 绑定窗口关闭事件
        def on_cell_window_close():
            if cell.name in self.cell_info_windows:
                del self.cell_info_windows[cell.name]
            cell_window.destroy()
        
        cell_window.protocol("WM_DELETE_WINDOW", on_cell_window_close)
        
        # 创建主框架
        main_frame = ttk.Frame(cell_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 将canvas和scrollbar放入网格
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 设置字体
        title_font = ('Arial', 12, 'bold')
        label_font = ('Arial', 10)
        value_font = ('Arial', 10, 'italic')
        
        # 标题
        title_label = ttk.Label(
            scrollable_frame, 
            text=f"细胞: {cell.name}",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 基本信息部分
        info_frame = ttk.LabelFrame(scrollable_frame, text="基本信息", padding=10)
        info_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # 创建信息行
        row = 0
        
        # 名称
        self.add_info_row(info_frame, row, "名称:", cell.name, label_font, value_font)
        row += 1
        
        # 坐标
        self.add_info_row(info_frame, row, "坐标:", f"({cell.x}, {cell.y})", label_font, value_font)
        row += 1
        
        # 年龄
        self.add_info_row(info_frame, row, "年龄:", str(cell.age), label_font, value_font)
        row += 1
        
        # 能量
        if hasattr(cell.energy, 'value'):
            energy_value = round(cell.energy.value, 2)
            energy_progress = ttk.Progressbar(info_frame, length=200, mode='determinate')
            energy_progress['value'] = min(energy_value, 100)  # 假设最大能量为100
            self.add_info_row_with_widget(
                info_frame, row, "能量:", f"{energy_value}", 
                energy_progress, label_font, value_font
            )
        else:
            self.add_info_row(info_frame, row, "能量:", str(cell.energy), label_font, value_font)
        row += 1
        
        # 结构强度
        #if hasattr(cell, 'strong'):
        self.add_info_row(info_frame, row, "结构强度:", str(cell.strong), label_font, value_font)
        row += 1
        
        # 颜色
        #if hasattr(cell, 'color'):
        if 1:
            color_frame = ttk.Frame(info_frame)
            color_label = ttk.Label(color_frame, text="颜色:", font=label_font)
            color_label.pack(side='left')
            
            # 显示颜色方块
            color_canvas = tk.Canvas(color_frame, width=30, height=20)
            if isinstance(cell.color, tuple) and len(cell.color) >= 3:
                color_canvas.create_rectangle(0, 0, 30, 20, fill=f"#{cell.color[0]:02x}{cell.color[1]:02x}{cell.color[2]:02x}")
            color_canvas.pack(side='left', padx=5)
            
            color_value = ttk.Label(color_frame, text=str(cell.color), font=value_font)
            color_value.pack(side='left')
            
            color_frame.grid(row=row, column=0, columnspan=2, sticky='w', pady=2)
            row += 1
        
        # DNA信息部分
        dna_frame = ttk.LabelFrame(scrollable_frame, text="DNA信息", padding=10)
        dna_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # DNA序列
        dna_row = 0
        if hasattr(cell, 'dna') and hasattr(cell.dna, 'sequence'):
            dna_seq = cell.dna.sequence
            dna_length = len(dna_seq)
            dna_preview = dna_seq[:50] + "..." if dna_length > 50 else dna_seq
            
            self.add_info_row(dna_frame, dna_row, "DNA序列长度:", str(dna_length), label_font, value_font)
            dna_row += 1
            
            # DNA预览
            dna_preview_label = ttk.Label(dna_frame, text="DNA预览:", font=label_font)
            dna_preview_label.grid(row=dna_row, column=0, sticky='w', pady=2)
            
            dna_preview_text = tk.Text(dna_frame, height=3, width=50, wrap='word')
            dna_preview_text.insert('1.0', dna_preview)
            dna_preview_text.config(state='disabled')
            dna_preview_text.grid(row=dna_row, column=1, sticky='w', pady=2, padx=(10, 0))
            dna_row += 1
        
        # RNA信息
        if hasattr(cell, 'rna') and hasattr(cell.rna, 'sequence'):
            rna_seq = cell.rna.sequence
            rna_length = len(rna_seq)
            rna_preview = rna_seq[:50] + "..." if rna_length > 50 else rna_seq
            
            self.add_info_row(dna_frame, dna_row, "RNA序列长度:", str(rna_length), label_font, value_font)
            dna_row += 1
            
            # RNA预览
            rna_preview_label = ttk.Label(dna_frame, text="RNA预览:", font=label_font)
            rna_preview_label.grid(row=dna_row, column=0, sticky='w', pady=2)
            
            rna_preview_text = tk.Text(dna_frame, height=3, width=50, wrap='word')
            rna_preview_text.insert('1.0', rna_preview)
            rna_preview_text.config(state='disabled')
            rna_preview_text.grid(row=dna_row, column=1, sticky='w', pady=2, padx=(10, 0))
        
        # 蛋白质信息部分
        protein_frame = ttk.LabelFrame(scrollable_frame, text="蛋白质信息", padding=10)
        protein_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # 蛋白质数量
        if hasattr(cell, 'protein_list'):
            protein_count = len(cell.protein_list)
            protein_count_label = ttk.Label(
                protein_frame, 
                text=f"蛋白质数量: {protein_count}",
                font=('Arial', 10, 'bold')
            )
            protein_count_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
            
            # 查看蛋白质列表按钮
            protein_button = ttk.Button(
                protein_frame,
                text="查看蛋白质列表",
                command=lambda: self.show_protein_list(cell),
                width=20
            )
            protein_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 细胞状态信息
        status_frame = ttk.LabelFrame(scrollable_frame, text="细胞状态", padding=10)
        status_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        status_row = 0
        
        # 是否死亡
        if hasattr(cell, 'dead'):
            status_text = "死亡" if cell.dead else "存活"
            status_color = "red" if cell.dead else "green"
            status_label = ttk.Label(status_frame, text="状态:", font=label_font)
            status_label.grid(row=status_row, column=0, sticky='w', pady=2)
            
            status_value = ttk.Label(
                status_frame, 
                text=status_text, 
                font=('Arial', 10, 'bold'),
                foreground=status_color
            )
            status_value.grid(row=status_row, column=1, sticky='w', pady=2, padx=(10, 0))
            status_row += 1
        
        # 代谢率
        if hasattr(cell, 'metabolic_rate'):
            self.add_info_row(status_frame, status_row, "代谢率:", f"{cell.metabolic_rate:.2f}", label_font, value_font)
            status_row += 1
        
        # 变异率
        if hasattr(cell, 'variation_rate'):
            self.add_info_row(status_frame, status_row, "变异率:", f"{cell.variation_rate:.2f}", label_font, value_font)
            status_row += 1
        
        # 细胞功能信息（如果存在）
        if hasattr(cell, 'info') and cell.info:
            info_frame2 = ttk.LabelFrame(scrollable_frame, text="细胞功能信息", padding=10)
            info_frame2.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 10))
            
            info_row = 0
            for key, value in cell.info.items():
                if isinstance(value, (int, float)):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)
                
                self.add_info_row(info_frame2, info_row, f"{key}:", value_str, label_font, value_font)
                info_row += 1
        
        # 操作按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        # 刷新按钮
        refresh_button = ttk.Button(
            button_frame,
            text="刷新信息",
            command=lambda: self.refresh_cell_info(cell_window, cell),
            width=15
        )
        refresh_button.pack(side='left', padx=5)
        
        # 关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=on_cell_window_close,
            width=15
        )
        close_button.pack(side='left', padx=5)
    
    def add_info_row(self, parent, row, label_text, value_text, label_font, value_font):
        """添加信息行（标签+值）"""
        label = ttk.Label(parent, text=label_text, font=label_font)
        label.grid(row=row, column=0, sticky='w', pady=2)
        
        value = ttk.Label(parent, text=value_text, font=value_font)
        value.grid(row=row, column=1, sticky='w', pady=2, padx=(10, 0))
    
    def add_info_row_with_widget(self, parent, row, label_text, value_text, widget, label_font, value_font):
        """添加信息行（带额外小部件）"""
        label = ttk.Label(parent, text=label_text, font=label_font)
        label.grid(row=row, column=0, sticky='w', pady=2)
        
        # 值标签
        value_frame = ttk.Frame(parent)
        value_frame.grid(row=row, column=1, sticky='w', pady=2, padx=(10, 0))
        
        value = ttk.Label(value_frame, text=value_text, font=value_font)
        value.pack(side='left')
        
        widget.pack(side='left', padx=(10, 0))
    
    def refresh_cell_info(self, window, cell):
        """刷新细胞信息窗口"""
        # 先关闭旧窗口
        if cell.name in self.cell_info_windows:
            old_window = self.cell_info_windows[cell.name]
            old_window.destroy()
            del self.cell_info_windows[cell.name]
        
        # 重新获取最新细胞信息
        if not self.simulation_controller:
            return
        
        try:
            with self.simulation_controller.lock:
                # 找到最新的细胞对象
                for c in self.simulation_controller.cell_list:
                    if c.name == cell.name:
                        # 创建新窗口
                        self.create_cell_info_window(c)
                        break
        except Exception as e:
            self.add_log(f"刷新细胞信息时出错: {e}")
    
    def show_protein_list(self, cell):
        """显示蛋白质列表窗口"""
        if not hasattr(cell, 'protein_list') or not cell.protein_list:
            messagebox.showinfo("提示", "该细胞没有蛋白质")
            return
        
        # 如果窗口已经存在，就将其带到前台
        window_key = f"{cell.name}_proteins"
        if window_key in self.protein_info_windows:
            window = self.protein_info_windows[window_key]
            window.deiconify()  # 显示窗口
            window.lift()       # 置于顶层
            return
        
        # 创建新窗口
        protein_window = tk.Toplevel(self.root)
        protein_window.title(f"蛋白质列表 - {cell.name}")
        protein_window.geometry("900x600")
        
        # 保存窗口引用
        self.protein_info_windows[window_key] = protein_window
        
        # 绑定窗口关闭事件
        def on_protein_window_close():
            if window_key in self.protein_info_windows:
                del self.protein_info_windows[window_key]
            protein_window.destroy()
        
        protein_window.protocol("WM_DELETE_WINDOW", on_protein_window_close)
        
        # 创建主框架
        main_frame = ttk.Frame(protein_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=f"细胞 {cell.name} 的蛋白质列表",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 创建带有滚动条的列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建Treeview显示蛋白质列表
        columns = ("序号", "蛋白质序列", "长度", "代谢率")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        
        # 调整列宽
        tree.column("序号", width=50)
        tree.column("蛋白质序列", width=400)
        tree.column("长度", width=80)
        tree.column("代谢率", width=100)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll.grid(row=0, column=1, sticky='ns')
        
        # 配置网格权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 填充数据
        for i, protein in enumerate(cell.protein_list, 1):
            sequence = str(protein)
            length = len(sequence)
            metabolic_rate = getattr(protein, 'metabolic', 0)
            
            # 截断长序列用于显示
            display_seq = sequence[:50] + "..." if length > 50 else sequence
            
            tree.insert("", "end", values=(
                i, 
                display_seq, 
                length, 
                f"{metabolic_rate:.2f}"
            ))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        # 查看蛋白质结构按钮
        def on_view_structure():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("提示", "请先选择一个蛋白质")
                return
            
            # 获取选中的蛋白质索引
            item = tree.selection()[0]
            item_index = tree.index(item)
            
            if 0 <= item_index < len(cell.protein_list):
                selected_protein = cell.protein_list[item_index]
                self.show_protein_structure(selected_protein, cell.name, item_index+1)
        
        view_button = ttk.Button(
            button_frame,
            text="查看蛋白质结构",
            command=on_view_structure,
            width=20
        )
        view_button.pack(side='left', padx=5)
        
        # 刷新按钮
        def on_refresh():
            # 关闭当前窗口
            on_protein_window_close()
            # 重新打开窗口
            self.show_protein_list(cell)
        
        refresh_button = ttk.Button(
            button_frame,
            text="刷新列表",
            command=on_refresh,
            width=15
        )
        refresh_button.pack(side='left', padx=5)
        
        # 关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=on_protein_window_close,
            width=15
        )
        close_button.pack(side='left', padx=5)
        
        # 双击查看蛋白质结构
        tree.bind("<Double-1>", lambda e: on_view_structure())
    
    def show_protein_structure(self, protein, cell_name, protein_index):
        """显示蛋白质结构（预留函数，由你填充具体实现）"""
        # 创建新窗口
        structure_window = tk.Toplevel(self.root)
        structure_window.title(f"蛋白质结构 - {cell_name} 的蛋白质 {protein_index}")
        structure_window.geometry("600x400")
        
        # 主框架
        main_frame = ttk.Frame(structure_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=f"细胞 {cell_name} 的蛋白质 {protein_index}",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 基本信息
        info_frame = ttk.LabelFrame(main_frame, text="蛋白质信息", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        # 序列
        sequence = str(protein)
        length = len(sequence)
        
        self.add_info_row(info_frame, 0, "序列长度:", str(length), ('Arial', 10), ('Arial', 10, 'italic'))
        
        # 代谢率
        metabolic_rate = getattr(protein, 'metabolic', 0)
        self.add_info_row(info_frame, 1, "代谢率:", f"{metabolic_rate:.2f}", ('Arial', 10), ('Arial', 10, 'italic'))
        
        # 功能字典（如果有）
        if hasattr(protein, 'function_dict') and protein.function_dict:
            self.add_info_row(info_frame, 2, "功能数量:", str(len(protein.function_dict)), ('Arial', 10), ('Arial', 10, 'italic'))
        
        # 序列显示区域
        seq_frame = ttk.LabelFrame(main_frame, text="蛋白质序列", padding=10)
        seq_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建文本区域显示完整序列
        seq_text = scrolledtext.ScrolledText(seq_frame, height=8, wrap='word')
        seq_text.pack(fill='both', expand=True)
        
        # 显示序列，可以按氨基酸着色
        seq_text.insert('1.0', sequence)
        seq_text.config(state='normal')
        
        # 氨基酸颜色映射（与draw_cell.py中的一致）
        amino_acid_colors = {
            'A': '#C8C8C8', 'R': '#145AFF', 'N': '#00DCDC', 'D': '#E60A0A',
            'C': '#E6E600', 'Q': '#00DCDC', 'E': '#E60A0A', 'G': '#EBEBEB',
            'H': '#8282D2', 'I': '#0F820F', 'L': '#0F820F', 'K': '#145AFF',
            'M': '#E6E600', 'F': '#3232AA', 'P': '#DC9682', 'S': '#FA9600',
            'T': '#FA9600', 'W': '#B45AB4', 'Y': '#3232AA', 'V': '#0F820F'
        }
        
        # 为每个氨基酸着色
        for i, aa in enumerate(sequence):
            if aa.upper() in amino_acid_colors:
                color = amino_acid_colors[aa.upper()]
                # 计算插入位置
                start_index = f"1.{i}"
                end_index = f"1.{i+1}"
                seq_text.tag_add(aa, start_index, end_index)
                seq_text.tag_config(aa, foreground=color)
        
        seq_text.config(state='disabled')
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        # 关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=structure_window.destroy,
            width=15
        )
        close_button.pack()
        
        # 提示信息
        ttk.Label(
            main_frame,
            text="提示：这里可以添加蛋白质3D结构可视化或其他分析功能",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack(pady=(10, 0))