"""
VitaeCanvas GUI界面
使用dearpygui 2.2版本创建
"""
import dearpygui.dearpygui as dpg
import threading
import time
import math
from typing import Optional, Tuple, List, Dict, Any
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 尝试导入项目模块
try:
    from main import SimulationController
    from vitae_system import cells, env
    from vitae_system.random_DNA import generate_dna
    HAS_PROJECT_MODULES = True
except ImportError as e:
    print(f"警告: 无法导入项目模块: {e}")
    print("将以模拟模式运行GUI")
    HAS_PROJECT_MODULES = False

# 如果项目模块不可用，创建模拟类
if not HAS_PROJECT_MODULES:
    class MockDNA:
        def __init__(self, seq="ATCG"):
            self.sequence = seq
            
    class MockRNA:
        def __init__(self, seq="AUCG"):
            self.sequence = seq
            
    class MockCell:
        def __init__(self, env, x, y, dna=None, name=None):
            self.env = env
            self.x = x
            self.y = y
            self.dna = dna or MockDNA()
            self.name = name or f"Cell_{x}_{y}"
            self.rna = MockRNA()
            self.color = (255, 255, 255)  # 白色
            
    class MockEnvironment:
        def __init__(self, width=100, height=100):
            self.width = width
            self.height = height
            self.env = {}
            self.type_register_table = {}
            
        def read(self, coordinate):
            return self.env.get(coordinate, [])
            
        def write(self, coordinate, content):
            if coordinate not in self.env:
                self.env[coordinate] = []
            self.env[coordinate].append(content)
            
        def in_env(self, x, y):
            if self.width < 0 or self.height < 0:
                return True
            return 0 <= x < self.width and 0 <= y < self.height
                
    class MockSimulationController:
        def __init__(self):
            self.env = MockEnvironment(50, 50)
            self.running = False
            # 添加一些测试数据
            self._setup_test_data()
            
        def _setup_test_data(self):
            # 添加一些细胞
            for i in range(5):
                x = i * 10 + 5
                y = i * 10 + 5
                cell = MockCell(self.env, x, y, name=f"TestCell_{i}")
                cell.color = (100 + i*30, 150 + i*20, 200 - i*40)
                self.env.write((x, y), cell)
                
            # 添加一些能量
            for i in range(20):
                x = (i * 7) % 50
                y = (i * 11) % 50
                class MockEnergy:
                    def __init__(self, value):
                        self.value = value
                self.env.write((x, y), MockEnergy(100))
                
    # 使用模拟类
    cells = type('cells', (), {})()
    cells.Cell = MockCell
    cells.DNA = MockDNA
    cells.RNA = MockRNA
    cells.Sugar = lambda a,b,c: type('Sugar', (), {'formula': f'C{a}H{b}O{c}'})()
    
    env = type('env', (), {})()
    env.Energy = lambda v: type('Energy', (), {'value': v})()
    env.O2 = lambda v: type('O2', (), {'value': v})()
    env.H2O = lambda v: type('H2O', (), {'value': v})()
    
    generate_dna = lambda length=300: "ATCG" * (length // 4)
    SimulationController = MockSimulationController

class VitaeCanvasGUI:
    """VitaeCanvas GUI主类"""
    
    def __init__(self):
        # 模拟控制器
        self.sim_controller = SimulationController()
        self.env = self.sim_controller.env
        
        # GUI状态
        self.running = False
        self.simulation_thread = None
        self.selected_cell = None
        self.view_offset = [0, 0]  # 视口偏移，用于无限大环境
        self.view_scale = 10.0  # 缩放比例
        self.auto_scroll = True  # 是否自动滚动视图
        
        # 颜色定义
        self.colors = {
            'background': (40, 40, 40),
            'panel_bg': (50, 50, 50),
            'text': (240, 240, 240),
            'grid': (60, 60, 60),
            'energy': (255, 255, 0, 255),  # 黄色
            'o2': (0, 120, 255, 255),      # 蓝色
            'h2o': (100, 200, 255, 255),   # 浅蓝色
            'sugar': (0, 200, 100, 255),   # 绿色
            'cell_default': (255, 100, 100, 255),  # 红色
            'selected': (255, 255, 0, 255)  # 黄色
        }
        
        # 初始化dearpygui
        self.setup_gui()
        
    def setup_gui(self):
        """设置GUI界面"""
        dpg.create_context()
        
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)

        # 创建主窗口
        with dpg.window(label="VitaeCanvas - 生命绘卷", tag="main_window"):
            # 创建菜单栏
            with dpg.menu_bar():
                with dpg.menu(label="文件"):
                    dpg.add_menu_item(label="退出", callback=lambda: dpg.stop_dearpygui())
                    
                with dpg.menu(label="视图"):
                    dpg.add_menu_item(label="重置视图", callback=self.reset_view)
                    dpg.add_checkbox(label="自动滚动", default_value=True, 
                                    callback=lambda s, a: setattr(self, 'auto_scroll', a))
                    
                with dpg.menu(label="帮助"):
                    dpg.add_menu_item(label="关于", callback=self.show_about)
            
            # 主布局：左中右三列
            with dpg.group(horizontal=True):
                # 左侧控制面板 (宽度占25%)
                with dpg.child_window(width=300, tag="left_panel"):
                    self.setup_control_panel()
                
                # 中间画布 (宽度占50%)
                with dpg.child_window(width=-1, tag="center_canvas"):
                    self.setup_canvas()
                
                # 右侧信息面板 (宽度占25%)
                with dpg.child_window(width=300, tag="right_panel"):
                    self.setup_info_panel()
        
        # 设置主窗口
        dpg.create_viewport(title='VitaeCanvas - 生命绘卷', width=1600, height=900)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        
        # 设置定时器用于更新界面
        dpg.set_frame_callback(1, self.update_canvas)
        
    def setup_control_panel(self):
        """设置左侧控制面板"""
        dpg.add_text("控制面板", color=self.colors['text'])
        dpg.add_separator()
        
        # 模拟控制
        with dpg.collapsing_header(label="模拟控制", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_button(label="开始模拟", callback=self.start_simulation, width=100)
                dpg.add_button(label="停止模拟", callback=self.stop_simulation, width=100)
            
            dpg.add_slider_int(label="模拟速度", default_value=10, min_value=1, 
                             max_value=100, callback=self.set_simulation_speed)
            
            dpg.add_button(label="单步执行", callback=self.step_simulation, width=200)
            
        # 环境控制
        with dpg.collapsing_header(label="环境控制", default_open=True):
            dpg.add_input_int(label="宽度", default_value=50 if self.env.width >= 0 else 100, 
                           callback=self.set_env_size, width=200)
            dpg.add_input_int(label="高度", default_value=50 if self.env.height >= 0 else 100,
                           callback=self.set_env_size, width=200)
            
            dpg.add_separator()
            dpg.add_text("添加物质:")
            with dpg.group(horizontal=True):
                dpg.add_combo(["能量", "氧气", "水", "糖"], default_value="能量", 
                            tag="substance_type", width=100)
                dpg.add_input_int(label="数量", default_value=100, tag="substance_amount", width=80)
            
            dpg.add_button(label="随机添加", callback=self.add_random_substances, width=200)
            
        # 细胞控制
        with dpg.collapsing_header(label="细胞控制", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X坐标", default_value=0, tag="cell_x", width=80)
                dpg.add_input_int(label="Y坐标", default_value=0, tag="cell_y", width=80)
            
            dpg.add_input_text(label="细胞名称", default_value="新细胞", tag="cell_name", width=200)
            dpg.add_input_text(label="DNA序列(可选)", hint_text="留空则随机生成", 
                             tag="cell_dna", width=200)
            
            dpg.add_button(label="添加细胞", callback=self.add_cell, width=200)
            dpg.add_button(label="删除选中细胞", callback=self.delete_selected_cell, width=200)
            
        # 视图控制
        with dpg.collapsing_header(label="视图控制"):
            dpg.add_slider_float(label="缩放", default_value=self.view_scale, 
                               min_value=1.0, max_value=50.0, callback=self.set_view_scale)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="←", callback=lambda: self.pan_view(-10, 0), width=40)
                dpg.add_button(label="→", callback=lambda: self.pan_view(10, 0), width=40)
                dpg.add_button(label="↑", callback=lambda: self.pan_view(0, -10), width=40)
                dpg.add_button(label="↓", callback=lambda: self.pan_view(0, 10), width=40)
            
            dpg.add_button(label="重置视图", callback=self.reset_view, width=200)
            
        # 状态信息
        with dpg.collapsing_header(label="状态信息", default_open=True):
            dpg.add_text("模拟状态: 停止", tag="sim_status")
            dpg.add_text("细胞数量: 0", tag="cell_count")
            dpg.add_text("环境大小: 0x0", tag="env_size")
            dpg.add_text("选中细胞: 无", tag="selected_cell_info")
            
    def setup_canvas(self):
        """设置中间画布"""
        # 创建绘图区域
        with dpg.drawlist(width=-1, height=-1, tag="drawlist"):
            # 绘图区域将在update_canvas中更新
            pass
            
    def setup_info_panel(self):
        """设置右侧信息面板"""
        dpg.add_text("细胞信息", color=self.colors['text'])
        dpg.add_separator()
        
        # 基本信息
        with dpg.collapsing_header(label="基本信息", default_open=True):
            dpg.add_text("名称: 无", tag="info_name")
            dpg.add_text("位置: (0, 0)", tag="info_position")
            dpg.add_text("颜色: (255, 255, 255)", tag="info_color")
            
        # DNA信息
        with dpg.collapsing_header(label="DNA序列"):
            dpg.add_input_text(multiline=True, height=200, width=-1, 
                             readonly=True, tag="info_dna")
            
        # RNA信息
        with dpg.collapsing_header(label="RNA序列"):
            dpg.add_input_text(multiline=True, height=200, width=-1,
                             readonly=True, tag="info_rna")
            
        # 环境信息
        with dpg.collapsing_header(label="所在位置物质", default_open=True):
            dpg.add_text("无物质", tag="info_substances")
            
        # 操作
        with dpg.collapsing_header(label="操作"):
            dpg.add_button(label="查看DNA详情", callback=self.show_dna_detail, width=-1)
            dpg.add_button(label="克隆此细胞", callback=self.clone_cell, width=-1)
            dpg.add_button(label="追踪此细胞", callback=self.track_cell, width=-1)
            
    def update_canvas(self):
        """更新画布内容"""
        dpg.delete_item("drawlist", children_only=True)
        
        # 获取画布尺寸
        canvas_width = dpg.get_item_width("center_canvas")
        canvas_height = dpg.get_item_height("center_canvas")
        
        # 计算环境边界
        env_width = self.env.width
        env_height = self.env.height
        
        # 如果是无限大环境，使用视图偏移
        if env_width < 0 or env_height < 0:
            # 无限大环境，使用固定范围显示
            visible_min_x = self.view_offset[0]
            visible_max_x = self.view_offset[0] + canvas_width / self.view_scale
            visible_min_y = self.view_offset[1]
            visible_max_y = self.view_offset[1] + canvas_height / self.view_scale
            
            # 绘制网格
            self.draw_grid(visible_min_x, visible_max_x, visible_min_y, visible_max_y, 
                          canvas_width, canvas_height)
            
            # 绘制可见区域内的物质和细胞
            self.draw_visible_objects(visible_min_x, visible_max_x, 
                                      visible_min_y, visible_max_y,
                                      canvas_width, canvas_height)
        else:
            # 有限大环境
            visible_min_x = 0
            visible_max_x = env_width
            visible_min_y = 0
            visible_max_y = env_height
            
            # 计算缩放以适合画布
            cell_size = min(canvas_width / env_width, canvas_height / env_height) 
            cell_size = max(5, min(cell_size, 20))  # 限制最小和最大尺寸
            
            # 绘制网格
            self.draw_grid(0, env_width, 0, env_height, canvas_width, canvas_height)
            
            # 绘制所有物质和细胞
            self.draw_all_objects(canvas_width, canvas_height, cell_size)
            
        # 更新状态信息
        self.update_status()
        
        # 设置下一帧更新
        dpg.set_frame_callback(dpg.get_frame_count() + 1, self.update_canvas)
        
    def draw_grid(self, min_x, max_x, min_y, max_y, canvas_width, canvas_height):
        """绘制网格"""
        drawlist = dpg.get_item_children("drawlist", slot=1)[0]
        
        # 计算网格线间距
        grid_spacing = 20
        
        # 计算实际绘制范围
        start_x = int(min_x / grid_spacing) * grid_spacing
        end_x = int(max_x / grid_spacing + 1) * grid_spacing
        start_y = int(min_y / grid_spacing) * grid_spacing
        end_y = int(max_y / grid_spacing + 1) * grid_spacing
        
        # 绘制网格线
        for x in range(start_x, end_x + 1, grid_spacing):
            draw_x = (x - min_x) * self.view_scale
            if 0 <= draw_x <= canvas_width:
                dpg.draw_line((draw_x, 0), (draw_x, canvas_height), 
                            color=self.colors['grid'], parent=drawlist)
                
        for y in range(start_y, end_y + 1, grid_spacing):
            draw_y = (y - min_y) * self.view_scale
            if 0 <= draw_y <= canvas_height:
                dpg.draw_line((0, draw_y), (canvas_width, draw_y), 
                            color=self.colors['grid'], parent=drawlist)
                
    def draw_all_objects(self, canvas_width, canvas_height, cell_size):
        """绘制有限大环境中的所有对象"""
        drawlist = dpg.get_item_children("drawlist", slot=1)[0]
        
        # 绘制物质
        if hasattr(self.env, 'env') and isinstance(self.env.env, dict):
            for (x, y), substances in self.env.env.items():
                if 0 <= x < self.env.width and 0 <= y < self.env.height:
                    screen_x = x * cell_size
                    screen_y = y * cell_size
                    
                    # 绘制物质
                    for substance in substances:
                        if hasattr(substance, '__class__'):
                            substance_type = substance.__class__.__name__
                            color = self.get_substance_color(substance_type)
                            
                            # 绘制小点表示物质
                            dpg.draw_circle((screen_x + cell_size/2, screen_y + cell_size/2), 
                                          cell_size/8, color=color, fill=color, 
                                          parent=drawlist)
                    
                    # 绘制细胞
                    for substance in substances:
                        if isinstance(substance, cells.Cell):
                            # 检查是否被选中
                            is_selected = (self.selected_cell is not None and 
                                          substance.x == getattr(self.selected_cell, 'x', -1) and
                                          substance.y == getattr(self.selected_cell, 'y', -1))
                            
                            # 细胞颜色
                            if hasattr(substance, 'color') and substance.color:
                                cell_color = (*substance.color[:3], 255)
                            else:
                                cell_color = self.colors['cell_default']
                                
                            # 绘制细胞
                            radius = cell_size * 0.4
                            dpg.draw_circle((screen_x + cell_size/2, screen_y + cell_size/2), 
                                          radius, color=cell_color, fill=cell_color, 
                                          parent=drawlist)
                            
                            # 如果被选中，绘制选中框
                            if is_selected:
                                dpg.draw_circle((screen_x + cell_size/2, screen_y + cell_size/2), 
                                              radius + 2, color=self.colors['selected'], 
                                              thickness=2, parent=drawlist)
                                
    def draw_visible_objects(self, min_x, max_x, min_y, max_y, canvas_width, canvas_height):
        """绘制无限大环境中的可见对象"""
        drawlist = dpg.get_item_children("drawlist", slot=1)[0]
        
        # 绘制物质和细胞
        if hasattr(self.env, 'env') and isinstance(self.env.env, dict):
            for (x, y), substances in self.env.env.items():
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    screen_x = (x - min_x) * self.view_scale
                    screen_y = (y - min_y) * self.view_scale
                    
                    # 绘制物质
                    for substance in substances:
                        if hasattr(substance, '__class__'):
                            substance_type = substance.__class__.__name__
                            color = self.get_substance_color(substance_type)
                            
                            # 绘制小点表示物质
                            dpg.draw_circle((screen_x, screen_y), 3, 
                                          color=color, fill=color, parent=drawlist)
                    
                    # 绘制细胞
                    for substance in substances:
                        if isinstance(substance, cells.Cell):
                            # 检查是否被选中
                            is_selected = (self.selected_cell is not None and 
                                          substance.x == getattr(self.selected_cell, 'x', -1) and
                                          substance.y == getattr(self.selected_cell, 'y', -1))
                            
                            # 细胞颜色
                            if hasattr(substance, 'color') and substance.color:
                                cell_color = (*substance.color[:3], 255)
                            else:
                                cell_color = self.colors['cell_default']
                                
                            # 绘制细胞
                            radius = 5
                            dpg.draw_circle((screen_x, screen_y), radius, 
                                          color=cell_color, fill=cell_color, 
                                          parent=drawlist)
                            
                            # 如果被选中，绘制选中框
                            if is_selected:
                                dpg.draw_circle((screen_x, screen_y), radius + 2, 
                                              color=self.colors['selected'], 
                                              thickness=2, parent=drawlist)
                                
    def get_substance_color(self, substance_type):
        """根据物质类型获取颜色"""
        color_map = {
            'Energy': self.colors['energy'],
            'O2': self.colors['o2'],
            'H2O': self.colors['h2o'],
            'Sugar': self.colors['sugar']
        }
        return color_map.get(substance_type, (200, 200, 200, 255))
        
    def update_status(self):
        """更新状态信息"""
        # 更新模拟状态
        status_text = "运行中" if self.running else "停止"
        dpg.set_value("sim_status", f"模拟状态: {status_text}")
        
        # 计算细胞数量
        cell_count = 0
        if hasattr(self.env, 'env') and isinstance(self.env.env, dict):
            for substances in self.env.env.values():
                for substance in substances:
                    if isinstance(substance, cells.Cell):
                        cell_count += 1
                        
        dpg.set_value("cell_count", f"细胞数量: {cell_count}")
        
        # 更新环境大小
        if self.env.width < 0 or self.env.height < 0:
            env_size = "无限大"
        else:
            env_size = f"{self.env.width}x{self.env.height}"
        dpg.set_value("env_size", f"环境大小: {env_size}")
        
        # 更新选中细胞信息
        if self.selected_cell:
            cell_info = f"{getattr(self.selected_cell, 'name', '未知')}"
        else:
            cell_info = "无"
        dpg.set_value("selected_cell_info", f"选中细胞: {cell_info}")
        
    def start_simulation(self):
        """开始模拟"""
        if not self.running:
            self.running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            
    def stop_simulation(self):
        """停止模拟"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
            
    def simulation_loop(self):
        """模拟循环"""
        while self.running:
            # 这里可以添加模拟逻辑
            # 例如：更新细胞状态、物质扩散等
            time.sleep(0.1)  # 模拟时间间隔
            
    def set_simulation_speed(self, sender, app_data):
        """设置模拟速度"""
        # 这里可以实现模拟速度控制
        pass
        
    def step_simulation(self):
        """单步执行模拟"""
        # 这里可以实现单步模拟逻辑
        pass
        
    def set_env_size(self, sender, app_data):
        """设置环境大小"""
        # 注意：在实际项目中，可能需要重新创建环境
        pass
        
    def add_random_substances(self):
        """随机添加物质"""
        import random
        
        substance_type = dpg.get_value("substance_type")
        amount = dpg.get_value("substance_amount")
        
        # 获取环境边界
        if self.env.width < 0 or self.env.height < 0:
            # 无限大环境，在视图范围内添加
            visible_width = 100
            visible_height = 100
            offset_x = self.view_offset[0]
            offset_y = self.view_offset[1]
        else:
            visible_width = self.env.width
            visible_height = self.env.height
            offset_x = 0
            offset_y = 0
            
        for _ in range(amount):
            x = random.randint(0, visible_width - 1) + offset_x
            y = random.randint(0, visible_height - 1) + offset_y
            
            # 创建物质
            if substance_type == "能量":
                substance = env.Energy(100)
            elif substance_type == "氧气":
                substance = env.O2(200)
            elif substance_type == "水":
                substance = env.H2O(200)
            elif substance_type == "糖":
                substance = cells.Sugar(6, 12, 6)
            else:
                continue
                
            # 添加到环境
            self.env.write((x, y), substance)
            
    def add_cell(self):
        """添加细胞"""
        x = dpg.get_value("cell_x")
        y = dpg.get_value("cell_y")
        name = dpg.get_value("cell_name")
        dna_str = dpg.get_value("cell_dna")
        
        # 检查坐标是否在环境内
        if not self.env.in_env(x, y):
            print(f"错误: 坐标({x}, {y})不在环境范围内")
            return
            
        # 创建DNA
        if dna_str:
            dna = cells.DNA(dna_str)
        else:
            # 生成随机DNA
            dna_seq = generate_dna(300)
            dna = cells.DNA(dna_seq)
            
        # 创建细胞
        try:
            cell = cells.Cell(self.env, x, y, dna=dna, name=name)
            self.env.write((x, y), cell)
            print(f"已添加细胞: {name} 在位置({x}, {y})")
        except Exception as e:
            print(f"添加细胞时出错: {e}")
            
    def delete_selected_cell(self):
        """删除选中的细胞"""
        if not self.selected_cell:
            print("没有选中的细胞")
            return
            
        try:
            # 从环境中删除细胞
            coordinate = (self.selected_cell.x, self.selected_cell.y)
            substances = self.env.read(coordinate)
            if substances:
                for i, substance in enumerate(substances):
                    if substance is self.selected_cell:
                        self.env.delete(coordinate, i)
                        print(f"已删除细胞: {self.selected_cell.name}")
                        self.selected_cell = None
                        self.update_cell_info()
                        break
        except Exception as e:
            print(f"删除细胞时出错: {e}")
            
    def set_view_scale(self, sender, app_data):
        """设置视图缩放"""
        self.view_scale = app_data
        
    def pan_view(self, dx, dy):
        """平移视图"""
        self.view_offset[0] += dx
        self.view_offset[1] += dy
        
    def reset_view(self):
        """重置视图"""
        self.view_offset = [0, 0]
        self.view_scale = 10.0
        
    def show_about(self):
        """显示关于对话框"""
        with dpg.window(label="关于 VitaeCanvas", width=400, height=300):
            dpg.add_text("VitaeCanvas - 生命绘卷")
            dpg.add_text("版本: 0.1.0")
            dpg.add_text("一个细胞级演化模拟框架")
            dpg.add_separator()
            dpg.add_text("开发者: SteveZhang08")
            dpg.add_text("使用 dearpygui 2.2 创建")
            
    def update_cell_info(self):
        """更新选中的细胞信息"""
        if not self.selected_cell:
            dpg.set_value("info_name", "名称: 无")
            dpg.set_value("info_position", "位置: (0, 0)")
            dpg.set_value("info_color", "颜色: (255, 255, 255)")
            dpg.set_value("info_dna", "")
            dpg.set_value("info_rna", "")
            dpg.set_value("info_substances", "无物质")
            return
            
        # 更新基本信息
        dpg.set_value("info_name", f"名称: {getattr(self.selected_cell, 'name', '未知')}")
        dpg.set_value("info_position", f"位置: ({self.selected_cell.x}, {self.selected_cell.y})")
        
        if hasattr(self.selected_cell, 'color') and self.selected_cell.color:
            color = self.selected_cell.color
            dpg.set_value("info_color", f"颜色: ({color[0]}, {color[1]}, {color[2]})")
        else:
            dpg.set_value("info_color", "颜色: (255, 255, 255)")
            
        # 更新DNA信息
        if hasattr(self.selected_cell, 'dna') and self.selected_cell.dna:
            dna_str = str(self.selected_cell.dna)
            # 限制显示长度
            if len(dna_str) > 500:
                dna_str = dna_str[:500] + "..."
            dpg.set_value("info_dna", dna_str)
        else:
            dpg.set_value("info_dna", "无DNA信息")
            
        # 更新RNA信息
        if hasattr(self.selected_cell, 'rna') and self.selected_cell.rna:
            rna_str = str(self.selected_cell.rna)
            if len(rna_str) > 500:
                rna_str = rna_str[:500] + "..."
            dpg.set_value("info_rna", rna_str)
        else:
            dpg.set_value("info_rna", "无RNA信息")
            
        # 更新所在位置物质信息
        coordinate = (self.selected_cell.x, self.selected_cell.y)
        substances = self.env.read(coordinate) if hasattr(self.env, 'read') else []
        
        if substances:
            substance_info = []
            for substance in substances:
                if substance is self.selected_cell:
                    continue
                substance_type = substance.__class__.__name__
                substance_info.append(substance_type)
                
            if substance_info:
                dpg.set_value("info_substances", "\n".join(substance_info))
            else:
                dpg.set_value("info_substances", "无其他物质")
        else:
            dpg.set_value("info_substances", "无物质")
            
    def show_dna_detail(self):
        """显示DNA详情"""
        if not self.selected_cell or not hasattr(self.selected_cell, 'dna'):
            return
            
        dna_str = str(self.selected_cell.dna)
        with dpg.window(label="DNA详情", width=600, height=400):
            dpg.add_input_text(multiline=True, width=-1, height=-1, 
                             default_value=dna_str, readonly=True)
            
    def clone_cell(self):
        """克隆选中的细胞"""
        if not self.selected_cell:
            return
            
        # 在相邻位置创建克隆
        import random
        x = self.selected_cell.x + random.randint(-2, 2)
        y = self.selected_cell.y + random.randint(-2, 2)
        
        if not self.env.in_env(x, y):
            print(f"错误: 坐标({x}, {y})不在环境范围内")
            return
            
        try:
            # 创建新细胞，使用相同的DNA
            new_cell = cells.Cell(
                self.env, x, y, 
                dna=self.selected_cell.dna,
                name=f"{getattr(self.selected_cell, 'name', '细胞')}_克隆"
            )
            self.env.write((x, y), new_cell)
            print(f"已克隆细胞到位置({x}, {y})")
        except Exception as e:
            print(f"克隆细胞时出错: {e}")
            
    def track_cell(self):
        """追踪选中的细胞（将视图中心对准该细胞）"""
        if not self.selected_cell:
            return
            
        # 将视图中心对准选中的细胞
        canvas_width = dpg.get_item_width("center_canvas")
        canvas_height = dpg.get_item_height("center_canvas")
        
        if self.env.width < 0 or self.env.height < 0:
            # 无限大环境，调整视图偏移
            self.view_offset[0] = self.selected_cell.x - canvas_width / (2 * self.view_scale)
            self.view_offset[1] = self.selected_cell.y - canvas_height / (2 * self.view_scale)
            
    def run(self):
        """运行GUI"""
        dpg.start_dearpygui()
        dpg.destroy_context()
        
def main():
    """主函数"""
    gui = VitaeCanvasGUI()
    gui.run()
    
if __name__ == "__main__":
    main()
