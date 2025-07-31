from __seq import ESeq

from enum import Enum, auto
from typing import Set, NamedTuple, List
from dataclasses import dataclass


class E_RNA(Enum):
    A = 0
    U = 1
    C = 2
    G = 3


class E_DNA(Enum):
    A = 0
    T = 1
    C = 2
    G = 3


class E_Protein(Enum):
    A = auto()
    R = auto()
    N = auto()
    D = auto()
    C = auto()
    E = auto()
    Q = auto()
    G = auto()
    H = auto()
    I = auto()
    L = auto()
    K = auto()
    M = auto()
    F = auto()
    P = auto()
    S = auto()
    T = auto()
    W = auto()
    Y = auto()
    V = auto()


class E_ProteinFunc(Enum):
    ANTIOXIDANT = auto()  # Antioxidant
    MEMBRANE_TRANSPORT = auto()  # Membrane transport
    CYTOSKELETON = auto()  # Cytoskeleton
    VARIATION_CONTROL = auto()  # Vibration control


class FunctionPattern(NamedTuple):
    pattern: str
    function: E_ProteinFunc
    skip: int  # Num of char that should be cut after matching


A_FUNCTION_PATTERNS: Set[FunctionPattern] = {
    FunctionPattern("GACLICYWSCCMN", E_ProteinFunc.ANTIOXIDANT, 13),
    FunctionPattern("CYSTMTR", E_ProteinFunc.MEMBRANE_TRANSPORT, 7),
    FunctionPattern("ACTIN", E_ProteinFunc.CYTOSKELETON, 5),
    FunctionPattern("SKNQK", E_ProteinFunc.VARIATION_CONTROL, 5),
    FunctionPattern("GASL", E_ProteinFunc.VARIATION_CONTROL, 4),
}

A_ADD_AMINO_ACIDS: Set[E_Protein] = {
    E_Protein.L, E_Protein.I, E_Protein.V,
    E_Protein.Q, E_Protein.A, E_Protein.R,
    E_Protein.S, E_Protein.D
}

A_INHIBIT_AMINO_ACIDS: Set[E_Protein] = {
    E_Protein.W, E_Protein.G, E_Protein.H,
    E_Protein.P, E_Protein.M
}


@dataclass(frozen=True)
class FunctionRule:
    seq: ESeq  # Sequence for matching
    function: E_ProteinFunc
    priority: int = 100  # Priority, use 100 as medium
    exclusive: bool = True  # If exclusive skip the current section in next matching


A_PROTEIN_FUNC_RULES: Set[FunctionRule] = {
    FunctionRule(ESeq(E_Protein, "GACLICYWSCCMN"), E_ProteinFunc.ANTIOXIDANT, priority=1),
    FunctionRule(ESeq(E_Protein, "CYSTMTR"), E_ProteinFunc.MEMBRANE_TRANSPORT, priority=2),
    FunctionRule(ESeq(E_Protein, "ACTIN"), E_ProteinFunc.CYTOSKELETON, priority=3),
    FunctionRule(ESeq(E_Protein, "SKNQK"), E_ProteinFunc.VARIATION_CONTROL, priority=4),
    FunctionRule(ESeq(E_Protein, "GASL"), E_ProteinFunc.VARIATION_CONTROL, priority=5),
}

I_MAX_GENE_LENGTH: int = 300  # DNA的最大有效长度
F_MAX_METABOLIC: float = 0.8  # 最大能量转化率
F_MIN_METABOLIC: float = 0.1  # 最小能量转化率