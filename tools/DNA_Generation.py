# === VitaeCanvas ===
# ./tools/DNA_Generation.py
# by SteveZhang08
# Helpers: None
# These AI_Models that provide help for the file:
# DeepSeek-R1

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
reverse_codon_table = {v: k for k, v in codon_table.items()}    # 反向密码子表
translation_table = str.maketrans(
    {"U": "A", 
     "A": "T", 
     "C": "G", 
     "G": "C"})
def re_translate(protein_sequence:list):
    rna = ""
    amino_acid_sequence = "M"
    for idx, protein in enumerate(protein_sequence):
        amino_acid_sequence += str(protein)
        amino_acid_sequence += "*"
        idx1 = idx
        for idx2, amino_acid in enumerate(protein):
            if not amino_acid in reverse_codon_table:
                return {'rna':f"The illegal amino acid “{amino_acid}” is at the {idx2 + 1} character of item {idx1 + 1}",
                        'dna':f"The illegal amino acid “{amino_acid}” is at the {idx2 + 1} character of item {idx1 + 1}"}
    for amino_acid1 in amino_acid_sequence:
        rna += reverse_codon_table[amino_acid1]
    dna = rna.translate(translation_table)
    return {'rna':rna, 'dna':dna}

if __name__ == "__main__":
    input_list = input("Please enter the list of proteins, separated by ',' >>>").replace(" ", "").split(',')
    print(re_translate(input_list))
