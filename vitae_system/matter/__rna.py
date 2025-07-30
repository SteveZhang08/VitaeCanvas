from vitae_system.matter import Codon
from vitae_system.matter.Enums import E_RNA
from vitae_system.matter.Seq import ESeq
from typing import List


class RNA(ESeq[E_RNA]):
    def __init__(self, sequence: str):
        super().__init__(E_RNA)
        self.from_string(sequence)

    def to_codon(self) -> List[Codon]:
        """Split sequence into codons, by 3"""
        codons: List[Codon] = []
        bases: List[E_RNA] = self.to_list()
        for i in range(0, len(bases), 3):
            group: List[E_RNA] = bases[i:i + 3]
            if len(group) == 3:
                codons.append(Codon(group))
            else:
                raise ValueError("RNA sequence length must be a multiple of 3")
        return codons
