import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *

DNA = cells.DNA("TACCCCCGCACGGACTATACGATGACCTCGACGACGTACTTGACTACGATGTCGTGCTACTGCTCCACTCGCACGTGCTATTTGACTTCGTTCTTGGTCTTCACTCCCCGCTCGGACACTTACCGCAAGGACCACTCCGGCATGTATACGCCCTCGACTCACCACCACACTCACATGCTCACT")
env1 = env.Environment(width=10, height=10)

cell1 = cells.Cell(env1, 3, 0, DNA, name="cell1")
cell2 = cells.Cell(env1, 1, 0, DNA, name="cell2")
cell3 = cells.Cell(env1, 2, 0, DNA, name="cell3")
print(env1.type_register_table)
env1.horizontal_move_the_whole_row(0, cells.Cell, begin=5, offset=-1)   # 将所有满足 (x <= 5 and y == 0) 的细胞向左移动 1 个单位
print(env1.read(0, 0))
print(env1.read(1, 0))
print(env1.type_register_table)