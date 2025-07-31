from dataclasses import dataclass


@dataclass
class HydroProd:
    energy_value: float
    nadh_value: float


@dataclass
class Sugar:
    """
    :param C: Carbon
    :param H: Hydrogen
    :param O: Oxygen
    """

    C: int
    H: int
    O: int

    def hydrolyze(self) -> HydroProd:
        """
        Hydrolysis of Sugar
        :return: HydroProd
        """
        # Calculate energy value: (C - O)/3 + 2
        energy_value: float = (self.C - self.O) / 3 + 2
        # Calculate NADH value: (H - C)/3
        nadh_value: float = (self.H - self.C) / 3

        return HydroProd(energy_value, nadh_value)
