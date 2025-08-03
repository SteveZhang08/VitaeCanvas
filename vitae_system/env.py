# === VitaeCanvas ===
# ./vitae_system/env.py
# by SteveZhang08
# Helpers: None
# These AI_Models that provide help for the file:
# Kimi  DeepSeek-R1
DIFFUSION_RATE = 0.1
DEBUG = False
WARNING = False

def debug(message):
    if DEBUG == True:
        print(message)

def warning(message):
    if WARNING == True:
        print(message)

class Environment_Error(Exception):
    """环境错误"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return self.message

class Energy:
    """Energy 类，包含能量大小以及是否能够扩散"""
    # Energy 类基本框架由 Kimi 生成
    def __init__(self, value, diffuse=True):
        """初始化 Energy 对象"""
        self.value = value  # 能量的大小
        self.diffuse = diffuse  # 能量是否能够扩散
        self.name = "Energy"

    def __str__(self):
        """返回 Energy 对象的字符串表示"""
        return f"{self.name}({self.value}, diffuse={self.diffuse})"

    def __repr__(self):
        """返回 Energy 对象的正式字符串表示"""
        return f"{self.name}({self.value}, diffuse={self.diffuse})"

    def __eq__(self, other):
        if type(other) == type(self):
            return self.value == other.value and self.diffuse == other.diffuse
        return NotImplemented

class O2(Energy):
    def __init__(self, value, diffuse=True):
        super().__init__(value, diffuse)
        self.name = "O2"

class H2O(Energy):
    def __init__(self, value, diffuse=True):
        super().__init__(value, diffuse)
        self.name = "H2O"

class Environment:
    """二维环境模拟与协调"""
    def __init__(self, width: int = 100, height: int = 100) -> None:
        ''' 注意：环境坐标范围是从(0,0)到(width,height)，包括边界值'''
        self.width = width
        self.height = height
        self.env = {(0, 0):[Energy(0)]}
        self.type_register_table = {Energy:[(0,0)]}

    def read(self, x: int = 0, y: int = 0) -> list:
        """读取环境信息"""
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise Environment_Error(f"[function]read:错误，坐标({x}, {y})超出范围！\nError, coordinate ({x}, {y}) out of range!")
        return self.env.get((x, y), [])

    def write(self,x: int, y: int, content: any):
        """写入环境信息（相同类型的信息会被覆盖）"""
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise Environment_Error(f"[function]write:错误，坐标({x}, {y})超出范围！\nError, coordinate ({x}, {y}) out of range!")
        grid = self.read(x, y)
        # 检查是否已经存在该类型信息，如果存在就删除
        for idx in reversed(range(len(grid))):
            if isinstance(grid[idx], type(content)):
                grid.pop(idx)
        grid.append(content)
        self.env[(x, y)] = grid     # 因为惰性加载，这一步是必须的，请不要删除
        # 将类型注册到类型表中
        type_grid = self.type_register_table.get(type(content), [])
        if not (x, y) in type_grid:
            type_grid.append((x, y))
        self.type_register_table[type(content)] = type_grid

    def find_type(self, check_type):
        """指定类型查找
        返回值：所在位置的集合组成的列表；
               None：不存在该类型"""
        result = []
        type_grid = self.type_register_table.get(check_type, [])
        for env_coordinates in type_grid:
            idx = self.check_type_on_env(self.read(env_coordinates[0], env_coordinates[1]), check_type)
            if idx != None:
                result.append(env_coordinates + (idx,))
        if result == []:
            warning(f"[function]find_type:警告，类型{check_type}未找到！\nWarning, data type {check_type} not found!")
            return None
        else:
            return result

    def check_type_on_env(self, layer:list, check_type):
        """在网格中指定类型查找
        :param layer: 要查找的环境网格列表
        :param check_type: 要查找的类型
        return：所在位置的索引；
               None：不存在该类型"""
        for idx, item in enumerate(layer):
            if isinstance(item, check_type):
                return idx
        warning(f"[function]check_type_on_env:警告，类型{check_type}未找到！\nWarning, data type {check_type} not found!")
        return None

    def energy_diffusion(self):
        def add_energy(x, y, value):
            # 直接修改现有 Energy 值，避免覆盖
            layer = self.read(x, y)
            z = self.check_type_on_env(layer, Energy)
            if z != None:
                layer[z].value += value
            else:
                self.write(x, y, Energy(value))

        # 统一扩散方向数和计算逻辑
        for location in self.find_type(Energy):
            x, y, z = location
            energy = self.read(x, y)[z]
            if energy.value <= 0:
                continue

            diffusion_value = energy.value * DIFFUSION_RATE
            directions = []

            # 计算有效扩散方向
            if x > 0: directions.append((-1, 0))     # 左
            if x < self.width-1: directions.append((1, 0))  # 右
            if y > 0: directions.append((0, -1))     # 上
            if y < self.height-1: directions.append((0, 1)) # 下

            num_directions = len(directions)
            if num_directions == 0:
                continue

            max_diffusion = energy.value / (1 + num_directions)  # 稳定约束
            actual_diffusion = min(diffusion_value, max_diffusion)

            # 向有效方向扩散
            for dx, dy in directions:
                add_energy(x + dx, y + dy, actual_diffusion)

            # 源网格减少能量
            energy.value -= actual_diffusion * num_directions

    def delete(self, x: int, y: int, idx: int):
        """
        删除环境中的元素
        :param x: 要删除的元素的x坐标
        :param y: 要删除的元素的y坐标
        :param idx: 要删除的元素的索引
        """
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise Environment_Error(f"[function]delete:错误，坐标({x}, {y})超出范围！\nError, coordinate ({x}, {y}) out of range!")
        self.env[(x, y)].pop(idx)
        # 待完善：删除后需要更新类型表
        # self.type_register_table[type(content)].remove((x, y))

if __name__ == "__main__":
    env1 = Environment(width=10, height=10)
    energy_1 = Energy(2, diffuse=True)
    env1.write(1, 0, energy_1)
    env1.energy_diffusion()
    import time
    count = 0
    while count < 10:
        print("==============================================")
        for x in range(env1.width):
            out = []
            for y in range(env1.height):
                grid_content = env1.read(x, y)  
                result = env1.check_type_on_env(grid_content, Energy)  
                if result is None:
                    out.append([0])
                else:
                    out.append([round(grid_content[result].value, 2)])
            print(out)
        env1.energy_diffusion()
        time.sleep(1)
        count += 1