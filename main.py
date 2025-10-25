from vitae_system import *
import time

DNA = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")

class SimulationController:
    """主控模拟器，协调各系统运行"""
    def __init__(self) -> None:
        self.env = env.Environment(-1, -1)
        cell_list = []
        cell_list.append(cells.Cell(self.env, 0, 0, dna = DNA, name="Vita"))
        resource_list = [env.Energy(100), env.O2(200), env.H2O(200), cells.SugarList([cells.Sugar(6,12,6)])]
        for resource in resource_list:
            self.env.write(0, 0, resource)
        self.env.write(0,1,env.Energy(200))
        for i in self.env.read(0,0):
            print(i)
        print("细胞载入完成")
        print(f"共{len(cell_list)}个细胞")
        while True:
            for cell in cell_list:
                new_cell = metabolism.MetabolismSystem(cell, self.env).re_info()
                if new_cell != None:
                    cell_list.append(new_cell)
                self.env.resources_diffusion()
                print(f"细胞{cell.name}代谢完成，当前能量值：{round(cell.energy.value,2)}")
                print(f"细胞当前所在位置信息：\n坐标：{cell.x, cell.y}")
                grid_data = self.env.read(cell.x, cell.y)
                #print(f'当前坐标能量值{round(grid_data[self.env.check_type_on_env(grid_data, env.Energy)].value, 2)}')
            time.sleep(0.1)

SimulationController()
