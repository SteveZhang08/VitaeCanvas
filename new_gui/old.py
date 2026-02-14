import pygame
import sys
import threading
import time
from typing import List
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *
from draw_cell import *

class SimulationController:
    """主控系统"""
    def __init__(self, screen) -> None:
        self.screen = screen
        self.env = env.Environment(-1, -1)
        self.cell_list: List[cells.Cell] = []
        self.cell_list.append(cells.Cell(self.env, 0, 0, dna=cells.DEFAULT_DNA, name="Vita1"))
        self.cell_list.append(cells.Cell(self.env, 1, 0, dna=cells.DEFAULT_DNA, name="Vita2"))
        
        resource_list = [env.Energy(100), env.O2(200), env.H2O(200), 
                        cells.SugarList([cells.Sugar(6,12,6)])]
        for resource in resource_list:
            self.env.write(0, 0, resource)
        self.env.write(0, 1, env.Energy(200))
        
        self.draw_cell_list = []
        for cell in self.cell_list:
            self.draw_cell_list.append(Draw_Cell(screen, cell))
        
        # 拖拽相关变量
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
        # 线程控制和同步
        self.running = True
        self.lock = threading.Lock()  # 用于保护共享数据
        self.needs_redraw = True  # 添加重绘标志
        
        # 坐标显示相关
        self.display_pos = [2.0, 3.0]  # 初始坐标 (2, 3)
        self.display_scale_x = 200  # X轴放缩量
        self.display_scale_y = 220  # Y轴放缩量
        
        # 初始化字体用于显示坐标
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 28)
        
        debug = 0
        if debug:
            # 启动测试线程 - 持续移动细胞
            self.ces_thread = threading.Thread(target=self.ces_loop, daemon=True)
            self.ces_thread.start()
        else:
            # 启动代谢线程
            self.metabolism_thread = threading.Thread(target=self.metabolism_loop, daemon=True)
            self.metabolism_thread.start()
        
        # 主线程运行Pygame事件循环
        self.main_loop()

    def draw(self):
        """绘制函数 - 必须在主线程中调用"""
        self.screen.fill((0, 130, 180))
        
        # 只加锁读取数据，不要在整个绘制过程中持有锁
        cells_to_draw = []
        with self.lock:
            cells_to_draw = list(self.draw_cell_list)  # 创建副本，快速释放锁
        
        # 不加锁绘制，避免阻塞其他线程
        for draw_cell in cells_to_draw:
            draw_cell.draw()
        
        # 绘制坐标信息
        self.draw_coordinates()
        
        pygame.display.flip()
        self.needs_redraw = False  # 重置重绘标志

    def draw_coordinates(self):
        """绘制坐标信息到屏幕左上角"""
        # 格式化坐标显示，保留2位小数
        coord_text = f"x, y: ({self.display_pos[0]:.2f}, {self.display_pos[1]:.2f})"
        
        # 渲染坐标文本
        coord_surface = self.font.render(coord_text, True, (255, 255, 255))  # 白色文字
        coord_rect = coord_surface.get_rect()
        
        # 添加半透明背景
        bg_rect = pygame.Rect(10, 10, coord_rect.width + 10, coord_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))  # 半透明黑色背景
        
        # 绘制背景和文本
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(coord_surface, (15, 15))

    def handle_events(self):
        """处理事件 - 必须在主线程中调用"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    self.needs_redraw = True  # 标记需要重绘
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键
                    self.dragging = False
                    self.needs_redraw = True  # 标记需要重绘
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_mouse_pos = event.pos
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]
                    
                    # 更新显示坐标（根据鼠标位移和放缩量）
                    # 注意：这里需要根据你的坐标系统逻辑来决定是加还是减
                    # 通常鼠标向右/下拖动，坐标值应该增加
                    self.display_pos[0] -= dx / self.display_scale_x
                    self.display_pos[1] -= dy / self.display_scale_y
                    
                    # 快速获取锁，移动细胞，然后释放锁
                    with self.lock:
                        for draw_cell in self.draw_cell_list:
                            draw_cell.move(dx, dy)
                    
                    self.last_mouse_pos = current_mouse_pos
                    self.needs_redraw = True  # 标记需要重绘

    def cells_metabolism(self):
        """单个代谢周期 - 可以在子线程中运行"""
        cells_to_add = []  # 临时存储新细胞
        draw_cells_to_add = []  # 临时存储新绘制细胞
        
        with self.lock:  # 加锁保护共享数据
            for cell in self.cell_list:
                new_cell = metabolism.MetabolismSystem(cell, self.env).re_info()
                if new_cell['new'] is not None:
                    # 不直接修改列表，先收集
                    cells_to_add.append(new_cell['new'])
                    draw_cells_to_add.append(Draw_Cell(self.screen, new_cell['new']))
                
                self.env.resources_diffusion()
                print(f"细胞{cell.name}代谢完成，当前能量值：{round(cell.energy.value, 2)}")
                print(f"细胞当前所在位置信息：\n坐标：{cell.x, cell.y}")
            
            # 一次性添加新细胞
            for new_cell in cells_to_add:
                self.cell_list.append(new_cell)
            for new_draw_cell in draw_cells_to_add:
                self.draw_cell_list.append(new_draw_cell)
        
        self.needs_redraw = True  # 标记需要重绘

    def ces_loop(self):
        """测试循环 - 持续移动细胞"""
        move_count = 0
        while self.running:
            time.sleep(0.5)  # 每0.5秒移动一次
            
            with self.lock:
                if len(self.cell_list) > 0:
                    # 每次移动更大的距离，方便观察
                    self.cell_list[0].move(1, move_count)
                    move_count += 1
                    print(f"测试移动 #{move_count}: 细胞{self.cell_list[0].name}移动到了({self.cell_list[0].x}, {self.cell_list[0].y})")
            
            self.needs_redraw = True  # 标记需要重绘

    def metabolism_loop(self):
        """代谢线程的主循环"""
        while self.running:
            self.cells_metabolism()
            time.sleep(5)  # 控制代谢速度，避免过于频繁

    def main_loop(self):
        """主循环 - 必须在主线程中运行"""
        clock = pygame.time.Clock()
        
        while self.running:
            # 1. 处理事件（必须在主线程）
            self.handle_events()
            
            # 2. 绘制（只有在需要重绘或固定帧率时）
            # 优化：只在需要时重绘，避免不必要的绘制调用
            # if self.needs_redraw or clock.get_fps() < 30:
            self.draw()
            
            # 控制帧率
            clock.tick(100)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("VitaeCanvas")
    screen = pygame.display.set_mode((1200, 800))
    
    try:
        controller = SimulationController(screen)
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()