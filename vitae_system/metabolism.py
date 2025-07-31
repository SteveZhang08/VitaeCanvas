# === VitaeCanvas ===
# ./vitae_system/metabolism.py
# by SteveZhang08
# Helpers: None

if __name__ == "__main__":
    # 当作为主程序直接运行时，绝对导入同级模块
    from cells import*
    from env import*
    import time
else:
    # 当作为模块被导入时，相对导入库内同级模块
    from .cells import*
    from .env import*

class MetabolismSystem:
    """代谢系统控制器，处理能量转换与物质交换"""
    def __init__(self, cell:Cell, env:Environment) -> None:
        """
        执行细胞完整代谢周期
        :param cell: 目标细胞实例（必须包含有效坐标）
        :param env: 环境控制器实例（必须已初始化）
        :raises ValueError: 当细胞坐标超出环境范围时抛出
        :side effect: 
            - 修改cell.energy值
            - 修改Cell所在坐标的Energy的值
            - 将cell.age增加 1
        """
        self.x = cell.x
        self.y = cell.y
        self.env:Environment = env
        self.cell:Cell = cell
        self.metabolic_rate = min(self.cell.metabolic_rate*(1+self.cell.efficiency_increase),1)   # 计算细胞能量转化率（算上增幅）
        self.grid_data = self.env.read(self.x, self.y)
        idx = env.check_type_on_env(self.grid_data, Energy)
        if idx != None:
            self.env_energy:Energy = self.grid_data[idx]
        else:
            self.env_energy = Energy(0)
        self.absorb_sugar()
        if self.sugar != None:
            self.hydrolysis()
        self.cell.age += 1
        # 更新环境能量
        self.env.write(self.x, self.y, self.env_energy)

    def absorb_sugar(self) -> Sugar:
        # 从环境中吸收糖类
        sugar_idx = self.env.check_type_on_env(self.grid_data, Sugar)
        if sugar_idx == None:
            self.sugar = None
        else:
            self.sugar:Sugar = self.grid_data[sugar_idx]
            # 如果吸收到糖类，删除环境中的糖类，消耗细胞物质交换能量，耗能返还环境
            self.env.delete(self.x,self.y,sugar_idx)
            self.cell.energy -= self.cell.material_exchange_energy
            self.env_energy.value += self.cell.material_exchange_energy

    def hydrolysis(self):
        '''
        糖的水解
        '''
        self.NADH:NADH = self.sugar.Hydrolysis()['NADH']
        self.cell.energy += self.metabolic_energy(self.sugar.Hydrolysis()['energy'])

    def metabolic_energy(self, energy:Energy) -> Energy:
        # 计算细胞能量转换
        # 计算吸收能量
        absorb = energy.value * self.metabolic_rate
        # 计算输出能量
        out = energy.value - absorb
        self.env_energy.value += out
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