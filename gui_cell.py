import tkinter as tk
from tkinter import ttk
from collections import Counter
from vitae_system.cells import Cell, DNA, Protein
from vitae_system.env import Environment
from vitae_system.random_DNA import *

class CellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("细胞模拟器")
        self.root.geometry("800x600")
        
        # 记录最高代谢率及其蛋白质序列
        self.max_metabolic_rate = 0.0
        self.max_metabolic_proteins = []
        
        # 记录所有出现过的蛋白质(存储字符串形式)
        self.all_protein_strings = []
        self.most_common_protein = "NONE"
        
        # 蛋白质统计相关
        self.total_proteins_count = 0
        self.total_proteins_length = 0
        self.avg_length = 0.0
        
        # 细胞计数器
        self.cell_counter = 0
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建显示区域
        self.create_display_area()
        
        # 创建控制区域
        self.create_control_area()
        
        # 绑定回车键
        self.root.bind('<Return>', self.on_enter_pressed)
        
        # 初始状态
        self.env1 = None
        self.cell1 = None
        
    def create_display_area(self):
        # 显示区域框架
        display_frame = ttk.LabelFrame(self.main_frame, text="细胞信息", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 细胞ID显示
        self.cell_id_label = ttk.Label(display_frame, text="细胞ID: 未创建")
        self.cell_id_label.pack(anchor=tk.W)
        
        # 位置信息
        self.position_label = ttk.Label(display_frame, text="细胞位置: 未创建")
        self.position_label.pack(anchor=tk.W)
        
        # 蛋白质序列显示
        self.protein_label = ttk.Label(display_frame, text="蛋白质序列: 未创建", wraplength=700)
        self.protein_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 5))
        
        # 代谢率
        self.metabolic_label = ttk.Label(display_frame, text="代谢率: 未创建")
        self.metabolic_label.pack(anchor=tk.W)
        
        # 最高代谢率记录
        self.max_metabolic_label = ttk.Label(display_frame, 
                                          text=f"最高代谢率: {self.max_metabolic_rate:.4f} (未记录)")
        self.max_metabolic_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.max_protein_label = ttk.Label(display_frame, 
                                         text="最高代谢率的蛋白质序列: 无", 
                                         wraplength=700)
        self.max_protein_label.pack(anchor=tk.W, fill=tk.X)
        
        # 最常见蛋白质
        self.common_protein_label = ttk.Label(display_frame, 
                                           text="出现最多的蛋白质: NONE")
        self.common_protein_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 蛋白质平均长度
        self.avg_length_label = ttk.Label(display_frame,
                                       text="蛋白质平均长度: 0.00")
        self.avg_length_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 颜色显示
        self.color_label = ttk.Label(display_frame, text="细胞颜色: 未创建")
        self.color_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.color_display = tk.Canvas(display_frame, width=50, height=20, bg='white')
        self.color_display.pack(anchor=tk.W, pady=(0, 10))
        
        # 环境信息
        self.env_label = ttk.Label(display_frame, text="环境信息: 未创建")
        self.env_label.pack(anchor=tk.W)
        
    def create_control_area(self):
        # 控制区域框架
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X)
        
        # 提示标签
        ttk.Label(control_frame, text="按回车键创建新细胞").pack(side=tk.LEFT)
        
        # 重置按钮
        ttk.Button(control_frame, text="重置统计", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        ttk.Button(control_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT)
    
    def on_enter_pressed(self, event=None):
        # 创建新环境和细胞
        self.env1 = Environment()
        self.cell1 = Cell(self.env1, 0, 0, dna=DNA(generate_dna(300)))
        
        # 更新细胞计数器
        self.cell_counter += 1
        
        # 更新蛋白质统计
        self.update_protein_stats()
        
        # 更新显示
        self.update_display()
        
        # 检查并更新最高代谢率记录
        self.update_metabolic_stats()
    
    def update_protein_stats(self):
        """更新蛋白质统计信息"""
        # 添加当前细胞的蛋白质(转换为字符串)到总列表
        self.all_protein_strings.extend(str(protein) for protein in self.cell1.protein_list)
        
        # 更新蛋白质长度统计
        current_proteins = len(self.cell1.protein_list)
        if current_proteins > 0:
            self.total_proteins_count += current_proteins
            self.total_proteins_length += sum(len(p) for p in self.cell1.protein_list)
            self.avg_length = self.total_proteins_length / self.total_proteins_count
        
        # 计算最常见的蛋白质
        if self.all_protein_strings:
            protein_counts = Counter(self.all_protein_strings)
            max_count = max(protein_counts.values())
            
            # 找出所有达到最大计数的蛋白质
            most_common = [p for p, count in protein_counts.items() if count == max_count]
            
            # 如果有多个蛋白质并列最多，显示NONE
            if len(most_common) == 1:
                self.most_common_protein = most_common[0]
            else:
                self.most_common_protein = "NONE (并列)"
    
    def update_metabolic_stats(self):
        """更新代谢率统计信息"""
        if self.cell1.metabolic_rate > self.max_metabolic_rate:
            self.max_metabolic_rate = self.cell1.metabolic_rate
            # 存储蛋白质的字符串表示
            self.max_metabolic_proteins = [str(p) for p in self.cell1.protein_list]
            self.max_metabolic_label.config(
                text=f"最高代谢率: {self.max_metabolic_rate:.4f} (新记录!)",
                foreground="red")
            self.max_protein_label.config(
                text=f"最高代谢率的蛋白质序列: {self.max_metabolic_proteins}")
        else:
            self.max_metabolic_label.config(
                text=f"最高代谢率: {self.max_metabolic_rate:.4f} (当前: {self.cell1.metabolic_rate:.4f})",
                foreground="black")
    
    def update_display(self):
        """更新所有显示信息"""
        # 更新细胞ID
        self.cell_id_label.config(text=f"细胞ID: {self.cell_counter}")
        
        # 更新位置信息
        self.position_label.config(text=f"细胞位置: ({self.cell1.x}, {self.cell1.y})")
        
        # 更新蛋白质序列(显示原始Protein对象)
        self.protein_label.config(text=f"蛋白质序列: {self.cell1.protein_list}")
        
        # 更新代谢率
        self.metabolic_label.config(text=f"代谢率: {self.cell1.metabolic_rate:.4f}")
        
        # 更新最常见蛋白质
        self.common_protein_label.config(text=f"出现最多的蛋白质: {self.most_common_protein}")
        
        # 更新蛋白质平均长度
        self.avg_length_label.config(text=f"蛋白质平均长度: {self.avg_length:.2f}")
        
        # 更新颜色显示
        if hasattr(self.cell1, 'color'):
            color_hex = self.rgb_to_hex(self.cell1.color)
            self.color_label.config(text=f"细胞颜色: {self.cell1.color}")
            self.color_display.config(bg=color_hex)
        else:
            self.color_label.config(text="细胞颜色: 无颜色属性")
            self.color_display.config(bg='white')
        
        # 更新环境信息
        env_info = self.env1.read(1, 1)
        self.env_label.config(text=f"环境信息: {env_info}")
    
    def reset_stats(self):
        """重置所有统计信息"""
        self.max_metabolic_rate = 0.0
        self.max_metabolic_proteins = []
        self.all_protein_strings = []
        self.most_common_protein = "NONE"
        self.total_proteins_count = 0
        self.total_proteins_length = 0
        self.avg_length = 0.0
        self.cell_counter = 0
        
        # 更新显示
        self.max_metabolic_label.config(text=f"最高代谢率: {self.max_metabolic_rate:.4f} (已重置)")
        self.max_protein_label.config(text="最高代谢率的蛋白质序列: 无")
        self.common_protein_label.config(text=f"出现最多的蛋白质: {self.most_common_protein}")
        self.avg_length_label.config(text="蛋白质平均长度: 0.00")
        self.cell_id_label.config(text="细胞ID: 未创建")
    
    @staticmethod
    def rgb_to_hex(rgb):
        """将RGB元组转换为十六进制颜色代码"""
        return "#{:02x}{:02x}{:02x}".format(*rgb)

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = CellGUI(root)
    root.mainloop()