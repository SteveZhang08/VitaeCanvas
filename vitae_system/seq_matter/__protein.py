from vitae_system.seq_matter.Enums import E_Protein, ADD_AMINO_ACIDS, INHIBIT_AMINO_ACIDS
from vitae_system.seq_matter.Seq import ESeq
from typing import Optional

MAX_GENE_LENGTH: int = 300  # DNA的最大有效长度
MAX_METABOLIC: float = 0.8  # 最大能量转化率
MIN_METABOLIC: float = 0.1  # 最小能量转化率


class Protein(ESeq[E_Protein]):
    def __init__(self, sequence: str) -> None:
        super().__init__(E_Protein)
        self.from_string(sequence)

    def calc_metabolic(self) -> Optional[float]:
        """
        Metabolic Rate = (Num of Promoting AA − Num of Inhibitory AA) / Num of AA
        Promoting Amino Acids: L, I, V, Q, A, R, S, D
        Inhibitory Amino Acids: W, G, H, P, M

        Returns -1 if no sequence provided
        """
        if not self.__seq:
            return None

        total: int = len(self.__seq)
        add_count: int = sum(1 for aa in self.__seq if aa in ADD_AMINO_ACIDS)
        inhibit_count: int = sum(1 for aa in self.__seq if aa in INHIBIT_AMINO_ACIDS)

        raw_rate: float = (add_count - inhibit_count) / total
        rate: float = min(max(raw_rate, MIN_METABOLIC), MAX_METABOLIC)
        return rate
