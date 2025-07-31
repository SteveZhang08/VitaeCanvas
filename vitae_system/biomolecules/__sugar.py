from dataclasses import dataclass
from vitae_system.biomolecules import NADH, Energy


@dataclass
class HydroProd:
    energy: Energy
    nadh: NADH


@dataclass
class Sugar:
    """
    :param C: Carbon
    :param H: Hydrogen
    :param O: Oxygen
    """

    C: int = 6
    H: int = 12
    O: int = 6

    def hydrolyze(self) -> HydroProd:
        """
        Hydrolysis of Sugar
        :return: HydroProd
        """
        # Calculate energy value: (C - O)/3 + 2
        energy_value: float = (self.C - self.O) / 3 + 2
        # Calculate NADH value: (H - C)/3
        nadh_value: float = (self.H - self.C) / 3

        return HydroProd(
            Energy(energy_value),
            NADH(nadh_value),
        )
