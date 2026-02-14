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
    """模拟控制器 - 负责Pygame显示和模拟逻辑"""
    
    def __init__(self, screen_width=1200, screen_height=800, tkinter_control=None):
        self.tkinter_control = tkinter_control  # Tkinter控制面板引用
        self.running = False  # 初始化为False，等待启动
        
    def initialize(self):
        """初始化模拟（必须在主线程中调用）"""
        # Pygame初始化
        pygame.init()
        pygame.display.set_caption("VitaeCanvas")
        self.screen = pygame.display.set_mode((1200, 800))
        
        # 环境初始化
        self.env = env.Environment(-1, -1)
        self.cell_list: List[cells.Cell] = []
        self.cell_list.append(cells.Cell(self.env, 0, 0, dna=cells.DEFAULT_DNA, name="Vita1"))
        self.cell_list.append(cells.Cell(self.env, 1, 0, dna=cells.DEFAULT_DNA, name="Vita2"))
        
        # 资源初始化
        resource_list = [env.Energy(100), env.O2(200), env.H2O(200), 
                        cells.SugarList([cells.Sugar(6,12,6)])]
        for resource in resource_list:
            self.env.write(0, 0, resource)
        self.env.write(0, 1, env.Energy(200))
        
        # 绘制细胞列表
        self.draw_cell_list = []
        for cell in self.cell_list:
            self.draw_cell_list.append(Draw_Cell(self.screen, cell))
        
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
        
        # 模拟控制标志
        self.metabolism_enabled = True
        self.metabolism_interval = 5  # 代谢间隔（秒）
        
        # 初始化字体用于显示坐标
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 28)
        
        # 初始化完成，通知控制面板
        if self.tkinter_control and hasattr(self.tkinter_control, 'add_log'):
            self.tkinter_control.add_log("模拟控制器初始化完成")
            
        return True
    
    def start_metabolism_thread(self):
        """启动代谢线程"""
        if not hasattr(self, 'metabolism_thread') or not self.metabolism_thread.is_alive():
            self.metabolism_thread = threading.Thread(target=self.metabolism_loop, daemon=True)
            self.metabolism_thread.start()
            if self.tkinter_control and hasattr(self.tkinter_control, 'add_log'):
                self.tkinter_control.add_log("代谢线程已启动")
    
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
        
        # 绘制状态信息
        status_text = f"Cell_Count: {len(self.cell_list)}"
        status_surface = self.font.render(status_text, True, (255, 255, 255))
        status_rect = status_surface.get_rect()
        status_bg_rect = pygame.Rect(10, 50, status_rect.width + 10, status_rect.height + 10)
        status_bg_surface = pygame.Surface((status_bg_rect.width, status_bg_rect.height), pygame.SRCALPHA)
        status_bg_surface.fill((0, 0, 0, 128))
        
        self.screen.blit(status_bg_surface, status_bg_rect)
        self.screen.blit(status_surface, (15, 55))

    def handle_events(self):
        """处理事件 - 必须在主线程中调用"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False  # 返回False表示需要退出
            
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
                    
                    # 更新显示坐标
                    self.display_pos[0] -= dx / self.display_scale_x
                    self.display_pos[1] -= dy / self.display_scale_y
                    
                    # 更新Tkinter控制面板中的坐标显示（如果存在）
                    if self.tkinter_control and hasattr(self.tkinter_control, 'update_coordinate_display'):
                        # 使用线程安全的方式更新
                        self.tkinter_control.update_coordinate_display(
                            self.display_pos[0], self.display_pos[1])
                    
                    # 快速获取锁，移动细胞，然后释放锁
                    with self.lock:
                        for draw_cell in self.draw_cell_list:
                            draw_cell.move(dx, dy)
                    
                    self.last_mouse_pos = current_mouse_pos
                    self.needs_redraw = True  # 标记需要重绘
        
        return True  # 返回True表示继续运行

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
                # 使用线程安全的方式更新Tkinter日志（如果存在）
                if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
                    self.tkinter_control.add_log_safe(
                        f"细胞{cell.name}代谢完成，能量: {round(cell.energy.value, 2)}")
            
            # 一次性添加新细胞
            for new_cell in cells_to_add:
                self.cell_list.append(new_cell)
            for new_draw_cell in draw_cells_to_add:
                self.draw_cell_list.append(new_draw_cell)
        
        self.needs_redraw = True  # 标记需要重绘

    def metabolism_loop(self):
        """代谢线程的主循环"""
        while self.running:
            if self.metabolism_enabled:
                self.cells_metabolism()
            time.sleep(self.metabolism_interval)  # 控制代谢速度

    def run_main_loop(self):
        """运行Pygame主循环"""
        clock = pygame.time.Clock()
        
        while self.running:
            # 1. 处理事件（必须在主线程）
            if not self.handle_events():
                break  # 如果handle_events返回False，退出循环
            
            # 2. 绘制
            #if self.needs_redraw:
            self.draw()
            
            # 控制帧率
            clock.tick(60)
        
        # 清理资源
        self.cleanup()

    def add_cell(self, x, y, name=None):
        """添加新细胞"""
        with self.lock:
            if name is None:
                import random
                name = f"Vita{len(self.cell_list)+1}"
            new_cell = cells.Cell(self.env, x, y, dna=cells.DEFAULT_DNA, name=name)
            self.cell_list.append(new_cell)
            self.draw_cell_list.append(Draw_Cell(self.screen, new_cell))
            
            # 使用线程安全的方式更新Tkinter日志
            if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
                self.tkinter_control.add_log_safe(f"添加细胞: {name} 在({x}, {y})")
            
        self.needs_redraw = True

    def remove_cell(self, index):
        """移除细胞"""
        with self.lock:
            if 0 <= index < len(self.cell_list):
                cell_name = self.cell_list[index].name
                self.cell_list.pop(index)
                self.draw_cell_list.pop(index)
                
                # 使用线程安全的方式更新Tkinter日志
                if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
                    self.tkinter_control.add_log_safe(f"移除细胞: {cell_name}")
            
        self.needs_redraw = True

    def toggle_metabolism(self):
        """切换代谢状态"""
        self.metabolism_enabled = not self.metabolism_enabled
        # 使用线程安全的方式更新Tkinter日志
        if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
            self.tkinter_control.add_log_safe(f"代谢: {'开启' if self.metabolism_enabled else '关闭'}")

    def set_metabolism_interval(self, interval):
        """设置代谢间隔"""
        self.metabolism_interval = interval
        # 使用线程安全的方式更新Tkinter日志
        if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
            self.tkinter_control.add_log_safe(f"代谢间隔设置为: {interval}秒")

    def reset_simulation(self):
        """重置模拟"""
        with self.lock:
            # 清除所有细胞
            self.cell_list.clear()
            self.draw_cell_list.clear()
            
            # 重新初始化细胞
            self.cell_list.append(cells.Cell(self.env, 0, 0, dna=cells.DEFAULT_DNA, name="Vita1"))
            self.cell_list.append(cells.Cell(self.env, 1, 0, dna=cells.DEFAULT_DNA, name="Vita2"))
            
            for cell in self.cell_list:
                self.draw_cell_list.append(Draw_Cell(self.screen, cell))
            
            # 重置坐标显示
            self.display_pos = [2.0, 3.0]
            
            # 使用线程安全的方式更新Tkinter显示
            if self.tkinter_control:
                if hasattr(self.tkinter_control, 'update_coordinate_display'):
                    self.tkinter_control.update_coordinate_display(2.0, 3.0)
                if hasattr(self.tkinter_control, 'add_log_safe'):
                    self.tkinter_control.add_log_safe("模拟已重置")
        
        self.needs_redraw = True

    def cleanup(self):
        """清理资源"""
        self.running = False
        # 等待代谢线程结束
        if hasattr(self, 'metabolism_thread') and self.metabolism_thread.is_alive():
            self.metabolism_thread.join(timeout=1.0)

    def stop(self):
        """停止模拟"""
        self.running = False
        # 使用线程安全的方式更新Tkinter日志
        if self.tkinter_control and hasattr(self.tkinter_control, 'add_log_safe'):
            self.tkinter_control.add_log_safe("模拟已停止")