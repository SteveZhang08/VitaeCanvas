from dataclasses import dataclass
from typing import Self


@dataclass
class Energy:
    value: float
    diffuse: bool = True

    def __repr__(self):
        return f"Energy(value={self.value}, diffuse={self.diffuse})"

    # Comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Energy):
            return NotImplemented

        return self.value == other.value and self.diffuse == other.diffuse

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Energy):
            return self.value < other.value
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Energy):
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Energy):
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Energy):
            return self.value >= other.value
        return NotImplemented

    # Calculation
    def __add__(self, other: object) -> Self | NotImplemented:
        if isinstance(other, int | float):
            return Energy(self.value + other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value + other.value, self.diffuse and other.diffuse)
        return NotImplemented

    def __sub__(self, other: object) -> Self | NotImplemented:
        if isinstance(other, int | float):
            return Energy(self.value - other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value - other.value, self.diffuse and other.diffuse)
        return NotImplemented

    def __radd__(self, other: object) -> Self | NotImplemented:
        return self.__add__(other)

    def __rsub__(self, other: object) -> Self | NotImplemented:
        if isinstance(other, int | float):
            return Energy(other - self.value, self.diffuse)
        return NotImplemented
