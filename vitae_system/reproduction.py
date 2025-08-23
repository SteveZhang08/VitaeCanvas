# === VitaeCanvas ===
# ./vitae_system/cells.py
# by SteveZhang08
# Helpers: None

if __name__ == "__main__":
    # 当作为主程序直接运行时，绝对导入同级模块
    from cells import*
    from env import*
    import random
else:
    # 当作为模块被导入时，相对导入库内同级模块
    from .env import *
    from .cells import *
    import random

class Reproduction:
    def __init__(self, cell: Cell):
        self.cell: Cell = cell
    def reproduce(self):
        new_dna = DNA(self.copy_dna(variation = True))
        x, y = self.where_new_cell()
        new_cell = Cell(new_dna)

    def copy_dna(self, variation = False):
        new_dna = list(str(self.cell.dna))
        if variation:
            variation_rate = self.cell.variation_rate
            if random.random() <= variation_rate:
                num = random.randint(0, 10)
                end_idx = len(new_dna) - 1
                if num <= 7:
                    # 模式一：随机替换单碱基
                    new_dna[random.randint(0, end_idx)] = random.choice("ACGT")
                elif num <= 9:
                    # 模式二：随机删除单碱基
                    del new_dna[random.randint(0, end_idx)]
                elif num == 10:
                    # 模式三：随机插入单碱基
                    new_dna.insert(random.randint(0, end_idx), random.choice("ACGT"))
        return str(new_dna)

    def where_new_cell(self):
        up_x, up_y =  self.cell.x, self.cell.y - 1
        down_x, down_y = self.cell.x, self.cell.y + 1
        left_x, left_y = self.cell.x - 1, self.cell.y
        right_x, right_y = self.cell.x + 1, self.cell.y

        # 检查是否超出环境范围
        if self.cell.env.in_env(up_x, up_y):
            up_grid = self.cell.env.read(up_x, up_y)
            up_idx = self.cell.env.check_type_on_env(up_grid, Cell)
        else:
            up_grid = []
            up_idx = False
        if self.cell.env.in_env(down_x, down_y):
            down_grid = self.cell.env.read(down_x, down_y)
            down_idx = self.cell.env.check_type_on_env(down_grid, Cell)
        else:
            down_grid = []
            down_idx = False
        if self.cell.env.in_env(left_x, left_y):
            left_grid = self.cell.env.read(left_x, left_y)
            left_idx = self.cell.env.check_type_on_env(left_grid, Cell)
        else:
            left_grid = []
            left_idx = False
        if self.cell.env.in_env(right_x, right_y):
            right_grid = self.cell.env.read(right_x, right_y)
            right_idx = self.cell.env.check_type_on_env(right_grid, Cell)
        else:
            right_grid = []
            right_idx = False

        # 检查是否有空白位置
        if up_idx == None:
            x, y = up_x, up_y
        elif down_idx == None:
            x, y = down_x, down_y
        elif left_idx == None:
            x, y = left_x, left_y
        elif right_idx == None:
            x, y = right_x, right_y
        else:
            # 比较周围最薄弱的细胞
            temp_x_y_list = [(up_x, up_y), (down_x, down_y), (left_x, left_y), (right_x, right_y)]
            cell_idx_list = [up_idx, down_idx, left_idx, right_idx]
            direction_list = [up_grid, down_grid, left_grid, right_grid]
            x_y_list = []
            cell_strong_list = []
            for x_y, cell_idx, direction in zip(temp_x_y_list, cell_idx_list, direction_list):
                if cell_idx != False:
                    x_y_list.append(x_y)
                    cell_strong_list.append(direction[cell_idx].strong)
            weak_cell = cell_strong_list[0]
            for x_y, cell_strong in zip(x_y_list, cell_strong_list):
                if cell_strong < weak_cell:
                    weak_cell = cell_strong
                    x, y = x_y

        return x, y
