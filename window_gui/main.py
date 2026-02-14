#!/usr/bin/env python3
"""
Vitae Canvas - 生命绘卷主程序入口
使用多线程分离显示与计算
"""

import tkinter as tk
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controllers.simulation_thread import SimulationThread
from controllers.event_bus import global_event_bus, EventTypes
from views.main_window import MainWindow

def setup_event_handlers():
    """设置全局事件处理器"""
    
    def on_simulation_started(event):
        print(f"模拟开始: {event.data}")
    
    def on_simulation_error(event):
        print(f"模拟错误: {event.data}")
    
    def on_cell_added(event):
        print(f"细胞添加: {event.data}")
    
    # 订阅事件
    global_event_bus.subscribe(EventTypes.SIMULATION_STARTED, on_simulation_started)
    global_event_bus.subscribe(EventTypes.SIMULATION_ERROR, on_simulation_error)
    global_event_bus.subscribe(EventTypes.CELL_ADDED, on_cell_added)

def main():
    """主函数"""
    # 设置事件处理器
    setup_event_handlers()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("Vitae Canvas - 生命绘卷")
    root.geometry("1200x800")
    
    # 创建事件队列用于线程间通信
    import queue
    event_queue = queue.Queue()
    
    # 创建模拟线程
    sim_thread = SimulationThread(event_queue, global_event_bus)
    sim_thread.start()
    
    # 创建主窗口
    app = MainWindow(root, sim_thread, event_queue)
    
    # 设置关闭事件处理
    def on_closing():
        """窗口关闭时清理资源"""
        # 发布系统关闭事件
        global_event_bus.publish(EventTypes.SYSTEM_SHUTDOWN, "应用程序关闭")
        
        # 停止模拟线程
        sim_thread.stop()
        sim_thread.join(timeout=2.0)
        
        # 停止事件总线
        global_event_bus.stop()
        
        # 关闭窗口
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()
    except Exception as e:
        print(f"程序错误: {e}")
        on_closing()

if __name__ == "__main__":
    main()