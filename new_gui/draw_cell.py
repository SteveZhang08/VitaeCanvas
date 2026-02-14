import pygame
import sys
import random
import math
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *

class ColoredCircle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x, self.y)
    
    def change_color(self, new_color):
        self.color = new_color
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

L = [(-4,0),(-3.7,1),(-3.4,2),(-3.7,-1),(-3.4,-2)]
R = [(4,0),(3.7,1),(3.4,2),(3.7,-1),(3.4,-2)]
U = [(-2,4),(-1,4.7),(0,5),(1,4.7),(2,4)]
D = [(-2,-4),(-1,-4.7),(0,-5),(1,-4.7),(2,-4)]
LU = [(-3,3)]
LD = [(-3,-3)]
RU = [(3,3)]
RD = [(3,-3)]

def re_draw_circle(x, y, color):
    global circles
    circles = []
    
    directions = [L, R, U, D, LU, LD, RU, RD]
    
    for direction_coords in directions:
        direction_circles = []
        for _x, _y in direction_coords:
            screen_x = _x * 20 + x
            screen_y = _y * 20 + y
            circle = ColoredCircle(screen_x, screen_y, 5, color)
            direction_circles.append(circle)
        circles.append(direction_circles)

amino_acid_colors = {
    'A': (200, 200, 200),  
    'R': (20, 90, 255),    
    'N': (0, 220, 220),    
    'D': (230, 10, 10),    
    'C': (230, 230, 0),    
    'Q': (0, 220, 220),    
    'E': (230, 10, 10),    
    'G': (235, 235, 235),  
    'H': (130, 130, 210),  
    'I': (15, 130, 15),    
    'L': (15, 130, 15),    
    'K': (20, 90, 255),    
    'M': (230, 230, 0),    
    'F': (50, 50, 170),    
    'P': (220, 150, 130),  
    'S': (250, 150, 0),    
    'T': (250, 150, 0),    
    'W': (180, 90, 180),   
    'Y': (50, 50, 170),    
    'V': (15, 130, 15)     
}

def draw_protein(protein_sequence, x, y, radius, spacing):
    for i, aa in enumerate(protein_sequence):
        color = amino_acid_colors.get(aa, (255, 255, 255))
        circle = ColoredCircle(x + i * spacing, y, radius, color)
        circle.draw(screen)

def create_protein_circle(protein_sequence, x, y, base_radius=2):
    """
    将蛋白质序列转换为一个彩色圆形对象
    
    参数:
    protein_sequence: 蛋白质氨基酸序列字符串
    x, y: 圆形中心坐标
    base_radius: 半径
    
    返回:
    ColoredCircle对象
    """  
    # 过滤无效字符
    valid_sequence = [aa for aa in protein_sequence.upper() if aa in amino_acid_colors]
    
    if not valid_sequence:
        # 如果没有有效氨基酸，返回默认灰色圆形
        return ColoredCircle(x, y, base_radius, (128, 128, 128))
    
    # 计算平均颜色
    total_r, total_g, total_b = 0, 0, 0
    count = len(valid_sequence)
    
    for amino_acid in valid_sequence:
        r, g, b = amino_acid_colors[amino_acid]
        total_r += r
        total_g += g
        total_b += b
    
    # 计算平均值
    avg_color = (
        int(total_r / count),
        int(total_g / count),
        int(total_b / count)
    )
    sequence_length = len(valid_sequence)
    radius = min(base_radius + int(math.log(sequence_length + 1) * 2), base_radius * 2)

    return ColoredCircle(x, y, radius, avg_color)

class Draw_Cell():
    def __init__(self, screen, cell:cells.Cell):
        self.screen = screen
        self.cell = cell
        self.cell_x = self.cell.x
        self.cell_y = self.cell.y
        self.calc_cell_coordinates()
        self.calc_protein_coordinates()
        
    def draw(self):
        if self.cell.x != self.cell_x or self.cell.y != self.cell_y:
            # 如果细胞发生移动，先移动细胞
            self.move((self.cell.x-self.cell_x)*200, (self.cell.y-self.cell_y)*220)
            self.cell_x = self.cell.x
            self.cell_y = self.cell.y
            

        re_draw_circle(self.x,self.y, self.cell.color)
        for idx, direction in enumerate(circles):
            for circle in direction:
                if idx in (0,1):
                    circle.move(random.randint(-1, 1), 0)
                elif idx in (2,3):
                    circle.move(0, random.randint(-1, 1))
                elif idx in (4,5,6,7):
                    circle.move(random.randint(-1, 1), random.randint(-1, 1))
                circle.draw(self.screen)

        protein_list = self.cell.protein_list
        for protein, (x, y) in zip(protein_list, self.protein_coordinates):
            protein_circle = create_protein_circle(str(protein), x, y)
            protein_circle.move(random.randint(-1,1), random.randint(-1,1))
            protein_circle.draw(self.screen)
        Cell_Nucleus = ColoredCircle(self.x-30,self.y, 15, (125, 2, 128))
        Cell_Nucleus.move(random.randint(-1,1), random.randint(-1,1))
        Cell_Nucleus.draw(self.screen)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        for idx, (x, y) in enumerate(self.protein_coordinates):
            self.protein_coordinates[idx] = (x + dx, y + dy)
        # self.calc_protein_coordinates()

    def calc_protein_coordinates(self):
        self.protein_coordinates = []
        for _ in self.cell.protein_list:
            self.protein_coordinates.append((random.randint(self.x-15,self.x+50), random.randint(self.y-30,self.y+50)))

    def calc_cell_coordinates(self):
        self.x = self.cell.x*200
        self.y = self.cell.y*220

if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("VitaeCanvas CELL")

    from vitae_system import env
    env1 = env.Environment(-1,-1)
    cell = cells.Cell(env1,0,0)
    draw_cell = Draw_Cell(screen, cell)

    while True:
        screen.fill((0, 130, 180))  # 用蓝色填充屏幕，清除上一帧
        draw_cell.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock = pygame.time.Clock()
        clock.tick(10)