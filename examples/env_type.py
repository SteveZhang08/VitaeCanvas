import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import *

env1 = env.Environment(width=10, height=10)
env1.write(0,0,env.Energy(10,diffuse=False))
env1.write(0,0,env.Energy(10,diffuse=False))
grid = env1.read(0,0)
print(grid)
print(env1.type_register_table)
print(env1.check_type_on_env(grid,env.Energy,mode="all"))
print(env1.check_type_on_env(grid,env.Energy,mode="none"))
env1.delete(0,0,env1.check_type_on_env(grid,env.Energy))
print(env1.type_register_table)
env1.remove_type(0,0,env.Energy)
print(env1.type_register_table)