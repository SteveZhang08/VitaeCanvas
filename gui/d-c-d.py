"""
VitaeCanvas GUI - Life Canvas Simulation Interface
使用 DearPyGui 2.2 构建的左中右布局交互界面
左: 全局控制面板 | 中: 环境画布 | 右: 细胞信息面板
"""

import dearpygui.dearpygui as dpg
import threading
import time
import random
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 导入项目组件
from main import SimulationController
from vitae_system.cells import Cell, DNA
from vitae_system import random_DNA

# 物质类型颜色映射（用于画布显示）
MATERIAL_COLORS = {
    "Energy": (255, 255, 0, 255),
    "O2": (100, 100, 255, 255),
    "H2O": (100, 200, 255, 255),
    "Sugar": (255, 255, 255, 255),
    "Cell": None  # 使用细胞自身颜色
}

class VitaeCanvasGUI:
    """VitaeCanvas 主 GUI 类"""

    def __init__(self):
        # --- 模拟控制器与线程 ---
        self.controller = None
        self.sim_thread = None
        self.running = False

        # --- 画布视口参数 ---
        self.view_center = [0.0, 0.0]   # 世界坐标中心
        self.zoom = 20.0                # 像素/单位
        self.canvas_size = [800, 600]   # 画布像素尺寸（动态更新）

        # --- 交互状态 ---
        self.panning = False
        self.drag_start = None          # 鼠标拖拽起始位置
        self.selected_cell = None       # 当前选中的细胞

        # 命中测试缓存：[(world_rect, tag, obj), ...]
        self.objects_bbox = []

        # --- 线程控制 ---
        self.stop_event = threading.Event()
        self.view_initialized = False

    # ================== 模拟控制 ==================
    def init_controller(self):
        """初始化 SimulationController"""
        self.controller = SimulationController()
        self.view_initialized = False

    def start_simulation(self):
        """在新的守护线程中启动模拟"""
        if self.sim_thread and self.sim_thread.is_alive():
            print("模拟已在运行")
            return
        if not self.controller:
            self.init_controller()
        self.stop_event.clear()
        self.sim_thread = threading.Thread(target=self._sim_loop, daemon=True)
        self.sim_thread.start()
        self.running = True
        print("模拟已启动")

    def _sim_loop(self):
        """模拟循环（运行在独立线程）"""
        try:
            # 假设 SimulationController 有 run() 方法进行无限循环
            self.controller.run()
        except AttributeError:
            # 如果 controller 没有 run 方法，我们通过一个简单的循环单步推进
            # 此处假设 controller 有 step() 方法，若无则持续更新环境
            while not self.stop_event.is_set():
                if hasattr(self.controller, 'step'):
                    self.controller.step()
                time.sleep(0.05)
        except Exception as e:
            print(f"模拟线程错误: {e}")

    def stop_simulation(self):
        """停止模拟（尝试设置停止标志）"""
        self.stop_event.set()
        # 尝试调用 controller 的终止方法（如果存在）
        if self.controller:
            try:
                self.controller.stop()
            except AttributeError:
                pass
        self.running = False

    def toggle_pause(self):
        """暂停/恢复 UI 更新（画布刷新暂停，模拟后台继续）"""
        # 通过控制定时器实现
        if dpg.does_item_exist("update_timer"):
            dpg.toggle_item("update_timer")
        else:
            # 重新创建定时器
            self._create_timer()

    def reset_simulation(self):
        """重置模拟：停止当前，创建新实例，启动"""
        self.stop_simulation()
        # 等待线程结束（最多 1 秒）
        if self.sim_thread and self.sim_thread.is_alive():
            self.sim_thread.join(timeout=1)
        self.controller = None
        self.selected_cell = None
        self.view_initialized = False
        self.start_simulation()
        self.fit_view()

    # ================== 画布视口计算 ==================
    def get_canvas_center(self):
        """返回画布在屏幕上的中心坐标"""
        if dpg.does_item_exist("canvas_panel"):
            min_rect = dpg.get_item_rect_min("canvas_panel")
            size = dpg.get_item_rect_size("canvas_panel")
            return min_rect[0] + size[0]/2, min_rect[1] + size[1]/2
        return 0, 0

    def world_to_screen(self, wx, wy):
        """世界坐标 -> 画布屏幕坐标（y 轴向上）"""
        cx, cy = self.get_canvas_center()
        sx = cx + (wx - self.view_center[0]) * self.zoom
        sy = cy - (wy - self.view_center[1]) * self.zoom   # y 轴反向映射
        return sx, sy

    def screen_to_world(self, sx, sy):
        """屏幕坐标 -> 世界坐标"""
        cx, cy = self.get_canvas_center()
        wx = self.view_center[0] + (sx - cx) / self.zoom
        wy = self.view_center[1] - (sy - cy) / self.zoom   # y 轴反向
        return wx, wy

    def get_view_bounds(self):
        """获取当前视口的世界坐标边界 (left, right, bottom, top)"""
        half_w = self.canvas_size[0] / (2 * self.zoom) if self.zoom > 0 else 100
        half_h = self.canvas_size[1] / (2 * self.zoom) if self.zoom > 0 else 100
        left = self.view_center[0] - half_w
        right = self.view_center[0] + half_w
        bottom = self.view_center[1] - half_h
        top = self.view_center[1] + half_h
        return left, right, bottom, top

    def fit_view(self):
        """调整视口以显示所有物体（或环境边界）"""
        if not self.controller:
            return
        env = self.controller.env
        # 收集所有非空坐标
        all_coords = list(env.env.keys())
        if env.width > 0 and env.height > 0:
            # 有限环境：考虑整个范围
            all_coords.extend([(0,0), (env.width, env.height)])
        if not all_coords:
            # 没有任何物体，保持默认
            self.view_center = [0, 0]
            self.zoom = 20.0
            return
        min_x = min(c[0] for c in all_coords)
        max_x = max(c[0] for c in all_coords)
        min_y = min(c[1] for c in all_coords)
        max_y = max(c[1] for c in all_coords)
        # 加边距
        margin = 2
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin

        # 计算适应画布的比例
        world_width = max_x - min_x
        world_height = max_y - min_y
        canvas_size = dpg.get_item_rect_size("canvas_panel")
        if canvas_size[0] <= 0 or canvas_size[1] <= 0:
            canvas_size = [800, 600]
        self.canvas_size = canvas_size
        if world_width > 0 and world_height > 0:
            self.zoom = min(canvas_size[0] / world_width, canvas_size[1] / world_height)
        else:
            self.zoom = 20.0
        self.view_center = [(min_x + max_x) / 2, (min_y + max_y) / 2]

    # ================== 画布更新与绘制 ==================
    def update_canvas(self):
        """定时器回调：清除并重绘画布内容"""
        if not self.controller or not dpg.does_item_exist("canvas_node"):
            return

        env = self.controller.env
        # 更新画布尺寸
        canvas_size = dpg.get_item_rect_size("canvas_panel")
        if canvas_size[0] > 0 and canvas_size[1] > 0:
            self.canvas_size = canvas_size

        # 首次自动适应视图
        if not self.view_initialized:
            self.fit_view()
            self.view_initialized = True

        # 清除画布节点下所有绘制项
        dpg.delete_item("canvas_node", children_only=True)
        self.objects_bbox.clear()

        # 获取视口范围
        view_left, view_right, view_bottom, view_top = self.get_view_bounds()

        # ---------- 绘制网格 ----------
        # 确定网格步长（根据缩放避免太密）
        step = 1
        if self.zoom < 8:
            step = max(1, int(10 / self.zoom))
        # 竖线
        x_start = int(view_left) - 1
        x_end = int(view_right) + 1
        for x in range(x_start, x_end + 1, step):
            p1 = self.world_to_screen(x, view_bottom)
            p2 = self.world_to_screen(x, view_top)
            dpg.draw_line(p1, p2, color=(80, 80, 80, 80), thickness=1, parent="canvas_node")
        # 横线
        y_start = int(view_bottom) - 1
        y_end = int(view_top) + 1
        for y in range(y_start, y_end + 1, step):
            p1 = self.world_to_screen(view_left, y)
            p2 = self.world_to_screen(view_right, y)
            dpg.draw_line(p1, p2, color=(80, 80, 80, 80), thickness=1, parent="canvas_node")

        # 绘制环境边界（如果是有限环境）
        if env.width > 0 and env.height > 0:
            # 用矩形表示环境区域
            p0 = self.world_to_screen(0, 0)
            p1 = self.world_to_screen(env.width, env.height)
            dpg.draw_rectangle(p0, p1, color=(200, 200, 200, 255), thickness=2, parent="canvas_node")

        # ---------- 绘制物质与细胞 ----------
        # 为避免迭代时修改异常，复制字典快照
        env_snapshot = list(env.env.items())
        for coord, substances in env_snapshot:
            wx, wy = coord
            # 跳过不在视口内的坐标（粗略剔除）
            if wx < view_left or wx > view_right or wy < view_bottom or wy > view_top:
                continue

            for obj in substances:
                obj_type = type(obj).__name__
                center = self.world_to_screen(wx, wy)
                half_size = self.zoom * 0.4   # 单元格占据半径

                if obj_type == "Cell":
                    color = obj.color if hasattr(obj, 'color') and obj.color else (0, 255, 0, 255)
                    tag = f"cell_{id(obj)}"
                    left_top = (center[0] - half_size, center[1] - half_size)
                    right_bottom = (center[0] + half_size, center[1] + half_size)
                    dpg.draw_rectangle(left_top, right_bottom, color=color, fill=color,
                                       thickness=1, parent="canvas_node", tag=tag)
                    # 如果选中，绘制高亮边框
                    if self.selected_cell is obj:
                        dpg.draw_rectangle(left_top, right_bottom, color=(255, 255, 255, 255),
                                           fill=(0,0,0,0), thickness=3, parent="canvas_node")
                    # 记录边界用于点击检测
                    world_rect = (wx - half_size/self.zoom, wy - half_size/self.zoom,
                                  wx + half_size/self.zoom, wy + half_size/self.zoom)
                    self.objects_bbox.append((world_rect, tag, obj))
                else:
                    # 普通物质：小圆点
                    default_color = MATERIAL_COLORS.get(obj_type, (255, 255, 255, 255))
                    dpg.draw_circle(center, half_size * 0.6, color=default_color, fill=default_color,
                                    parent="canvas_node")

        # 更新右侧信息面板
        if self.selected_cell:
            self._update_info_panel()
        else:
            self._clear_info_panel()

    def _update_info_panel(self):
        """右侧信息面板更新"""
        cell = self.selected_cell
        # 检查细胞是否还存活（仍在环境中）
        env = self.controller.env
        alive = False
        try:
            if Cell in env.type_register_table:
                for coord in env.type_register_table[Cell]:
                    substances = env.read(coord)
                    for obj in substances:
                        if obj is cell:
                            alive = True
                            break
                    if alive:
                        break
        except:
            pass
        if not alive:
            self.selected_cell = None
            self._clear_info_panel()
            return

        dpg.set_value("info_name", f"名称: {cell.name}")
        dpg.set_value("info_pos", f"坐标: ({cell.x}, {cell.y})")
        dpg.set_value("info_dna", f"DNA: {str(cell.dna)}")
        dpg.set_value("info_rna", f"RNA: {str(cell.rna) if cell.rna else '无'}")
        dpg.set_value("info_color", f"颜色: {cell.color}")

    def _clear_info_panel(self):
        """清空信息面板"""
        dpg.set_value("info_name", "名称: ---")
        dpg.set_value("info_pos", "坐标: ---")
        dpg.set_value("info_dna", "DNA: ---")
        dpg.set_value("info_rna", "RNA: ---")
        dpg.set_value("info_color", "颜色: ---")

    # ================== 交互处理 ==================
    def on_mouse_down(self, sender, app_data):
        """鼠标按下：记录起始位置"""
        if app_data[0] == 0:  # 左键
            self.drag_start = dpg.get_mouse_pos(local=False)
            self.panning = False

    def on_mouse_move(self, sender, app_data):
        """鼠标移动：平移视口"""
        if not dpg.is_mouse_button_down(0) or self.drag_start is None:
            return
        if not dpg.is_item_hovered("canvas_panel"):
            return
        curr = dpg.get_mouse_pos(local=False)
        dx = curr[0] - self.drag_start[0]
        dy = curr[1] - self.drag_start[1]
        if abs(dx) > 3 or abs(dy) > 3:
            self.panning = True
        if self.panning:
            # 平移世界坐标
            self.view_center[0] -= dx / self.zoom
            self.view_center[1] += dy / self.zoom   # y 轴反转
            self.drag_start = curr

    def on_mouse_release(self, sender, app_data):
        """鼠标释放：判断是否为点击"""
        if app_data[0] != 0:
            return
        if not self.panning and self.drag_start is not None:
            # 短点击，进行命中测试
            mouse_pos = dpg.get_mouse_pos(local=False)
            self._handle_click(mouse_pos)
        self.drag_start = None
        self.panning = False

    def on_mouse_wheel(self, sender, app_data):
        """鼠标滚轮：缩放视口，以鼠标位置为中心"""
        if not dpg.is_item_hovered("canvas_panel"):
            return
        delta = app_data
        mouse_pos = dpg.get_mouse_pos(local=False)
        wx, wy = self.screen_to_world(*mouse_pos)
        # 缩放因子
        zoom_factor = 1.1 if delta > 0 else 0.9
        new_zoom = max(1.0, min(500.0, self.zoom * zoom_factor))  # 限制范围
        # 计算新的视口中心，保持鼠标指向的世界坐标不变
        cx, cy = self.get_canvas_center()
        self.view_center[0] = wx - (mouse_pos[0] - cx) / new_zoom
        self.view_center[1] = wy + (mouse_pos[1] - cy) / new_zoom
        self.zoom = new_zoom

    def _handle_click(self, screen_pos):
        """处理画布点击事件，尝试选中细胞"""
        wx, wy = self.screen_to_world(*screen_pos)
        # 从后向前遍历（后绘制的在上层）
        for brect, tag, obj in reversed(self.objects_bbox):
            x1, y1, x2, y2 = brect
            if x1 <= wx <= x2 and y1 <= wy <= y2:
                if isinstance(obj, Cell):
                    self.selected_cell = obj
                    print(f"选中细胞: {obj.name}")
                    return
        # 未命中任何细胞，取消选中
        self.selected_cell = None

    # ================== 对话框：添加细胞/物质 ==================
    def show_add_cell_dialog(self):
        """弹出添加细胞的窗口"""
        if dpg.does_item_exist("add_cell_win"):
            dpg.delete_item("add_cell_win")
        with dpg.window(label="添加细胞", modal=True, tag="add_cell_win", width=300, height=250,
                         pos=(200, 200)):
            dpg.add_text("输入新细胞参数:")
            dpg.add_input_int(label="X坐标", tag="cell_x", default_value=0)
            dpg.add_input_int(label="Y坐标", tag="cell_y", default_value=0)
            dpg.add_input_text(label="DNA序列 (留空随机)", tag="cell_dna", default_value="")
            dpg.add_input_text(label="名称", tag="cell_name", default_value="Cell")
            dpg.add_button(label="确认", callback=self.add_cell_callback)

    def add_cell_callback(self):
        """处理添加细胞"""
        if not self.controller:
            return
        x = dpg.get_value("cell_x")
        y = dpg.get_value("cell_y")
        dna_str = dpg.get_value("cell_dna").strip().upper()
        name = dpg.get_value("cell_name").strip() or "Cell"
        # 准备 DNA
        if dna_str:
            try:
                dna_obj = DNA(dna_str)
            except:
                dna_obj = DNA(random_DNA.generate_dna(300))
        else:
            dna_obj = DNA(random_DNA.generate_dna(300))
        # 创建细胞（会自动注册到环境中）
        try:
            Cell(self.controller.env, x, y, dna=dna_obj, name=name)
            print(f"已添加细胞 {name} 于 ({x},{y})")
        except Exception as e:
            print(f"创建细胞失败: {e}")
        dpg.delete_item("add_cell_win")

    def show_add_substance_dialog(self):
        """弹出添加物质的窗口"""
        if dpg.does_item_exist("add_sub_win"):
            dpg.delete_item("add_sub_win")
        with dpg.window(label="添加物质", modal=True, tag="add_sub_win", width=300, height=250,
                         pos=(200, 200)):
            dpg.add_text("选择物质类型及数量:")
            dpg.add_combo(("Energy", "O2", "H2O", "Sugar"), label="类型", tag="sub_type",
                          default_value="Energy")
            dpg.add_input_int(label="数值", tag="sub_value", default_value=100)
            dpg.add_input_int(label="X坐标", tag="sub_x", default_value=0)
            dpg.add_input_int(label="Y坐标", tag="sub_y", default_value=0)
            dpg.add_button(label="确认", callback=self.add_substance_callback)

    def add_substance_callback(self):
        """处理添加物质"""
        if not self.controller:
            return
        env = self.controller.env
        sub_type = dpg.get_value("sub_type")
        value = dpg.get_value("sub_value")
        x = dpg.get_value("sub_x")
        y = dpg.get_value("sub_y")
        try:
            if sub_type == "Energy":
                obj = env.Energy(value)
            elif sub_type == "O2":
                obj = env.O2(value)
            elif sub_type == "H2O":
                obj = env.H2O(value)
            elif sub_type == "Sugar":
                obj = env.Sugar(6, 12, 6)  # 假设为葡萄糖
            else:
                return
            env.write((x, y), obj)
            print(f"已添加 {sub_type} 于 ({x},{y})")
        except Exception as e:
            print(f"添加物质失败: {e}")
        dpg.delete_item("add_sub_win")

    # ================== GUI 搭建 ==================
    def setup_gui(self):
        """创建完整的 GUI 布局和控件"""
        dpg.create_context()

        # 设置字体
        with dpg.font_registry():
            with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                dpg.bind_font(font)
        # 主窗口
        with dpg.window(label="VitaeCanvas - 生命绘卷", tag="main_window",
                        width=1280, height=720, no_close=True):
            # 使用表格布局实现左中右三列
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
                # 列宽比例：左20% 中50% 右30% （中间占40~50%）
                dpg.add_table_column(init_width_or_weight=0.2)
                dpg.add_table_column(init_width_or_weight=0.5)
                dpg.add_table_column(init_width_or_weight=0.3)

                with dpg.table_row():
                    # ---------- 左侧控制面板 ----------
                    with dpg.child_window(tag="left_panel", autosize_x=True, autosize_y=True):
                        dpg.add_text("控制面板", color=(255, 255, 0))
                        dpg.add_separator()
                        dpg.add_button(label="启动模拟", callback=self.start_simulation, width=120)
                        dpg.add_button(label="暂停/恢复更新", callback=self.toggle_pause, width=120)
                        dpg.add_button(label="重置模拟", callback=self.reset_simulation, width=120)
                        dpg.add_separator()
                        dpg.add_text("手动添加对象:")
                        dpg.add_button(label="添加细胞", callback=self.show_add_cell_dialog, width=120)
                        dpg.add_button(label="添加物质", callback=self.show_add_substance_dialog, width=120)
                        dpg.add_separator()
                        dpg.add_button(label="适应视图", callback=self.fit_view, width=120)

                    # ---------- 中间画布区域 ----------
                    with dpg.child_window(tag="canvas_panel", autosize_x=True, autosize_y=True):
                        # 使用 drawlist 和 draw_node 便于整体变换（虽然我们手动管理变换）
                        with dpg.drawlist(tag="canvas_drawlist", width=-1, height=-1):
                            dpg.add_draw_node(tag="canvas_node")

                    # ---------- 右侧信息面板 ----------
                    with dpg.child_window(tag="right_panel", autosize_x=True, autosize_y=True):
                        dpg.add_text("细胞信息", color=(255, 255, 0))
                        dpg.add_separator()
                        dpg.add_text("名称: ---", tag="info_name")
                        dpg.add_text("坐标: ---", tag="info_pos")
                        dpg.add_text("DNA: ---", tag="info_dna")
                        dpg.add_text("RNA: ---", tag="info_rna")
                        dpg.add_text("颜色: ---", tag="info_color")

        # ---------- 画布交互事件绑定 ----------
        with dpg.item_handler_registry(tag="canvas_handler"):
            dpg.add_mouse_down_handler(callback=self.on_mouse_down)
            dpg.add_mouse_move_handler(callback=self.on_mouse_move)
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)
            dpg.add_mouse_wheel_handler(callback=self.on_mouse_wheel)
        dpg.bind_item_handler_registry("canvas_panel", "canvas_handler")

        # 创建更新画布的定时器
        self._create_timer()

        # DearPyGui 视口设置
        dpg.create_viewport(title="VitaeCanvas - 生命绘卷", width=1280, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def _create_timer(self):
        """创建/重建画布更新定时器"""
        if dpg.does_item_exist("update_timer"):
            dpg.delete_item("update_timer")
        dpg.add_timer(delay=0.05, callback=self.update_canvas, tag="update_timer")


if __name__ == "__main__":
    gui = VitaeCanvasGUI()
    gui.setup_gui()