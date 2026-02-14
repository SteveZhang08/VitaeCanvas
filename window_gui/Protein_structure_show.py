import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

class MatplotlibTurtle:
    def __init__(self, ax, start_pos=(0, 0), start_angle=0):
        """
        初始化Matplotlib画笔对象
        
        参数:
        ax: Matplotlib的Axes对象
        start_pos: 起始位置 (x, y)
        start_angle: 起始角度（度），0表示向右（正东）
        """
        self.ax = ax
        self.x, self.y = start_pos
        self.angle = start_angle  # 角度制
        self.pen_down = True
        self.pen_color = 'black'
        self.pen_size = 1
        self.paths = []  # 存储所有路径段: [(points, color, size), ...]
        self.current_path = []  # 当前路径点
        
        # 如果画笔落下，开始记录路径
        if self.pen_down:
            self.current_path.append((self.x, self.y))
    
    def goto(self, x, y):
        """
        移动到指定位置
        
        参数:
        x, y: 目标位置坐标
        """
        if self.pen_down:
            # 如果画笔落下，记录路径
            self.current_path.append((x, y))
        
        # 更新位置
        self.x, self.y = x, y
    
    def setheading(self, angle):
        """
        设置画笔方向
        
        参数:
        angle: 新的角度（度）
        """
        self.angle = angle
    
    def heading(self):
        """
        获取当前画笔方向
        
        返回:
        当前角度（度）
        """
        head = self.angle%360
        if head > 180:
            return head - 360
        return head
    
    def up(self):
        """抬起画笔（停止绘制）"""
        self.pen_down = False
        # 结束当前路径段
        if self.current_path:
            self.paths.append((self.current_path, self.pen_color, self.pen_size))
            self.current_path = []
    
    def down(self):
        """落下画笔（开始绘制）"""
        self.pen_down = True
        # 开始新路径段
        self.current_path = [(self.x, self.y)]
    
    def pensize(self, size):
        """
        设置画笔粗细
        
        参数:
        size: 画笔粗细
        """
        self.pen_size = size
    
    def color(self, color):
        """
        设置画笔颜色
        
        参数:
        color: 颜色值（可以是字符串名称或十六进制代码）
        """
        self.up()
        self.pen_color = color
        self.down()
    
    def forward(self, distance):
        """
        向前移动指定距离
        
        参数:
        distance: 移动距离
        """
        # 计算终点
        rad = np.radians(self.angle)
        dx = distance * np.cos(rad)
        dy = distance * np.sin(rad)
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 移动到新位置
        self.goto(new_x, new_y)
    
    def backward(self, distance):
        """
        向后移动指定距离
        
        参数:
        distance: 移动距离
        """
        self.forward(-distance)
    
    def right(self, angle):
        """
        向右旋转指定角度
        
        参数:
        angle: 旋转角度（度）
        """
        self.angle -= angle
    
    def left(self, angle):
        """
        向左旋转指定角度
        
        参数:
        angle: 旋转角度（度）
        """
        self.angle += angle
    
    def draw(self):
        """
        绘制所有记录的路径到Matplotlib图表
        """
        # 确保当前路径被保存
        if self.pen_down and self.current_path:
            self.up()
        
        # 绘制所有路径
        for path, color, size in self.paths:
            if len(path) > 1:
                x_vals = [p[0] for p in path]
                y_vals = [p[1] for p in path]
                self.ax.plot(x_vals, y_vals, color=color, linewidth=size, solid_capstyle='round')
    
    def get_position(self):
        """
        获取当前位置
        
        返回:
        (x, y) 元组
        """
        return (self.x, self.y)

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import protein

amino_acid_colors = {
    'A': '#C8C8C8',  # 铝灰 (疏水)
    'R': '#145AFF',  # 钴蓝 (碱性)
    'N': '#00DCDC',  # 青蓝 (极性)
    'D': '#E60A0A',  # 鲜红 (酸性)
    'C': '#E6E600',  # 明黄 (含硫)
    'Q': '#00DCDC',  # 青蓝 (极性)
    'E': '#E60A0A',  # 鲜红 (酸性)
    'G': '#EBEBEB',  # 银白 (特殊结构)
    'H': '#8282D2',  # 淡紫 (碱性)
    'I': '#0F820F',  # 深绿 (疏水)
    'L': '#0F820F',  # 深绿 (疏水)
    'K': '#145AFF',  # 钴蓝 (碱性)
    'M': '#E6E600',  # 明黄 (含硫)
    'F': '#3232AA',  # 靛蓝 (芳香)
    'P': '#DC9682',  # 粉橙 (环状)
    'S': '#FA9600',  # 橙黄 (极性)
    'T': '#FA9600',  # 橙黄 (极性)
    'W': '#B45AB4',  # 紫红 (芳香)
    'Y': '#3232AA',  # 靛蓝 (芳香)
    'V': '#0F820F'   # 深绿 (疏水)
}

global LENGTH

# GACLICYWSCCMNEEEFGQEGHILKMFPS
# [['GACL', 'sheet'], ['ICYW', 'sheet'], ['SCCM', 'sheet'], ['NEEE', 'helix'], ['FG', 'none']]

# 在绘制蛋白质结构之前添加图例
def add_amino_acid_legend(ax, protein_structure, amino_acid_colors):
    """添加氨基酸颜色图例，基于实际出现的氨基酸"""
    # 收集所有实际出现的氨基酸
    unique_amino_acids = set()
    for segment in protein_structure:
        sequence = segment[0]
        for aa in sequence:
            unique_amino_acids.add(aa)
    
    # 按字母顺序排序
    sorted_amino_acids = sorted(unique_amino_acids)
    
    # 创建图例元素
    legend_elements = []
    for aa in sorted_amino_acids:
        color = amino_acid_colors.get(aa, '#000000')  # 默认黑色
        legend_elements.append(
            plt.Line2D([0], [0], color=color, lw=4, label=f"{aa}")
        )
    
    # 添加图例
    ax.legend(
        handles=legend_elements,
        loc='center left',
        bbox_to_anchor=(1.05, 0.5),
        frameon=False,
        title="Amino Acids in Protein",
        title_fontsize='large',
        fontsize=10,
        ncol=2  # 分两列显示
    )

def sheet(pen: MatplotlibTurtle, sequence):
    global direction
    if pen.heading() == 0:
        direction = 1
    elif pen.heading() == 180:
        direction = -1
    def turn(angle):
        if direction == 1:
            pen.right(angle)
        elif direction == -1:
            pen.left(angle)

    pen.color(amino_acid_colors[sequence[0]])
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[1]])
    turn(35)
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[2]])
    turn(110)
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[3]])
    turn(35)
    pen.forward(LENGTH)

def helix(pen: MatplotlibTurtle, sequence):
    global direction
    if pen.heading() == 0:
        direction = 1
    elif pen.heading() == 180:
        direction = -1
    def turn(angle):
        if direction == 1:
            pen.right(angle)
        elif direction == -1:
            pen.left(angle)
    pen.color(amino_acid_colors[sequence[0]])
    pen.forward(LENGTH/10)
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(8)
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(10)
    pen.color(amino_acid_colors[sequence[1]])
    for _ in range(10):
        pen.forward(LENGTH/10)
        turn(9)
    pen.color(amino_acid_colors[sequence[2]])
    for _ in range(10):
        pen.forward(LENGTH/15)
        turn(9)
    pen.color(amino_acid_colors[sequence[3]])
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(10)
    for _ in range(5):
        pen.forward(LENGTH/20)
        turn(8)
    pen.forward(LENGTH)

def none(pen: MatplotlibTurtle, sequence):
    for amino_acid in sequence:
        pen.color(amino_acid_colors[amino_acid])
        pen.forward(LENGTH)

draw = {'sheet': sheet, 'helix': helix, 'none': none}

def draw_protein(protein_structure, title="Protein Structure Visualization", length=50, show=False):
    global LENGTH
    LENGTH = length
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.set_axis_off()  # 隐藏坐标轴
    p = MatplotlibTurtle(ax, start_pos=(-50, 100), start_angle=0)
    p.up()
    p.goto(-50, 100)
    p.down()
    p.pensize(10)
    protein_structure = protein.structure(protein_structure)
    # 在绘制之前添加图例
    add_amino_acid_legend(ax, protein_structure, amino_acid_colors)
    for sequence in protein_structure:
        draw[sequence[1]](p, sequence[0])
    p.draw()
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # 右侧留出15%空间给图例
    # 显示图像
    if show:
        plt.tight_layout()
        plt.show()
    return fig

if __name__ == "__main__":
    draw_protein("GACLICYWSCCMNEEEFGQEGHILKMFPS")
