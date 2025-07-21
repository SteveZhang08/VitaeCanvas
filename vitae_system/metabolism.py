# === VitaeCanvas ===
# ./vitae_system/metabolism.py
# by SteveZhang08
# Helpers: None

from .cells import*
from .env import*
import time

class MetabolismSystem:
    """代谢系统控制器，处理能量转换与物质交换"""
    def __init__(self, cell:Cell, env:Environment) -> None:
        """
        执行细胞完整代谢周期
        :param cell: 目标细胞实例（必须包含有效坐标）
        :param env: 环境控制器实例（必须已初始化）
        :return: True表示存活，False表示死亡
        :raises ValueError: 当细胞坐标超出环境范围时抛出
        :side effect: 
            - 修改cell.energy值
            - 修改Cell所在坐标的Energy的值
        """
        self.x = cell.x
        self.y = cell.y
        self.metabolic_rate = cell.metabolic_rate
        grid_data = env.read(cell.x, cell.y)
        energy_index = env.check_type_on_env(grid_data, Energy)
        if energy_index != None:
            self.energy:Energy = grid_data[energy_index]
        else:
            debug("Energy对象未找到，自动初始化为0")
            self.energy = Energy(0)
            env.write(self.x, self.y, self.energy)
        self.env = env
        self.cell:Cell = grid_data[env.check_type_on_env(grid_data, Cell)]
        self.cell.energy += self.metabolic_energy(self.absorb_energy())
        env.write(self.x, self.y, self.cell)

    def absorb_energy(self) -> Energy:
        if self.energy.value - 1 <= 0:
            get_value = abs(self.energy.value)
        else:
            get_value = 1
        self.energy.value = max(self.energy.value - 1, 0)
        return Energy(get_value, diffuse = False)
    
    def metabolic_energy(self, energy:Energy) -> Energy:
        absorb = energy.value * self.metabolic_rate
        out = energy.value - absorb
        self.energy.value += out
        self.env.write(self.x, self.y, self.energy)
        return Energy(absorb, diffuse=False)   

if __name__ == "__main__":
    env1 = env.Environment()
    env1.write(0,0,Energy(114))
    cell1 = Cell(env1, 0, 0, dna=DNA(random_DNA.generate_dna(9)))
    while True:
        print(f'细胞能量转化率：{cell1.metabolic_rate}')
        MetabolismSystem(cell1, env1)
        print(cell1.energy)
        print(f'细胞当前坐标能量值：{env1.read(cell1.x, cell1.y)[env1.check_type_on_env(env1.read(cell1.x, cell1.y), Energy)]}')
        env1.energy_diffusion()
        time.sleep(1)