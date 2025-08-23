import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *

DNA = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")
env1 = env.Environment(width=10, height=10)

cell1 = cells.Cell(env1, 0, 0, DNA, name="cell1")
print(env1.type_register_table)
cell1.move(1, 0)
print(env1.read(0, 0))
print(env1.read(1, 0))