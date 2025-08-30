# === VitaeCanvas ===
# ./vitae_system/cells.py
# by SteveZhang08
# Helpers: zyying
# These AI_Models that provide help for the file:
# Kimi    DeepSeek-R1

import re
from typing import List
import math

if __name__ == "__main__":
    # 当作为主程序直接运行时，绝对导入同级模块
    import random_DNA
    import env
    import vitae_math

else:
    # 当作为模块被导入时，相对导入库内同级模块
    from . import random_DNA
    from . import env
    from . import vitae_math

class CellError(Exception):
    """细胞活动异常"""
    def __init__(self, message:str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class DNA:
    """DNA对象，包含碱基 ATCG"""

    def __init__(self, sequence:str):
        """初始化 DNA 对象，键入碱基"""
        # 移除非法字符
        self.sequence = self._validate_sequence(sequence)

    def _validate_sequence(self, sequence):
        """验证序列是否只包含 A, T, C, G"""
        # 移除非法字符
        cleaned_sequence = re.sub(r'[^ATCG]', '', sequence.upper())
        return cleaned_sequence

    def __str__(self):
        """返回 DNA 序列的字符串表示"""
        return self.sequence

    def __repr__(self):
        """返回 DNA 对象的正式字符串表示"""
        return f"DNA('{self.sequence}')"

    def __add__(self, other):
        """重载加法操作符，允许连接两个 DNA 对象"""
        if isinstance(other, DNA):
            return DNA(self.sequence + other.sequence)
        raise TypeError("只能将 DNA 对象与另一个 DNA 对象相加")

    def __eq__(self, other):
        """定义等于操作符的行为"""
        if isinstance(other, DNA):
            return self.sequence == other.sequence
        return False

    def __len__(self):
        """返回 DNA 序列的长度"""
        return len(self.sequence)

class RNA:
    """RNA对象，包含碱基 AUCG"""

    def __init__(self, sequence):
        """初始化 RNA 对象，键入碱基"""
        # 移除非法字符
        self.sequence = self._validate_sequence(sequence)
        self.split = self._split(self.sequence)

    def _validate_sequence(self, sequence):
        """验证序列是否只包含 A, U, C, G"""
        # 移除非法字符
        cleaned_sequence = re.sub(r'[^AUCG]', '', sequence.upper())
        return cleaned_sequence

    def __str__(self):
        """返回 RNA 序列的字符串表示"""
        return self.sequence

    def __repr__(self):
        """返回 RNA 对象的正式字符串表示"""
        return f"RNA('{self.sequence}')"

    def __add__(self, other):
        """重载加法操作符，允许连接两个 RNA 对象"""
        if isinstance(other, RNA):
            return RNA(self.sequence + other.sequence)
        raise TypeError("只能将 RNA 对象与另一个 RNA 对象相加")

    def __eq__(self, other):
        """定义等于操作符的行为"""
        if isinstance(other, RNA):
            return self.sequence == other.sequence
        return False

    def __len__(self):
        """返回 RNA 序列的长度"""
        return len(self.sequence)

    def _split(self, sequence) -> str:
        """返回拆分后的 RNA"""
        rna = ""
        for i in range(0, len(sequence), 3):
            codon = sequence[i:i+3]
            rna += (codon + "-")
        return rna[:-1]

class Protein:
    """蛋白质"""
    def __init__(self, sequence:str):
        """初始化蛋白质对象，确保序列只包含合法氨基酸"""
        if sequence == "":
            raise CellError('Protein error: The protein is "None"' + "\n蛋白质错误:蛋白质为空")
        self.sequence = self._validate_sequence(sequence)
        self.metabolic = self._metabolic(self.sequence)
        self.function_dict = self.function()

    def _validate_sequence(self, sequence):
        """验证序列是否只包含合法氨基酸"""
        # 合法氨基酸单字母缩写
        valid_amino_acids = set("ARNDCEQGHILKMFPSTWYV")
        # 移除非法字符并转换为大写
        cleaned_sequence = ''.join([aa.upper() for aa in sequence if aa.upper() in valid_amino_acids])
        if cleaned_sequence != sequence.upper():
            env.warning(f"警告：输入序列包含非法氨基酸，已移除非法字符。原始序列：{sequence}")
        return cleaned_sequence

    def __str__(self):
        """返回蛋白质序列的字符串表示"""
        return self.sequence

    def __repr__(self):
        """返回蛋白质对象的正式字符串表示"""
        return f"Protein('{self.sequence}')"

    def __add__(self, other):
        """重载加法操作符，允许连接两个蛋白质对象"""
        if isinstance(other, Protein):
            return Protein(self.sequence + other.sequence)
        raise TypeError("只能将 Protein 对象与另一个 Protein 对象相加")

    def __eq__(self, other):
        """定义等于操作符的行为"""
        if isinstance(other, Protein):
            return self.sequence == other.sequence
        return False

    def __len__(self):
        """返回蛋白质序列的长度"""
        return len(self.sequence)

    def _metabolic(self, sequence):
        """
        代谢率 = (加成氨基酸数 - 抑制氨基酸数) / 总氨基酸数
        加成氨基酸：L,I,V,Q,A,R,S,D
        抑制氨基酸：W,G,H,P,M
        """

        a = 0
        add = ["L","I","V","Q","A","R","S","D"]
        sub = ["W","G","H","P","M"]
        for i in add:
            a += sequence.count(i)
        for i in sub:
            a -= sequence.count(i)
        metabolic = max(min(a/len(sequence), Cell.MAX_METABOLIC),Cell.MIN_METABOLIC)    #保证能量转化率在规定范围内
        return metabolic

    def function(self) -> dict:
        """
        蛋白质功能
        """
        sequence = self.sequence
        result = {}
        patterns = dict(
            sorted(
                {
                    "GACLICYWSCCMN": (self.antioxidant,"antioxidant"),  # 抗氧化蛋白
                    "CYSTMTR": (self.membrane_transoprt,"membrane_transoprt"), # 膜运输蛋白
                    "ACTIN": (self.cytoskeleton,"cytoskeleton"),         # 细胞骨架蛋白
                    "SKNQK": (self.variation,"variation"),            # 调控变异蛋白
                    "GASL": (self.variation,"variation"),             # 调控变异蛋白
                    "MAFLVRPYICGS": (self.aerobic_respiration_enzymes,"aerobic_respiration_enzymes"),   # 有氧呼吸酶
                    "VVV": (self.env_receptor,"env_receptor"),                  # 环境受体蛋白
                    "VYE":(self.move,"move"),                            # 移动蛋白
                }.items(),
                key=lambda item: len(item[0]),  # 按key的长度排序
                reverse=True  # 倒序（长键在前）
            )
        )
        while sequence:
            unmatched = True
            for key, value in patterns.items():
                if sequence.startswith(key):
                    unmatched = False
                    result[value[1]] = value[0]
                    sequence = sequence[len(key):]
                    break
            if unmatched:
                sequence = sequence[1:]
        return result

    @staticmethod
    def antioxidant(cell:'Cell'):
        """
        抗氧化能力
        """
        cell.efficiency_increase += 0.1  # 细胞转化效率增加    

    @staticmethod
    def variation(cell:'Cell'):
        """
        变异能力
        """
        cell.variation_rate += 0.1  # 细胞变异概率增加    

    @staticmethod
    def membrane_transoprt(cell:'Cell'):
        """
        膜运输能力
        """
        cell.material_exchange_energy = max(cell.material_exchange_energy * 0.8, 2.5) # 细胞物质交换耗能减少

    @staticmethod
    def cytoskeleton(cell:'Cell'):
        """
        细胞骨架调控能力
        """
        cell.material_exchange_energy = max(cell.material_exchange_energy * 1.2, 2.5) # 细胞物质交换耗能增加
        cell.strong += 1

    @staticmethod
    def aerobic_respiration_enzymes(cell:'Cell'):
        """
        有氧呼吸酶增益
        """
        cell.aerobic_respiration_enzymes += 0.1  # 细胞有氧呼吸酶增益增加

    @staticmethod
    def env_receptor(cell: 'Cell',call = False):
        """
        环境受体蛋白增益
        自动扫描四个方向的环境能量值，并更新细胞状态
        """
        if not call:
            return

        for direction, (dx, dy), key in [
            ('up', (0, -1), 'env_energy_up'),
            ('down', (0, 1), 'env_energy_down'),
            ('left', (-1, 0), 'env_energy_left'),
            ('right', (1, 0), 'env_energy_right')]:
            try:
                # 直接读取并解包有效结果
                env.debug(f"细胞{cell.name}的{direction}方向环境坐标为({cell.x + dx},{cell.y + dy})")
                if grid_content := cell.env.read(cell.x + dx, cell.y + dy):
                    env.debug(f"数据为{grid_content}")
                    idx = cell.env.check_type_on_env(grid_content, env.Energy)
                    if idx != None:
                        cell.info[key] = grid_content[idx].value
                        env.debug(f"细胞{cell.name}的{direction}方向环境能量值为{cell.info[key]}")
            except Exception as e:
                env.warning(f"方向 {direction} 读取失败: {e}")

    @staticmethod
    def move(cell:'Cell',call=False):
        """
        移动能力
        """
        if not call:
            return

        up = down = left = right = 0
        up_weight = down_weight = left_weight = right_weight = 0

        if num := cell.info.get('env_energy_up'):
            up_weight = vitae_math.vac_curve(num)
        if num := cell.info.get('env_energy_down'):
            down_weight = vitae_math.vac_curve(num)
        if num := cell.info.get('env_energy_left'):
            left_weight = vitae_math.vac_curve(num)
        if num := cell.info.get('env_energy_right'):
            right_weight = vitae_math.vac_curve(num)
        
        up = up_weight * 1j
        down = down_weight * 1j
        left = left_weight * -1
        right = right_weight * 1

        direction_vector:complex = up + down + left + right
        if direction_vector == 0:
            env.debug(f"细胞{cell.name}不打算移动")
            return
        direction = math.degrees(math.atan2(direction_vector.imag, direction_vector.real))

        if direction > -45 and direction <= 45:
            env.debug(f"细胞{cell.name}打算移动到({cell.x + 1},{cell.y})")
            cell.move(cell.x + 1,cell.y)
        elif direction > 45 and direction <= 135:
            env.debug(f"细胞{cell.name}打算移动到({cell.x},{cell.y + 1})")
            cell.move(cell.x,cell.y + 1)
        elif direction > 135 or direction <= -135:
            env.debug(f"细胞{cell.name}打算移动到({cell.x - 1},{cell.y})")
            cell.move(cell.x - 1,cell.y)
        elif direction > -135 and direction <= -45:
            env.debug(f"细胞{cell.name}打算移动到({cell.x},{cell.y - 1})")
            cell.move(cell.x,cell.y - 1)

class NADH(env.Energy):
    def __init__(self, value, diffuse=False):
        super().__init__(value, diffuse)
        self.name = "NADH"

class Sugar:
    def __init__(self, C:int=6, H:int=12, O:int=6) -> None:
        """
        糖的分子式
        :param C: 糖的碳原子数量
        :param H: 糖的氢原子数量
        :param O: 糖的氧原子数量
        """
        self.C = C
        self.H = H
        self.O = O

    def __str__(self):
        """返回 Sugar 的字符串表示"""
        return f"C{self.C}H{self.H}O{self.O}"

    def __repr__(self) -> str:
        return f"Sugar(C={self.C}, H={self.H}, O={self.O})"

    def Hydrolysis(self) -> dict:
        """
        糖的水解
        return: 糖的水解产物构成的字典，键为产物名称，值为产物数量
        """
        energy_value = (self.C * 12 + self.H + self.O * 16) / 6
        NADH_value = (self.C * 12 + self.H + self.O * 16) / 18
        env.debug(f"糖{str(self)}的水解产生了{energy_value}的能量和{NADH_value}个NADH")
        return {'energy':env.Energy(energy_value), 'NADH':NADH(NADH_value)}

class SugarList(list):
    pass

class Cell:
    """细胞实体类，包含遗传信息与代谢属性"""

    MAX_GENE_LENGTH = 300 # DNA的最大有效长度
    MAX_METABOLIC = 0.8  # 最大能量转化率
    MIN_METABOLIC = 0.1  # 最小能量转化率

    def __init__(self, env1:env.Environment,x:int, y:int, dna:DNA = DNA("ATCG"), name = None) -> None:
        """
        初始化细胞实例
        :param x: X坐标
        :param y: Y坐标
        :param dna: 基因序列（自动截取有效长度并用T补足）
        """
        self.name = name
        self.energy = env.Energy(200.0,diffuse=False)
        self.age = 0
        self.x = x
        self.y = y
        self.dna = self.normalize_dna(dna)
        self.rna = self.DNA_translate(dna)
        self.protein_list:List[Protein] = self.ribosome(self.rna)        
        self.info = {}
        self.env = env1
        self.color = self._color()
        self.strong = 5     # 细胞结构强度
        self.metabolic_init()
        # 细胞初始化完成
        self.env.write(self.x, self.y, self)           # 移动细胞到初始位置

    def metabolic_init(self):
        """
        细胞代谢初始化：在代谢时被调用进行初始化
        """
        self.metabolic_rate = self._metabolic(self.protein_list)    # 细胞能量转化率
        self.efficiency_increase = 0.0    # 转化效率增幅
        self.variation_rate = 0.1    # 变异概率
        self.material_exchange_energy = 5   # 物质交换耗能
        self.aerobic_respiration_enzymes = 0.0   # 有氧呼吸酶增益
        self.abosrbed_substances = [Sugar, env.O2]           # 细胞允许吸收的物质列表
        self.resource = {'NADH':NADH(10)}
        self.function(self.protein_list)

    def __str__(self) -> str:
        return f"{r'{'}Cell' s Name: {self.name}, Age: {self.age}{r'}'}"

    def __repr__(self) -> str:
        return f"{r'{'}Cell' s Name: {self.name}, Age: {self.age}, Energy: {self.energy}{r'}'}"


    def normalize_dna(self, dna:DNA) -> DNA:
        """标准化DNA序列"""
        # 用T补足长度并截取有效长度
        if not isinstance(dna, DNA):    # 检查传入的是否是 DNA
            raise CellError(f"Provided DNA is invalid. Supplied DNA type is {type(dna)}, expected type is DNA. \n传入的DNA不合法，传入的DNA类型为{type(dna)}，期待类型为 DNA")
        effective_dna = str((dna + DNA('T' * self.MAX_GENE_LENGTH)))[:self.MAX_GENE_LENGTH]
        return DNA(effective_dna.upper())

    def DNA_translate(self, dna:DNA) -> RNA:
        """转录 DNA 为 RNA"""
        translation_table = str.maketrans({
            "A": "U", 
            "T": "A", 
            "C": "G", 
            "G": "C"
            })
        return RNA(str(dna).translate(translation_table))

    def ribosome(self, rna:RNA) -> list:
        """翻译密码子"""
        # 密码子对照表由 DeepSeek-R1 生成
        codon_table = {
        "UUU": "F", "UUC": "F",
        "UUA": "L", "UUG": "L", "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L",
        "AUU": "I", "AUC": "I", "AUA": "I",
        "AUG": "M",
        "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V",
        "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S", "AGU": "S", "AGC": "S",
        "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
        "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T",
        "GCU": "A", "GCC": "A", "GCA": "A", "GCG": "A",
        "UAU": "Y", "UAC": "Y",
        "UAA": "*", "UAG": "*", "UGA": "*",         #终止密码子
        "CAU": "H", "CAC": "H",
        "CAA": "Q", "CAG": "Q",
        "AAU": "N", "AAC": "N",
        "AAA": "K", "AAG": "K",
        "GAU": "D", "GAC": "D",
        "GAA": "E", "GAG": "E",
        "UGU": "C", "UGC": "C",
        "UGG": "W",
        "CGU": "R", "CGC": "R", "CGA": "R", "CGG": "R", "AGA": "R", "AGG": "R",
        "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G"
        }
        start_codon_index = str(rna).find("AUG")     #寻找起始密码子的位置
        if start_codon_index == -1:
            return []  # 没有找到起始密码子，返回空列表
        protein_list = []   # 蛋白质列表
        protein = ""
        a = start_codon_index
        # 翻译思路由 Kimi 提供
        while (a + 3) <= len(rna):
            for i in range(a, len(rna), 3):
                codon = str(rna)[i:i+3]
                if len(codon) == 3:
                    amino_acid = codon_table.get(codon, "*")
                    if amino_acid == "*":
                        break               # 遇到终止密码子停止翻译
                    protein += amino_acid
            try:
                protein_list.append(Protein(protein))
            except:
                pass
            protein = ""
            a = i + 3
        return protein_list     # 返回合成的蛋白质（列表）

    def _metabolic(self, protein_list:list) -> float:
        """细胞能量转化率计算"""
        metabolic = 0
        for i in protein_list:
            metabolic += i.metabolic
        return round(metabolic/len(protein_list), 2)

    def function(self, protein_list:List[Protein]):
        """根据细胞内的蛋白质执行操作"""
        for protein in protein_list:
            for protein_function in protein.function_dict.values():
                protein_function(self)

    def move(self, x: int, y: int):
        """移动细胞至指定坐标"""
        if not (0 <= x < self.env.width and 0 <= y < self.env.height):
            env.debug(f"Cell {self.name} tried to move out of bounds.\n细胞 {self.name} 试图冲击边界")
            self.strong -= 1
            return False
        grid_data = self.env.read(x, y)
        idx = self.env.check_type_on_env(grid_data, Cell)
        if idx != None: # 如果新网格中存在细胞
            self.strong -= 1
            other_cell:Cell = grid_data[idx]
            other_cell.strong -= 1
            env.debug(f"细胞 {self.name} 与 {other_cell.name} 发生碰撞，Cell.strong 均失去 1 点")
            return False
        self.env.remove_type(self.x, self.y, Cell)
        self.x = x
        self.y = y
        self.env.write(x, y, self)
        return True

    def _color(self):
        """计算细胞RGB颜色"""
        sequence = ""
        # 统计细胞内所有氨基酸
        for i in self.protein_list:
            sequence += str(i)
        return self.calculate_rgb(sequence)

    def calculate_rgb(self, sequence):
        """根据氨基酸序列计算RGB值（包含所有20种氨基酸）"""
        # 此处代码由 DeepSeek-R1 生成
        # 定义氨基酸对RGB通道的影响权重
        r_weights = {"W": 1.0, "Y": 0.8, "F": 0.6, "Q": 0.3, "N": 0.25, "S": 0.4, "T": 0.2, "C": 0.15}
        g_weights = {"L": 1.0, "I": 0.8, "V": 0.6, "M": 0.5, "A": 0.4, "P": 0.3, "G": 0.2}
        b_weights = {"R": 1.0, "K": 0.8, "H": 0.6, "D": 0.4, "E": 0.2}

        # 统计氨基酸数目
        counts = {}
        for aa in sequence:
            counts[aa] = counts.get(aa, 0) + 1

        # 计算RGB值
        r = sum(counts.get(aa, 0) * weight for aa, weight in r_weights.items())
        g = sum(counts.get(aa, 0) * weight for aa, weight in g_weights.items())
        b = sum(counts.get(aa, 0) * weight for aa, weight in b_weights.items())

        # 归一化到0-255
        max_value = max(r, g, b)
        if max_value > 0:
            r = int((r / max_value) * 255)
            g = int((g / max_value) * 255)
            b = int((b / max_value) * 255)
        else:
            r, g, b = 0, 0, 0

        return (r, g, b)

if __name__ == "__main__":
    env1 = env.Environment()
    env1.write(0,1,env.Energy(200))
    cell1 = Cell(env1, 0, 0, dna=DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT"))
    print(cell1.protein_list)
    print(f"细胞{cell1.name}的能量转化率为{cell1.metabolic_rate}")
    print(env1.read(0, 1))
    print(f"细胞{cell1.name}的颜色RGB为{cell1.color}")
    print(f"细胞{cell1.name}的转化率增幅{cell1.efficiency_increase}")