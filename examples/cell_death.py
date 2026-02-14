import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *

DNA = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")
env1 = env.Environment(width=10, height=10)

cell1 = cells.Cell(env1, 1, 1, DNA, name="cell1")
cell1.energy.value = -100
metabolism = metabolism.MetabolismSystem(cell1, env1)
metabolism.read_env()
#metabolism.metabolism()

