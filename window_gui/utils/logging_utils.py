"""
日志工具
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import time

class LogWidget(ttk.Frame):
    """日志控件"""
    
    def __init__(self, parent, height=10, **kwargs):
        """
        初始化日志控件
        
        Args:
            parent: 父容器
            height: 文本区域高度
        """
        super().__init__(parent, **kwargs)
        
        # 创建滚动文本框
        self.text_area = scrolledtext.ScrolledText(self, height=height, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签
        self.text_area.tag_config('info', foreground='lightgray')
        self.text_area.tag_config('warning', foreground='yellow')
        self.text_area.tag_config('error', foreground='red')
        self.text_area.tag_config('success', foreground='lightgreen')
        
        # 初始为只读
        self.text_area.config(state=tk.DISABLED)
        
        # 清空按钮
        clear_btn = ttk.Button(self, text="清空日志", command=self.clear)
        clear_btn.pack(side=tk.RIGHT, pady=(5, 0))
    
    def log_message(self, message, level='info'):
        """
        记录消息
        
        Args:
            message: 消息内容
            level: 日志级别 (info, warning, error, success)
        """
        self.text_area.config(state=tk.NORMAL)
        
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.text_area.insert(tk.END, log_entry, level)
        self.text_area.see(tk.END)
        
        self.text_area.config(state=tk.DISABLED)
    
    def clear(self):
        """清空日志"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)