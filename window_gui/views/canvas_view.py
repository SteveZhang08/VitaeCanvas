"""
画布视图 - 负责显示模拟
"""

import tkinter as tk
import math
from utils.color_utils import get_cell_color

class CanvasView:
    """画布视图"""
    
    def __init__(self, parent, simulation_thread):
        """
        初始化画布视图
        
        Args:
            parent: 父容器
            simulation_thread: 模拟线程
        """
        self.parent = parent
        self.sim_thread = simulation_thread
        self.cell_size = 40
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.dragging = False
        self.last_x = 0
        self.last_y = 0
        
        # 创建画布
        self.canvas = tk.Canvas(parent, bg='#0a1428', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件
        self._bind_events()
        
        # 启动更新循环
        self._update_loop()
    
    def _bind_events(self):
        """绑定事件"""
        # 鼠标事件
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        
        # 滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux 向上
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux 向下
        
        # 画布大小变化事件
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_mouse_press(self, event):
        """鼠标按下事件"""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
        self.canvas.config(cursor="fleur")
    
    def _on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if self.dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.view_offset_x += dx
            self.view_offset_y += dy
            self.last_x = event.x
            self.last_y = event.y
            self.update_display()
    
    def _on_mouse_release(self, event):
        """鼠标释放事件"""
        self.dragging = False
        self.canvas.config(cursor="")
    
    def _on_mouse_wheel(self, event):
        """鼠标滚轮事件"""
        if event.delta > 0 or event.num == 4:  # 向上滚轮
            self.cell_size = min(100, self.cell_size + 5)
        else:  # 向下滚轮
            self.cell_size = max(10, self.cell_size - 5)
        self.update_display()
    
    def _on_canvas_configure(self, event):
        """画布大小变化事件"""
        self.update_display()
    
    def _update_loop(self):
        """更新循环"""
        self.update_display()
        self.parent.after(50, self._update_loop)  # 20 FPS更新
    
    def update_display(self):
        """更新显示"""
        # 获取模拟状态
        state = self.sim_thread.get_state()
        
        if not state:
            return
            
        self.canvas.delete("all")
        
        # 绘制网格
        self._draw_grid()
        
        # 绘制资源
        self._draw_resources(state.get('resources', []))
        
        # 绘制细胞
        self._draw_cells(state.get('cells', []))
    
    def _draw_grid(self):
        """绘制网格"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        # 计算可见区域
        start_x = math.floor(-self.view_offset_x / self.cell_size) - 1
        end_x = math.ceil((width - self.view_offset_x) / self.cell_size) + 1
        start_y = math.floor(-self.view_offset_y / self.cell_size) - 1
        end_y = math.ceil((height - self.view_offset_y) / self.cell_size) + 1
        
        # 绘制网格线
        grid_color = '#283c5f'
        
        for x in range(start_x, end_x + 1):
            screen_x = x * self.cell_size + self.view_offset_x
            self.canvas.create_line(screen_x, 0, screen_x, height, 
                                   fill=grid_color, width=1)
        
        for y in range(start_y, end_y + 1):
            screen_y = y * self.cell_size + self.view_offset_y
            self.canvas.create_line(0, screen_y, width, screen_y, 
                                   fill=grid_color, width=1)
        
        # 绘制原点标记
        origin_x = self.view_offset_x
        origin_y = self.view_offset_y
        self.canvas.create_oval(
            origin_x - 3, origin_y - 3,
            origin_x + 3, origin_y + 3,
            fill='red', outline='white'
        )
    
    def _draw_cells(self, cells):
        """绘制细胞"""
        for cell in cells:
            x = cell.get('x', 0)
            y = cell.get('y', 0)
            name = cell.get('name', 'Cell')
            
            screen_x = x * self.cell_size + self.view_offset_x
            screen_y = y * self.cell_size + self.view_offset_y
            
            # 检查是否在可见区域内
            if self._is_visible(screen_x, screen_y):
                # 绘制细胞
                radius = self.cell_size // 2 - 2
                color = get_cell_color(cell)
                
                self.canvas.create_oval(
                    screen_x - radius, screen_y - radius,
                    screen_x + radius, screen_y + radius,
                    fill=color, outline='white', width=2
                )
                
                # 绘制细胞名称（如果细胞足够大）
                if self.cell_size >= 20:
                    self.canvas.create_text(
                        screen_x, screen_y, 
                        text=name, 
                        fill='white', 
                        font=('Arial', min(10, self.cell_size // 4))
                    )
    
    def _draw_resources(self, resources):
        """绘制资源"""
        for resource in resources:
            x = resource.get('x', 0)
            y = resource.get('y', 0)
            r_type = resource.get('type', 'Energy')
            
            screen_x = x * self.cell_size + self.view_offset_x
            screen_y = y * self.cell_size + self.view_offset_y
            
            if self._is_visible(screen_x, screen_y):
                # 根据资源类型选择颜色
                colors = {
                    'Energy': ('yellow', 'orange'),
                    'O2': ('lightblue', 'blue'),
                    'H2O': ('cyan', 'darkcyan'),
                    'Sugar': ('lightgreen', 'green')
                }
                
                fill_color, outline_color = colors.get(r_type, ('yellow', 'orange'))
                
                # 绘制资源点
                size = max(3, min(8, self.cell_size // 8))
                self.canvas.create_rectangle(
                    screen_x - size, screen_y - size,
                    screen_x + size, screen_y + size,
                    fill=fill_color, outline=outline_color, width=1
                )
    
    def _is_visible(self, x, y, margin=50):
        """检查点是否在可见区域内"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (-margin <= x <= width + margin and 
                -margin <= y <= height + margin)