import os
import sys
import threading
import time
import dearpygui.dearpygui as dpg

# 确保项目库能被导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sim import SimulationController
from vitae_system import cells, random_DNA, env as venv

# 创建仿真控制器
sim_controller = SimulationController()
env = sim_controller.env

# GUI参数
CANVAS_WIDTH_RATIO = 0.45  # 中间画布占窗口宽度比例
CELL_SIZE = 5  # 单个细胞绘制像素大小
selected_cell = None  # 当前选中细胞

# 中文字体支持
with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
        dpg.bind_font(font)

# ----------- 环境绘制函数 -----------
def draw_environment():
    dpg.delete_item("env_canvas", children_only=True)  # 清空画布
    width = env.width if env.width > 0 else 100
    height = env.height if env.height > 0 else 100
    
    # 绘制能量、O2、水、糖、细胞
    for coord, items in env.env.items():
        x, y = coord
        for item in items:
            color = (0, 0, 0)
            if isinstance(item, venv.Energy):
                color = (255, 255, 0)
            elif isinstance(item, venv.O2):
                color = (0, 0, 255)
            elif isinstance(item, venv.H2O):
                color = (0, 255, 255)
            elif isinstance(item, cells.Sugar):
                color = (255, 0, 255)
            elif isinstance(item, cells.Cell):
                color = item.color
            dpg.draw_rectangle(
                (x*CELL_SIZE, y*CELL_SIZE),
                ((x+1)*CELL_SIZE, (y+1)*CELL_SIZE),
                color=color,
                fill=color,
                parent="env_canvas"
            )

# ----------- 细胞信息显示 -----------
def show_cell_info(cell):
    global selected_cell
    selected_cell = cell
    dpg.set_value("cell_name", f"名字: {cell.name}")
    dpg.set_value("cell_pos", f"位置: ({cell.x}, {cell.y})")
    dpg.set_value("cell_dna", f"DNA: {str(cell.dna)}")
    dpg.set_value("cell_rna", f"RNA: {str(cell.rna)}")

# ----------- 控制按钮回调 -----------
def add_random_cell():
    dna_str = random_DNA.generate_dna(length=300)
    x, y = 0, 0
    new_cell = cells.Cell(env, x, y, dna=cells.DNA(dna_str), name=f"Cell{len(env.env)}")
    env.write((x, y), new_cell)
    draw_environment()

def add_energy():
    env.write((0,0), venv.Energy(100))
    draw_environment()

def step_simulation():
    sim_controller.run()
    draw_environment()

# ----------- GUI布局 -----------
with dpg.window(label="VitaeCanvas GUI", width=1200, height=600):
    with dpg.group(horizontal=True):
        # 左侧控制面板
        with dpg.child_window(width=200, height=-1):
            dpg.add_text("控制面板")
            dpg.add_button(label="添加随机细胞", callback=add_random_cell)
            dpg.add_button(label="添加能量", callback=add_energy)
            dpg.add_button(label="推进一步仿真", callback=step_simulation)
        
        # 中间环境画布
        with dpg.child_window(width=int(1200*CANVAS_WIDTH_RATIO), height=-1):
            dpg.add_drawlist(width=-1, height=-1, tag="env_canvas")
        
        # 右侧信息面板
        with dpg.child_window(width=200, height=-1):
            dpg.add_text("信息面板")
            dpg.add_text("", tag="cell_name")
            dpg.add_text("", tag="cell_pos")
            dpg.add_text("", tag="cell_dna")
            dpg.add_text("", tag="cell_rna")

# ----------- 鼠标点击选中细胞 -----------
def canvas_click(sender, app_data):
    x, y = int(app_data[0] // CELL_SIZE), int(app_data[1] // CELL_SIZE)
    items = env.read((x, y))
    for item in items:
        if isinstance(item, cells.Cell):
            show_cell_info(item)
            break

dpg.set_item_callback("env_canvas", canvas_click)

# ----------- 启动GUI -----------
draw_environment()
dpg.start_dearpygui()