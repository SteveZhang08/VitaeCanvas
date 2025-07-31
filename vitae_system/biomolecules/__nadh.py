from vitae_system.biomolecules import Energy
from dataclasses import dataclass


@dataclass
class NADH(Energy):
    value: float = 1.0

    super().__init__(value, diffuse=False)
