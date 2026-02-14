"""
模拟线程 - 负责模拟计算
"""

import threading
import time
import queue
from models.simulation import SimulationController

class SimulationThread(threading.Thread):
    """模拟线程"""
    
    def __init__(self, event_queue=None, event_bus=None, update_rate=60):
        """
        初始化模拟线程
        
        Args:
            event_queue: 事件队列，用于向主线程发送消息（可选）
            event_bus: 事件总线（可选）
            update_rate: 更新频率（Hz）
        """
        super().__init__(daemon=True)
        self.event_queue = event_queue
        self.event_bus = event_bus
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        
        self.simulation = SimulationController()
        self.running = True
        self.paused = False
        self.requests = queue.Queue()
        
        # 线程同步
        self.lock = threading.Lock()
        
        # 验证参数
        if event_queue is None and event_bus is None:
            print("警告：既没有设置event_queue也没有设置event_bus，线程通信将不可用")
    
    def run(self):
        """线程主循环"""
        last_time = time.time()
        accumulator = 0.0
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # 处理请求
            self._process_requests()
            
            if not self.paused:
                # 使用固定时间步长更新模拟
                accumulator += delta_time
                
                while accumulator >= self.update_interval:
                    self._update_simulation(self.update_interval)
                    accumulator -= self.update_interval
                
                # 发送模拟状态到主线程
                self._send_simulation_state()
            
            # 控制帧率
            time.sleep(max(0, self.update_interval - (time.time() - current_time)))
    
    def _update_simulation(self, dt):
        """更新模拟"""
        try:
            with self.lock:
                self.simulation.update(dt)
        except Exception as e:
            self._send_error(f"模拟更新错误: {e}")
    
    def _process_requests(self):
        """处理请求"""
        try:
            while True:
                request = self.requests.get_nowait()
                self._handle_request(request)
        except queue.Empty:
            pass
    
    def _handle_request(self, request):
        """处理单个请求"""
        request_type = request.get('type')
        
        if request_type == 'add_cell':
            data = request.get('data', {})
            success = self.simulation.add_cell(**data)
            if success:
                self._send_log(f"添加细胞: {data.get('name', '未知')}")
            else:
                self._send_error(f"添加细胞失败: {data.get('name', '未知')}")
                
        elif request_type == 'add_resource':
            data = request.get('data', {})
            success = self.simulation.add_resource(**data)
            if success:
                self._send_log(f"添加资源: {data.get('type', '未知')}")
            else:
                self._send_error(f"添加资源失败: {data.get('type', '未知')}")
                
        elif request_type == 'reset':
            with self.lock:
                self.simulation = SimulationController()
            self._send_log("模拟已重置")
    
    def _send_simulation_state(self):
        """发送模拟状态"""
        try:
            with self.lock:
                info = self.simulation.get_simulation_info()
                
                # 准备细胞数据
                cells_data = []
                for cell in self.simulation.cell_list:
                    cells_data.append({
                        'x': getattr(cell, 'x', 0),
                        'y': getattr(cell, 'y', 0),
                        'name': getattr(cell, 'name', 'Cell'),
                        'color': getattr(cell, 'color', (0, 255, 0))
                    })
                
                # 发送到主线程
                self.event_queue.put({
                    'type': 'simulation_info',
                    'data': info
                })
                
                # 发送细胞状态（仅在有变化时发送）
                self.event_queue.put({
                    'type': 'simulation_state',
                    'data': {
                        'cells': cells_data,
                        'resources': self.simulation.resources,
                        'info': info
                    }
                })
                
        except Exception as e:
            self._send_error(f"发送状态错误: {e}")
    
    def _send_log(self, message):
        """发送日志消息"""
        # 优先使用事件总线
        if self.event_bus:
            self.event_bus.publish('simulation_log', {'message': message, 'source': 'simulation'})
        # 其次使用事件队列
        elif self.event_queue:
            self.event_queue.put({
                'type': 'simulation_log',
                'data': message
            })
        else:
            print(f"模拟日志: {message}")
    
    def _send_error(self, error):
        """发送错误消息"""
        if self.event_bus:
            self.event_bus.publish('simulation_error', {'error': str(error), 'source': 'simulation'})
        elif self.event_queue:
            self.event_queue.put({
                'type': 'simulation_error',
                'data': str(error)
            })
        else:
            print(f"模拟错误: {error}")
    
    def add_cell(self, x, y, dna_sequence, name="Cell"):
        """添加细胞（线程安全）"""
        self.requests.put({
            'type': 'add_cell',
            'data': {
                'x': x,
                'y': y,
                'dna_sequence': dna_sequence,
                'name': name
            }
        })
        return True
    
    def add_resource(self, x, y, resource_type, amount):
        """添加资源（线程安全）"""
        self.requests.put({
            'type': 'add_resource',
            'data': {
                'x': x,
                'y': y,
                'resource_type': resource_type,
                'amount': amount
            }
        })
        return True
    
    def reset(self):
        """重置模拟"""
        self.requests.put({'type': 'reset'})
    
    def pause(self):
        """暂停模拟"""
        self.paused = True
        self._send_log("模拟已暂停")
    
    def resume(self):
        """恢复模拟"""
        self.paused = False
        self._send_log("模拟已恢复")
    
    def stop(self):
        """停止线程"""
        self.running = False
    
    def get_state(self):
        """获取当前状态（用于显示）"""
        try:
            with self.lock:
                cells_data = []
                for cell in self.simulation.cell_list:
                    cells_data.append({
                        'x': getattr(cell, 'x', 0),
                        'y': getattr(cell, 'y', 0),
                        'name': getattr(cell, 'name', 'Cell'),
                        'color': getattr(cell, 'color', (0, 255, 0))
                    })
                
                return {
                    'cells': cells_data,
                    'resources': self.simulation.resources,
                    'info': self.simulation.get_simulation_info()
                }
        except:
            return None