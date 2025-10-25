from turtle import *
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vitae_system import protein

amino_acid_colors = {
    'A': '#C8C8C8',  # 铝灰 (疏水)
    'R': '#145AFF',  # 钴蓝 (碱性)
    'N': '#00DCDC',  # 青蓝 (极性)
    'D': '#E60A0A',  # 鲜红 (酸性)
    'C': '#E6E600',  # 明黄 (含硫)
    'Q': '#00DCDC',  # 青蓝 (极性)
    'E': '#E60A0A',  # 鲜红 (酸性)
    'G': '#EBEBEB',  # 银白 (特殊结构)
    'H': '#8282D2',  # 淡紫 (碱性)
    'I': '#0F820F',  # 深绿 (疏水)
    'L': '#0F820F',  # 深绿 (疏水)
    'K': '#145AFF',  # 钴蓝 (碱性)
    'M': '#E6E600',  # 明黄 (含硫)
    'F': '#3232AA',  # 靛蓝 (芳香)
    'P': '#DC9682',  # 粉橙 (环状)
    'S': '#FA9600',  # 橙黄 (极性)
    'T': '#FA9600',  # 橙黄 (极性)
    'W': '#B45AB4',  # 紫红 (芳香)
    'Y': '#3232AA',  # 靛蓝 (芳香)
    'V': '#0F820F'   # 深绿 (疏水)
}

protein_structure = protein.structure("KMFPAAAGACLICYFPSTWYVWSCCMNEEEFGQEGHILKMFPS")
# GACLICYWSCCMNEEEFGQEGHILKMFPS
# [['GACL', 'sheet'], ['ICYW', 'sheet'], ['SCCM', 'sheet'], ['NEEE', 'helix'], ['FG', 'none']]

p = Pen()
p.up()
p.goto(-50, 100)
p.down()
p.pensize(10)
p.speed(0)
p.ht()

LENGTH = 50

def sheet(pen: Pen, sequence):
    global direction
    if pen.heading() == 0:
        direction = 1
    elif pen.heading() == 180:
        direction = -1
    def turn(angle):
        if direction == 1:
            pen.right(angle)
        elif direction == -1:
            pen.left(angle)

    pen.color(amino_acid_colors[sequence[0]])
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[1]])
    turn(35)
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[2]])
    turn(110)
    pen.forward(LENGTH)
    pen.color(amino_acid_colors[sequence[3]])
    turn(35)
    pen.forward(LENGTH)

def helix(pen: Pen, sequence):
    global direction
    if pen.heading() == 0:
        direction = 1
    elif pen.heading() == 180:
        direction = -1
    def turn(angle):
        if direction == 1:
            pen.right(angle)
        elif direction == -1:
            pen.left(angle)
    pen.color(amino_acid_colors[sequence[0]])
    pen.forward(LENGTH/10)
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(8)
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(10)
    pen.color(amino_acid_colors[sequence[1]])
    for _ in range(10):
        pen.forward(LENGTH/10)
        turn(9)
    pen.color(amino_acid_colors[sequence[2]])
    for _ in range(10):
        pen.forward(LENGTH/15)
        turn(9)
    pen.color(amino_acid_colors[sequence[3]])
    for _ in range(5):
        pen.forward(LENGTH/10)
        turn(10)
    for _ in range(5):
        pen.forward(LENGTH/20)
        turn(8)
    pen.forward(LENGTH)

def none(pen: Pen, sequence):
    for amino_acid in sequence:
        pen.color(amino_acid_colors[amino_acid])
        pen.forward(LENGTH)

draw = {'sheet': sheet, 'helix': helix, 'none': none}

for sequence in protein_structure:
    draw[sequence[1]](p, sequence[0])

done()
