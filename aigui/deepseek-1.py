import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dearpygui.dearpygui as dpg
import threading
import time
import math
from sim import SimulationController
from vitae_system import cells, random_DNA
from vitae_system.env import Energy, O2, H2O

# ---------------------------- 全局变量 ----------------------------
sim = SimulationController()
env = sim.env
selected_cell = None          # 当前选中的细胞对象
running = False               # 模拟运行标志
timer_id = None               # 定时器ID

# 视图控制参数（支持平移和缩放）
view_offset_x = 0.0
view_offset_y = 0.0
view_zoom = 1.0               # 缩放因子，越大显示越详细
is_dragging = False
drag_start = (0, 0)

# 环境边界类型（有限/无限）
finite_width = env.width
finite_height = env.height
is_infinite = (finite_width < 0 or finite_height < 0)

# 如果是无限大，默认视图范围设为 [-100, 100] 的区间（基于偏移和缩放调整）
def get_world_bounds():
    """获取当前视图的世界坐标边界 (left, right, top, bottom)"""
    vp_width = dpg.get_item_width("drawing_canvas") if dpg.does_item_exist("drawing_canvas") else 800
    vp_height = dpg.get_item_height("drawing_canvas") if dpg.does_item_exist("drawing_canvas") else 600
    # 屏幕中心对应的世界坐标
    center_x = view_offset_x
    center_y = view_offset_y
    # 屏幕尺寸对应的世界宽度/高度
    world_width = vp_width / view_zoom
    world_height = vp_height / view_zoom
    left = center_x - world_width / 2
    right = center_x + world_width / 2
    top = center_y - world_height / 2   # Y轴向上
    bottom = center_y + world_height / 2
    return left, right, top, bottom

# ---------------------------- 绘图函数 ----------------------------
def redraw_environment():
    """清除并重绘画布上的所有元素"""
    if not dpg.does_item_exist("drawing_canvas"):
        return
    dpg.delete_item("drawing_canvas", children_only=True)
    
    left, right, top, bottom = get_world_bounds()
    vp_width = dpg.get_item_width("drawing_canvas")
    vp_height = dpg.get_item_height("drawing_canvas")
    
    # 世界 -> 屏幕坐标转换函数
    def world_to_screen(x, y):
        sx = (x - left) / (right - left) * vp_width
        sy = (y - top) / (bottom - top) * vp_height
        return sx, sy
    
    # 绘制网格（世界坐标中步长自适应）
    # 计算合适的网格间距：使得屏幕上的网格间距大约在 30~80 像素之间
    grid_step_world = 10 * (50 / view_zoom)    # 粗略步长
    # 取整到合适数量级
    if grid_step_world < 1:
        grid_step_world = 1
    # 根据世界边界计算起始/结束网格线
    start_x = math.floor(left / grid_step_world) * grid_step_world
    end_x = math.ceil(right / grid_step_world) * grid_step_world
    start_y = math.floor(top / grid_step_world) * grid_step_world
    end_y = math.ceil(bottom / grid_step_world) * grid_step_world
    
    # 绘制纵向网格线
    x = start_x
    while x <= end_x:
        sx, sy1 = world_to_screen(x, top)
        sx, sy2 = world_to_screen(x, bottom)
        dpg.draw_line((sx, sy1), (sx, sy2), color=(100, 100, 100, 100), thickness=1, parent="drawing_canvas")
        x += grid_step_world
    # 绘制横向网格线
    y = start_y
    while y <= end_y:
        sx1, sy = world_to_screen(left, y)
        sx2, sy = world_to_screen(right, y)
        dpg.draw_line((sx1, sy), (sx2, sy), color=(100, 100, 100, 100), thickness=1, parent="drawing_canvas")
        y += grid_step_world
    
    # 遍历环境中的所有物质并绘制
    for (cx, cy), substances in env.env.items():
        # 只绘制在视图范围内的坐标
        if cx < left or cx > right or cy < top or cy > bottom:
            continue
        sx, sy = world_to_screen(cx, cy)
        # 绘制每个物质
        for substance in substances:
            if isinstance(substance, cells.Cell):
                # 细胞：矩形或圆形，使用细胞的颜色
                color = substance.color if hasattr(substance, 'color') else (200, 200, 200)
                radius = max(4, 15 / view_zoom)   # 半径随缩放变化，保证可见
                dpg.draw_circle((sx, sy), radius, color=color, fill=color, parent="drawing_canvas")
                # 绘制细胞名字缩写
                name_text = substance.name[:2] if substance.name else "C"
                dpg.draw_text((sx-4, sy-4), name_text, color=(0,0,0), size=12, parent="drawing_canvas")
            elif isinstance(substance, Energy):
                dpg.draw_circle((sx, sy), 5, color=(0,255,0), fill=(0,255,0,200), parent="drawing_canvas")
            elif isinstance(substance, O2):
                dpg.draw_circle((sx, sy), 4, color=(100,200,255), fill=(100,200,255,200), parent="drawing_canvas")
            elif isinstance(substance, H2O):
                dpg.draw_circle((sx, sy), 4, color=(0,0,255), fill=(0,0,255,200), parent="drawing_canvas")
            else:
                # 其他物质（如糖）用棕色表示
                dpg.draw_circle((sx, sy), 4, color=(139,69,19), fill=(139,69,19,200), parent="drawing_canvas")
    
    # 如果是有限大环境，绘制边缘红线
    if not is_infinite:
        sx1, sy1 = world_to_screen(0, 0)
        sx2, sy2 = world_to_screen(finite_width, finite_height)
        dpg.draw_rectangle((sx1, sy1), (sx2, sy2), color=(255,0,0,255), thickness=2, parent="drawing_canvas")

# ---------------------------- 细胞选中与信息更新 ----------------------------
def update_info_panel():
    """根据 selected_cell 刷新右侧信息面板"""
    if not dpg.does_item_exist("info_text"):
        return
    if selected_cell is None:
        dpg.set_value("info_text", "未选中任何细胞\n点击画布上的细胞以查看详细信息")
        return
    # 获取细胞的各种属性（如果不存在则显示未知）
    info = f"名称: {selected_cell.name if hasattr(selected_cell, 'name') else '未知'}\n"
    info += f"坐标: ({selected_cell.x}, {selected_cell.y})\n"
    info += f"颜色: {selected_cell.color if hasattr(selected_cell, 'color') else '默认'}\n"
    if hasattr(selected_cell, 'dna'):
        dna_str = str(selected_cell.dna)[:50] + ('...' if len(str(selected_cell.dna)) > 50 else '')
        info += f"DNA: {dna_str}\n"
    if hasattr(selected_cell, 'rna'):
        rna_str = str(selected_cell.rna)[:50] + ('...' if len(str(selected_cell.rna)) > 50 else '')
        info += f"RNA: {rna_str}\n"
    # 尝试获取能量
    if hasattr(selected_cell, 'energy'):
        info += f"能量: {selected_cell.energy:.2f}\n"
    elif hasattr(selected_cell, 'get_energy'):
        info += f"能量: {selected_cell.get_energy():.2f}\n"
    # 年龄（如果存在）
    if hasattr(selected_cell, 'age'):
        info += f"年龄: {selected_cell.age}\n"
    dpg.set_value("info_text", info)

def find_cell_at_world(x_world, y_world):
    """在世界坐标中查找最近的细胞，返回细胞对象或None"""
    # 阈值：世界坐标下 10 单位（可根据缩放调整）
    threshold = 10.0 / view_zoom
    closest_cell = None
    min_dist = threshold
    for (cx, cy), substances in env.env.items():
        for sub in substances:
            if isinstance(sub, cells.Cell):
                dx = cx - x_world
                dy = cy - y_world
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    min_dist = dist
                    closest_cell = sub
    return closest_cell

def mouse_click_callback(sender, app_data):
    """鼠标点击画布，选中细胞"""
    if not dpg.does_item_exist("drawing_canvas"):
        return
    # 获取鼠标在画布中的像素坐标
    mouse_x, mouse_y = dpg.get_mouse_pos(local=False)
    canvas_rect = dpg.get_item_rect_size("drawing_canvas")
    canvas_pos = dpg.get_item_rect_min("drawing_canvas")
    # 计算相对画布的位置
    rel_x = mouse_x - canvas_pos[0]
    rel_y = mouse_y - canvas_pos[1]
    if rel_x < 0 or rel_y < 0 or rel_x > canvas_rect[0] or rel_y > canvas_rect[1]:
        return
    # 转换到世界坐标
    left, right, top, bottom = get_world_bounds()
    world_x = left + (rel_x / canvas_rect[0]) * (right - left)
    world_y = top + (rel_y / canvas_rect[1]) * (bottom - top)
    cell = find_cell_at_world(world_x, world_y)
    global selected_cell
    selected_cell = cell
    update_info_panel()

# ---------------------------- 模拟循环与定时器 ----------------------------
def simulation_step():
    """执行一步模拟并刷新界面"""
    global running
    if running:
        sim.run()          # 推进模拟一步
        redraw_environment()
        # 如果当前选中的细胞仍然存在（对象有效），保留选中；否则置空
        if selected_cell is not None:
            # 简单检查：尝试访问细胞坐标，若异常则无效
            try:
                _ = selected_cell.x
            except:
                global selected_cell
                selected_cell = None
                update_info_panel()
    # 无论是否运行，都安排下一次调用（定时器方式）
    if running and dpg.does_item_exist("drawing_canvas"):
        dpg.set_value("sim_timer", time.time() + 0.05)   # 大约20fps

def start_simulation():
    global running, timer_id
    if not running:
        running = True
        dpg.set_value("sim_timer", time.time() + 0.05)   # 启动定时器
        dpg.configure_item("btn_start", enabled=False)
        dpg.configure_item("btn_stop", enabled=True)

def stop_simulation():
    global running
    running = False
    dpg.configure_item("btn_start", enabled=True)
    dpg.configure_item("btn_stop", enabled=False)

def step_simulation():
    """单步执行"""
    sim.run()
    redraw_environment()

# ---------------------------- 界面操作 ----------------------------
def add_random_cell():
    """在随机位置添加一个具有随机DNA的细胞"""
    # 确定有效坐标范围
    if is_infinite:
        # 在视图中心附近随机生成
        left, right, top, bottom = get_world_bounds()
        x = left + (right-left)*0.5 + (random_DNA.generate_dna_int(0, 10) - 5)
        y = top + (bottom-top)*0.5 + (random_DNA.generate_dna_int(0, 10) - 5)
    else:
        x = random_DNA.generate_dna_int(0, finite_width)
        y = random_DNA.generate_dna_int(0, finite_height)
    # 生成随机DNA
    dna_str = random_DNA.generate_dna(length=50)   # 较短的DNA用于测试
    dna_obj = cells.DNA(dna_str)
    # 创建细胞并添加到环境
    new_cell = cells.Cell(env, int(x), int(y), dna=dna_obj, name="RandomCell")
    env.write((int(x), int(y)), new_cell)
    redraw_environment()

def add_energy_at(world_x, world_y):
    """在世界坐标指定位置添加能量"""
    # 注意：坐标必须是整数，因为环境字典键是整数元组
    # 将世界坐标四舍五入到最近的整数
    int_x = int(round(world_x))
    int_y = int(round(world_y))
    # 检查是否为无限大或边界内
    if not is_infinite and (int_x < 0 or int_x > finite_width or int_y < 0 or int_y > finite_height):
        return
    env.write((int_x, int_y), Energy(100))
    redraw_environment()

def add_energy_from_ui():
    """从左侧面板输入框获取坐标添加能量"""
    try:
        x = int(dpg.get_value("energy_x_input"))
        y = int(dpg.get_value("energy_y_input"))
        env.write((x, y), Energy(100))
        redraw_environment()
    except:
        pass

def add_cell_from_ui():
    """从左侧面板输入创建细胞"""
    try:
        x = int(dpg.get_value("cell_x_input"))
        y = int(dpg.get_value("cell_y_input"))
        dna_text = dpg.get_value("cell_dna_input")
        if dna_text.strip():
            dna_obj = cells.DNA(dna_text)
        else:
            dna_obj = cells.DNA(random_DNA.generate_dna(50))
        name = dpg.get_value("cell_name_input") or "UserCell"
        new_cell = cells.Cell(env, x, y, dna=dna_obj, name=name)
        env.write((x, y), new_cell)
        redraw_environment()
    except:
        pass

# ---------------------------- 视图控制回调 ----------------------------
def canvas_mouse_drag(sender, app_data):
    """鼠标拖拽平移视图"""
    global view_offset_x, view_offset_y, is_dragging, drag_start
    if not is_dragging:
        is_dragging = True
        drag_start = dpg.get_mouse_pos(local=True)
        return
    current = dpg.get_mouse_pos(local=True)
    dx_pixel = current[0] - drag_start[0]
    dy_pixel = current[1] - drag_start[1]
    # 像素偏移转世界偏移
    vp_width = dpg.get_item_width("drawing_canvas")
    vp_height = dpg.get_item_height("drawing_canvas")
    left, right, top, bottom = get_world_bounds()
    world_dx = dx_pixel / vp_width * (right - left)
    world_dy = dy_pixel / vp_height * (bottom - top)
    view_offset_x -= world_dx
    view_offset_y -= world_dy
    drag_start = current
    redraw_environment()

def canvas_mouse_release(sender, app_data):
    global is_dragging
    is_dragging = False

def canvas_mouse_wheel(sender, app_data):
    """滚轮缩放"""
    global view_zoom
    delta = app_data
    zoom_factor = 1.1 if delta > 0 else 0.9
    new_zoom = view_zoom * zoom_factor
    # 限制缩放范围
    if 0.1 <= new_zoom <= 50:
        view_zoom = new_zoom
        redraw_environment()

def reset_view():
    """重置视图，适应环境边界或默认区域"""
    global view_offset_x, view_offset_y, view_zoom
    if is_infinite:
        view_offset_x = 0.0
        view_offset_y = 0.0
        view_zoom = 1.0
    else:
        view_offset_x = finite_width / 2.0
        view_offset_y = finite_height / 2.0
        view_zoom = 1.0
    redraw_environment()

# ---------------------------- DearPyGui 界面构建 ----------------------------
def main():
    dpg.create_context()
    dpg.create_viewport(title="VitaeCanvas - 生命绘卷", width=1200, height=800)
    dpg.setup_dearpygui()
    
    # 字体支持中文
    with dpg.font_registry():
        with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.bind_font(font)
    
    # 主布局：左中右
    with dpg.window(label="Main", tag="main_window"):
        with dpg.menu_bar():
            with dpg.menu(label="视图"):
                dpg.add_menu_item(label="重置视图", callback=reset_view)
        
        with dpg.group(horizontal=True):
            # 左侧控制面板
            with dpg.child_window(width=250, tag="left_panel"):
                dpg.add_text("控制面板")
                dpg.add_button(label="启动模拟", tag="btn_start", callback=start_simulation)
                dpg.add_button(label="停止模拟", tag="btn_stop", callback=stop_simulation, enabled=False)
                dpg.add_button(label="单步推进", callback=step_simulation)
                dpg.add_separator()
                dpg.add_text("添加随机细胞")
                dpg.add_button(label="添加随机细胞", callback=add_random_cell)
                dpg.add_separator()
                dpg.add_text("添加能量 (坐标)")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="X", width=80, tag="energy_x_input")
                    dpg.add_input_text(label="Y", width=80, tag="energy_y_input")
                dpg.add_button(label="添加能量", callback=add_energy_from_ui)
                dpg.add_separator()
                dpg.add_text("手动创建细胞")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="X", width=60, tag="cell_x_input")
                    dpg.add_input_text(label="Y", width=60, tag="cell_y_input")
                dpg.add_input_text(label="名称", tag="cell_name_input", default_value="Cell")
                dpg.add_input_text(label="DNA序列 (可选)", tag="cell_dna_input", width=200)
                dpg.add_button(label="创建细胞", callback=add_cell_from_ui)
                dpg.add_separator()
                dpg.add_text("环境信息")
                if is_infinite:
                    dpg.add_text("环境类型: 无限大（无边）")
                else:
                    dpg.add_text(f"环境尺寸: {finite_width} x {finite_height}")
            
            # 中间画布
            with dpg.child_window(width=-300, tag="center_panel"):
                dpg.add_drawing(width=-1, height=-1, tag="drawing_canvas")
                # 绑定鼠标事件
                dpg.set_item_callback("drawing_canvas", "on_click", mouse_click_callback)
                dpg.set_item_callback("drawing_canvas", "on_drag", canvas_mouse_drag)
                dpg.set_item_callback("drawing_canvas", "on_release", canvas_mouse_release)
                dpg.set_item_callback("drawing_canvas", "on_mouse_wheel", canvas_mouse_wheel)
            
            # 右侧信息面板
            with dpg.child_window(width=280, tag="right_panel"):
                dpg.add_text("细胞详细信息", tag="info_title")
                dpg.add_text("未选中任何细胞", tag="info_text", wrap=250)
    
    # 初始化视图
    reset_view()
    # 启动定时器（用于模拟更新，这里使用一个隐藏的文本控件存储下次更新时间）
    dpg.add_text("", tag="sim_timer", show=False)
    dpg.set_value("sim_timer", time.time())
    
    # 注册定时器回调（每一帧检查）
    def timer_check():
        now = time.time()
        next_time = dpg.get_value("sim_timer")
        if now >= next_time:
            simulation_step()
        dpg.set_value("sim_timer", next_time)  # 保持值不变，等下次回调
	
    # 在主循环中不断检查（也可以用dpg.set_frame_callback，但简单用循环）
    def render_loop():
        while dpg.is_dearpygui_running():
            # 处理模拟定时器
            if running and dpg.get_value("sim_timer") <= time.time():
                simulation_step()
            dpg.render_dearpygui_frame()
    
    dpg.show_viewport()
    # 显示窗口并进入循环（使用自定义循环以支持定时检查）
    # 注意：dearpygui 2.2 可以直接用 start_dearpygui，它会阻塞，我们使用自定义 loop
    # 但因为需要定时器，使用 start_dearpygui 并配合 dpg.set_frame_callback 更好
    # 简单起见我们使用框架自带帧回调
    def frame_callback():
        if running and dpg.get_value("sim_timer") <= time.time():
            simulation_step()
        dpg.set_frame_callback(1, frame_callback)
    
    dpg.set_frame_callback(1, frame_callback)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()