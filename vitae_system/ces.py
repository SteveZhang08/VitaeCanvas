import cells
import env
import random_DNA

env1 = env.Environment(2, 2)
dna = cells.DNA(random_DNA.generate_dna(300))
cell1 = cells.Cell(env1, 1, 0, dna,"he")
print(cell1.x, cell1.y)
cell2 = cells.Cell(env1, 0, 0, dna,"520")
where_cell = env.Environment.find_type(env1, cells.Cell)
print(where_cell)
cell2.move(where_cell[0][0], where_cell[0][1])
print(env1.read(1, 0)[0].name)