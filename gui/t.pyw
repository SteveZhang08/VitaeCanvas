"""
Vitae Canvas 细胞模拟演示程序 (Dear PyGui 2.2 修正版)
作者：元宝
版本：1.0.0
兼容：Dear PyGui 2.2+
"""

import dearpygui.dearpygui as dpg
import random
import math
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import threading
import queue
import sys

# ==================== 核心数据结构 ====================
@dataclass
class Cell:
    """细胞类"""
    id: int
    x: float
    y: float
    energy: float
    velocity_x: float
    velocity_y: float
    size: float
    dna: str
    generation: int
    color: Tuple[int, int, int, int]
    
    def update_position(self, width: int, height: int):
        """更新位置，边界反弹"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # 边界反弹
        if self.x <= self.size or self.x >= width - self.size:
            self.velocity_x *= -1
            self.x = max(self.size, min(self.x, width - self.size))
        if self.y <= self.size or self.y >= height - self.size:
            self.velocity_y *= -1
            self.y = max(self.size, min(self.y, height - self.size))
    
    def metabolize(self):
        """细胞代谢，消耗能量"""
        self.energy -= 0.1
        
        # 能量不足时减慢速度
        if self.energy < 30:
            self.velocity_x *= 0.95
            self.velocity_y *= 0.95
    
    def is_alive(self) -> bool:
        """检查细胞是否存活"""
        return self.energy > 0
    
    def reproduce(self, new_id: int) -> Optional['Cell']:
        """细胞分裂繁殖"""
        if self.energy > 80:  # 需要足够能量才能分裂
            self.energy /= 2
            
            # 创建子细胞
            child = Cell(
                id=new_id,
                x=self.x + random.uniform(-20, 20),
                y=self.y + random.uniform(-20, 20),
                energy=self.energy,
                velocity_x=self.velocity_x + random.uniform(-0.5, 0.5),
                velocity_y=self.velocity_y + random.uniform(-0.5, 0.5),
                size=self.size * random.uniform(0.8, 1.2),
                dna=self.mutate_dna(),
                generation=self.generation + 1,
                color=self.mutate_color()
            )
            return child
        return None
    
    def mutate_dna(self) -> str:
        """DNA突变"""
        dna_chars = "ATCG"
        dna_list = list(self.dna)
        
        # 随机突变1-2个位置
        for _ in range(random.randint(1, 2)):
            pos = random.randint(0, len(dna_list) - 1)
            dna_list[pos] = random.choice(dna_chars)
        
        return "".join(dna_list)
    
    def mutate_color(self) -> Tuple[int, int, int, int]:
        """颜色突变"""
        r, g, b, a = self.color
        r = max(0, min(255, r + random.randint(-20, 20)))
        g = max(0, min(255, g + random.randint(-20, 20)))
        b = max(0, min(255, b + random.randint(-20, 20)))
        return (r, g, b, a)
    
    def interact(self, other: 'Cell'):
        """细胞交互：能量交换"""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
        if distance < (self.size + other.size) * 2:  # 如果足够近
            # 能量从高浓度向低浓度流动
            if self.energy > other.energy:
                transfer = (self.energy - other.energy) * 0.05
                self.energy -= transfer
                other.energy += transfer
            else:
                transfer = (other.energy - self.energy) * 0.05
                other.energy -= transfer
                self.energy += transfer

@dataclass
class Food:
    """食物粒子"""
    id: int
    x: float
    y: float
    energy: float
    size: float = 3.0
    color: Tuple[int, int, int, int] = (255, 200, 0, 255)  # 黄色

# ==================== 模拟引擎 ====================
class SimulationEngine:
    """模拟引擎核心"""
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.cells: List[Cell] = []
        self.foods: List[Food] = []
        self.next_cell_id = 1
        self.next_food_id = 1
        self.time_step = 0
        self.is_running = False
        self.simulation_speed = 1.0
        self.selected_cell_id: Optional[int] = None
        
        # 初始化模拟
        self.initialize_simulation()
    
    def initialize_simulation(self, num_cells: int = 20, num_foods: int = 50):
        """初始化模拟"""
        self.cells.clear()
        self.foods.clear()
        self.next_cell_id = 1
        self.next_food_id = 1
        self.time_step = 0
        self.selected_cell_id = None
        
        # 创建初始细胞
        for i in range(num_cells):
            cell = Cell(
                id=self.next_cell_id,
                x=random.uniform(50, self.canvas_width - 50),
                y=random.uniform(50, self.canvas_height - 50),
                energy=random.uniform(50, 100),
                velocity_x=random.uniform(-1, 1),
                velocity_y=random.uniform(-1, 1),
                size=random.uniform(8, 15),
                dna="".join(random.choice("ATCG") for _ in range(20)),
                generation=1,
                color=(
                    random.randint(0, 255),  # R
                    random.randint(100, 255),  # G
                    random.randint(0, 100),  # B
                    255  # A
                )
            )
            self.cells.append(cell)
            self.next_cell_id += 1
        
        # 创建食物
        for i in range(num_foods):
            food = Food(
                id=self.next_food_id,
                x=random.uniform(0, self.canvas_width),
                y=random.uniform(0, self.canvas_height),
                energy=random.uniform(10, 30)
            )
            self.foods.append(food)
            self.next_food_id += 1
    
    def update(self):
        """更新模拟状态"""
        if not self.is_running:
            return
        
        self.time_step += 1
        
        # 1. 更新细胞
        cells_to_remove = []
        new_cells = []
        
        for cell in self.cells[:]:  # 复制列表以防修改
            # 更新位置
            cell.update_position(self.canvas_width, self.canvas_height)
            
            # 代谢消耗
            cell.metabolize()
            
            # 检查死亡
            if not cell.is_alive():
                cells_to_remove.append(cell)
                continue
            
            # 细胞交互
            for other in self.cells:
                if other.id != cell.id:
                    cell.interact(other)
            
            # 细胞分裂
            if random.random() < 0.005:  # 0.5%概率分裂
                child = cell.reproduce(self.next_cell_id)
                if child:
                    new_cells.append(child)
                    self.next_cell_id += 1
            
            # 寻找食物
            foods_to_remove = []
            for food in self.foods:
                distance = math.sqrt((cell.x - food.x)**2 + (cell.y - food.y)**2)
                if distance < cell.size + food.size:
                    cell.energy += food.energy
                    foods_to_remove.append(food)
            
            # 移除被吃掉的食物
            for food in foods_to_remove:
                if food in self.foods:
                    self.foods.remove(food)
        
        # 移除死亡细胞
        for cell in cells_to_remove:
            if cell in self.cells:
                self.cells.remove(cell)
                if cell.id == self.selected_cell_id:
                    self.selected_cell_id = None
        
        # 添加新细胞
        self.cells.extend(new_cells)
        
        # 2. 生成新食物
        if random.random() < 0.3:  # 30%概率生成新食物
            food = Food(
                id=self.next_food_id,
                x=random.uniform(0, self.canvas_width),
                y=random.uniform(0, self.canvas_height),
                energy=random.uniform(10, 30)
            )
            self.foods.append(food)
            self.next_food_id += 1
        
        # 3. 如果细胞太少，自动添加
        if len(self.cells) < 5:
            for _ in range(3):
                cell = Cell(
                    id=self.next_cell_id,
                    x=random.uniform(50, self.canvas_width - 50),
                    y=random.uniform(50, self.canvas_height - 50),
                    energy=random.uniform(50, 100),
                    velocity_x=random.uniform(-1, 1),
                    velocity_y=random.uniform(-1, 1),
                    size=random.uniform(8, 15),
                    dna="".join(random.choice("ATCG") for _ in range(20)),
                    generation=1,
                    color=(
                        random.randint(0, 255),
                        random.randint(100, 255),
                        random.randint(0, 100),
                        255
                    )
                )
                self.cells.append(cell)
                self.next_cell_id += 1
    
    def get_cell_by_id(self, cell_id: int) -> Optional[Cell]:
        """根据ID获取细胞"""
        for cell in self.cells:
            if cell.id == cell_id:
                return cell
        return None
    
    def get_selected_cell(self) -> Optional[Cell]:
        """获取选中的细胞"""
        if self.selected_cell_id is None:
            return None
        return self.get_cell_by_id(self.selected_cell_id)
    
    def select_cell_at_position(self, x: float, y: float) -> bool:
        """选择指定位置的细胞"""
        for cell in self.cells:
            distance = math.sqrt((x - cell.x)**2 + (y - cell.y)**2)
            if distance <= cell.size:
                self.selected_cell_id = cell.id
                return True
        
        self.selected_cell_id = None
        return False
    
    def get_statistics(self) -> dict:
        """获取模拟统计数据"""
        if not self.cells:
            return {
                "total_cells": 0,
                "total_energy": 0,
                "avg_energy": 0,
                "avg_size": 0,
                "avg_generation": 0
            }
        
        total_energy = sum(cell.energy for cell in self.cells)
        avg_energy = total_energy / len(self.cells)
        avg_size = sum(cell.size for cell in self.cells) / len(self.cells)
        avg_generation = sum(cell.generation for cell in self.cells) / len(self.cells)
        
        return {
            "total_cells": len(self.cells),
            "total_energy": total_energy,
            "avg_energy": avg_energy,
            "avg_size": avg_size,
            "avg_generation": avg_generation
        }

# ==================== GUI界面 (Dear PyGui 2.2版本) ====================
class VitaeCanvasGUI:
    """主GUI界面"""
    def __init__(self):
        # 模拟引擎
        self.sim = SimulationEngine()
        self.last_update_time = time.time()
        self.fps = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        
        # 状态
        self.is_paused = False
        self.show_food = True
        self.show_cell_info = True
        self.show_energy_grid = False
        
        # Dear PyGui 上下文
        self.context = None
        self.viewport = None
        
        # 初始化GUI
        self.init_gui()
        
        # 启动模拟线程
        self.sim.is_running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
    
    def init_gui(self):
        """初始化GUI界面"""
        # 创建上下文
        self.context = dpg.create_context()
        
        # 设置主题
        self.setup_theme()
        
        # 创建视口
        self.viewport = dpg.create_viewport(
            title='Vitae Canvas - 生命绘卷模拟器',
            width=1200,
            height=800
        )
        
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)


        # 主窗口
        with dpg.window(
            label="生命绘卷",
            tag="main_window",
            width=1200,
            height=800
        ):
            # 顶部工具栏
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="▶ 开始模拟",
                    tag="start_btn",
                    callback=self.toggle_simulation,
                    width=100
                )
                dpg.add_button(
                    label="↺ 重置模拟",
                    tag="reset_btn",
                    callback=self.reset_simulation,
                    width=100
                )
                dpg.add_slider_float(
                    label="速度",
                    tag="speed_slider",
                    default_value=1.0,
                    min_value=0.1,
                    max_value=5.0,
                    width=150,
                    callback=lambda s, a: self.set_simulation_speed(a)
                )
                dpg.add_text("", tag="fps_display")
                dpg.add_spacer(width=20)
                dpg.add_text("时间步: 0", tag="time_step_display")
            
            dpg.add_separator()
            
            # 主内容区
            with dpg.group(horizontal=True):
                # 左侧画布区域 - 使用窗口而不是child_window
                with dpg.child_window(width=800, height=600, tag="canvas_container", no_scrollbar=True):
                    # 创建绘图画布
                    dpg.add_drawlist(width=800, height=600, tag="simulation_canvas")
                
                # 右侧控制面板
                with dpg.child_window(width=380, height=600, tag="control_panel"):
                    # 模拟控制
                    with dpg.collapsing_header(label="模拟控制", default_open=True):
                        dpg.add_input_int(
                            label="初始细胞数",
                            tag="initial_cells_input",
                            default_value=20,
                            min_value=1,
                            max_value=100
                        )
                        dpg.add_input_int(
                            label="初始食物数",
                            tag="initial_food_input",
                            default_value=50,
                            min_value=0,
                            max_value=200
                        )
                        dpg.add_button(
                            label="添加细胞",
                            callback=self.add_random_cell
                        )
                        dpg.add_button(
                            label="添加食物",
                            callback=self.add_random_food
                        )
                    
                    # 显示设置
                    with dpg.collapsing_header(label="显示设置", default_open=True):
                        dpg.add_checkbox(
                            label="显示食物",
                            tag="show_food_check",
                            default_value=True,
                            callback=lambda s, a: setattr(self, 'show_food', a)
                        )
                        dpg.add_checkbox(
                            label="显示细胞信息",
                            tag="show_cell_info_check",
                            default_value=True,
                            callback=lambda s, a: setattr(self, 'show_cell_info', a)
                        )
                        dpg.add_checkbox(
                            label="显示能量网格",
                            tag="show_energy_grid_check",
                            default_value=False,
                            callback=lambda s, a: setattr(self, 'show_energy_grid', a)
                        )
                    
                    # 选中细胞信息
                    dpg.add_text("选中细胞信息", color=(0, 200, 255))
                    dpg.add_separator()
                    dpg.add_text(
                        "点击画布中的细胞以选中",
                        tag="selected_cell_info",
                        wrap=350
                    )
                    
                    # 模拟统计
                    dpg.add_spacer(height=20)
                    dpg.add_text("模拟统计", color=(0, 200, 255))
                    dpg.add_separator()
                    dpg.add_text("细胞总数: 0", tag="stat_cell_count")
                    dpg.add_text("总能量: 0", tag="stat_total_energy")
                    dpg.add_text("平均能量: 0", tag="stat_avg_energy")
                    dpg.add_text("平均大小: 0", tag="stat_avg_size")
                    dpg.add_text("平均世代: 0", tag="stat_avg_generation")
                    
                    # 操作说明
                    dpg.add_spacer(height=20)
                    dpg.add_text("操作说明", color=(255, 200, 0))
                    dpg.add_text("- 左键点击: 选中细胞", bullet=True)
                    dpg.add_text("- 空格键: 暂停/继续", bullet=True)
                    dpg.add_text("- R键: 重置模拟", bullet=True)
        
        # 设置键盘快捷键
        with dpg.handler_registry():
            dpg.add_key_press_handler(
                key=32,  # 空格键的键码
                callback=self.toggle_simulation
            )
            dpg.add_key_press_handler(
                key=82,  # R键的键码
                callback=self.reset_simulation
            )
        
        # 设置画布点击事件
        with dpg.item_handler_registry(tag="canvas_click_handler"):
            dpg.add_item_clicked_handler(callback=self.on_canvas_click)
        
        dpg.bind_item_handler_registry("simulation_canvas", "canvas_click_handler")
        
        # 完成设置
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
    
    def setup_theme(self):
        """设置主题"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 35, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 70, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 90, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 100, 110, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (40, 40, 45, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (100, 150, 200, 255))
        
        dpg.bind_theme(global_theme)
    
    def simulation_loop(self):
        """模拟循环（在单独线程中运行）"""
        while True:
            if not self.is_paused:
                # 根据速度控制更新频率
                time.sleep(0.05 / self.sim.simulation_speed)
                self.sim.update()
            else:
                time.sleep(0.1)  # 暂停时减少CPU占用
    
    def render_frame(self):
        """渲染帧"""
        # 更新FPS计算
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
            
            # 更新FPS显示
            dpg.set_value("fps_display", f"FPS: {self.fps}")
            dpg.set_value("time_step_display", f"时间步: {self.sim.time_step}")
        
        # 清空画布
        dpg.delete_item("simulation_canvas", children_only=True)
        
        # 绘制背景
        with dpg.draw_node(parent="simulation_canvas"):
            dpg.draw_rectangle(
                pmin=(0, 0),
                pmax=(800, 600),
                color=(20, 20, 25, 255),
                fill=(20, 20, 25, 255)
            )
            
            # 绘制网格背景
            if self.show_energy_grid:
                grid_size = 40
                for x in range(0, 801, grid_size):
                    dpg.draw_line(
                        p1=(x, 0),
                        p2=(x, 600),
                        color=(40, 40, 50, 100),
                        thickness=1
                    )
                for y in range(0, 601, grid_size):
                    dpg.draw_line(
                        p1=(0, y),
                        p2=(800, y),
                        color=(40, 40, 50, 100),
                        thickness=1
                    )
        
        # 绘制食物
        if self.show_food:
            with dpg.draw_node(parent="simulation_canvas"):
                for food in self.sim.foods:
                    dpg.draw_circle(
                        center=(food.x, food.y),
                        radius=food.size,
                        color=food.color,
                        fill=food.color
                    )
        
        # 绘制细胞
        with dpg.draw_node(parent="simulation_canvas"):
            for cell in self.sim.cells:
                # 基础颜色
                base_color = cell.color
                
                # 能量低于20%时变红
                if cell.energy < 20:
                    base_color = (255, 50, 50, 255)
                # 能量低于50%时变黄
                elif cell.energy < 50:
                    base_color = (255, 255, 100, 255)
                
                # 绘制细胞主体
                dpg.draw_circle(
                    center=(cell.x, cell.y),
                    radius=cell.size,
                    color=base_color,
                    fill=base_color
                )
                
                # 如果被选中，添加选中光环
                if cell.id == self.sim.selected_cell_id:
                    dpg.draw_circle(
                        center=(cell.x, cell.y),
                        radius=cell.size + 3,
                        color=(255, 255, 0, 255),
                        thickness=2
                    )
                
                # 绘制细胞ID
                if self.show_cell_info:
                    dpg.draw_text(
                        pos=(cell.x - 10, cell.y - cell.size - 15),
                        text=str(cell.id),
                        color=(200, 200, 200, 200),
                        size=12
                    )
                    
                    # 绘制能量条
                    energy_percent = min(1.0, cell.energy / 100.0)
                    bar_width = 20
                    bar_height = 3
                    dpg.draw_rectangle(
                        pmin=(cell.x - bar_width/2, cell.y + cell.size + 5),
                        pmax=(cell.x - bar_width/2 + bar_width * energy_percent, 
                              cell.y + cell.size + 5 + bar_height),
                        color=(0, 255, 0, 200),
                        fill=(0, 255, 0, 200)
                    )
        
        # 更新统计数据
        stats = self.sim.get_statistics()
        dpg.set_value("stat_cell_count", f"细胞总数: {stats['total_cells']}")
        dpg.set_value("stat_total_energy", f"总能量: {stats['total_energy']:.1f}")
        dpg.set_value("stat_avg_energy", f"平均能量: {stats['avg_energy']:.1f}")
        dpg.set_value("stat_avg_size", f"平均大小: {stats['avg_size']:.1f}")
        dpg.set_value("stat_avg_generation", f"平均世代: {stats['avg_generation']:.1f}")
        
        # 更新选中细胞信息
        selected_cell = self.sim.get_selected_cell()
        if selected_cell:
            info_text = f"""
细胞 ID: {selected_cell.id}
位置: ({selected_cell.x:.1f}, {selected_cell.y:.1f})
能量: {selected_cell.energy:.1f}
大小: {selected_cell.size:.1f}
速度: ({selected_cell.velocity_x:.2f}, {selected_cell.velocity_y:.2f})
世代: {selected_cell.generation}
DNA: {selected_cell.dna}
            """
            dpg.set_value("selected_cell_info", info_text.strip())
        else:
            dpg.set_value("selected_cell_info", "点击画布中的细胞以选中")
    
    def on_canvas_click(self, sender, app_data):
        """画布点击事件"""
        mouse_button = app_data[0]
        mouse_pos = app_data[1]
        
        if mouse_button == 0:  # 左键
            # 选择细胞
            if self.sim.select_cell_at_position(mouse_pos[0], mouse_pos[1]):
                print(f"选中细胞: {self.sim.selected_cell_id}")
    
    def toggle_simulation(self):
        """切换模拟状态"""
        self.is_paused = not self.is_paused
        self.sim.is_running = not self.is_paused
        
        if self.is_paused:
            dpg.set_value("start_btn", "▶ 继续模拟")
        else:
            dpg.set_value("start_btn", "⏸ 暂停模拟")
    
    def reset_simulation(self):
        """重置模拟"""
        initial_cells = dpg.get_value("initial_cells_input")
        initial_food = dpg.get_value("initial_food_input")
        
        self.sim.initialize_simulation(initial_cells, initial_food)
        self.is_paused = False
        self.sim.is_running = True
        dpg.set_value("start_btn", "⏸ 暂停模拟")
    
    def set_simulation_speed(self, speed: float):
        """设置模拟速度"""
        self.sim.simulation_speed = speed
    
    def add_random_cell(self):
        """添加随机细胞"""
        cell = Cell(
            id=self.sim.next_cell_id,
            x=random.uniform(50, self.sim.canvas_width - 50),
            y=random.uniform(50, self.sim.canvas_height - 50),
            energy=random.uniform(50, 100),
            velocity_x=random.uniform(-1, 1),
            velocity_y=random.uniform(-1, 1),
            size=random.uniform(8, 15),
            dna="".join(random.choice("ATCG") for _ in range(20)),
            generation=1,
            color=(
                random.randint(0, 255),
                random.randint(100, 255),
                random.randint(0, 100),
                255
            )
        )
        self.sim.cells.append(cell)
        self.sim.next_cell_id += 1
    
    def add_random_food(self):
        """添加随机食物"""
        food = Food(
            id=self.sim.next_food_id,
            x=random.uniform(0, self.sim.canvas_width),
            y=random.uniform(0, self.sim.canvas_height),
            energy=random.uniform(10, 30)
        )
        self.sim.foods.append(food)
        self.sim.next_food_id += 1
    
    def run(self):
        """运行应用"""
        # Dear PyGui 2.2 手动渲染循环
        while dpg.is_dearpygui_running():
            # 渲染当前帧
            self.render_frame()
            
            # 渲染DearPyGui帧
            dpg.render_dearpygui_frame()
        
        # 清理
        dpg.destroy_context()

# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("Vitae Canvas - 生命绘卷模拟器 (Dear PyGui 2.2 修正版)")
    print("正在启动细胞模拟演示程序...")
    print("=" * 60)
    print()
    print("功能说明:")
    print("1. 细胞会自动移动、代谢、繁殖")
    print("2. 细胞可以互相交换能量")
    print("3. 细胞可以吃掉食物恢复能量")
    print("4. 左键点击细胞可以选中查看详情")
    print("5. 空格键暂停/继续，R键重置模拟")
    print()
    
    # 创建并运行应用
    app = VitaeCanvasGUI()
    app.run()