## ```./vitae_system/cells.py```

### **cells.CellError**
细胞活动异常基类，继承自 Python 的 `Exception` 类。  
**方法**：
- `__init__(self, message:str)`  
  初始化异常对象，接收错误信息字符串
- `__str__(self)`  
  返回异常的错误信息字符串

---

### **cells.DNA**
DNA 序列对象，包含碱基 ATCG。  
**方法**：
- `__init__(self, sequence:str)`  
  初始化 DNA 对象，自动过滤非法字符并转为大写
- `__add__(self, other)`  
  重载 `+` 操作符，支持连接两个 DNA 对象
- `__eq__(self, other)`  
  重载 `==` 操作符，比较两个 DNA 序列是否相同
- `__len__(self)`  
  返回 DNA 序列长度
- `__str__(self)`  
  返回 DNA 序列字符串
- `__repr__(self)`  
  返回可重建对象的正式字符串表示
- `_validate_sequence(sequence)`  
  （内部）验证序列合法性，移除非 ATCG 字符

---

### **cells.RNA**
RNA 序列对象，包含碱基 AUCG。  
**方法**：
- `__init__(self, sequence)`  
  初始化 RNA 对象，自动过滤非法字符并转为大写
- `__add__(self, other)`  
  重载 `+` 操作符，支持连接两个 RNA 对象
- `__eq__(self, other)`  
  重载 `==` 操作符，比较两个 RNA 序列是否相同
- `__len__(self)`  
  返回 RNA 序列长度
- `__str__(self)`  
  返回 RNA 序列字符串
- `__repr__(self)`  
  返回可重建对象的正式字符串表示
- `_validate_sequence(sequence)`  
  （内部）验证序列合法性，移除非 AUCG 字符
- `_split(sequence)`  
  （内部）将 RNA 序列按密码子（3碱基）拆分

---

### **cells.Protein**
蛋白质序列对象。  
**方法**：
- `__init__(self, sequence:str)`  
  初始化蛋白质对象，验证氨基酸合法性
- `__add__(self, other)`  
  重载 `+` 操作符，支持连接两个蛋白质对象
- `__eq__(self, other)`  
  重载 `==` 操作符，比较两个蛋白质序列是否相同
- `__len__(self)`  
  返回蛋白质序列长度
- `__str__(self)`  
  返回蛋白质序列字符串
- `__repr__(self)`  
  返回可重建对象的正式字符串表示
- `_validate_sequence(sequence)`  
  （内部）验证氨基酸合法性，移除非标准字符
- `_metabolic(sequence)`  
  （内部）计算蛋白质代谢率：(加成氨基酸数 - 抑制氨基酸数) / 总氨基酸数

---

### **cells.Cell**
细胞实体类，包含遗传信息与代谢属性。  
**类常量**：
- `MAX_GENE_LENGTH = 300`：DNA 最大有效长度
- `MAX_METABOLIC = 0.8`：最大能量转化率
- `MIN_METABOLIC = 0.1`：最小能量转化率

**方法**：
- `__init__(self, env1:env.Environment, x:int, y:int, dna:DNA=DNA("ATCG"), name=None)`  
  初始化细胞实例，自动完成 DNA 转录翻译流程
- `__str__(self)`  
  返回细胞名称的字符串表示
- `normalize_dna(dna:DNA)`  
  标准化 DNA：截取有效长度并用 'T' 补足
- `DNA_translate(dna:DNA)`  
  转录 DNA → RNA（A→U, T→A, C→G, G→C）
- `ribosome(rna:RNA)`  
  翻译 RNA → 蛋白质列表（使用密码子对照表）
- `_metabolic(protein_list:list)`  
  计算细胞整体代谢率（所有蛋白质平均值）
- `consume_energy()`  
  执行基础能量消耗：能量 -= 代谢率，年龄 +1
- `move(x:int, y:int)`  
  移动细胞到指定坐标并更新环境
- `_color()`  
  根据蛋白质序列计算细胞 RGB 颜色
- `calculate_rgb(sequence)`  
  RGB 计算核心：使用预定义氨基酸权重计算三通道值

---

### **使用示例**
```python
# 创建环境
env1 = env.Environment()

# 创建随机 DNA 的细胞
cell = Cell(env1, 0, 0, dna=DNA(random_DNA.generate_dna(300)))

# 获取细胞信息
print(cell.dna)          # DNA序列
print(cell.rna.split)    # RNA密码子拆分
print(cell.protein_list) # 蛋白质列表
print(cell.color)        # RGB颜色值

# 移动细胞
cell.move(10, 5)
```