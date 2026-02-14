"""
模拟控制器模型
"""

import time
import random
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
try:
    from vitae_system import env, cells, metabolism, random_DNA
    print("success")
except ImportError:
    # 创建模拟类作为fallback
    class Fallback:
        pass
    env = cells = metabolism = random_DNA = Fallback()

class SimulationController:
    """模拟控制器"""
    
    def __init__(self, width=100, height=100):
        """
        初始化模拟环境
        
        Args:
            width: 环境宽度
            height: 环境高度
        """
        self.width = width
        self.height = height
        self.cell_list = []
        self.resources = []
        self.simulation_time = 0
        self.frame_count = 0
        self.last_update_time = time.time()
        self.fps = 0
        
        try:
            self.env = env.Environment(width, height)
            self._initialize_environment()
        except Exception as e:
            print(f"模拟环境初始化错误: {e}")
            self.env = None
    
    def _initialize_environment(self):
        """初始化环境"""
        # 添加示例细胞
        if hasattr(random_DNA, 'generate_dna'):
            dna_sequence = random_DNA.generate_dna(100)
        else:
            dna_sequence = "TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT"
        
        dna = cells.DNA(dna_sequence)
        self.cell_list.append(cells.Cell(self.env, 0, 0, dna=dna, name="Vita"))
        
        # 添加初始资源
        self._add_initial_resources()
    
    def _add_initial_resources(self):
        """添加初始资源"""
        if not hasattr(env, 'Energy'):
            return
            
        resource_positions = [
            (0, 0, env.Energy(100)),
            (0, 0, env.O2(200)),
            (0, 0, env.H2O(200)),
            (0, 1, env.Energy(200))
        ]
        
        if hasattr(cells, 'SugarList') and hasattr(cells, 'Sugar'):
            resource_positions.append((0, 0, cells.SugarList([cells.Sugar(6, 12, 6)])))
        
        for x, y, resource in resource_positions:
            self.env.write(x, y, resource)
            self.resources.append({
                'x': x, 
                'y': y, 
                'type': resource.__class__.__name__,
                'amount': getattr(resource, 'amount', 100)
            })
    
    def update(self, dt):
        """
        更新模拟状态
        
        Args:
            dt: 时间步长（秒）
        """
        if not self.env:
            return
            
        self.simulation_time += dt
        self.frame_count += 1
        
        try:
            # 更新细胞代谢
            new_cells = []
            for cell in self.cell_list[:]:  # 使用切片创建副本
                if hasattr(cell, 'is_alive') and not cell.is_alive:
                    self.cell_list.remove(cell)
                    continue
                    
                metabolism_system = metabolism.MetabolismSystem(cell, self.env)
                new_cell = metabolism_system.re_info()
                
                if new_cell:
                    new_cells.append(new_cell)
            
            self.cell_list.extend(new_cells)
            
            # 资源扩散
            self.env.resources_diffusion()
            
            # 更新资源列表
            self._update_resource_list()
            
        except Exception as e:
            print(f"模拟更新错误: {e}")
        
        # 计算FPS
        current_time = time.time()
        if current_time - self.last_update_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_update_time = current_time
    
    def _update_resource_list(self):
        """更新资源列表（简化实现）"""
        # 这里需要根据实际环境更新资源位置和数量
        # 简化实现：随机移动资源
        for resource in self.resources:
            resource['x'] += random.randint(-1, 1)
            resource['y'] += random.randint(-1, 1)
            resource['x'] = max(0, min(self.width - 1, resource['x']))
            resource['y'] = max(0, min(self.height - 1, resource['y']))
    
    def add_cell(self, x, y, dna_sequence, name="Cell"):
        """添加新细胞"""
        try:
            dna = cells.DNA(dna_sequence)
            new_cell = cells.Cell(self.env, x, y, dna=dna, name=name)
            self.cell_list.append(new_cell)
            return True
        except Exception as e:
            print(f"添加细胞错误: {e}")
            return False
    
    def add_resource(self, x, y, resource_type, amount):
        """添加资源"""
        try:
            if resource_type == "Energy":
                resource = env.Energy(amount)
            elif resource_type == "O2":
                resource = env.O2(amount)
            elif resource_type == "H2O":
                resource = env.H2O(amount)
            elif resource_type == "Sugar" and hasattr(cells, 'SugarList'):
                resource = cells.SugarList([cells.Sugar(6, 12, 6)])
            else:
                return False
            
            self.env.write(x, y, resource)
            self.resources.append({
                'x': x, 
                'y': y, 
                'type': resource_type,
                'amount': amount
            })
            return True
        except Exception as e:
            print(f"添加资源错误: {e}")
            return False
    
    def get_simulation_info(self):
        """获取模拟信息"""
        return {
            'cell_count': len(self.cell_list),
            'resource_count': len(self.resources),
            'simulation_time': self.simulation_time,
            'fps': self.fps,
            'width': self.width,
            'height': self.height
        }