"""
蛋白质结构查看器对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ProteinViewerDialog:
    """蛋白质结构查看器"""
    
    def __init__(self, parent):
        """
        初始化蛋白质查看器
        
        Args:
            parent: 父窗口
        """
        self.top = tk.Toplevel(parent)
        self.top.title("蛋白质结构查看器")
        self.top.geometry("900x700")
        self.top.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 蛋白质序列输入
        input_frame = ttk.LabelFrame(control_frame, text="蛋白质序列输入", padding=10)
        input_frame.pack(fill=tk.X)
        
        # 序列输入
        seq_frame = ttk.Frame(input_frame)
        seq_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(seq_frame, text="序列:").pack(side=tk.LEFT)
        self.sequence_var = tk.StringVar(value="GACLICYWSCCMNEEEFGQEGHILKMFPS")
        sequence_entry = ttk.Entry(seq_frame, textvariable=self.sequence_var, width=50)
        sequence_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # 示例序列按钮
        example_frame = ttk.Frame(input_frame)
        example_frame.pack(fill=tk.X)
        
        ttk.Label(example_frame, text="示例序列:").pack(side=tk.LEFT)
        
        examples = [
            ("短链", "GACLIC"),
            ("中等链", "GACLICYWSCCMNE"),
            ("长链", "GACLICYWSCCMNEEEFGQEGHILKMFPS")
        ]
        
        for name, seq in examples:
            ttk.Button(example_frame, text=name, 
                      command=lambda s=seq: self.sequence_var.set(s)) \
                .pack(side=tk.LEFT, padx=(5, 0))
        
        # 控制按钮
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="显示结构", 
                  command=self.show_structure).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="清除", 
                  command=self.clear_display).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="保存图像", 
                  command=self.save_image).pack(side=tk.RIGHT)
        
        # 显示区域
        display_frame = ttk.LabelFrame(main_frame, text="蛋白质结构显示", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布容器
        self.canvas_frame = ttk.Frame(display_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    def show_structure(self):
        """显示蛋白质结构"""
        sequence = self.sequence_var.get().strip()
        
        if not sequence:
            messagebox.showwarning("警告", "请输入蛋白质序列")
            return
        
        self.status_var.set("正在绘制蛋白质结构...")
        self.top.update()
        
        try:
            # 清除之前的显示
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            # 创建图形
            fig = self._create_protein_figure(sequence)
            
            # 嵌入到Tkinter
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.status_var.set(f"蛋白质结构已显示 (序列长度: {len(sequence)})")
            
        except Exception as e:
            messagebox.showerror("错误", f"显示蛋白质结构失败: {e}")
            self.status_var.set("显示失败")
    
    def _create_protein_figure(self, sequence):
        """
        创建蛋白质结构图形
        
        Args:
            sequence: 蛋白质序列
            
        Returns:
            matplotlib.figure.Figure: 蛋白质结构图形
        """
        # 尝试使用专业的蛋白质可视化模块
        try:
            # 如果可用，使用更专业的蛋白质可视化
            from Protein_structure_show import draw_protein
            fig = draw_protein(sequence)
        except ImportError:
            # 备选方案：使用matplotlib绘制简化版本
            fig = self._draw_simple_protein(sequence)
        
        return fig
    
    def _draw_simple_protein(self, sequence):
        """
        绘制简化的蛋白质结构
        
        Args:
            sequence: 蛋白质序列
            
        Returns:
            matplotlib.figure.Figure: 蛋白质结构图形
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 氨基酸颜色映射
        amino_colors = {
            'A': 'red',    # 丙氨酸
            'R': 'blue',   # 精氨酸
            'N': 'green',  # 天冬酰胺
            'D': 'cyan',   # 天冬氨酸
            'C': 'yellow', # 半胱氨酸
            'E': 'magenta',# 谷氨酸
            'Q': 'orange', # 谷氨酰胺
            'G': 'pink',   # 甘氨酸
            'H': 'brown',  # 组氨酸
            'I': 'purple', # 异亮氨酸
            'L': 'gray',   # 亮氨酸
            'K': 'olive',  # 赖氨酸
            'M': 'teal',   # 甲硫氨酸
            'F': 'navy',   # 苯丙氨酸
            'P': 'coral',  # 脯氨酸
            'S': 'lime',   # 丝氨酸
            'T': 'gold',   # 苏氨酸
            'W': 'indigo', # 色氨酸
            'Y': 'violet', # 酪氨酸
            'V': 'salmon'  # 缬氨酸
        }
        
        # 绘制蛋白质链
        x_positions = []
        y_positions = []
        colors = []
        
        # 生成蛋白质结构数据（简化：螺旋和折叠）
        import numpy as np
        
        for i, aa in enumerate(sequence.upper()):
            # 模拟二级结构
            if i % 4 == 0:
                # α-螺旋
                x = i * 0.5
                y = np.sin(i * 0.5) * 0.3
            elif i % 4 == 2:
                # β-折叠
                x = i * 0.5
                y = np.cos(i * 0.3) * 0.5
            else:
                # 无规则卷曲
                x = i * 0.5
                y = np.random.normal(0, 0.2)
            
            x_positions.append(x)
            y_positions.append(y)
            colors.append(amino_colors.get(aa, 'black'))
        
        # 绘制连接线
        ax.plot(x_positions, y_positions, 'k-', alpha=0.3, linewidth=1)
        
        # 绘制氨基酸点
        for i, (x, y, color) in enumerate(zip(x_positions, y_positions, colors)):
            ax.scatter(x, y, s=100, c=color, edgecolors='black', linewidths=1, zorder=5)
            
            # 标记氨基酸
            if len(sequence) <= 30:  # 只在序列较短时显示标签
                ax.text(x, y + 0.05, sequence[i], 
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # 设置图形属性
        ax.set_title(f"蛋白质结构可视化: {sequence[:20]}..." if len(sequence) > 20 else f"蛋白质结构可视化: {sequence}")
        ax.set_xlabel("序列位置")
        ax.set_ylabel("结构坐标")
        ax.grid(True, alpha=0.3)
        
        # 添加颜色图例
        from matplotlib.patches import Patch
        
        # 选择部分氨基酸显示图例
        unique_aas = set(sequence.upper())
        legend_elements = []
        for aa in sorted(unique_aas):
            if aa in amino_colors:
                legend_elements.append(
                    Patch(facecolor=amino_colors[aa], edgecolor='black', 
                         label=f"{aa}: {self._get_amino_name(aa)}")
                )
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', 
                     fontsize=8, title="氨基酸")
        
        fig.tight_layout()
        return fig
    
    def _get_amino_name(self, code):
        """获取氨基酸名称"""
        amino_names = {
            'A': 'Alanine',
            'R': 'Arginine',
            'N': 'Asparagine',
            'D': 'Aspartic Acid',
            'C': 'Cysteine',
            'E': 'Glutamic Acid',
            'Q': 'Glutamine',
            'G': 'Glycine',
            'H': 'Histidine',
            'I': 'Isoleucine',
            'L': 'Leucine',
            'K': 'Lysine',
            'M': 'Methionine',
            'F': 'Phenylalanine',
            'P': 'Proline',
            'S': 'Serine',
            'T': 'Threonine',
            'W': 'Tryptophan',
            'Y': 'Tyrosine',
            'V': 'Valine'
        }
        return amino_names.get(code, 'Unknown')
    
    def clear_display(self):
        """清除显示"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.status_var.set("显示已清除")
    
    def save_image(self):
        """保存图像"""
        from tkinter import filedialog
        
        # 获取当前图形
        for widget in self.canvas_frame.winfo_children():
            if hasattr(widget, 'figure'):
                fig = widget.figure
                break
        else:
            messagebox.showwarning("警告", "没有可保存的图像")
            return
        
        # 选择保存路径
        filetypes = [
            ("PNG图像", "*.png"),
            ("PDF文档", "*.pdf"),
            ("SVG矢量图", "*.svg"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="保存蛋白质结构图像",
            defaultextension=".png",
            filetypes=filetypes
        )
        
        if filename:
            try:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", f"图像已保存到:\n{filename}")
                self.status_var.set(f"图像已保存: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图像失败: {e}")