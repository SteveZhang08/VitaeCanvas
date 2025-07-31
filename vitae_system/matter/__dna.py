from vitae_system.matter.Constants import E_DNA
from vitae_system.matter.__seq import ESeq


class DNA(ESeq[E_DNA]):
    def __init__(self, sequence: str):
        super().__init__(E_DNA, sequence)
