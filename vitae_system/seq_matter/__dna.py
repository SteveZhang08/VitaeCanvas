from vitae_system.seq_matter.Enums import E_DNA
from vitae_system.seq_matter.Seq import ESeq


class DNA(ESeq[E_DNA]):
    def __init__(self, sequence: str):
        super().__init__(E_DNA)
        self.from_string(sequence)
