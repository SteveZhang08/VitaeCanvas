import os
import sys
import threading
import time

# 确保库路径正确
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dearpygui.dearpygui as dpg
from sim import SimulationController
from vitae_system import cells, env, random_DNA

class VitaeCanvasGUI:
    def __init__(self):
        self.controller = SimulationController()
        self.is_running = False
        self.selected_cell = None
        self.draw_scale = 20  # 绘图缩放比例
        self.sim_thread = None

        self.setup_dpg()
        self.create_windows()
        self.setup_fonts()

    def setup_fonts(self):
        # 中文支持设置
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)

    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='VitaeCanvas - 生命绘卷', width=1200, height=800)
        dpg.setup_dearpygui()

    def sim_loop(self):
        """模拟逻辑循环线程"""
        while self.is_running:
            self.controller.run()
            time.sleep(0.1)  # 控制模拟频率

    def toggle_simulation(self):
        self.is_running = not self.is_running
        if self.is_running:
            dpg.configure_item("status_text", default_value="状态: 运行中", color=[0, 255, 0])
            dpg.configure_item("start_stop_btn", label="暂停模拟")
            self.sim_thread = threading.Thread(target=self.sim_loop, daemon=True)
            self.sim_thread.start()
        else:
            dpg.configure_item("status_text", default_value="状态: 已停止", color=[255, 0, 0])
            dpg.configure_item("start_stop_btn", label="开始模拟")

    def add_random_cell(self):
        # 随机位置
        width = self.controller.env.width if self.controller.env.width > 0 else 50
        height = self.controller.env.height if self.controller.env.height > 0 else 50
        import random
        rx, ry = random.randint(0, width), random.randint(0, height)
        
        # 生成DNA并创建细胞
        dna_str = random_DNA.generate_dna(300)
        new_dna = cells.DNA(dna_str)
        new_cell = cells.Cell(self.controller.env, rx, ry, dna=new_dna, name=f"Cell_{rx}_{ry}")
        
        # 写入环境
        self.controller.env.write((rx, ry), new_cell)

    def update_canvas(self):
        """刷新画布绘制环境中的物质和细胞"""
        dpg.delete_item("env_drawing", children_only=True)
        
        e = self.controller.env
        # 获取所有已注册类型的坐标
        type_table = e.type_register_table
        
        for obj_type, coords in type_table.items():
            for coord in coords:
                items = e.read(coord)
                if not items: continue
                
                for item in items:
                    x, y = coord[0] * self.draw_scale, coord[1] * self.draw_scale
                    size = self.draw_scale - 2
                    
                    if isinstance(item, cells.Cell):
                        # 绘制细胞
                        color = item.color if hasattr(item, 'color') else (0, 255, 0)
                        dpg.draw_circle(center=(x + size/2, y + size/2), radius=size/2, 
                                        fill=(color[0], color[1], color[2], 200), parent="env_drawing")
                    else:
                        # 绘制能量或资源
                        dpg.draw_rect(pmin=(x, y), pmax=(x + size, y + size), 
                                      fill=(100, 100, 255, 150), parent="env_drawing")

    def on_canvas_click(self):
        """点击画布选择细胞"""
        mouse_pos = dpg.get_drawing_mouse_pos()
        grid_x = int(mouse_pos[0] // self.draw_scale)
        grid_y = int(mouse_pos[1] // self.draw_scale)
        
        contents = self.controller.env.read((grid_x, grid_y))
        if contents:
            for item in contents:
                if isinstance(item, cells.Cell):
                    self.selected_cell = item
                    self.update_info_panel()
                    return
        self.selected_cell = None
        self.update_info_panel()

    def update_info_panel(self):
        """更新右侧信息面板"""
        if self.selected_cell:
            dpg.set_value("info_name", f"名称: {self.selected_cell.name}")
            dpg.set_value("info_pos", f"位置: ({self.selected_cell.x}, {self.selected_cell.y})")
            dpg.set_value("info_dna", f"DNA: {str(self.selected_cell.dna)[:50]}...")
            dpg.set_value("info_rna", f"RNA: {str(self.selected_cell.rna)[:50]}...")
        else:
            dpg.set_value("info_name", "名称: 未选中")
            dpg.set_value("info_pos", "位置: -")
            dpg.set_value("info_dna", "DNA: -")
            dpg.set_value("info_rna", "RNA: -")

    def create_windows(self):
        # 左侧控制面板
        with dpg.window(label="控制面板", width=300, height=800, pos=(0, 0), no_close=True):
            dpg.add_text("全局操作")
            dpg.add_button(label="开始模拟", tag="start_stop_btn", callback=self.toggle_simulation, width=-1)
            dpg.add_button(label="添加随机细胞", callback=self.add_random_cell, width=-1)
            dpg.add_spacer(height=10)
            dpg.add_text("状态: 已停止", tag="status_text", color=[255, 0, 0])
            dpg.add_slider_int(label="缩放比例", default_value=20, min_value=5, max_value=50, 
                               callback=lambda s, d: setattr(self, 'draw_scale', d))

        # 中间画布
        with dpg.window(label="环境预览 (Canvas)", width=600, height=800, pos=(300, 0), no_close=True):
            with dpg.drawlist(width=1000, height=1000, tag="canvas_list"):
                with dpg.draw_layer(tag="env_drawing"):
                    pass
            # 画布点击检测
            with dpg.item_handler_registry(tag="canvas_handler"):
                dpg.add_item_clicked_handler(callback=self.on_canvas_click)
            dpg.bind_item_handler_registry("canvas_list", "canvas_handler")

        # 右侧信息面板
        with dpg.window(label="详细信息", width=300, height=800, pos=(900, 0), no_close=True):
            dpg.add_text("细胞属性", color=(255, 255, 0))
            dpg.add_text("名称: 未选中", tag="info_name")
            dpg.add_text("位置: -", tag="info_pos")
            dpg.add_separator()
            dpg.add_text("遗传信息")
            dpg.add_input_text(label="", tag="info_dna", multiline=True, readonly=True, height=100)
            dpg.add_input_text(label="", tag="info_rna", multiline=True, readonly=True, height=100)

    def run(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            self.update_canvas() # 实时刷新画布
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

if __name__ == "__main__":
    app = VitaeCanvasGUI()
    app.run()