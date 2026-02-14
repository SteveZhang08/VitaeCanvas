"""
添加资源对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random

class AddResourceDialog:
    """添加资源对话框"""
    
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
        self.top.title("添加资源")
        self.top.geometry("400x350")
        self.top.transient(parent)
        self.top.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 资源类型
        ttk.Label(main_frame, text="资源类型:").grid(row=0, column=0, sticky='w', pady=5)
        
        self.resource_type = tk.StringVar(value="Energy")
        resource_types = ["Energy", "O2", "H2O", "Sugar", "Protein", "Lipid"]
        
        resource_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.resource_type,
            values=resource_types,
            state="readonly",
            width=20
        )
        resource_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 资源描述
        self.description_var = tk.StringVar(value="能量资源")
        description_label = ttk.Label(main_frame, textvariable=self.description_var, 
                                     font=('Arial', 9), foreground='gray')
        description_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # 绑定资源类型变化事件
        resource_combo.bind('<<ComboboxSelected>>', self._on_resource_type_changed)
        
        # 数量
        ttk.Label(main_frame, text="数量:").grid(row=2, column=0, sticky='w', pady=5)
        
        self.amount_var = tk.StringVar(value="100")
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var)
        amount_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # 数量滑块
        amount_scale = ttk.Scale(
            main_frame,
            from_=10,
            to=500,
            orient=tk.HORIZONTAL,
            command=lambda v: self.amount_var.set(str(int(float(v))))
        )
        amount_scale.set(100)
        amount_scale.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5, 10))
        
        # 坐标输入
        coord_frame = ttk.LabelFrame(main_frame, text="坐标设置", padding=10)
        coord_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        # X坐标
        ttk.Label(coord_frame, text="X坐标:").grid(row=0, column=0, sticky='w', pady=5)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(coord_frame, textvariable=self.x_var, width=10)
        x_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Y坐标
        ttk.Label(coord_frame, text="Y坐标:").grid(row=0, column=2, sticky='w', pady=5, padx=(20, 0))
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(coord_frame, textvariable=self.y_var, width=10)
        y_entry.grid(row=0, column=3, sticky='w', pady=5, padx=(10, 0))
        
        # 随机坐标按钮
        ttk.Button(
            coord_frame, 
            text="随机坐标", 
            command=self._set_random_coordinates,
            width=10
        ).grid(row=0, column=4, sticky='e', padx=(20, 0))
        
        # 分布设置
        distribution_frame = ttk.Frame(coord_frame)
        distribution_frame.grid(row=1, column=0, columnspan=5, sticky='ew', pady=(10, 0))
        
        ttk.Label(distribution_frame, text="分布:").pack(side=tk.LEFT)
        
        self.distribution_var = tk.StringVar(value="single")
        
        ttk.Radiobutton(
            distribution_frame, 
            text="单点", 
            variable=self.distribution_var, 
            value="single"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Radiobutton(
            distribution_frame, 
            text="3x3区域", 
            variable=self.distribution_var, 
            value="area"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(
            btn_frame, 
            text="确定", 
            command=self._on_ok
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            btn_frame, 
            text="取消", 
            command=self._on_cancel
        ).pack(side=tk.RIGHT)
        
        main_frame.columnconfigure(1, weight=1)
    
    def _on_resource_type_changed(self, event=None):
        """资源类型变化事件"""
        resource_type = self.resource_type.get()
        
        descriptions = {
            "Energy": "细胞代谢所需的基本能量",
            "O2": "氧气，用于细胞呼吸作用",
            "H2O": "水，细胞代谢的重要溶剂",
            "Sugar": "糖类，细胞能量的主要来源",
            "Protein": "蛋白质，细胞结构和功能分子",
            "Lipid": "脂质，细胞膜和能量储存"
        }
        
        self.description_var.set(descriptions.get(resource_type, ""))
        
        # 根据资源类型调整默认数量
        default_amounts = {
            "Energy": "100",
            "O2": "200",
            "H2O": "200",
            "Sugar": "50",
            "Protein": "30",
            "Lipid": "20"
        }
        
        self.amount_var.set(default_amounts.get(resource_type, "100"))
    
    def _set_random_coordinates(self):
        """设置随机坐标"""
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        self.x_var.set(str(x))
        self.y_var.set(str(y))
    
    def _on_ok(self):
        """确定按钮回调"""
        try:
            # 验证输入
            resource_type = self.resource_type.get()
            if not resource_type:
                messagebox.showerror("错误", "请选择资源类型")
                return
            
            try:
                amount = int(self.amount_var.get())
                if amount <= 0:
                    messagebox.showerror("错误", "数量必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "数量必须为整数")
                return
            
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                messagebox.showerror("错误", "坐标必须为整数")
                return
            
            distribution = self.distribution_var.get()
            
            # 准备资源数据
            resource_data = {
                'x': x,
                'y': y,
                'resource_type': resource_type,
                'amount': amount,
                'distribution': distribution
            }
            
            # 调用回调函数
            self.on_confirm(resource_data)
            
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加资源失败: {e}")
    
    def _on_cancel(self):
        """取消按钮回调"""
        self.top.destroy()