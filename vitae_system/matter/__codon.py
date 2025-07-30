from typing import List
from dataclasses import dataclass
from Enums import E_RNA

@dataclass(frozen=True)
class Codon:
    bases: List[E_RNA]

    def __post_init__(self) -> None:
        if len(self.bases) != 3:
            raise ValueError("A codon must have exactly 3 bases")

    def __str__(self) -> str:
        return ''.join(base.name for base in self.bases)

    def to_list(self) -> List[E_RNA]:
        return self.bases
