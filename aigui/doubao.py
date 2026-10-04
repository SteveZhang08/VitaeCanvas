import os
import sys
import threading
import time
# 确保项目模块可被导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目核心模块
import sim
from vitae_system import *
import dearpygui.dearpygui as dpg

# ==============================================
# 全局配置与核心对象
# ==============================================
# 初始化模拟器控制器
sim_controller = sim.SimulationController()
env = sim_controller.env  # 环境对象

# 界面状态变量
selected_cell = None  # 当前选中的细胞
sim_running = False   # 模拟运行状态
sim_thread = None     # 模拟线程

# ==============================================
# DPG 初始化 + 中文显示设置
# ==============================================
dpg.create_context()
dpg.create_viewport(title="VitaeCanvas - 生命绘卷", width=1200, height=800)

# 中文字体配置（按要求固定路径）
with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
        dpg.bind_font(font)

# ==============================================
# 工具函数
# ==============================================
def get_all_cells():
    """获取环境中所有细胞对象"""
    cell_positions = env.type_register_table.get(cells.Cell, [])
    cell_list = []
    for pos in cell_positions:
        contents = env.read(pos)
        for obj in contents:
            if isinstance(obj, cells.Cell):
                cell_list.append(obj)
    return cell_list

def update_cell_info_panel():
    """更新右侧细胞信息面板"""
    dpg.delete_item("cell_info_group", children_only=True)
    if not selected_cell:
        dpg.add_text("No cell selected", parent="cell_info_group")
        return

    # 显示细胞详细信息
    dpg.add_text(f"Name: {selected_cell.name}", parent="cell_info_group")
    dpg.add_text(f"Position: ({selected_cell.x}, {selected_cell.y})", parent="cell_info_group")
    dpg.add_text(f"Color: {selected_cell.color}", parent="cell_info_group")
    dpg.add_text(f"DNA Length: {len(str(selected_cell.dna))}", parent="cell_info_group")
    dpg.add_text("DNA Sequence:", parent="cell_info_group")
    dpg.add_input_text(default_value=str(selected_cell.dna), parent="cell_info_group", 
                      multiline=True, height=100, readonly=True)
    dpg.add_text(f"RNA: {str(selected_cell.rna)}", parent="cell_info_group")

def refresh_canvas():
    """刷新中间环境画布"""
    dpg.configure_item("canvas", clear=True)
    
    env_w = env.width
    env_h = env.height
    canvas_w = dpg.get_item_width("canvas")
    canvas_h = dpg.get_item_height("canvas")

    # 计算缩放比例
    scale_x = canvas_w / env_w if env_w > 0 else 20
    scale_y = canvas_h / env_h if env_h > 0 else 20

    # 绘制能量/资源
    if env.Energy in env.type_register_table:
        for (x, y) in env.type_register_table[env.Energy]:
            draw_x = x * scale_x
            draw_y = y * scale_y
            dpg.draw_circle((draw_x, draw_y), 3, fill=(255, 255, 0), parent="canvas")

    # 绘制细胞
    cells_list = get_all_cells()
    for cell in cells_list:
        x, y = cell.x, cell.y
        draw_x = x * scale_x
        draw_y = y * scale_y
        r, g, b = cell.color
        # 绘制细胞本体
        dpg.draw_circle((draw_x, draw_y), 6, fill=(r, g, b), parent="canvas")
        # 绘制细胞名称
        dpg.draw_text((draw_x + 8, draw_y - 8), cell.name, size=12, parent="canvas")

def simulation_loop():
    """模拟主循环（独立线程）"""
    while sim_running:
        sim_controller.run()  # 模拟前进一步
        refresh_canvas()
        time.sleep(0.1)

# ==============================================
# 按钮回调函数
# ==============================================
def start_sim_callback():
    """启动模拟"""
    global sim_running, sim_thread
    if not sim_running:
        sim_running = True
        sim_thread = threading.Thread(target=simulation_loop, daemon=True)
        sim_thread.start()
        dpg.set_value("sim_status", "Simulation Status: Running")

def stop_sim_callback():
    """停止模拟"""
    global sim_running
    sim_running = False
    dpg.set_value("sim_status", "Simulation Status: Stopped")

def step_sim_callback():
    """单步执行模拟"""
    sim_controller.run()
    refresh_canvas()

def create_cell_callback(sender, app_data):
    """创建新细胞"""
    try:
        x = int(dpg.get_value("cell_x"))
        y = int(dpg.get_value("cell_y"))
        dna_str = dpg.get_value("cell_dna")
        name = dpg.get_value("cell_name")

        # 处理DNA
        if dna_str.strip() == "":
            dna_obj = cells.DEFAULT_DNA
        else:
            dna_obj = cells.DNA(dna_str)
        
        # 创建并添加细胞
        new_cell = cells.Cell(env1=env, x=x, y=y, dna=dna_obj, name=name)
        refresh_canvas()
    except Exception as e:
        print(f"Create cell error: {e}")

def random_dna_callback():
	"""生成随机DNA"""
	import vitae_system
	rand_dna = vitae_system.random_DNA.generate_dna(300)
	dpg.set_value("cell_dna", rand_dna)

def select_cell_by_name(sender, app_data):
    """通过名称选择细胞"""
    global selected_cell
    cell_name = app_data
    for cell in get_all_cells():
        if cell.name == cell_name:
            selected_cell = cell
            update_cell_info_panel()
            break

# ==============================================
# 界面布局：左(控制) + 中(画布) + 右(信息)
# ==============================================
with dpg.window(tag="main_window", no_title_bar=True, no_resize=True, no_move=True):
    # 主水平布局
    with dpg.group(horizontal=True):
        # ==================== 左侧：控制面板 ====================
        with dpg.child_window(width=280, height=760, tag="left_panel"):
            dpg.add_text("=== Global Control ===", bullet=True)
            dpg.add_button(label="Start Simulation", callback=start_sim_callback, width=260)
            dpg.add_button(label="Stop Simulation", callback=stop_sim_callback, width=260)
            dpg.add_button(label="Step Forward", callback=step_sim_callback, width=260)
            dpg.add_text("", tag="sim_status", default_value="Simulation Status: Stopped")
            
            dpg.add_spacer(height=20)
            dpg.add_text("=== Create Cell ===", bullet=True)
            dpg.add_input_int(label="X", tag="cell_x", default_value=5)
            dpg.add_input_int(label="Y", tag="cell_y", default_value=5)
            dpg.add_input_text(label="Name", tag="cell_name", default_value="NewCell")
            dpg.add_input_text(label="DNA", tag="cell_dna", multiline=True, height=80)
            dpg.add_button(label="Generate Random DNA", callback=random_dna_callback, width=260)
            dpg.add_button(label="Create Cell", callback=create_cell_callback, width=260)
            
            dpg.add_spacer(height=20)
            dpg.add_text("=== Cell List ===", bullet=True)
            dpg.add_listbox(items=[], tag="cell_list", width=260, num_items=8, callback=select_cell_by_name)

        # ==================== 中间：环境画布（45%宽度） ====================
        with dpg.child_window(width=540, height=760, tag="center_panel"):
            dpg.add_text("Environment Canvas", bullet=True)
            dpg.add_drawlist(width=520, height=700, tag="canvas")

        # ==================== 右侧：细胞信息面板 ====================
        with dpg.child_window(width=340, height=760, tag="right_panel"):
            dpg.add_text("=== Cell Information ===", bullet=True)
            with dpg.group(tag="cell_info_group"):
                dpg.add_text("No cell selected")

# ==============================================
# 启动界面
# ==============================================
dpg.setup_dearpygui()
dpg.show_viewport()
refresh_canvas()
dpg.start_dearpygui()
dpg.destroy_context()