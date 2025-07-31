# === VitaeCanvas ===
# ./vitae_system/env.py
# by SteveZhang08
# Helpers: None
# These AI_Models that provide help for the file:
# Kimi  DeepSeek-R1
DIFFUSION_RATE = 0.1
DEBUG = True
WARNING = False

def debug(message):
    if DEBUG == True:
        print(message)

def warning(message):
    if WARNING == True:
        print(message)

class Energy:
    """Energy 类，包含能量大小以及是否能够扩散"""
    # Energy 类基本框架由 Kimi 生成
    def __init__(self, value, diffuse=True):
        """初始化 Energy 对象"""
        self.value = value  # 能量的大小
        self.diffuse = diffuse  # 能量是否能够扩散

    def __str__(self):
        """返回 Energy 对象的字符串表示"""
        return f"Energy({self.value}, diffuse={self.diffuse})"

    def __repr__(self):
        """返回 Energy 对象的正式字符串表示"""
        return f"Energy({self.value}, diffuse={self.diffuse})"

    # 支持比较运算符
    def __eq__(self, other):
        if isinstance(other, Energy):
            return self.value == other.value and self.diffuse == other.diffuse
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Energy):
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Energy):
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Energy):
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Energy):
            return self.value >= other.value
        return NotImplemented

    # 支持算术运算
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Energy(self.value + other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value + other.value, self.diffuse and other.diffuse)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Energy(self.value - other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value - other.value, self.diffuse and other.diffuse)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Energy(self.value * other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value * other.value, self.diffuse and other.diffuse)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other != 0:
                return Energy(self.value / other, self.diffuse)
            else:
                raise ZeroDivisionError("除数不能为零")
        elif isinstance(other, Energy):
            if other.value != 0:
                return Energy(self.value / other.value, self.diffuse and other.diffuse)
            else:
                raise ZeroDivisionError("除数不能为零")
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            return Energy(self.value ** other, self.diffuse)
        elif isinstance(other, Energy):
            return Energy(self.value ** other.value, self.diffuse and other.diffuse)
        return NotImplemented

    # 支持反向运算符
    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Energy(other - self.value, self.diffuse)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            if self.value != 0:
                return Energy(other / self.value, self.diffuse)
            else:
                raise ZeroDivisionError("除数不能为零")
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            return Energy(other ** self.value, self.diffuse)
        return NotImplemented

    # 支持原地运算符
    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            self.value += other
        elif isinstance(other, Energy):
            self.value += other.value
            self.diffuse = self.diffuse and other.diffuse
        return self

    def __isub__(self, other):
        if isinstance(other, (int, float)):
            self.value -= other
        elif isinstance(other, Energy):
            self.value -= other.value
            self.diffuse = self.diffuse and other.diffuse
        return self

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self.value *= other
        elif isinstance(other, Energy):
            self.value *= other.value
            self.diffuse = self.diffuse and other.diffuse
        return self

    def __itruediv__(self, other):
        if isinstance(other, (int, float)):
            if other != 0:
                self.value /= other
            else:
                raise ZeroDivisionError("除数不能为零")
        elif isinstance(other, Energy):
            if other.value != 0:
                self.value /= other.value
                self.diffuse = self.diffuse and other.diffuse
            else:
                raise ZeroDivisionError("除数不能为零")
        return self

    def __ipow__(self, other):
        if isinstance(other, (int, float)):
            self.value **= other
        elif isinstance(other, Energy):
            self.value **= other.value
            self.diffuse = self.diffuse and other.diffuse
        return self

class Environment:
    """二维环境模拟与协调"""
    def __init__(self, width: int = 100, height: int = 100) -> None:
        self.width = width + 1
        self.height = height + 1
        self.env = []
        # 初始化环境网格
        #错误写法：所有行共享同一列列表
        #此错误十分严重，造成环境数据污染
        #该错误由 DeepSeek-R1 指出
        #y = []
        #for _count in range(self.height):
        #    y.append([])
        #for _count in range(self.width):
        #    self.env.append(y)
        # 正确写法：每行独立生成新列表
        self.env = [
        [[] for _ in range(self.height)] 
        for _ in range(self.width)
        ]

    def read(self, x: int = 0, y: int = 0):
        """读取环境信息"""
        return self.env[x][y]

    def write(self,x: int, y: int, content: any):
        """写入环境信息（相同类型的信息会被覆盖）"""
        # 检查是否已经存在该类型信息，如果存在就删除
        for idx in reversed(range(len(self.env[x][y]))):
            if isinstance(self.env[x][y][idx], type(content)):
                self.env[x][y].pop(idx)
        self.env[x][y].append(content)

    def find_type(self, check_type):
        """指定类型查找
        返回值：所在位置的集合组成的列表；
               None：不存在该类型"""
        result = []
        for idx1, layer in enumerate(self.env):
            for idx2, sub_layer in enumerate(layer):
                for idx3, item in enumerate(sub_layer):
                    if isinstance(item, check_type):
                        result.append((idx1, idx2, idx3))
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
        self.env[x][y].pop(idx)

if __name__ == "__main__":
    env1 = Environment(width=10,height=10)
    energy_1 = Energy(2, diffuse=True)
    env1.write(1, 0, energy_1)
    env1.energy_diffusion()
    import time
    while True:
        print("==============================================")
        for i in env1.env:
            out = []
            for a in i:
                result = Environment.check_type_on_env(env1, a, Energy)
                if result == None :
                    out.append([0])
                else:
                    out.append([round(a[result].value, 2)])
            print(out)
        env1.energy_diffusion()
        time.sleep(1)