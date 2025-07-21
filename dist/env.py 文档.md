## ```./vitae_system/env.py```
### **env.debug**  
全局调试输出函数。  
- `debug(message)`  
  当 `DEBUG = True` 时，打印调试信息  
  所有的调试输出均由`env.DEBUG` 控制，默认 `False`  
  **参数**：  
  - `message`: 要输出的调试信息  

---

### **env.warning**  
全局警告输出函数。  
- `warning(message)`  
  当 `WARNING = True` 时，打印警告信息  
  **参数**：  
  - `message`: 要输出的警告信息  

---

### **env.Energy**  
能量类，包含能量值及扩散属性。  
**方法**：  
- `__init__(self, value, diffuse=True)`  
  初始化能量对象  
  **参数**：  
  - `value`: 能量数值  
  - `diffuse`: 是否允许扩散 (默认True)  

- `__str__()`, `__repr__()`  
  返回能量对象的字符串表示  

- 全套运算符重载：  
  - 比较运算：`==`, `<`, `<=`, `>`, `>=`  
  - 算术运算：`+`, `-`, `*`, `/`, `**`  
  - 反向运算：`__radd__`等  
  - 原地运算：`+=`, `-=`, `*=`, `/=`, `**=`  
  *支持与数值或另一Energy对象运算*

---

### **env.Environment**  
二维环境网格系统。  
**方法**：  
- `__init__(self, width=100, height=100)`  
  初始化环境网格  
  **参数**：  
  - `width`: 环境宽度  
  - `height`: 环境高度  

- `read(self, x=0, y=0)`  
  读取指定坐标的环境信息  
  **返回**：该坐标的物体列表  

- `write(self, x, y, content)`  
  写入/更新环境信息  
  **特性**：同类型对象自动覆盖  
  **参数**：  
  - `x`, `y`: 目标坐标  
  - `content`: 要写入的对象  

- `find_type(self, check_type)`  
  全局查找指定类型对象  
  **返回**：找到的位置三元组列表 `(x, y, index)`  

- `check_type_on_env(self, layer, check_type)`  
  在单个网格单元中查找类型  
  **返回**：对象在单元列表中的索引  

- `energy_diffusion(self)`  
  执行能量扩散算法：  
  1. 查找所有可扩散能量源  
  2. 向有效相邻方向分配能量  
  3. 遵循稳定约束：`max_diffusion = energy.value / (1 + 有效方向数)`  

---

### **使用示例**  
```python
# 创建环境
env = Environment(width=10, height=10)

# 添加能量源
energy = Energy(100.0, diffuse=True)
env.write(5, 5, energy)

# 执行能量扩散
env.energy_diffusion()

# 读取扩散结果
print(env.read(4, 5))  # 查看左侧网格的能量值
```