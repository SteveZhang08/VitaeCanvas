from Constants import E_Protein, A_ADD_AMINO_ACIDS, A_INHIBIT_AMINO_ACIDS, E_ProteinFunc, A_PROTEIN_FUNC_RULES, \
    I_MAX_GENE_LENGTH, F_MAX_METABOLIC, F_MIN_METABOLIC
from __seq import BioSeq, E
from __matcher import ProteinFunctionMatcher

from typing import Optional, List, Tuple


class Protein(BioSeq[E_Protein]):
    def __init__(self, sequence: str | List[E]) -> None:
        super().__init__(E_Protein, sequence)

    def __calc_metabolic(self) -> Optional[float]:
        """
        Metabolic Rate = (Num of Promoting AA − Num of Inhibitory AA) / Num of AA
        Promoting Amino Acids: L, I, V, Q, A, R, S, D
        Inhibitory Amino Acids: W, G, H, P, M

        Returns -1 if no sequence provided
        """
        if not self.sequence:
            return None

        total: int = len(self.sequence)
        add_count: int = sum(1 for aa in self.sequence if aa in A_ADD_AMINO_ACIDS)
        inhibit_count: int = sum(1 for aa in self.sequence if aa in A_INHIBIT_AMINO_ACIDS)

        raw_rate: float = (add_count - inhibit_count) / total
        rate: float = min(max(raw_rate, F_MIN_METABOLIC), F_MAX_METABOLIC)
        return rate

    def __rec_functions(self) -> Tuple[E_ProteinFunc, ...]:
        """
        Recognize functions of protein
        """
        matcher: ProteinFunctionMatcher = ProteinFunctionMatcher(A_PROTEIN_FUNC_RULES)
        return matcher.match(self.sequence)

    @property
    def metabolic(self) -> float:
        return self.__calc_metabolic()

    @property
    def functions(self) -> Tuple[E_ProteinFunc, ...]:
        return self.__rec_functions()
