
import os
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dearpygui.dearpygui as dpg
from vitae_system import *
from vitae_system import random_DNA
import sim

class VitaeCanvasGUI:
    def __init__(self):
        self.controller = sim.SimulationController()
        self.env = self.controller.env
        self.selected_cell = None
        self.simulation_running = False
        self.sim_thread = None
        self.cell_size = 20
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.zoom_level = 1.0

        # 获取环境信息
        self.update_env_info()

    def update_env_info(self):
        """更新环境信息"""
        self.env_width = self.env.width
        self.env_height = self.env.height
        self.is_infinite = self.env_width < 0 or self.env_height < 0

    def get_cells(self):
        """获取所有细胞"""
        cells_list = []
        try:
            cell_positions = self.env.type_register_table.get(cells.Cell, [])
            for pos in cell_positions:
                contents = self.env.read(pos)
                for item in contents:
                    if isinstance(item, cells.Cell):
                        cells_list.append(item)
        except Exception as e:
            print(f"Get cells error: {e}")
        return cells_list

    def get_energies(self):
        """获取所有能量"""
        energy_list = []
        try:
            energy_positions = self.env.type_register_table.get(env.Energy, [])
            for pos in energy_positions:
                contents = self.env.read(pos)
                for item in contents:
                    if isinstance(item, env.Energy):
                        energy_list.append((pos, item))
        except Exception as e:
            print(f"Get energies error: {e}")
        return energy_list

    def get_other_substances(self):
        """获取其他物质"""
        substances = []
        try:
            for dtype, positions in self.env.type_register_table.items():
                if dtype not in [cells.Cell, env.Energy]:
                    for pos in positions:
                        contents = self.env.read(pos)
                        for item in contents:
                            if type(item) == dtype:
                                substances.append((pos, item))
        except Exception as e:
            print(f"Get substances error: {e}")
        return substances

    def run_simulation(self):
        """在后台线程中运行模拟"""
        while self.simulation_running:
            try:
                self.controller.run()
            except Exception as e:
                print(f"Simulation error: {e}")
            time.sleep(0.1)

    def toggle_simulation(self, sender, app_data):
        """切换模拟运行状态"""
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            dpg.set_item_label(sender, "暂停模拟")
            self.sim_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.sim_thread.start()
        else:
            dpg.set_item_label(sender, "开始模拟")

    def step_simulation(self, sender, app_data):
        """单步运行模拟"""
        try:
            self.controller.run()
        except Exception as e:
            print(f"Step error: {e}")

    def create_cell(self, sender, app_data):
        """创建新细胞"""
        try:
            x = dpg.get_value("new_cell_x")
            y = dpg.get_value("new_cell_y")
            dna_str = dpg.get_value("new_cell_dna")
            name = dpg.get_value("new_cell_name")

            if not name:
                name = None

            if dna_str:
                dna = cells.DNA(dna_str)
            else:
                dna_str = random_DNA.generate_dna()
                dna = cells.DNA(dna_str)

            new_cell = cells.Cell(self.env, x, y, dna=dna, name=name)

            # 更新细胞列表
            self.update_cell_list()
        except Exception as e:
            print(f"Create cell error: {e}")

    def add_energy(self, sender, app_data):
        """添加能量"""
        try:
            x = dpg.get_value("energy_x")
            y = dpg.get_value("energy_y")
            amount = dpg.get_value("energy_amount")

            energy = env.Energy(amount)
            self.env.write((x, y), energy)
        except Exception as e:
            print(f"Add energy error: {e}")

    def add_o2(self, sender, app_data):
        """添加氧气"""
        try:
            x = dpg.get_value("substance_x")
            y = dpg.get_value("substance_y")
            amount = dpg.get_value("substance_amount")

            o2 = env.O2(amount)
            self.env.write((x, y), o2)
        except Exception as e:
            print(f"Add O2 error: {e}")

    def add_h2o(self, sender, app_data):
        """添加水"""
        try:
            x = dpg.get_value("substance_x")
            y = dpg.get_value("substance_y")
            amount = dpg.get_value("substance_amount")

            h2o = env.H2O(amount)
            self.env.write((x, y), h2o)
        except Exception as e:
            print(f"Add H2O error: {e}")

    def add_sugar(self, sender, app_data):
        """添加糖"""
        try:
            x = dpg.get_value("substance_x")
            y = dpg.get_value("substance_y")
            c = dpg.get_value("sugar_c")
            h = dpg.get_value("sugar_h")
            o = dpg.get_value("sugar_o")

            sugar = cells.Sugar(c, h, o)
            self.env.write((x, y), sugar)
        except Exception as e:
            print(f"Add sugar error: {e}")

    def update_cell_list(self):
        """更新细胞列表"""
        dpg.delete_item("cell_list", children_only=True)
        cell_list = self.get_cells()
        for cell in cell_list:
            cell_name = cell.name if cell.name else f"Cell({cell.x},{cell.y})"
            dpg.add_selectable(label=f"{cell_name} - ({cell.x}, {cell.y})", 
                              parent="cell_list",
                              callback=self.select_cell,
                              user_data=cell)

    def select_cell(self, sender, app_data, user_data):
        """选择细胞"""
        self.selected_cell = user_data
        self.update_info_panel()

    def update_info_panel(self):
        """更新信息面板"""
        if self.selected_cell is None:
            dpg.set_value("info_text", "未选择细胞\n请在画布或列表中选择一个细胞")
            return

        cell = self.selected_cell
        info = f"""
细胞名称: {cell.name if cell.name else '未命名'}
坐标: ({cell.x}, {cell.y})
颜色: RGB{cell.color}

--- DNA信息 ---
{str(cell.dna)[:100]}...

--- RNA信息 ---
{str(cell.rna)[:100]}...
"""
        dpg.set_value("info_text", info)

        # 更新颜色预览
        dpg.configure_item("cell_color_preview", fill=cell.color)

    def on_canvas_click(self, sender, app_data):
        """画布点击事件"""
        mouse_pos = dpg.get_drawing_mouse_pos()
        canvas_x = (mouse_pos[0] - self.canvas_offset_x) / (self.cell_size * self.zoom_level)
        canvas_y = (mouse_pos[1] - self.canvas_offset_y) / (self.cell_size * self.zoom_level)

        grid_x = int(canvas_x)
        grid_y = int(canvas_y)

        # 检查是否有细胞在此位置
        cell_list = self.get_cells()
        for cell in cell_list:
            if cell.x == grid_x and cell.y == grid_y:
                self.selected_cell = cell
                self.update_info_panel()
                return

        # 如果没有细胞，显示坐标信息
        self.selected_cell = None
        dpg.set_value("info_text", f"坐标: ({grid_x}, {grid_y})\n该位置没有细胞")

    def draw_canvas(self):
        """绘制画布"""
        dpg.delete_item("canvas_drawlist", children_only=True)

        # 获取画布大小
        canvas_width = dpg.get_item_width("canvas_window")
        canvas_height = dpg.get_item_height("canvas_window")

        if canvas_width == 0 or canvas_height == 0:
            canvas_width = 600
            canvas_height = 600

        # 计算偏移量使画布居中
        if not self.is_infinite:
            total_width = self.env_width * self.cell_size * self.zoom_level
            total_height = self.env_height * self.cell_size * self.zoom_level
            self.canvas_offset_x = max(0, (canvas_width - total_width) / 2)
            self.canvas_offset_y = max(0, (canvas_height - total_height) / 2)
        else:
            self.canvas_offset_x = canvas_width / 2
            self.canvas_offset_y = canvas_height / 2

        # 绘制网格背景
        if not self.is_infinite:
            for x in range(self.env_width + 1):
                px = self.canvas_offset_x + x * self.cell_size * self.zoom_level
                dpg.draw_line((px, self.canvas_offset_y), 
                             (px, self.canvas_offset_y + self.env_height * self.cell_size * self.zoom_level),
                             color=(50, 50, 50), thickness=1, parent="canvas_drawlist")

            for y in range(self.env_height + 1):
                py = self.canvas_offset_y + y * self.cell_size * self.zoom_level
                dpg.draw_line((self.canvas_offset_x, py), 
                             (self.canvas_offset_x + self.env_width * self.cell_size * self.zoom_level, py),
                             color=(50, 50, 50), thickness=1, parent="canvas_drawlist")
        else:
            # 无限环境绘制有限网格
            grid_range = 20
            for x in range(-grid_range, grid_range + 1):
                px = self.canvas_offset_x + x * self.cell_size * self.zoom_level
                dpg.draw_line((px, self.canvas_offset_y - grid_range * self.cell_size * self.zoom_level), 
                             (px, self.canvas_offset_y + grid_range * self.cell_size * self.zoom_level),
                             color=(50, 50, 50), thickness=1, parent="canvas_drawlist")

            for y in range(-grid_range, grid_range + 1):
                py = self.canvas_offset_y + y * self.cell_size * self.zoom_level
                dpg.draw_line((self.canvas_offset_x - grid_range * self.cell_size * self.zoom_level, py), 
                             (self.canvas_offset_x + grid_range * self.cell_size * self.zoom_level, py),
                             color=(50, 50, 50), thickness=1, parent="canvas_drawlist")

        # 绘制能量
        energies = self.get_energies()
        for pos, energy in energies:
            px = self.canvas_offset_x + pos[0] * self.cell_size * self.zoom_level
            py = self.canvas_offset_y + pos[1] * self.cell_size * self.zoom_level
            size = self.cell_size * self.zoom_level * 0.3
            dpg.draw_circle((px + self.cell_size * self.zoom_level / 2, py + self.cell_size * self.zoom_level / 2), 
                           size, color=(255, 255, 0), fill=(255, 255, 0), parent="canvas_drawlist")

        # 绘制其他物质
        substances = self.get_other_substances()
        for pos, substance in substances:
            px = self.canvas_offset_x + pos[0] * self.cell_size * self.zoom_level
            py = self.canvas_offset_y + pos[1] * self.cell_size * self.zoom_level
            if isinstance(substance, env.O2):
                color = (0, 150, 255)
            elif isinstance(substance, env.H2O):
                color = (0, 100, 200)
            elif isinstance(substance, cells.Sugar):
                color = (200, 200, 200)
            else:
                color = (150, 150, 150)
            size = self.cell_size * self.zoom_level * 0.2
            dpg.draw_circle((px + self.cell_size * self.zoom_level / 2, py + self.cell_size * self.zoom_level / 2), 
                           size, color=color, fill=color, parent="canvas_drawlist")

        # 绘制细胞
        cell_list = self.get_cells()
        for cell in cell_list:
            px = self.canvas_offset_x + cell.x * self.cell_size * self.zoom_level
            py = self.canvas_offset_y + cell.y * self.cell_size * self.zoom_level
            size = self.cell_size * self.zoom_level * 0.4

            # 高亮选中的细胞
            if self.selected_cell == cell:
                dpg.draw_rectangle((px - 2, py - 2), 
                                  (px + self.cell_size * self.zoom_level + 2, py + self.cell_size * self.zoom_level + 2),
                                  color=(255, 255, 255), thickness=2, parent="canvas_drawlist")

            dpg.draw_circle((px + self.cell_size * self.zoom_level / 2, py + self.cell_size * self.zoom_level / 2), 
                           size, color=cell.color, fill=cell.color, parent="canvas_drawlist")

            # 绘制细胞名称
            if cell.name:
                dpg.draw_text((px + 2, py + 2), cell.name[:8], color=(255, 255, 255), size=10 * self.zoom_level, parent="canvas_drawlist")

    def update_callback(self):
        """每帧更新回调"""
        self.update_env_info()
        self.draw_canvas()
        self.update_cell_list()
        if self.selected_cell:
            self.update_info_panel()

    def zoom_in(self, sender, app_data):
        """放大"""
        self.zoom_level = min(3.0, self.zoom_level + 0.2)
        dpg.set_value("zoom_text", f"缩放: {self.zoom_level:.1f}x")

    def zoom_out(self, sender, app_data):
        """缩小"""
        self.zoom_level = max(0.3, self.zoom_level - 0.2)
        dpg.set_value("zoom_text", f"缩放: {self.zoom_level:.1f}x")

    def reset_view(self, sender, app_data):
        """重置视图"""
        self.zoom_level = 1.0
        dpg.set_value("zoom_text", f"缩放: {self.zoom_level:.1f}x")

    def setup_ui(self):
        """设置UI界面"""
        # 中文字体设置
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)

        # 创建视口
        dpg.create_viewport(title="VitaeCanvas - 生命绘卷", width=1400, height=900)

        # 主窗口
        with dpg.window(tag="main_window", label="VitaeCanvas", no_title_bar=True, no_resize=True, no_move=True):
            dpg.add_menu_bar()
            with dpg.menu(label="文件"):
                dpg.add_menu_item(label="退出", callback=lambda: dpg.stop_dearpygui())
            with dpg.menu(label="视图"):
                dpg.add_menu_item(label="放大", callback=self.zoom_in)
                dpg.add_menu_item(label="缩小", callback=self.zoom_out)
                dpg.add_menu_item(label="重置视图", callback=self.reset_view)
            with dpg.menu(label="帮助"):
                dpg.add_menu_item(label="关于VitaeCanvas")

        # 左侧面板 - 控制面板 (25%)
        with dpg.child_window(tag="left_panel", parent="main_window", width=350, height=-1, pos=(0, 20)):
            dpg.add_text("控制面板", color=(100, 200, 255))
            dpg.add_separator()

            # 模拟控制
            with dpg.collapsing_header(label="模拟控制", default_open=True):
                dpg.add_button(label="开始模拟", tag="sim_toggle_btn", callback=self.toggle_simulation, width=-1)
                dpg.add_button(label="单步运行", callback=self.step_simulation, width=-1)
                dpg.add_text("缩放: 1.0x", tag="zoom_text")
                dpg.add_button(label="放大", callback=self.zoom_in, width=100)
                dpg.add_same_line()
                dpg.add_button(label="缩小", callback=self.zoom_out, width=100)
                dpg.add_same_line()
                dpg.add_button(label="重置", callback=self.reset_view, width=100)

            # 创建细胞
            with dpg.collapsing_header(label="创建细胞", default_open=True):
                dpg.add_text("坐标 X:")
                dpg.add_input_int(tag="new_cell_x", default_value=0, width=-1)
                dpg.add_text("坐标 Y:")
                dpg.add_input_int(tag="new_cell_y", default_value=0, width=-1)
                dpg.add_text("细胞名称:")
                dpg.add_input_text(tag="new_cell_name", default_value="", width=-1)
                dpg.add_text("DNA序列 (留空则随机生成):")
                dpg.add_input_text(tag="new_cell_dna", default_value="", width=-1)
                dpg.add_button(label="创建细胞", callback=self.create_cell, width=-1)

            # 添加物质
            with dpg.collapsing_header(label="添加物质", default_open=True):
                dpg.add_text("坐标 X:")
                dpg.add_input_int(tag="energy_x", default_value=0, width=-1)
                dpg.add_text("坐标 Y:")
                dpg.add_input_int(tag="energy_y", default_value=0, width=-1)

                dpg.add_text("--- 能量 ---")
                dpg.add_input_int(tag="energy_amount", default_value=100, width=-1)
                dpg.add_button(label="添加能量", callback=self.add_energy, width=-1)

                dpg.add_text("--- 其他物质 ---")
                dpg.add_input_int(tag="substance_x", default_value=0, width=-1)
                dpg.add_input_int(tag="substance_y", default_value=0, width=-1)
                dpg.add_input_int(tag="substance_amount", default_value=200, width=-1)
                dpg.add_button(label="添加氧气(O2)", callback=self.add_o2, width=-1)
                dpg.add_button(label="添加水(H2O)", callback=self.add_h2o, width=-1)

                dpg.add_text("--- 糖 ---")
                dpg.add_input_int(tag="sugar_c", label="C", default_value=6, width=80)
                dpg.add_same_line()
                dpg.add_input_int(tag="sugar_h", label="H", default_value=12, width=80)
                dpg.add_same_line()
                dpg.add_input_int(tag="sugar_o", label="O", default_value=6, width=80)
                dpg.add_button(label="添加糖", callback=self.add_sugar, width=-1)

            # 细胞列表
            with dpg.collapsing_header(label="细胞列表", default_open=True):
                with dpg.child_window(tag="cell_list", width=-1, height=200):
                    pass

        # 中间画布 (45%)
        with dpg.child_window(tag="canvas_window", parent="main_window", width=630, height=-1, pos=(355, 20)):
            dpg.add_text("环境画布", color=(100, 200, 255))
            dpg.add_separator()

            with dpg.drawlist(tag="canvas_drawlist", width=620, height=800):
                # 绘制内容将在update_callback中更新
                pass

            # 鼠标点击事件
            with dpg.handler_registry():
                dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=self.on_canvas_click)

        # 右侧面板 - 信息面板 (30%)
        with dpg.child_window(tag="right_panel", parent="main_window", width=-1, height=-1, pos=(990, 20)):
            dpg.add_text("信息面板", color=(100, 200, 255))
            dpg.add_separator()

            # 环境信息
            with dpg.collapsing_header(label="环境信息", default_open=True):
                dpg.add_text("环境大小:", tag="env_size_text")
                dpg.add_text("细胞数量:", tag="cell_count_text")
                dpg.add_text("能量数量:", tag="energy_count_text")

            # 选中细胞信息
            with dpg.collapsing_header(label="细胞详情", default_open=True):
                # 颜色预览
                with dpg.drawlist(width=50, height=50):
                    dpg.draw_rectangle((0, 0), (50, 50), color=(100, 100, 100), fill=(100, 100, 100), tag="cell_color_preview")

                dpg.add_text("未选择细胞", tag="info_text", wrap=380)

    def run(self):
        """运行GUI"""
        dpg.create_context()
        self.setup_ui()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

        # 主循环
        while dpg.is_dearpygui_running():
            self.update_callback()
            dpg.render_dearpygui_frame()

        self.simulation_running = False
        dpg.destroy_context()


if __name__ == "__main__":
    gui = VitaeCanvasGUI()
    gui.run()