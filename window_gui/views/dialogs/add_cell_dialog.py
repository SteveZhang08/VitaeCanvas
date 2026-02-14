"""
添加细胞对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

try:
    from vitae_system import random_DNA
except ImportError:
    random_DNA = None

class AddCellDialog:
    """添加细胞对话框"""
    
    def __init__(self, parent, on_confirm_callback):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            on_confirm_callback: 确认回调函数
        """
        self.on_confirm = on_confirm_callback
        self.result = None
        
        self.top = tk.Toplevel(parent)
        self.top.title("添加细胞")
        self.top.geometry("400x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 细胞名称
        ttk.Label(main_frame, text="细胞名称:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar(value=f"Cell_{int(time.time())}")
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
        ttk.Radiobutton(dna_frame, text="随机生成DNA", 
                       variable=self.dna_source, value="random",
                       command=self._toggle_dna_input).pack(anchor='w')
        
        ttk.Radiobutton(dna_frame, text="手动输入DNA", 
                       variable=self.dna_source, value="manual",
                       command=self._toggle_dna_input).pack(anchor='w')
        
        # DNA长度
        self.length_frame = ttk.Frame(dna_frame)
        self.length_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.length_frame, text="DNA长度:").pack(side=tk.LEFT)
        self.dna_length_var = tk.StringVar(value="100")
        length_entry = ttk.Entry(self.length_frame, textvariable=self.dna_length_var, width=10)
        length_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # DNA序列输入
        dna_input_frame = ttk.Frame(dna_frame)
        dna_input_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(dna_input_frame, text="DNA序列:").pack(anchor='w')
        self.dna_text = tk.Text(dna_input_frame, height=6, width=40)
        self.dna_scroll = ttk.Scrollbar(dna_input_frame, orient='vertical', command=self.dna_text.yview)
        self.dna_text.config(yscrollcommand=self.dna_scroll.set)
        
        self.dna_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dna_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.RIGHT)
        
        # 初始状态
        self._toggle_dna_input()
        main_frame.columnconfigure(1, weight=1)
    
    def _toggle_dna_input(self):
        """切换DNA输入模式"""
        if self.dna_source.get() == "random":
            self.length_frame.pack(fill=tk.X, pady=(10, 0))
            self.dna_text.config(state=tk.DISABLED)
        else:
            self.length_frame.pack_forget()
            self.dna_text.config(state=tk.NORMAL)
    
    def _on_ok(self):
        """确定按钮回调"""
        try:
            # 验证输入
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入细胞名称")
                return
                
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                messagebox.showerror("错误", "坐标必须为整数")
                return
            
            # 获取DNA序列
            if self.dna_source.get() == "random":
                try:
                    length = int(self.dna_length_var.get())
                    if length < 10 or length > 1000:
                        messagebox.showerror("错误", "DNA长度应在10-1000之间")
                        return
                        
                    if random_DNA and hasattr(random_DNA, 'generate_dna'):
                        dna_sequence = random_DNA.generate_dna(length)
                    else:
                        # 生成随机DNA序列（简化）
                        import random
                        bases = ['A', 'T', 'C', 'G']
                        dna_sequence = ''.join(random.choice(bases) for _ in range(length))
                except ValueError:
                    messagebox.showerror("错误", "DNA长度必须为整数")
                    return
            else:
                dna_sequence = self.dna_text.get(1.0, tk.END).strip()
                if not dna_sequence:
                    messagebox.showerror("错误", "请输入DNA序列")
                    return
            
            # 调用回调函数
            self.on_confirm({
                'name': name,
                'x': x,
                'y': y,
                'dna_sequence': dna_sequence
            })
            
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加细胞失败: {e}")
    
    def _on_cancel(self):
        """取消按钮回调"""
        self.top.destroy()