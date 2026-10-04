import os
import sys
import threading
import time
from typing import Tuple, List, Dict, Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dearpygui.dearpygui as dpg
import sim
from vitae_system import *

class VitaeCanvasGUI:
    def __init__(self):
        # 初始化模拟控制器
        self.sim_controller = sim.SimulationController()
        self.env = self.sim_controller.env
        
        # 线程控制
        self.simulation_running = False
        self.simulation_thread = None
        
        # 选中的细胞信息
        self.selected_cell = None
        self.selected_coord = None
        
        # 视口设置（用于无限大环境）
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 800
        self.viewport_height = 600
        self.zoom_level = 1.0
        
        # 颜色定义
        self.cell_colors = {}
        self.energy_color = (255, 255, 0, 255)     # 黄色
        self.o2_color = (0, 191, 255, 255)         # 天蓝色
        self.h2o_color = (30, 144, 255, 255)      # 道奇蓝
        self.sugar_color = (255, 182, 193, 255)   # 浅粉色
        
        # 初始化 GUI
        self.init_gui()
    
    def init_gui(self):
        """初始化 GUI 界面"""
        dpg.create_context()
        
        # 设置中文字体
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)
        
        # 创建主窗口
        dpg.create_viewport(title='VitaeCanvas - 生命绘卷', width=1600, height=900)
        
        # 创建窗口
        with dpg.window(label="主窗口", tag="main_window", width=1600, height=900):
            # 左中右布局
            with dpg.group(horizontal=True):
                # 左侧控制面板 (占20%)
                with dpg.child_window(width=320, tag="control_panel"):
                    self.create_control_panel()
                
                # 中间画布 (占50%)
                with dpg.child_window(width=800, tag="canvas_panel"):
                    self.create_canvas_panel()
                
                # 右侧信息面板 (占30%)
                with dpg.child_window(width=480, tag="info_panel"):
                    self.create_info_panel()
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
    
    def create_control_panel(self):
        """创建控制面板"""
        dpg.add_text("控制面板", color=(0, 200, 255))
        dpg.add_separator()
        
        # 模拟控制
        with dpg.collapsing_header(label="模拟控制", default_open=True):
            dpg.add_button(label="开始模拟", callback=self.start_simulation, width=280)
            dpg.add_button(label="暂停模拟", callback=self.pause_simulation, width=280)
            dpg.add_button(label="单步执行", callback=self.step_simulation, width=280)
            dpg.add_button(label="重置模拟", callback=self.reset_simulation, width=280)
        
        # 环境控制
        with dpg.collapsing_header(label="环境控制", default_open=True):
            dpg.add_text("添加物质:")
            dpg.add_input_int(label="X坐标", tag="add_x", default_value=0, width=280)
            dpg.add_input_int(label="Y坐标", tag="add_y", default_value=0, width=280)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="能量", callback=lambda: self.add_substance("energy"), width=90)
                dpg.add_button(label="氧气", callback=lambda: self.add_substance("o2"), width=90)
                dpg.add_button(label="水", callback=lambda: self.add_substance("h2o"), width=90)
            
            dpg.add_button(label="糖分", callback=lambda: self.add_substance("sugar"), width=280)
        
        # 细胞控制
        with dpg.collapsing_header(label="细胞控制", default_open=True):
            dpg.add_input_text(label="细胞名称", tag="cell_name", default_value="新细胞", width=280)
            dpg.add_input_int(label="细胞X", tag="cell_x", default_value=0, width=280)
            dpg.add_input_int(label="细胞Y", tag="cell_y", default_value=0, width=280)
            dpg.add_input_text(label="DNA序列", tag="cell_dna", default_value="", multiline=True, height=100, width=280)
            dpg.add_button(label="随机DNA", callback=self.generate_random_dna, width=280)
            dpg.add_button(label="添加细胞", callback=self.add_cell, width=280)
        
        # 视图控制
        with dpg.collapsing_header(label="视图控制", default_open=True):
            dpg.add_slider_float(label="缩放", tag="zoom_slider", min_value=0.1, max_value=5.0, 
                                default_value=1.0, callback=self.update_zoom, width=280)
            dpg.add_button(label="重置视图", callback=self.reset_view, width=280)
            dpg.add_checkbox(label="显示网格", tag="show_grid", default_value=True, callback=self.update_canvas)
            dpg.add_checkbox(label="显示坐标", tag="show_coords", default_value=False, callback=self.update_canvas)
        
        # 状态信息
        with dpg.collapsing_header(label="状态信息", default_open=True):
            dpg.add_text("模拟状态: 未运行", tag="sim_status")
            dpg.add_text("细胞数量: 0", tag="cell_count")
            dpg.add_text("环境大小: 未知", tag="env_size")
            dpg.add_text("帧率: 0", tag="fps_counter")
    
    def create_canvas_panel(self):
        """创建画布面板"""
        # 创建绘图节点
        with dpg.draw_node(tag="canvas_draw_node"):
            pass
        
        # 创建绘图层
        with dpg.draw_layer(tag="canvas_layer", parent="canvas_draw_node"):
            pass
        
        # 设置画布大小
        dpg.configure_item("canvas_draw_node", width=self.viewport_width, height=self.viewport_height)
        
        # 设置点击事件
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.canvas_click_handler)
            dpg.add_mouse_drag_handler(callback=self.canvas_drag_handler)
            dpg.add_mouse_wheel_handler(callback=self.canvas_wheel_handler)
    
    def create_info_panel(self):
        """创建信息面板"""
        dpg.add_text("细胞信息", color=(0, 200, 255))
        dpg.add_separator()
        
        dpg.add_text("未选择细胞", tag="cell_info_title")
        dpg.add_separator()
        
        with dpg.group(tag="cell_info_group"):
            dpg.add_text("名称: -", tag="info_name")
            dpg.add_text("坐标: (-, -)", tag="info_coord")
            dpg.add_text("颜色: -", tag="info_color")
            dpg.add_text("DNA长度: -", tag="info_dna_len")
            dpg.add_text("RNA长度: -", tag="info_rna_len")
            
            with dpg.collapsing_header(label="DNA序列", default_open=False):
                dpg.add_input_text(tag="info_dna_seq", multiline=True, readonly=True, 
                                  height=150, width=440)
            
            with dpg.collapsing_header(label="RNA序列", default_open=False):
                dpg.add_input_text(tag="info_rna_seq", multiline=True, readonly=True, 
                                  height=150, width=440)
            
            dpg.add_button(label="删除细胞", tag="delete_cell_btn", callback=self.delete_selected_cell, 
                          width=440, show=False)
    
    def draw_environment(self):
        """绘制环境"""
        dpg.delete_item("canvas_layer", children_only=True)
        
        # 获取环境信息
        env_width = self.env.width
        env_height = self.env.height
        
        # 计算绘制范围
        if env_width > 0 and env_height > 0:
            # 有限大环境
            draw_min_x = 0
            draw_max_x = env_width
            draw_min_y = 0
            draw_max_y = env_height
        else:
            # 无限大环境，使用视口
            draw_min_x = self.viewport_x
            draw_max_x = self.viewport_x + int(self.viewport_width / self.zoom_level)
            draw_min_y = self.viewport_y
            draw_max_y = self.viewport_y + int(self.viewport_height / self.zoom_level)
        
        # 绘制网格
        if dpg.get_value("show_grid"):
            grid_color = (100, 100, 100, 50)
            cell_size = 20 * self.zoom_level
            
            for x in range(draw_min_x, draw_max_x + 1):
                screen_x = (x - draw_min_x) * cell_size
                dpg.draw_line(
                    parent="canvas_layer",
                    p1=(screen_x, 0),
                    p2=(screen_x, self.viewport_height),
                    color=grid_color,
                    thickness=1
                )
            
            for y in range(draw_min_y, draw_max_y + 1):
                screen_y = (y - draw_min_y) * cell_size
                dpg.draw_line(
                    parent="canvas_layer",
                    p1=(0, screen_y),
                    p2=(self.viewport_width, screen_y),
                    color=grid_color,
                    thickness=1
                )
        
        # 绘制坐标标签
        if dpg.get_value("show_coords"):
            cell_size = 20 * self.zoom_level
            for x in range(draw_min_x, draw_max_x + 1, 5):
                for y in range(draw_min_y, draw_max_y + 1, 5):
                    screen_x = (x - draw_min_x) * cell_size + 2
                    screen_y = (y - draw_min_y) * cell_size + 2
                    dpg.draw_text(
                        parent="canvas_layer",
                        text=f"({x},{y})",
                        pos=(screen_x, screen_y),
                        size=10,
                        color=(150, 150, 150, 255)
                    )
        
        # 绘制物质
        cell_size = 20 * self.zoom_level
        dot_size = 3 * self.zoom_level
        
        # 获取所有物质
        try:
            if hasattr(self.env, 'type_register_table'):
                type_table = self.env.type_register_table
                
                # 绘制能量
                if env.Energy in type_table:
                    for coord in type_table[env.Energy]:
                        x, y = coord
                        if draw_min_x <= x <= draw_max_x and draw_min_y <= y <= draw_max_y:
                            screen_x = (x - draw_min_x) * cell_size
                            screen_y = (y - draw_min_y) * cell_size
                            dpg.draw_circle(
                                parent="canvas_layer",
                                center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                radius=dot_size,
                                color=self.energy_color,
                                fill=self.energy_color
                            )
                
                # 绘制氧气
                if env.O2 in type_table:
                    for coord in type_table[env.O2]:
                        x, y = coord
                        if draw_min_x <= x <= draw_max_x and draw_min_y <= y <= draw_max_y:
                            screen_x = (x - draw_min_x) * cell_size
                            screen_y = (y - draw_min_y) * cell_size
                            dpg.draw_circle(
                                parent="canvas_layer",
                                center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                radius=dot_size,
                                color=self.o2_color,
                                fill=self.o2_color
                            )
                
                # 绘制水
                if env.H2O in type_table:
                    for coord in type_table[env.H2O]:
                        x, y = coord
                        if draw_min_x <= x <= draw_max_x and draw_min_y <= y <= draw_max_y:
                            screen_x = (x - draw_min_x) * cell_size
                            screen_y = (y - draw_min_y) * cell_size
                            dpg.draw_circle(
                                parent="canvas_layer",
                                center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                radius=dot_size,
                                color=self.h2o_color,
                                fill=self.h2o_color
                            )
                
                # 绘制糖分
                if cells.Sugar in type_table:
                    for coord in type_table[cells.Sugar]:
                        x, y = coord
                        if draw_min_x <= x <= draw_max_x and draw_min_y <= y <= draw_max_y:
                            screen_x = (x - draw_min_x) * cell_size
                            screen_y = (y - draw_min_y) * cell_size
                            dpg.draw_circle(
                                parent="canvas_layer",
                                center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                radius=dot_size,
                                color=self.sugar_color,
                                fill=self.sugar_color
                            )
                
                # 绘制细胞
                if cells.Cell in type_table:
                    for coord in type_table[cells.Cell]:
                        x, y = coord
                        if draw_min_x <= x <= draw_max_x and draw_min_y <= y <= draw_max_y:
                            screen_x = (x - draw_min_x) * cell_size
                            screen_y = (y - draw_min_y) * cell_size
                            
                            # 获取细胞对象
                            cell_list = self.env.read((x, y))
                            cell = None
                            for obj in cell_list:
                                if isinstance(obj, cells.Cell):
                                    cell = obj
                                    break
                            
                            if cell:
                                # 获取或生成颜色
                                cell_id = id(cell)
                                if cell_id not in self.cell_colors:
                                    if hasattr(cell, 'color') and cell.color:
                                        self.cell_colors[cell_id] = (
                                            cell.color[0], 
                                            cell.color[1], 
                                            cell.color[2], 
                                            255
                                        )
                                    else:
                                        # 生成随机颜色
                                        self.cell_colors[cell_id] = (
                                            (hash(cell_id) % 200) + 55,
                                            ((hash(cell_id) // 256) % 200) + 55,
                                            ((hash(cell_id) // 65536) % 200) + 55,
                                            255
                                        )
                                
                                cell_color = self.cell_colors[cell_id]
                                
                                # 绘制细胞
                                radius = 8 * self.zoom_level
                                dpg.draw_circle(
                                    parent="canvas_layer",
                                    center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                    radius=radius,
                                    color=cell_color,
                                    fill=cell_color
                                )
                                
                                # 高亮选中的细胞
                                if self.selected_cell and id(cell) == id(self.selected_cell):
                                    dpg.draw_circle(
                                        parent="canvas_layer",
                                        center=(screen_x + cell_size/2, screen_y + cell_size/2),
                                        radius=radius + 2,
                                        color=(255, 255, 255, 255),
                                        thickness=2
                                    )
                                
                                # 绘制细胞名称
                                if hasattr(cell, 'name') and cell.name:
                                    dpg.draw_text(
                                        parent="canvas_layer",
                                        text=cell.name[:5],
                                        pos=(screen_x + 2, screen_y + 2),
                                        size=10 * self.zoom_level,
                                        color=(255, 255, 255, 255)
                                    )
        except Exception as e:
            print(f"绘制环境时出错: {e}")
    
    def update_canvas(self):
        """更新画布"""
        self.draw_environment()
        
        # 更新状态信息
        try:
            # 获取细胞数量
            cell_count = 0
            if hasattr(self.env, 'type_register_table') and cells.Cell in self.env.type_register_table:
                cell_count = len(self.env.type_register_table[cells.Cell])
            
            # 更新状态显示
            status = "运行中" if self.simulation_running else "已暂停"
            dpg.set_value("sim_status", f"模拟状态: {status}")
            dpg.set_value("cell_count", f"细胞数量: {cell_count}")
            
            env_width = self.env.width
            env_height = self.env.height
            if env_width > 0 and env_height > 0:
                dpg.set_value("env_size", f"环境大小: {env_width}x{env_height}")
            else:
                dpg.set_value("env_size", f"环境大小: 无限大 (视口: {self.viewport_x},{self.viewport_y})")
        except:
            pass
    
    def start_simulation(self):
        """开始模拟"""
        if not self.simulation_running:
            self.simulation_running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
    
    def pause_simulation(self):
        """暂停模拟"""
        self.simulation_running = False
    
    def step_simulation(self):
        """单步执行模拟"""
        try:
            self.sim_controller.run()
            self.update_canvas()
        except Exception as e:
            print(f"单步执行出错: {e}")
    
    def reset_simulation(self):
        """重置模拟"""
        self.pause_simulation()
        time.sleep(0.1)  # 等待线程结束
        
        # 重新创建模拟控制器
        self.sim_controller = sim.SimulationController()
        self.env = self.sim_controller.env
        
        # 重置视图
        self.viewport_x = 0
        self.viewport_y = 0
        self.zoom_level = 1.0
        dpg.set_value("zoom_slider", 1.0)
        
        # 清空选中
        self.selected_cell = None
        self.selected_coord = None
        self.update_cell_info()
        
        # 更新画布
        self.update_canvas()
    
    def simulation_loop(self):
        """模拟循环"""
        last_time = time.time()
        frame_count = 0
        
        while self.simulation_running:
            try:
                # 执行模拟步进
                self.sim_controller.run()
                
                # 每10帧更新一次界面
                frame_count += 1
                if frame_count >= 10:
                    dpg.set_value("fps_counter", f"帧率: {frame_count / (time.time() - last_time):.1f}")
                    dpg.configure_item("canvas_draw_node", width=self.viewport_width, height=self.viewport_height)
                    self.update_canvas()
                    last_time = time.time()
                    frame_count = 0
                
                time.sleep(0.01)  # 避免占用过多CPU
            except Exception as e:
                print(f"模拟循环出错: {e}")
                self.simulation_running = False
    
    def add_substance(self, substance_type):
        """添加物质到环境"""
        try:
            x = dpg.get_value("add_x")
            y = dpg.get_value("add_y")
            
            if substance_type == "energy":
                self.env.write((x, y), env.Energy(100))
            elif substance_type == "o2":
                self.env.write((x, y), env.O2(200))
            elif substance_type == "h2o":
                self.env.write((x, y), env.H2O(200))
            elif substance_type == "sugar":
                self.env.write((x, y), cells.Sugar(6, 12, 6))
            
            self.update_canvas()
        except Exception as e:
            print(f"添加物质出错: {e}")
    
    def generate_random_dna(self):
        """生成随机DNA序列"""
        try:
            import vitae_system
            dna_str = vitae_system.random_DNA.generate_dna(length=300)
            dpg.set_value("cell_dna", dna_str)
        except Exception as e:
            print(f"生成随机DNA出错: {e}")
    
    def add_cell(self):
        """添加细胞"""
        try:
            name = dpg.get_value("cell_name")
            x = dpg.get_value("cell_x")
            y = dpg.get_value("cell_y")
            dna_str = dpg.get_value("cell_dna")
            
            # 创建DNA
            if dna_str:
                dna = cells.DNA(dna_str)
            else:
                dna = cells.DEFAULT_DNA
            
            # 创建细胞
            cell = cells.Cell(self.env, x, y, dna, name)
            
            # 添加到环境
            self.env.write((x, y), cell)
            
            # 更新画布
            self.update_canvas()
        except Exception as e:
            print(f"添加细胞出错: {e}")
    
    def canvas_click_handler(self, sender, app_data):
        """画布点击事件处理"""
        if app_data[0] == 0:  # 左键点击
            # 获取点击坐标
            mouse_x = app_data[1]
            mouse_y = app_data[2]
            
            # 转换为环境坐标
            cell_size = 20 * self.zoom_level
            env_x = int(mouse_x / cell_size) + self.viewport_x
            env_y = int(mouse_y / cell_size) + self.viewport_y
            
            # 查找该位置的细胞
            try:
                objects = self.env.read((env_x, env_y))
                if objects:
                    for obj in objects:
                        if isinstance(obj, cells.Cell):
                            self.selected_cell = obj
                            self.selected_coord = (env_x, env_y)
                            self.update_cell_info()
                            self.update_canvas()
                            return
                
                # 如果没有细胞，取消选择
                self.selected_cell = None
                self.selected_coord = None
                self.update_cell_info()
                self.update_canvas()
            except:
                pass
    
    def canvas_drag_handler(self, sender, app_data):
        """画布拖拽事件处理（用于移动视口）"""
        if app_data[0] == 1:  # 左键拖拽
            dx = app_data[1]
            dy = app_data[2]
            
            # 移动视口
            cell_size = 20 * self.zoom_level
            self.viewport_x -= int(dx / cell_size)
            self.viewport_y -= int(dy / cell_size)
            
            self.update_canvas()
    
    def canvas_wheel_handler(self, sender, app_data):
        """画布滚轮事件处理（用于缩放）"""
        zoom_delta = 0.1
        if app_data > 0:
            # 放大
            self.zoom_level = min(5.0, self.zoom_level + zoom_delta)
        else:
            # 缩小
            self.zoom_level = max(0.1, self.zoom_level - zoom_delta)
        
        dpg.set_value("zoom_slider", self.zoom_level)
        self.update_canvas()
    
    def update_zoom(self):
        """更新缩放级别"""
        self.zoom_level = dpg.get_value("zoom_slider")
        self.update_canvas()
    
    def reset_view(self):
        """重置视图"""
        self.viewport_x = 0
        self.viewport_y = 0
        self.zoom_level = 1.0
        dpg.set_value("zoom_slider", 1.0)
        self.update_canvas()
    
    def update_cell_info(self):
        """更新细胞信息面板"""
        if self.selected_cell and hasattr(self.selected_cell, '__class__'):
            cell = self.selected_cell
            
            # 更新基本信息
            name = getattr(cell, 'name', '未命名')
            dpg.set_value("cell_info_title", f"细胞: {name}")
            dpg.set_value("info_name", f"名称: {name}")
            
            if self.selected_coord:
                dpg.set_value("info_coord", f"坐标: ({self.selected_coord[0]}, {self.selected_coord[1]})")
            
            # 颜色
            if hasattr(cell, 'color') and cell.color:
                color = cell.color
                dpg.set_value("info_color", f"颜色: RGB({color[0]}, {color[1]}, {color[2]})")
            else:
                dpg.set_value("info_color", "颜色: 默认")
            
            # DNA信息
            if hasattr(cell, 'dna') and cell.dna:
                dna_str = str(cell.dna)
                dpg.set_value("info_dna_len", f"DNA长度: {len(dna_str)}")
                dpg.set_value("info_dna_seq", dna_str[:1000])  # 限制显示长度
            else:
                dpg.set_value("info_dna_len", "DNA长度: 未知")
                dpg.set_value("info_dna_seq", "")
            
            # RNA信息
            if hasattr(cell, 'rna') and cell.rna:
                rna_str = str(cell.rna)
                dpg.set_value("info_rna_len", f"RNA长度: {len(rna_str)}")
                dpg.set_value("info_rna_seq", rna_str[:1000])  # 限制显示长度
            else:
                dpg.set_value("info_rna_len", "RNA长度: 未知")
                dpg.set_value("info_rna_seq", "")
            
            # 显示删除按钮
            dpg.show_item("delete_cell_btn")
        else:
            # 没有选中细胞
            dpg.set_value("cell_info_title", "未选择细胞")
            dpg.set_value("info_name", "名称: -")
            dpg.set_value("info_coord", "坐标: (-, -)")
            dpg.set_value("info_color", "颜色: -")
            dpg.set_value("info_dna_len", "DNA长度: -")
            dpg.set_value("info_rna_len", "RNA长度: -")
            dpg.set_value("info_dna_seq", "")
            dpg.set_value("info_rna_seq", "")
            
            # 隐藏删除按钮
            dpg.hide_item("delete_cell_btn")
    
    def delete_selected_cell(self):
        """删除选中的细胞"""
        if self.selected_cell and self.selected_coord:
            try:
                # 从环境中删除细胞
                objects = self.env.read(self.selected_coord)
                if objects:
                    for i, obj in enumerate(objects):
                        if isinstance(obj, cells.Cell) and id(obj) == id(self.selected_cell):
                            self.env.delete(self.selected_coord, i)
                            break
                
                # 清除选中
                self.selected_cell = None
                self.selected_coord = None
                self.update_cell_info()
                self.update_canvas()
            except Exception as e:
                print(f"删除细胞出错: {e}")
    
    def run(self):
        """运行GUI"""
        # 初始绘制
        self.update_canvas()
        
        # 启动主循环
        while dpg.is_dearpygui_running():
            # 可以在这里添加其他更新逻辑
            dpg.render_dearpygui_frame()
        
        dpg.destroy_context()

def main():
    """主函数"""
    gui = VitaeCanvasGUI()
    gui.run()

if __name__ == "__main__":
    main()
