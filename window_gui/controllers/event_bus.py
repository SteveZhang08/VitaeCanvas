"""
事件总线 - 用于模块间通信
"""

import threading
import queue
import time
from typing import Dict, Any, Callable, Optional

class Event:
    """事件类"""
    
    def __init__(self, event_type: str, data: Any = None, 
                 source: str = None, timestamp: float = None):
        """
        初始化事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
            timestamp: 时间戳
        """
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = timestamp or time.time()
    
    def __repr__(self):
        return f"Event(type={self.type}, source={self.source}, timestamp={self.timestamp})"

class EventBus:
    """事件总线"""
    
    def __init__(self):
        """初始化事件总线"""
        self._subscribers: Dict[str, list] = {}
        self._event_queue = queue.Queue()
        self._lock = threading.RLock()
        self._running = True
        
        # 启动事件处理线程
        self._processor_thread = threading.Thread(
            target=self._process_events,
            daemon=True
        )
        self._processor_thread.start()
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        with self._lock:
            if event_type in self._subscribers:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                
                # 如果该事件类型没有订阅者，删除键
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
    
    def publish(self, event_type: str, data: Any = None, 
                source: str = None) -> Event:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
            
        Returns:
            Event: 创建的事件对象
        """
        event = Event(event_type, data, source)
        self._event_queue.put(event)
        return event
    
    def publish_sync(self, event_type: str, data: Any = None, 
                    source: str = None) -> Event:
        """
        同步发布事件（立即处理）
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
            
        Returns:
            Event: 创建的事件对象
        """
        event = Event(event_type, data, source)
        self._handle_event(event)
        return event
    
    def _process_events(self):
        """处理事件队列"""
        while self._running:
            try:
                event = self._event_queue.get(timeout=0.1)
                self._handle_event(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"事件处理错误: {e}")
    
    def _handle_event(self, event: Event):
        """处理单个事件"""
        with self._lock:
            # 获取特定类型事件的订阅者
            specific_subscribers = self._subscribers.get(event.type, [])
            
            # 获取所有事件的订阅者
            all_subscribers = self._subscribers.get('*', [])
            
            # 合并订阅者
            subscribers = specific_subscribers + all_subscribers
        
        # 调用回调函数
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"事件回调错误: {e}")
    
    def wait_for_event(self, event_type: str, timeout: float = None) -> Optional[Event]:
        """
        等待特定事件
        
        Args:
            event_type: 等待的事件类型
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Event]: 接收到的事件，超时返回None
        """
        result = {'event': None}
        event_received = threading.Event()
        
        def handler(event):
            if event.type == event_type:
                result['event'] = event
                event_received.set()
        
        # 临时订阅
        self.subscribe(event_type, handler)
        
        # 等待事件或超时
        if timeout:
            event_received.wait(timeout)
        else:
            event_received.wait()
        
        # 取消订阅
        self.unsubscribe(event_type, handler)
        
        return result['event']
    
    def clear(self):
        """清空事件队列"""
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
                self._event_queue.task_done()
            except queue.Empty:
                break
    
    def stop(self):
        """停止事件总线"""
        self._running = False
        self.clear()
        
        if self._processor_thread.is_alive():
            self._processor_thread.join(timeout=1.0)
    
    def get_queue_size(self) -> int:
        """获取事件队列大小"""
        return self._event_queue.qsize()
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """
        获取订阅者数量
        
        Args:
            event_type: 事件类型，为None时返回所有订阅者
            
        Returns:
            int: 订阅者数量
        """
        with self._lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            else:
                total = 0
                for subscribers in self._subscribers.values():
                    total += len(subscribers)
                return total

# 全局事件总线实例
global_event_bus = EventBus()

# 预定义事件类型
class EventTypes:
    """事件类型常量"""
    
    # 模拟相关事件
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    SIMULATION_STOPPED = "simulation_stopped"
    SIMULATION_RESET = "simulation_reset"
    SIMULATION_UPDATED = "simulation_updated"
    SIMULATION_ERROR = "simulation_error"
    
    # 细胞相关事件
    CELL_ADDED = "cell_added"
    CELL_REMOVED = "cell_removed"
    CELL_UPDATED = "cell_updated"
    CELL_SPLIT = "cell_split"
    CELL_DIED = "cell_died"
    
    # 资源相关事件
    RESOURCE_ADDED = "resource_added"
    RESOURCE_REMOVED = "resource_removed"
    RESOURCE_UPDATED = "resource_updated"
    
    # 界面相关事件
    UI_REFRESH = "ui_refresh"
    UI_ERROR = "ui_error"
    UI_LOG = "ui_log"
    
    # 工具相关事件
    TOOL_OPENED = "tool_opened"
    TOOL_CLOSED = "tool_closed"
    
    # 系统事件
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"

# 方便的函数
def subscribe(event_type: str, callback: Callable):
    """订阅事件（全局）"""
    global_event_bus.subscribe(event_type, callback)

def unsubscribe(event_type: str, callback: Callable):
    """取消订阅事件（全局）"""
    global_event_bus.unsubscribe(event_type, callback)

def publish(event_type: str, data: Any = None, source: str = None) -> Event:
    """发布事件（全局）"""
    return global_event_bus.publish(event_type, data, source)

def publish_sync(event_type: str, data: Any = None, source: str = None) -> Event:
    """同步发布事件（全局）"""
    return global_event_bus.publish_sync(event_type, data, source)