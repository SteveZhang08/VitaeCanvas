# === VitaeCanvas ===
# ./vitae_system/metabolism.py
# by SteveZhang08
# Helpers: None

if __name__ == "__main__":
    # 当作为主程序直接运行时，绝对导入同级模块
    from cells import *
    from env import *
    from reproduction import *
    import time
else:
    # 当作为模块被导入时，相对导入库内同级模块
    from .cells import *
    from .env import *
    from .reproduction import *

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
        if type(cell) != Cell:
            raise ValueError(f"[function]MetabolismSystem.__init__: 参数 cell 必须是 {Cell} 类型，但我们得到了 {type(cell)} ？\n cell must be a Cell instance, but we got {type(cell)} ?")
        if type(env) != Environment:
            raise ValueError(f"[function]MetabolismSystem.__init__: 参数 env 必须是 {Environment} 类型，但我们得到了 {type(env)} ？\n env must be an Environment instance, but we got {type(env)} ?")
        
        self.x = cell.x
        self.y = cell.y
        self.env:Environment = env
        self.cell:Cell = cell
        if self.cell.dead:  # 如果细胞死亡
            self.vital_signs = 0
            return
        self.vital_signs = 1
        self.cell.metabolic_init()
        self.metabolic_rate = min(self.cell.metabolic_rate*(1+self.cell.efficiency_increase),1)   # 计算细胞能量转化率（算上增幅）
        self.aerobic_respiration_enzymes = min(self.cell.aerobic_respiration_enzymes, 0.8)         # 计算有氧呼吸酶增益
        self.NADH:NADH = self.cell.resource['NADH']
        self.grid_data = self.env.read(self.x, self.y)
        self.new_cell = None
        self.read_env()
        if Sugar in self.cell.absorbed_substances:
            debug(f"细胞{self.cell.name}开始进行糖的代谢")
            self.absorb_sugar()
            if self.sugar != None:
                self.hydrolysis()
        if O2 in self.cell.absorbed_substances:
            nadh = self.NADH
            allow_nadh = NADH(max(nadh.value * self.aerobic_respiration_enzymes, 1))
            need_o2 = O2(allow_nadh.value / 4)
            if need_o2.value <= self.O2.value:
                self.aerobic_respiration(need_o2, allow_nadh)
            else:
                allow_nadh = NADH(self.O2.value*4)
                self.aerobic_respiration(self.O2, allow_nadh)
        self.cell.age += 1
        # 更新细胞数据
        self.cell.resource['NADH'] = self.NADH

        # 处理细胞动作
        target_functions = {'env_receptor', 'move'}
        for protein in self.cell.protein_list:
            for func_name in target_functions.intersection(protein.function_dict.keys()):
                protein.function_dict[func_name](self.cell, call=True)

        # 细胞繁殖
        if self.cell.energy.value > 215:
            self.reproduction = Reproduction(self.cell)
            new_cell = self.reproduction.reproduce()
            if new_cell != None:
                debug(f"细胞{self.cell.name}在({self.x},{self.y})繁殖了一个新细胞{new_cell.name}")
                self.new_cell = new_cell

        # 更新环境数据
        self.env.write(self.x, self.y, self.env_energy)
        self.env.write(self.x, self.y, self.O2)
        self.env.write(self.x, self.y, self.H2O)

        if self.cell.energy.value < 0:
            self.cell.lysis()
            self.vital_signs = 0
            debug(f"细胞{self.cell.name}在({self.x},{self.y})死亡")

    def read_env(self):
        '''
        读取环境中的能量、氧气、水
        '''
        def read_type(_type):
            idx = self.env.check_type_on_env(self.grid_data, _type)
            if idx != None:
                return self.grid_data[idx]
            else:
                return _type(0) # 返回这个项目的空值
        self.env_energy:Energy = read_type(Energy)
        self.O2:O2 = read_type(O2)
        self.H2O:H2O = read_type(H2O)

    def absorb_sugar(self) -> Sugar:
        # 从环境中吸收糖类
        SugarList_idx = self.env.check_type_on_env(self.grid_data, SugarList)
        if SugarList_idx == None:
            self.sugar = None
        else:
            sugarlist:SugarList = self.grid_data[SugarList_idx]
            if len(sugarlist) != 0:
                import random
                self.sugar:Sugar = random.choice(sugarlist) # 获取糖类列表中随机一项
                # 如果吸收到糖类，删除环境中的糖类，消耗细胞物质交换能量，耗能返还环境
                self.env.delete(self.x,self.y,SugarList_idx)
                self.cell.energy.value -= self.cell.material_exchange_energy
                self.env_energy.value += self.cell.material_exchange_energy
                debug(f"细胞{self.cell.name}吸收了{str(self.sugar)}并耗能{self.cell.material_exchange_energy}")
            else:
                self.sugar = None

    def hydrolysis(self):
        '''
        糖的水解
        '''
        hydrolysis_return = self.sugar.Hydrolysis()
        self.NADH.value += hydrolysis_return['NADH'].value
        energy_get:Energy = self.metabolic_energy(hydrolysis_return['energy'])
        self.cell.energy.value += energy_get.value
        debug(f"细胞{self.cell.name}进行了{self.sugar}的水解，并从中吸收了{energy_get.value}的能量")

    def metabolic_energy(self, energy:Energy) -> Energy:
        if type(energy) != Energy:
            raise ValueError(f"[function]MetabolismSystem.__init__: 参数 energy 必须是 {Energy} 类型，但我们得到了 {type(energy)} ？\n energy must be a Energy instance, but we got {type(energy)} ?")
        # 计算吸收能量
        absorb = energy.value * self.metabolic_rate
        # 计算输出能量
        out = energy.value - absorb
        self.env_energy.value += out
        return Energy(absorb, diffuse=False)

    def aerobic_respiration(self, o2:O2, nadh:NADH):
        if type(o2) != O2:
            raise ValueError(f"[function]MetabolismSystem.__init__: 参数 o2 必须是 {O2} 类型，但我们得到了 {type(o2)} ？\n o2 must be a O2 instance, but we got {type(o2)} ?")
        if type(nadh) != NADH:
            raise ValueError(f"[function]MetabolismSystem.__init__: 参数 nadh 必须是 {NADH} 类型，但我们得到了 {type(nadh)} ？\n nadh must be a NADH instance, but we got {type(nadh)} ?")
        # 进行有氧呼吸
        # 1*O2 + 4*NADH -> 50*Energy + 2*H2O
        self.O2.value -= o2.value
        self.cell.resource['NADH'].value -= nadh.value
        self.H2O.value += 2*o2.value
        energy_get:Energy = self.metabolic_energy(Energy(50*o2.value))
        debug(f"细胞{self.cell.name}进行了有氧呼吸，并得到了{energy_get.value}的能量")
        self.cell.energy.value += energy_get.value

    def re_info(self):
        return {'new':self.new_cell, 'Vital_Signs':self.vital_signs}

if __name__ == "__main__":
    import random_DNA
    env1 = env.Environment()
    env1.write(0,0,Energy(114))
    cell1 = Cell(env1, 0, 0, dna=DNA(random_DNA.generate_dna(9)))
    while True:
        print(f'细胞能量转化率：{cell1.metabolic_rate}')
        MetabolismSystem(cell1, env1)
        print(cell1.energy)
        print(f'细胞当前坐标能量值：{env1.read(cell1.x, cell1.y)[env1.check_type_on_env(env1.read(cell1.x, cell1.y), Energy)]}')
        env1.resources_diffusion()
        time.sleep(1)