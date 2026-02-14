# === VitaeCanvas ===
# ./vitae_system/protein.py
# by SteveZhang08
# Helpers: none
# Chou-Fasman蛋白质二级结构预测实现
# 基于1974年Chou和Fasman提出的算法，使用滑动窗口检测α-螺旋和β-折叠
# 参考: Chou and Fasman, Biochemistry 13:211-222 (1974)

from . import *

chou_fasman = {
    'A': {'Pa': 1.42, 'Pb': 0.83, 'Pt': 0.66},
    'R': {'Pa': 0.98, 'Pb': 0.93, 'Pt': 0.95},
    'N': {'Pa': 0.67, 'Pb': 0.89, 'Pt': 1.56},
    'D': {'Pa': 1.01, 'Pb': 0.54, 'Pt': 1.46},
    'C': {'Pa': 0.70, 'Pb': 1.19, 'Pt': 1.19},
    'Q': {'Pa': 1.11, 'Pb': 1.10, 'Pt': 0.98},
    'E': {'Pa': 1.51, 'Pb': 0.37, 'Pt': 1.56},
    'G': {'Pa': 0.57, 'Pb': 0.75, 'Pt': 1.56},
    'H': {'Pa': 1.00, 'Pb': 0.87, 'Pt': 0.95},
    'I': {'Pa': 1.08, 'Pb': 1.60, 'Pt': 0.47},
    'L': {'Pa': 1.21, 'Pb': 1.30, 'Pt': 0.59},
    'K': {'Pa': 1.16, 'Pb': 0.74, 'Pt': 1.01},
    'M': {'Pa': 1.45, 'Pb': 1.05, 'Pt': 0.60},
    'F': {'Pa': 1.13, 'Pb': 1.38, 'Pt': 0.60},
    'P': {'Pa': 0.57, 'Pb': 0.55, 'Pt': 1.52},
    'S': {'Pa': 0.77, 'Pb': 0.75, 'Pt': 1.43},
    'T': {'Pa': 0.83, 'Pb': 1.19, 'Pt': 0.96},
    'W': {'Pa': 1.08, 'Pb': 1.37, 'Pt': 0.96},
    'Y': {'Pa': 0.69, 'Pb': 1.47, 'Pt': 1.14},
    'V': {'Pa': 1.06, 'Pb': 1.70, 'Pt': 0.50}
}

sheet_function = {
    'IVFA': env.O2,
    'TTSC': env.H2O,
    'YVTT': None,
    'RTTR': cells.DNA
    

}

class Protein:
    """蛋白质对象，包含氨基酸序列"""
    def __init__(self, sequence:str) -> None:
        """初始化蛋白质对象，键入氨基酸序列"""
        self.sequence = sequence.upper()    # 转换为大写字母
        self.structure = self.structure()   # 预测蛋白质结构
        self.direction = 0 # 蛋白质朝向
        self.on_membrane = False # 是否在膜上
        self.functional() # 预测蛋白质功能

    def __len__(self):
        """返回蛋白质序列的长度"""
        return len(self.sequence)

    def structure(self):
        """根据蛋白质序列预测蛋白质结构
        
        使用Chou-Fasman方法预测蛋白质二级结构，基于氨基酸构象倾向性参数
        算法原理：使用4氨基酸滑动窗口，计算Pa/Pb平均值(阈值1.0)
        最小结构长度：4个氨基酸
        
        :param protein: 蛋白质序列字符串，大写字母表示氨基酸
        :return: 二级结构预测结果列表，每个元素为[序列片段, 结构类型]
                 结构类型: 'helix'(α-螺旋), 'sheet'(β-折叠), 'none'(无规卷曲)
        
        示例:
        >>> structure("AAAA")
        [['AAAA', 'helix']]
        >>> structure("VVVV")
        [['VVVV', 'sheet']]
        >>> structure("GACLICYWSCCMNEEEFG")
        [['GACL', 'sheet'], ['ICYW', 'sheet'], ['SCCM', 'sheet'], ['NEEE', 'helix'], ['FG', 'none']]
        """
        structure = []     # 待返回的结构数据
        i = 0              # 循环变量
        none_sequence = []  # 无结构序列暂存器

        while i < len(self.sequence):
            count_protein = list(self.sequence[i:4+i])    # 按四个氨基酸切片
            count_a = []                            # 清零倾向性分数
            count_b = []
            calc = (len(count_protein) == 4)         # 判断是否为四个氨基酸，短片段默认标记为无结构(符合最小长度要求)
            # 统计倾向性分数
            if calc:
                for sequence in count_protein:
                    count_a.append(chou_fasman[sequence]['Pa'])
            else:
                count_a = [0]
            if calc:
                for sequence in count_protein:
                    count_b.append(chou_fasman[sequence]['Pb'])
            else:
                count_b = [0]
            # 判断结构类型
            if sum(count_a) > 4 and sum(count_b) < sum(count_a):    # 平均值>1.0且螺旋倾向更强
                # 如果存在无结构序列则先标记无结构序列
                if none_sequence != []:
                    structure.append(["".join(none_sequence), 'none'])
                    none_sequence = []
                structure.append(["".join(count_protein), 'helix']) # 满足 helix 条件，标记该序列
                i += 4
            elif sum(count_b) > 4 and sum(count_b) > sum(count_a):
                # 如果存在无结构序列则先标记无结构序列
                if none_sequence != []:
                    structure.append(["".join(none_sequence), 'none'])
                    none_sequence = []
                structure.append(["".join(count_protein), 'sheet']) # 满足 sheet 条件，标记该序列
                i += 4
            else:
                # 不满足任何条件，将当前第一个氨基酸加入无结构序列暂存器，滑动窗口位移一位
                none_sequence.append(count_protein[0])
                i += 1
    
            if none_sequence != []:
                structure.append(["".join(none_sequence), 'none'])
    
        return structure

    def functional(self):
        """根据蛋白质结构预测蛋白质功能"""
        functional = {}
        head ,end = self.structure[0][1], self.structure[-1][1]
        if (head ,end) == ('none', 'none'):
            # 如果是膜上蛋白
            self.on_membrane = True
            for structure in self.structure:
                if structure[1] == 'sheet':
                    functional.append(structure[0])

        # [['GACL', 'sheet'], ['ICYW', 'sheet'], ['SCCM', 'sheet'], ['NEEE', 'helix'], ['FG', 'none']]