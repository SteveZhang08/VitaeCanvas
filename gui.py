import pygame
import sys
import time
from vitae_system import env, cells, metabolism

# 初始化Pygame
pygame.init()

# 常量定义
global CELL_SIZE
CELL_SIZE = 40  # 每个网格的像素大小
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (10, 20, 30)  # 深蓝色背景
GRID_COLOR = (40, 50, 70)  # 网格线颜色

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vitae System Simulation")
clock = pygame.time.Clock()

# 视口控制变量
view_offset_x = 0
view_offset_y = 0
dragging = False
last_mouse_pos = (0, 0)

class SimulationController:
    """主控模拟器，协调各系统运行"""
    def __init__(self) -> None:
        self.env = env.Environment(-1, -1)  # 无限网格环境
        self.cell_list = []
        
        # 初始化细胞和资源
        dna = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")
        self.cell_list.append(cells.Cell(self.env, 0, 0, dna=dna, name="Vita"))
        
        # 添加初始资源
        resource_list = [
            env.Energy(100), 
            env.O2(200), 
            env.H2O(200), 
            cells.SugarList([cells.Sugar(6, 12, 6)])
        ]
        for resource in resource_list:
            self.env.write(0, 0, resource)
        
        # 在另一个位置添加能量
        self.env.write(0, 1, env.Energy(200))
    
    def update(self):
        """更新模拟状态"""
        new_cells = []
        for cell in self.cell_list:
            # 执行代谢过程
            metabolism_system = metabolism.MetabolismSystem(cell, self.env)
            new_cell = metabolism_system.re_info()
            
            if new_cell:
                new_cells.append(new_cell)
        
        # 添加新细胞到列表
        self.cell_list.extend(new_cells)
        
        # 资源扩散
        self.env.resources_diffusion()
    
    def get_cells_in_view(self, view_x, view_y, view_width, view_height):
        """获取当前视口范围内的细胞"""
        visible_cells = []
        for cell in self.cell_list:
            # 计算细胞在视口中的位置
            cell_screen_x = cell.x * CELL_SIZE + view_x
            cell_screen_y = cell.y * CELL_SIZE + view_y
            
            # 检查细胞是否在视口范围内
            if (0 <= cell_screen_x <= SCREEN_WIDTH and 
                0 <= cell_screen_y <= SCREEN_HEIGHT):
                visible_cells.append(cell)
        
        return visible_cells

# 创建模拟控制器
simulation = SimulationController()

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 鼠标拖动视口
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                dragging = True
                last_mouse_pos = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键
                dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                view_offset_x += dx
                view_offset_y += dy
                last_mouse_pos = event.pos
        
        # 鼠标滚轮缩放
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # 滚轮向上
                CELL_SIZE = min(100, CELL_SIZE + 5)
            elif event.y < 0:  # 滚轮向下
                CELL_SIZE = max(10, CELL_SIZE - 5)
    
    # 更新模拟状态
    simulation.update()
    
    # 渲染
    screen.fill(BACKGROUND_COLOR)
    
    # 计算网格绘制范围
    start_x = -view_offset_x // CELL_SIZE - 1
    end_x = start_x + SCREEN_WIDTH // CELL_SIZE + 2
    start_y = -view_offset_y // CELL_SIZE - 1
    end_y = start_y + SCREEN_HEIGHT // CELL_SIZE + 2
    
    # 绘制网格线
    for x in range(start_x, end_x):
        screen_x = x * CELL_SIZE + view_offset_x
        pygame.draw.line(screen, GRID_COLOR, (screen_x, 0), (screen_x, SCREEN_HEIGHT))
    
    for y in range(start_y, end_y):
        screen_y = y * CELL_SIZE + view_offset_y
        pygame.draw.line(screen, GRID_COLOR, (0, screen_y), (SCREEN_WIDTH, screen_y))
    
    # 绘制细胞
    for cell in simulation.cell_list:
        screen_x = cell.x * CELL_SIZE + view_offset_x
        screen_y = cell.y * CELL_SIZE + view_offset_y
        
        # 只绘制在屏幕范围内的细胞
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # 使用细胞颜色属性绘制圆形
            pygame.draw.circle(
                screen, 
                cell.color, 
                (int(screen_x), int(screen_y)), 
                CELL_SIZE // 2 - 2  # 留出2像素边界
            )
    
    # 显示信息
    font = pygame.font.Font("Font/SourceHanSansSC-Regular.otf", 24)
    info_text = f"细胞数量: {len(simulation.cell_list)} | 网格大小: {CELL_SIZE}px"
    text_surface = font.render(info_text, True, (200, 200, 200))
    screen.blit(text_surface, (10, 10))
    
    # 显示控制提示
    controls_text = "左键拖动: 移动视口 | 滚轮: 缩放"
    controls_surface = font.render(controls_text, True, (200, 200, 200))
    screen.blit(controls_surface, (10, SCREEN_HEIGHT - 30))
    
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(5)  # 每秒5帧

pygame.quit()
sys.exit()