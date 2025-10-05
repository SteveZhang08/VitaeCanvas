import unittest
from vitae_system.protein import structure

class TestChouFasmanPrediction(unittest.TestCase):   
    def test_all_alanine(self):
        """测试全丙氨酸序列（预计为螺旋）"""
        sequence = "AAAA"
        result = structure(sequence)
        expected = [['AAAA', 'helix']]
        self.assertEqual(result, expected)    
    def test_all_valine(self):
        """测试全缬氨酸序列（预计为折叠）"""
        sequence = "VVVV"
        result = structure(sequence)
        expected = [['VVVV', 'sheet']]
        self.assertEqual(result, expected)    
    def test_all_glutamic_acid(self):
        """测试全谷氨酸序列（预计为螺旋）"""
        sequence = "EEEE"
        result = structure(sequence)
        expected = [['EEEE', 'helix']]
        self.assertEqual(result, expected)    
    def test_all_tyrosine(self):
        """测试全酪氨酸序列（预计为折叠）"""
        sequence = "YYYY"
        result = structure(sequence)
        expected = [['YYYY', 'sheet']]
        self.assertEqual(result, expected)   
    def test_all_proline(self):
        """测试全脯氨酸序列（预计为无结构）"""
        sequence = "PPPP"
        result = structure(sequence)
        expected = [['PPPP', 'none']]
        self.assertEqual(result, expected)    
    def test_mixed_sequence(self):
        """测试混合序列（来自您的示例）"""
        sequence = "GACLICYWSCCMNEEEFG"
        result = structure(sequence)
        expected = [
            ['GACL', 'sheet'],
            ['ICYW', 'sheet'],
            ['SCCM', 'sheet'],
            ['NEEE', 'helix'],
            ['FG', 'none']
        ]
        self.assertEqual(result, expected)    
    def test_unstructured_sequence(self):
        """测试无结构序列（甘氨酸和脯氨酸混合）"""
        sequence = "GPGP"
        result = structure(sequence)
        expected = [['GPGP', 'none']]
        self.assertEqual(result, expected)    
    def test_boundary_case(self):
        """测试边界情况序列（长度不是4的倍数）"""
        sequence = "AAA"
        result = structure(sequence)
        expected = [['AAA', 'none']]
        self.assertEqual(result, expected)    
    def test_conflict_pa_higher(self):
        """测试冲突序列（Pa和Pb都高，但Pa更高）"""
        sequence = "AACC"
        result = structure(sequence)
        expected = [['AACC', 'helix']]
        self.assertEqual(result, expected)
    
    def test_conflict_pb_higher(self):
        """测试冲突序列（Pa和Pb都高，但Pb更高）"""
        sequence = "LLVV"
        result = structure(sequence)
        expected = [['LLVV', 'sheet']]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
