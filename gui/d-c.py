import dearpygui.dearpygui as dpg
import threading
import time
import random
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import *
from vitae_system import *
from vitae_system import cells
from vitae_system import random_DNA

class VitaeCanvasGUI:
    def __init__(self):
        self.controller = None
        self.selected_cell = None
        self.running = False
        self.simulation_thread = None
        
        # 存储环境状态的缓存
        self.env_cache = {}
        self.cell_info_cache = {}
        
        # 初始化GUI
        self.setup_gui()
        
    def setup_gui(self):
        """设置GUI界面"""
        dpg.create_context()
        
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)
        # 创建主窗口
        with dpg.window(label="VitaeCanvas - 生命绘卷", tag="main_window", 
                       width=1400, height=900, no_close=True):
            
            # 创建菜单栏
            with dpg.menu_bar():
                with dpg.menu(label="文件"):
                    dpg.add_menu_item(label="新建模拟", callback=self.new_simulation)
                    dpg.add_menu_item(label="加载模拟")
                    dpg.add_menu_item(label="保存模拟")
                    dpg.add_separator()
                    dpg.add_menu_item(label="退出", callback=lambda: dpg.stop_dearpygui())
                
                with dpg.menu(label="视图"):
                    dpg.add_menu_item(label="重置视图", callback=self.reset_view)
                    dpg.add_menu_item(label="适应窗口", callback=self.fit_to_window)
                
                with dpg.menu(label="帮助"):
                    dpg.add_menu_item(label="关于", callback=self.show_about)
            
            # 主布局 - 使用group和child实现左中右布局
            with dpg.group(horizontal=True):
                
                # 左侧控制面板 (25%宽度)
                with dpg.child_window(tag="left_panel", width=300, height=-1):
                    self.create_control_panel()
                
                # 中间画布 (50%宽度)  
                with dpg.child_window(tag="center_panel", width=700, height=-1):
                    self.create_canvas()
                
                # 右侧信息面板 (25%宽度)
                with dpg.child_window(tag="right_panel", width=300, height=-1):
                    self.create_info_panel()
        
        # 创建视口
        dpg.create_viewport(title="VitaeCanvas GUI", width=1400, height=900)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
    def create_control_panel(self):
        """创建左侧控制面板"""
        dpg.add_text("控制面板")
        dpg.add_separator()
        
        # 模拟控制区域
        with dpg.collapsing_header(label="模拟控制", default_open=True):
            dpg.add_button(label="初始化模拟", callback=self.initialize_simulation, width=-1)
            dpg.add_button(label="开始", callback=self.start_simulation, width=-1, tag="start_btn")
            dpg.add_button(label="暂停", callback=self.pause_simulation, width=-1, tag="pause_btn")
            dpg.add_button(label="重置", callback=self.reset_simulation, width=-1)
            
            dpg.add_separator()
            dpg.add_text("模拟速度")
            dpg.add_slider_int(label="", default_value=1, min_value=1, max_value=100, 
                             tag="speed_slider", width=-1)
        
        # 环境控制区域
        with dpg.collapsing_header(label="环境设置", default_open=True):
            dpg.add_input_int(label="环境宽度", default_value=100, tag="env_width", width=-1)
            dpg.add_input_int(label="环境高度", default_value=100, tag="env_height", width=-1)
            dpg.add_button(label="更新环境大小", callback=self.update_environment, width=-1)
            
            dpg.add_separator()
            dpg.add_text("环境参数")
            dpg.add_input_float(label="能量扩散率", default_value=0.1, tag="energy_diffusion", width=-1)
            dpg.add_input_float(label="初始能量密度", default_value=0.5, tag="energy_density", width=-1)
        
        # 细胞操作区域
        with dpg.collapsing_header(label="细胞操作", default_open=True):
            dpg.add_input_int(label="X坐标", default_value=50, tag="new_cell_x", width=-1)
            dpg.add_input_int(label="Y坐标", default_value=50, tag="new_cell_y", width=-1)
            
            dpg.add_text("DNA序列 (可选)")
            dpg.add_input_text(label="", default_value="", tag="new_cell_dna", width=-1)
            
            dpg.add_button(label="添加细胞", callback=self.add_cell, width=-1)
            dpg.add_button(label="添加随机细胞", callback=self.add_random_cell, width=-1)
            
            dpg.add_separator()
            dpg.add_text("批量添加")
            dpg.add_input_int(label="细胞数量", default_value=10, tag="batch_cell_count", width=-1)
            dpg.add_button(label="批量添加随机细胞", callback=self.batch_add_cells, width=-1)
        
        # 物质操作区域
        with dpg.collapsing_header(label="物质操作", default_open=True):
            dpg.add_input_int(label="X坐标", default_value=50, tag="resource_x", width=-1)
            dpg.add_input_int(label="Y坐标", default_value=50, tag="resource_y", width=-1)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="添加能量", callback=self.add_energy)
                dpg.add_button(label="添加氧气", callback=self.add_oxygen)
            
            dpg.add_button(label="添加水", callback=self.add_water, width=-1)
            dpg.add_button(label="添加糖分", callback=self.add_sugar, width=-1)
        
        # 统计信息
        with dpg.collapsing_header(label="模拟统计", default_open=True):
            dpg.add_text("", tag="stats_text")
    
    def create_canvas(self):
        """创建中间画布"""
        dpg.add_text("模拟环境画布")
        dpg.add_separator()
        
        # 创建绘图区域
        with dpg.plot(label="环境视图", height=-1, width=-1, tag="env_plot",
                     equal_aspects=True):
            dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label="Y", tag="y_axis")
            
            # 添加图层用于不同类型
            dpg.add_scatter_series([], [], label="能量", parent="y_axis", tag="energy_scatter")
            dpg.add_scatter_series([], [], label="细胞", parent="y_axis", tag="cells_scatter")
            dpg.add_scatter_series([], [], label="氧气", parent="y_axis", tag="oxygen_scatter")
            dpg.add_scatter_series([], [], label="水", parent="y_axis", tag="water_scatter")
            dpg.add_scatter_series([], [], label="糖分", parent="y_axis", tag="sugar_scatter")
            
            dpg.add_plot_legend()
        
        # 画布控制按钮
        with dpg.group(horizontal=True):
            dpg.add_button(label="刷新视图", callback=self.refresh_view)
            dpg.add_button(label="自动刷新", callback=self.toggle_auto_refresh, tag="auto_refresh_btn")
            dpg.add_text("刷新间隔(ms)")
            dpg.add_input_int(label="", default_value=100, min_value=10, max_value=5000, 
                            tag="refresh_interval", width=100)
    
    def create_info_panel(self):
        """创建右侧信息面板"""
        dpg.add_text("信息面板")
        dpg.add_separator()
        
        # 环境信息
        with dpg.collapsing_header(label="环境信息", default_open=True):
            dpg.add_text("环境尺寸: ", tag="env_size_text")
            dpg.add_text("总能量: ", tag="total_energy_text")
            dpg.add_text("细胞总数: ", tag="total_cells_text")
            dpg.add_text("模拟状态: 未初始化", tag="sim_status_text")
        
        # 选中细胞信息
        with dpg.collapsing_header(label="细胞详细信息", default_open=True):
            dpg.add_text("选择一个细胞以查看详细信息")
            dpg.add_separator()
            
            dpg.add_text("名称: ---", tag="cell_name_text")
            dpg.add_text("位置: ---", tag="cell_position_text")
            dpg.add_text("颜色: ---", tag="cell_color_text")
            
            with dpg.collapsing_header(label="DNA序列", tag="dna_header"):
                dpg.add_text("", tag="dna_sequence_text", wrap=250)
            
            with dpg.collapsing_header(label="RNA序列", tag="rna_header"):
                dpg.add_text("", tag="rna_sequence_text", wrap=250)
            
            with dpg.collapsing_header(label="蛋白质", tag="protein_header"):
                dpg.add_text("", tag="protein_info_text", wrap=250)
            
            dpg.add_separator()
            dpg.add_button(label="删除选中细胞", callback=self.delete_selected_cell, width=-1)
    
    def initialize_simulation(self, sender, app_data, user_data):
        """初始化模拟"""
        self.controller = SimulationController()
        self.running = False
        self.selected_cell = None
        
        # 更新信息显示
        dpg.set_value("sim_status_text", "模拟状态: 已初始化")
        self.update_environment_info()
        self.refresh_view()
    
    def start_simulation(self, sender, app_data, user_data):
        """开始模拟"""
        if self.controller is None:
            dpg.set_value("sim_status_text", "模拟状态: 请先初始化模拟")
            return
        
        if not self.running:
            self.running = True
            dpg.set_value("sim_status_text", "模拟状态: 运行中")
            
            # 在新线程中运行模拟
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()
            
            # 启动自动刷新
            self.start_auto_refresh()
    
    def run_simulation(self):
        """运行模拟循环"""
        while self.running and self.controller:
            try:
                speed = dpg.get_value("speed_slider")
                # 这里假设controller有step或update方法
                if hasattr(self.controller, 'step'):
                    for _ in range(speed):
                        self.controller.step()
                elif hasattr(self.controller, 'update'):
                    self.controller.update()
                
                time.sleep(0.01)
            except Exception as e:
                print(f"模拟运行错误: {e}")
                break
    
    def pause_simulation(self, sender, app_data, user_data):
        """暂停模拟"""
        self.running = False
        dpg.set_value("sim_status_text", "模拟状态: 已暂停")
    
    def reset_simulation(self, sender, app_data, user_data):
        """重置模拟"""
        self.running = False
        self.controller = None
        self.selected_cell = None
        self.env_cache.clear()
        dpg.set_value("sim_status_text", "模拟状态: 已重置")
        self.refresh_view()
    
    def add_cell(self, sender, app_data, user_data):
        """添加细胞"""
        if self.controller is None:
            return
        
        x = dpg.get_value("new_cell_x")
        y = dpg.get_value("new_cell_y")
        dna_str = dpg.get_value("new_cell_dna")
        
        try:
            if dna_str:
                dna = cells.DNA(dna_str)
            else:
                dna_str = random_DNA.generate_dna(300)
                dna = cells.DNA(dna_str)
            
            new_cell = cells.Cell(env1=self.controller.env, x=x, y=y, dna=dna)
            self.controller.env.write((x, y), new_cell)
            self.refresh_view()
            
        except Exception as e:
            print(f"添加细胞失败: {e}")
    
    def add_random_cell(self, sender, app_data, user_data):
        """添加随机DNA的细胞"""
        if self.controller is None:
            return
        
        x = dpg.get_value("new_cell_x")
        y = dpg.get_value("new_cell_y")
        
        try:
            dna_str = random_DNA.generate_dna(300)
            dna = cells.DNA(dna_str)
            new_cell = cells.Cell(env1=self.controller.env, x=x, y=y, dna=dna)
            self.controller.env.write((x, y), new_cell)
            self.refresh_view()
            
        except Exception as e:
            print(f"添加随机细胞失败: {e}")
    
    def batch_add_cells(self, sender, app_data, user_data):
        """批量添加细胞"""
        if self.controller is None:
            return
            
        count = dpg.get_value("batch_cell_count")
        env_width = dpg.get_value("env_width")
        env_height = dpg.get_value("env_height")
        
        try:
            for _ in range(count):
                x = random.randint(0, env_width)
                y = random.randint(0, env_height)
                dna_str = random_DNA.generate_dna(300)
                dna = cells.DNA(dna_str)
                new_cell = cells.Cell(env1=self.controller.env, x=x, y=y, dna=dna)
                self.controller.env.write((x, y), new_cell)
            
            self.refresh_view()
            
        except Exception as e:
            print(f"批量添加细胞失败: {e}")
    
    def add_energy(self, sender, app_data, user_data):
        """添加能量"""
        if self.controller is None:
            return
        
        x = dpg.get_value("resource_x")
        y = dpg.get_value("resource_y")
        
        try:
            energy = self.controller.env.Energy(100)
            self.controller.env.write((x, y), energy)
            self.refresh_view()
        except Exception as e:
            print(f"添加能量失败: {e}")
    
    def add_oxygen(self, sender, app_data, user_data):
        """添加氧气"""
        if self.controller is None:
            return
        
        x = dpg.get_value("resource_x")
        y = dpg.get_value("resource_y")
        
        try:
            oxygen = self.controller.env.O2(200)
            self.controller.env.write((x, y), oxygen)
            self.refresh_view()
        except Exception as e:
            print(f"添加氧气失败: {e}")
    
    def add_water(self, sender, app_data, user_data):
        """添加水"""
        if self.controller is None:
            return
        
        x = dpg.get_value("resource_x")
        y = dpg.get_value("resource_y")
        
        try:
            water = self.controller.env.H2O(200)
            self.controller.env.write((x, y), water)
            self.refresh_view()
        except Exception as e:
            print(f"添加水失败: {e}")
    
    def add_sugar(self, sender, app_data, user_data):
        """添加糖分"""
        if self.controller is None:
            return
        
        x = dpg.get_value("resource_x")
        y = dpg.get_value("resource_y")
        
        try:
            sugar = cells.Sugar(6, 12, 6)
            self.controller.env.write((x, y), sugar)
            self.refresh_view()
        except Exception as e:
            print(f"添加糖分失败: {e}")
    
    def update_environment(self, sender, app_data, user_data):
        """更新环境设置"""
        # 这里需要根据实际的Environment API来实现
        pass
    
    def refresh_view(self, sender=None, app_data=None, user_data=None):
        """刷新画布显示"""
        if self.controller is None:
            return
        
        try:
            env = self.controller.env
            type_table = env.type_register_table
            
            # 收集各类型的位置数据
            energy_positions = []
            cell_positions = []
            oxygen_positions = []
            water_positions = []
            sugar_positions = []
            
            for obj_type, positions in type_table.items():
                for pos in positions:
                    x, y = pos
                    
                    # 根据类型分类
                    type_name = obj_type.__name__
                    if "Energy" in type_name:
                        energy_positions.append([float(x), float(y)])
                    elif "Cell" in type_name:
                        cell_positions.append([float(x), float(y)])
                    elif "O2" in type_name:
                        oxygen_positions.append([float(x), float(y)])
                    elif "H2O" in type_name:
                        water_positions.append([float(x), float(y)])
                    elif "Sugar" in type_name:
                        sugar_positions.append([float(x), float(y)])
            
            # 更新散点图
            if energy_positions:
                x_data, y_data = zip(*energy_positions)
                dpg.set_value("energy_scatter", [list(x_data), list(y_data)])
            else:
                dpg.set_value("energy_scatter", [[], []])
                
            if cell_positions:
                x_data, y_data = zip(*cell_positions)
                dpg.set_value("cells_scatter", [list(x_data), list(y_data)])
            else:
                dpg.set_value("cells_scatter", [[], []])
                
            if oxygen_positions:
                x_data, y_data = zip(*oxygen_positions)
                dpg.set_value("oxygen_scatter", [list(x_data), list(y_data)])
            else:
                dpg.set_value("oxygen_scatter", [[], []])
                
            if water_positions:
                x_data, y_data = zip(*water_positions)
                dpg.set_value("water_scatter", [list(x_data), list(y_data)])
            else:
                dpg.set_value("water_scatter", [[], []])
                
            if sugar_positions:
                x_data, y_data = zip(*sugar_positions)
                dpg.set_value("sugar_scatter", [list(x_data), list(y_data)])
            else:
                dpg.set_value("sugar_scatter", [[], []])
            
            # 更新环境信息
            self.update_environment_info()
            
        except Exception as e:
            print(f"刷新视图失败: {e}")
    
    def update_environment_info(self):
        """更新环境信息显示"""
        if self.controller is None:
            return
        
        try:
            env = self.controller.env
            width = dpg.get_value("env_width")
            height = dpg.get_value("env_height")
            
            dpg.set_value("env_size_text", f"环境尺寸: {width} x {height}")
            
            # 统计细胞数量
            cell_count = 0
            for obj_type, positions in env.type_register_table.items():
                if "Cell" in obj_type.__name__:
                    cell_count = len(positions)
                    break
            
            dpg.set_value("total_cells_text", f"细胞总数: {cell_count}")
            
        except Exception as e:
            print(f"更新环境信息失败: {e}")
    
    def toggle_auto_refresh(self, sender, app_data, user_data):
        """切换自动刷新"""
        pass
    
    def start_auto_refresh(self):
        """开始自动刷新"""
        def auto_refresh():
            while self.running:
                interval = dpg.get_value("refresh_interval") / 1000.0
                time.sleep(interval)
                if self.running:
                    self.refresh_view()
        
        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()
    
    def select_cell(self, sender, app_data, user_data):
        """选择细胞"""
        # 处理细胞选择的逻辑
        pass
    
    def delete_selected_cell(self, sender, app_data, user_data):
        """删除选中的细胞"""
        if self.selected_cell and self.controller:
            try:
                x, y = self.selected_cell.x, self.selected_cell.y
                self.controller.env.remove_object((x, y), self.selected_cell)
                self.selected_cell = None
                self.refresh_view()
            except Exception as e:
                print(f"删除细胞失败: {e}")
    
    def update_cell_info(self, cell):
        """更新细胞信息显示"""
        if cell:
            dpg.set_value("cell_name_text", f"名称: {cell.name if cell.name else '未命名'}")
            dpg.set_value("cell_position_text", f"位置: ({cell.x}, {cell.y})")
            dpg.set_value("cell_color_text", f"颜色: {cell.color}")
            
            if hasattr(cell, 'dna'):
                dpg.set_value("dna_sequence_text", str(cell.dna))
            if hasattr(cell, 'rna'):
                dpg.set_value("rna_sequence_text", str(cell.rna))
    
    def show_about(self, sender, app_data, user_data):
        """显示关于对话框"""
        with dpg.window(label="关于 VitaeCanvas", modal=True, width=400, height=300):
            dpg.add_text("VitaeCanvas - 生命绘卷")
            dpg.add_text("版本: 0.1.0")
            dpg.add_text("一个细胞级生命演化模拟框架")
            dpg.add_separator()
            dpg.add_text("开发团队:")
            dpg.add_text("SteveZhang08, HLF1633, TSAVPYN")
            dpg.add_button(label="关闭", callback=lambda: dpg.delete_item(dpg.last_container()))
    
    def new_simulation(self, sender, app_data, user_data):
        """新建模拟"""
        self.reset_simulation(None, None, None)
        self.initialize_simulation(None, None, None)
    
    def reset_view(self, sender, app_data, user_data):
        """重置视图"""
        dpg.set_axis_limits("x_axis", 0, dpg.get_value("env_width"))
        dpg.set_axis_limits("y_axis", 0, dpg.get_value("env_height"))
    
    def fit_to_window(self, sender, app_data, user_data):
        """适应窗口"""
        dpg.set_axis_limits_auto("x_axis")
        dpg.set_axis_limits_auto("y_axis")
    
    def run(self):
        """运行GUI"""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

# 主程序入口
if __name__ == "__main__":
    gui = VitaeCanvasGUI()
    gui.run()