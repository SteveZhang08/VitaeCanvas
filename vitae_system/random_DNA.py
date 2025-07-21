# === VitaeCanvas ===
# ./vitae_system/random_DNA.py
# by SteveZhang08
# Helpers: None
# These AI_Models that provide help for the file:
# Kimi

import random

def generate_dna(length=30):
    """生成包含起始和终止密码子的随机DNA序列"""
    if length < 9:  # 确保有足够的长度包含起始和终止密码子
        raise ValueError("序列长度至少为9")

    # 定义DNA碱基
    bases = ['A', 'T', 'C', 'G']

    # 确保起始密码子（AUG对应的DNA是TAC）和终止密码子（如TAA、TAG、TGA对应的DNA是ATT、ATC、TCA）
    start_codon_dna = "TAC"  # 对应RNA的AUG
    stop_codons_dna = ["ATT", "ATC", "TCA"]  # 对应RNA的UAA、UAG、UGA

    # 生成随机DNA序列
    dna = [random.choice(bases) for _ in range(length)]

    # 确保起始密码子在序列开头
    for i in range(3):
        dna[i] = start_codon_dna[i]

    # 确保终止密码子在序列中间或末尾
    stop_position = random.randint(6, length - 3)  # 确保终止密码子至少在起始密码子之后
    stop_codon = random.choice(stop_codons_dna)
    for i in range(3):
        dna[stop_position + i] = stop_codon[i]

    return ''.join(dna)

if __name__ == "__main__":
    # 生成DNA序列
    dna_sequence = generate_dna(300)
    print("生成的DNA序列:", dna_sequence)