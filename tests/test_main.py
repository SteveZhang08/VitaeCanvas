"""
VitaeCanvas 系统集成测试
测试环境初始化、细胞创建和代谢系统功能
"""
import unittest
from vitae_system import cells, env, metabolism
import time

# 使用项目中的DNA序列
DNA = cells.DNA("TACTGTGATCGCCACCTAAGACGGAGATCGCGGAAGGTGCGACGAAAGTCTCCAAATACGAAGACATCCCGCTATGCGCGTTGCACTGCCGTATCGTTAGCCGTGCTTCACTGATACAAACTGACTTGGAATACGAAGAGTCGTAAGAAATATCGTGAAAAGTACGCCATCGGGTTCCGGCGGCCGGAATGTAGCTTTAGGGTAGAGATCATGTATGGAGGCGGCATCTTAGTTAAGGACGCTGGGGCAAATATTCGGAAGATATCTCTTAGGATTCGCGCGACAACGGCGGGAATGCAA")

class SimulationTestCase(unittest.TestCase):
    """模拟系统集成测试"""

    def setUp(self):
        """创建测试环境"""
        self.env = env.Environment(100, 100)
        self.cell_list = []
        
        # 创建100个测试细胞
        for cell_id in range(100):
            new_cell = cells.Cell(self.env, cell_id, cell_id, dna=DNA, name=f"cell_{cell_id}")
            self.cell_list.append(new_cell)
            self.env.write(cell_id, cell_id, env.Energy(10))

    def test_environment_initialization(self):
        """测试环境初始化"""
        # 验证环境尺寸
        self.assertEqual(self.env.width, 101, "环境宽度应为100")
        self.assertEqual(self.env.height, 101, "环境高度应为100")


    def test_cell_creation(self):
        """测试细胞创建"""
        self.assertEqual(len(self.cell_list), 100, "应创建100个细胞")
        
        # 验证DNA序列匹配
        for cell in self.cell_list:
            self.assertEqual(cell.dna.sequence, DNA.sequence, "细胞DNA序列应匹配")
    
    def test_metabolism_system(self):
        """测试代谢系统"""
        for cell in self.cell_list:
            # 应用代谢系统
            metabolism.MetabolismSystem(cell, self.env)
            
            # 能量扩散
            self.env.energy_diffusion()
            
            # 验证能量变化
            initial_energy = cell.energy.value
            # 应用代谢系统
            metabolism.MetabolismSystem(cell, self.env)       
            # 能量扩散
            self.env.energy_diffusion()
            new_energy = cell.energy.value
            self.assertNotEqual(initial_energy, new_energy, "代谢后细胞能量应变化")
            
            # 验证环境能量更新
            grid_data = self.env.read(cell.x, cell.y)
            self.assertIsInstance(grid_data, list, "网格数据应为 list 类型")
            self.assertAlmostEqual(grid_data.value, cell.energy.value, delta=1.0, 
                                msg="细胞能量与环境能量应接近")

    @unittest.skip("仅用于手动调试")
    def test_full_simulation_with_logging(self):
        """完整的模拟流程测试(带日志输出)"""
        print("细胞载入完成")
        for cell in self.cell_list:
            metabolism.MetabolismSystem(cell, self.env)
            self.env.energy_diffusion()
            print(f"细胞{cell.name}代谢完成，当前能量值：{round(cell.energy.value,2)}")
            print(f"细胞当前所在位置信息：\n坐标：({cell.x}, {cell.y})")
            grid_data = self.env.read(cell.x, cell.y)
            print(f'当前坐标能量值{round(grid_data.value, 2)}')
            time.sleep(0.01)  # 小幅延时便于观察

if __name__ == '__main__':
    unittest.main()