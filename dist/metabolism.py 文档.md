## ```./vitae_system/metabolism.py```
### **metabolism.MetabolismSystem**  
细胞代谢系统控制器，处理能量转换与物质交换过程。  

**方法**：  
- `__init__(self, cell:Cell, env:Environment)`  
  初始化代谢系统并执行完整代谢周期  
  **参数**：  
  - `cell`: 目标细胞实例（需包含有效坐标）  
  - `env`: 环境控制器实例  
  **功能流程**：  
  1. 检测细胞位置的环境能量  
  2. 执行能量吸收（`absorb_energy()`）  
  3. 执行能量转化（`metabolic_energy()`）  
  4. 更新细胞能量和环境能量  
  **异常**：  
  - `ValueError`: 细胞坐标超出环境范围  
  **副作用**：  
  - 修改细胞能量值  
  - 修改环境网格中的能量值  

- `absorb_energy(self) -> Energy`  
  从环境中吸收能量  
  **机制**：  
  - 每次最多吸收 1 单位能量  
  - 当环境能量≤1时吸收剩余全部能量  
  **返回**：被吸收的 Energy 对象（diffuse=False）  

- `metabolic_energy(self, energy:Energy) -> Energy`  
  将吸收的能量转化为细胞可用能量  
  **公式**：  
  转化能量 = 吸收能量 × 代谢率  
  剩余能量 = 吸收能量 - 转化能量  
  **返回**：转化后的 Energy 对象（diffuse=False）  

---

### **使用示例**  
```python
# 创建环境和细胞
env = Environment()
cell = Cell(env, 5, 5, dna=DNA("ATCGATCG"))

# 添加环境能量
env.write(5, 5, Energy(100.0))

# 执行代谢过程
metabolism = MetabolismSystem(cell, env)

# 查看结果
print(f"细胞能量: {cell.energy.value}")
print(f"环境剩余能量: {env.read(5,5)[0].value}")
```

**代谢过程说明**：  
1. 细胞从环境吸收能量（每次最多1单位）  
2. 吸收能量按代谢率转化为细胞可用能量  
3. 剩余能量返回环境  
4. 环境定期执行能量扩散（`env.energy_diffusion()`）