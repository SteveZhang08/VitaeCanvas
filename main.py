from vitae_system import *
import time

DNA = cells.DNA("TACTGTGATCGCCACCTAAGACGGAGATCGCGGAAGGTGCGACGAAAGTCTCCAAATACGAAGACATCCCGCTATGCGCGTTGCACTGCCGTATCGTTAGCCGTGCTTCACTGATACAAACTGACTTGGAATACGAAGAGTCGTAAGAAATATCGTGAAAAGTACGCCATCGGGTTCCGGCGGCCGGAATGTAGCTTTAGGGTAGAGATCATGTATGGAGGCGGCATCTTAGTTAAGGACGCTGGGGCAAATATTCGGAAGATATCTCTTAGGATTCGCGCGACAACGGCGGGAATGCAA")

class SimulationController:
    """主控模拟器，协调各系统运行"""
    def __init__(self) -> None:
        self.env = env.Environment(100, 100)
        cell_list = []
        cell_list.append(cells.Cell(self.env, 0, 0, dna = DNA, name=0))
        resource_list = [env.Energy(10), env.O2(10), env.H2O(10), cells.Sugar(6,12,6)]
        for resource in resource_list:
            self.env.write(0, 0, resource)
        print(self.env.read(0,0))
        print("细胞载入完成")
        for cell in cell_list:
            metabolism.MetabolismSystem(cell, self.env)
            self.env.resources_diffusion()
            print(f"细胞{cell.name}代谢完成，当前能量值：{round(cell.energy.value,2)}")
            print(f"细胞当前所在位置信息：\n坐标：{cell.name, cell.name}")
            grid_data = self.env.read(cell.name, cell.name)
            print(f'当前坐标能量值{round(grid_data[self.env.check_type_on_env(grid_data, env.Energy)].value, 2)}')
            time.sleep(0.1)

SimulationController()
