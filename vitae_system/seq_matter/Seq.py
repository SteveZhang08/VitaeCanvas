from typing import List, Type, TypeVar, Generic
from enum import Enum

# Define a generic Enum type
E = TypeVar('E', bound=Enum)


class ESeq(Generic[E]):
    """
    A class to store sequences of a specific Enum type.
    """

    def __init__(self, enum_type: Type[E], values: List[E] = None) -> None:
        if not issubclass(enum_type, Enum):
            raise TypeError("ESeq can only be used with Enum types")
        self.__etype = enum_type
        self.__seq: List[E] = values if values is not None else []

    def from_string(self, seq_str: str) -> bool:
        """Try to populate self._seq from a string like 'ABCC'."""
        name_to_member = {e.name: e for e in self.__etype}
        seq = []
        for ch in seq_str:
            if ch not in name_to_member:
                return False
            seq.append(name_to_member[ch])
        self.__seq = seq
        return True

    def to_string(self) -> str:
        """Return the sequence as a string of enum names, like 'ABCC'."""
        return ''.join(e.name for e in self.__seq)

    def to_list(self) -> List[E]:
        return list(self.__seq)

    def __repr__(self) -> str:
        return f"ESeq<{self.__etype.__name__}>({self.to_string()})"

    def __getitem__(self, index: int) -> E:
        return self.__seq[index]

    def __len__(self) -> int:
        return len(self.__seq)

    # Comparison based on length

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ESeq):
            return NotImplemented
        return self.__seq == other.__seq

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: "ESeq") -> bool:
        return len(self) < len(other)

    def __le__(self, other: "ESeq") -> bool:
        return len(self) <= len(other)

    def __gt__(self, other: "ESeq") -> bool:
        return len(self) > len(other)

    def __ge__(self, other: "ESeq") -> bool:
        return len(self) >= len(other)

    # Calculation

    def __add__(self, other: E) -> "ESeq[E]":
        if not isinstance(other, self.__etype):
            raise TypeError(f"Can only add {self.__etype.__name__} elements")
        return ESeq(self.__etype, self.__seq + [other])


if __name__ == '__main__':
    class ExampleEnum(Enum):
        A = 0
        B = 1
        C = 2


    # 创建实例
    es = ESeq(ExampleEnum)

    # 从字符串加载
    success = es.from_string("ABCCBB")
    print(success)  # True
    print(es)  # ESeq<ExampleEnum>(ABCCBB)
    print(es.to_list())  # [ExampleEnum.A, ExampleEnum.B, ExampleEnum.C, ...]

    # 追加元素
    es.append(ExampleEnum.A)
    print(es.to_string())  # ABCCBBA
