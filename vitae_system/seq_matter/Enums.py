from enum import Enum


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
    A = 0
    R = 1
    N = 2
    D = 3
    C = 4
    E = 5
    Q = 6
    G = 7
    H = 8
    I = 9
    L = 10
    K = 11
    M = 12
    F = 13
    P = 14
    S = 15
    T = 16
    W = 17
    Y = 18
    V = 19


ADD_AMINO_ACIDS = {
    E_Protein.L, E_Protein.I, E_Protein.V,
    E_Protein.Q, E_Protein.A, E_Protein.R,
    E_Protein.S, E_Protein.D
}

INHIBIT_AMINO_ACIDS = {
    E_Protein.W, E_Protein.G, E_Protein.H,
    E_Protein.P, E_Protein.M
}
