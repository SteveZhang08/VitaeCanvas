from vitae_system import *
import time

DNA = cells.DNA("TACTGTGATCGCCACCTAAGACGGAGATCGCGGAAGGTGCGACGAAAGTCTCCAAATACGAAGACATCCCGCTATGCGCGTTGCACTGCCGTATCGTTAGCCGTGCTTCACTGATACAAACTGACTTGGAATACGAAGAGTCGTAAGAAATATCGTGAAAAGTACGCCATCGGGTTCCGGCGGCCGGAATGTAGCTTTAGGGTAGAGATCATGTATGGAGGCGGCATCTTAGTTAAGGACGCTGGGGCAAATATTCGGAAGATATCTCTTAGGATTCGCGCGACAACGGCGGGAATGCAA")

class SimulationController:
    """主控模拟器，协调各系统运行"""
    def __init__(self) -> None:
        self.env = env.Environment(100, 100)
        cell_list = []
        for id in range(100):
            cell_list.append(cells.Cell(self.env, id, id, dna = DNA, name=id))
            self.env.write(id, id, env.Energy(10))
            print(self.env.read(id,id))
            time.sleep(0.02)
        print("细胞载入完成")
        for cell in cell_list:
            metabolism.MetabolismSystem(cell, self.env)
            self.env.energy_diffusion()
            print(f"细胞{cell.name}代谢完成，当前能量值：{round(cell.energy.value,2)}")
            print(f"细胞当前所在位置信息：\n坐标：{cell.name, cell.name}")
            grid_data = self.env.read(cell.name, cell.name)
            print(f'当前坐标能量值{round(grid_data[self.env.check_type_on_env(grid_data, env.Energy)].value, 2)}')
            time.sleep(0.1)

SimulationController()
