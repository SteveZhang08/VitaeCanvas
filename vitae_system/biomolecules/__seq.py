from typing import List, Type, TypeVar, Generic, Dict, Self, Optional, Iterable, Tuple, Iterator
from enum import Enum
from dataclasses import dataclass

# Define a generic Enum type
E = TypeVar('E', bound=Enum)


@dataclass(frozen=True)
class ESeq(Generic[E]):
    """
    A class to store sequences of a specific Enum type.
    """
    etype: Type[E]
    values: Tuple[E, ...] = tuple()

    def __init__(self, enum_type: Type[E], values: Optional[Iterable[E] | str] = None) -> None:
        if not issubclass(enum_type, Enum):
            raise TypeError("ESeq can only be used with Enum types")

        object.__setattr__(self, 'etype', enum_type)

        if isinstance(values, str):
            object.__setattr__(self, 'values', self.__from_string(values))
        elif isinstance(values, list | tuple):
            if not all(isinstance(v, enum_type) for v in values):
                raise ValueError("All elements in the list must be instances of the enum type.")
            object.__setattr__(self, 'values', tuple(values))

    def __from_string(self, seq_str: str) -> Tuple[E, ...]:
        """Try to populate self._seq from a string like 'ABCC'."""
        name_to_member: Dict[str, E] = {e.name: e for e in self.etype}
        seq: List[E] = []

        for ch in seq_str:
            if ch not in name_to_member:
                raise ValueError(f"Invalid character {ch} in seq")
            seq.append(name_to_member[ch])

        return tuple(seq)

    def to_string(self) -> str:
        """Return the sequence as a string of enum names, like 'ABCC'."""
        return ''.join(e.name for e in self.values)

    def to_list(self) -> List[E]:
        return list(self.values)

    def slice(self, start: int, end: int) -> Self:
        return self.values[start:end]

    def __repr__(self) -> str:
        return f"ESeq<{self.etype.__name__}>({self.to_string()})"

    def __getitem__(self, index: int) -> E:
        return self.values[index]

    def __len__(self) -> int:
        return len(self.values)

    # Comparison based on length

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ESeq):
            return NotImplemented
        return self.values == other.values

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: Self) -> bool:
        return len(self) < len(other)

    def __le__(self, other: Self) -> bool:
        return len(self) <= len(other)

    def __gt__(self, other: "ESeq") -> bool:
        return len(self) > len(other)

    def __ge__(self, other: Self) -> bool:
        return len(self) >= len(other)


class BioSeq(Generic[E]):
    def __init__(self, enum_type: type[E], sequence: str | List[E]) -> None:
        self.__seq: ESeq[E] = ESeq(enum_type, sequence)

    @property
    def sequence(self):
        return self.__seq


if __name__ == '__main__':
    class ExampleEnum(Enum):
        A = 0
        B = 1
        C = 2


    # Create instance
    es = ESeq(ExampleEnum, "ABCCBB")

    print(es)  # ESeq<ExampleEnum>(ABCCBB)
    print(es.to_list())  # [ExampleEnum.A, ExampleEnum.B, ExampleEnum.C, ...]
