import threading
import time
import sys
import os

# 确保Python能够找到模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """主函数"""
    
    # 导入需要的模块
    from tkinter_control import TkinterControlPanel
    from simulation_controller import SimulationController
    
    print("启动 VitaeCanvas 模拟系统...")
    print("=" * 50)
    
    # 创建Tkinter控制面板
    print("正在初始化控制面板...")
    control_panel = TkinterControlPanel()
    
    # 创建模拟控制器
    print("正在初始化模拟控制器...")
    simulation = SimulationController(tkinter_control=control_panel)
    
    # 将模拟控制器引用传递给控制面板
    control_panel.simulation_controller = simulation
    
    # 初始化模拟（在主线程中）
    print("初始化Pygame窗口...")
    try:
        success = simulation.initialize()
        if not success:
            control_panel.add_log("模拟初始化失败")
            print("模拟初始化失败")
            return
    except Exception as e:
        error_msg = f"模拟初始化失败: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        control_panel.add_log(error_msg)
        return
    
    control_panel.add_log("模拟控制器初始化完成")
    print("模拟控制器初始化完成")
    
    # 启动代谢线程
    simulation.start_metabolism_thread()
    
    # 创建一个函数来运行Pygame主循环
    def run_pygame_loop():
        """运行Pygame主循环的线程函数"""
        try:
            simulation.run_main_loop()
        except Exception as e:
            error_msg = f"Pygame主循环运行出错: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            # 在主线程中添加日志
            control_panel.root.after(0, control_panel.add_log, error_msg)
    
    # 在单独的线程中运行Pygame主循环
    pygame_thread = threading.Thread(target=run_pygame_loop, daemon=True)
    pygame_thread.start()
    
    # 等待Pygame窗口启动
    time.sleep(1)
    
    # 运行Tkinter控制面板（主线程）
    print("启动控制面板...")
    print("=" * 50)
    print("控制面板快捷键:")
    print("  - F1: 显示帮助")
    print("  - Ctrl+S: 保存日志")
    print("  - Ctrl+Q: 退出")
    print("=" * 50)
    
    try:
        control_panel.run()
    except Exception as e:
        print(f"控制面板运行出错: {e}")
    
    # 停止模拟
    simulation.stop()
    
    print("模拟系统已关闭")

if __name__ == "__main__":
    main()