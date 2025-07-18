# VitaeCanvas 生命绘卷
![logo](Logo/logo.png)

**[中文版本在下面]**
# VitaeCanvas
> VitaeCanvas - Life Canvas, a framework for creating cellular-level evolution simulations of simulated lifeforms  

> 🌱🌱 *"The meaning of life lies not only in existence, but in understanding existence itself"*



**VitaeCanvas - Life Canvas**

## Project Introduction
**VitaeCanvas** is an open-source project initiated by a Chinese high school student (SteveZhang08), aiming to simulate the behavior of low-level lifeforms (e.g., single cells) through computer programs and explore their evolutionary pathways. The project is written in Python and currently in early development stages.

> 📌📌 **Note**:  
> - Developer is a high school student with heavy academic workload, progress may be slow  
> - Limited development environment (family restrictions): Python 3.8.10 / Win7 x64 / AMD A8-5600K / 8GB RAM  
> - Project architecture may undergo reconstruction as the developer's knowledge advances  

## Project Goals
### Ultimate goal is to build an extensible simulation framework for:  

1. Simulating basic cellular life activities (metabolism, movement, energy exchange, etc.).  
2. Simulating genetic mechanisms (DNA transcription, RNA translation, protein synthesis).  
3. Exploring evolutionary processes of cell populations under environmental selection pressure.  

## Core Features
#### **Life Component Simulation**  
| Module          | Description                            | Key Classes/Functions        |  
|-----------------|----------------------------------------|-----------------------------|  
| **Genetic System** | DNA sequence generation, transcription-translation mechanism | `DNA`, `RNA`, `Protein` |  
| **Cell Entity**    | Cell metabolism/movement/energy conversion | `Cell`, `CellError`       |  
| **Environment Engine** | 2D grid environment & energy diffusion model | `Environment`, `Energy`  |  
| **Metabolic System** | Energy absorption and conversion control | `MetabolismSystem`         |  

### **Project Structure**  
```  
Vitae_System/  
├── cells.py          # Cell entities/genetic mechanisms  
├── env.py            # Environment engine/energy model  
├── metabolism.py     # Metabolic control system  
├── random_DNA.py     # DNA sequence generator  
└── __init__.py       # System configuration & version management  
```  

### **Development Roadmap**  
| Phase      | Goal                          | Status         |  
|------------|-------------------------------|---------------|  
| 0.1.x      | Single-cell basic metabolism  | 🚧 In development |  
| 0.2.x      | Multi-cell competition/cooperation | ⌛ Planned     |  
| 0.3.x      | Genetic mutation/evolution algorithm integration | ⌛ Planned  |  
| 1.0        | Ecosystem-level evolution simulation | ⏳ Long-term goal |  

## How to Run
- Ensure Python installation (recommended 3.8+).  
- Clone this repository.  
- Run the example main program (main.py)

## Project Status
Project is in **early development stage**, core framework still under construction. Due to the author's heavy academic workload, progress may be slow. Follow the project if interested, but **not actively soliciting code contributions** at this time.

## Future Directions
- Improve cell division and reproduction mechanisms.
- Introduce environmental factors (e.g., food, toxins).
- Implement natural selection and multi-generation evolution simulations.
- Optimize performance and visualization.

## Contribution  
> Currently not accepting external code contributions, but suggestions are welcome (via issues). May open for contributions in the future.  
### **How to Contribute**  

🙏 **Current Status**:  
Due to developer's academic constraints, code contributions are not accepted yet. Issues/feedback are welcome on GitHub.  
### Non-code Contribution Suggestions
1. Literature recommendations: Computational biology/evolutionary algorithm papers
2. Test scenarios: Simulation use cases under different environmental parameters
3. Educational applications: Demo cases for high school/university biology courses

> ⚠⚠⚠️ Warning: Project architecture may undergo breaking changes. Recommended to Fork for secondary development.  
### **Special Thanks**  
- **AI Collaboration**: Core algorithm suggestions from Kimi & DeepSeek-R1  
- **Academic Advisor**: SteveZhang08's high school biology teacher


**VitaeCanvas - 生命绘卷**

> VitaeCanvas - 生命绘卷 ，创造模拟生命体的细胞级演化框架  

> 🌱 *"生命的意义不仅在于存在，更在于理解存在本身"*
## 项目简介
**VitaeCanvas（生命绘卷）** 是一个由一位中国高中生（SteveZhang08）发起的开源项目，旨在通过计算机模拟低级生命体（如单个细胞）的行为，并探索其进化路径。项目使用Python编写，目前处于早期开发阶段。

> 📌 **注意**：  
> - 开发者为高中生，学业繁重，开发进度可能较慢  
> - 开发环境受限（家庭不支持）：Python 3.8.10 / Win7 x64 / AMD A8-5600K / 8GB RAM  
> - 项目架构可能随开发者认知提升而重构  

## 项目目标
### 最终目标是构建一个可扩展的模拟框架，用于：  

1.模拟细胞的基本生命活动（代谢、移动、能量交换等）。  
2.模拟遗传机制（DNA转录、RNA翻译、蛋白质合成）。  
3.探索在环境选择压力下，细胞群体的进化过程。  

## 核心功能 
#### **生命组件模拟**  
| 模块          | 功能描述                            | 关键类/函数                 |  
|---------------|-----------------------------------|---------------------------|  
| **遗传系统**   | DNA序列生成、转录翻译机制          | `DNA`, `RNA`, `Protein`   |  
| **细胞实体**   | 细胞代谢/移动/能量转换             | `Cell`, `CellError`        |  
| **环境引擎**   | 二维网格环境与能量扩散模型          | `Environment`, `Energy`   |  
| **代谢系统**   | 能量吸收与转化控制                 | `MetabolismSystem`         |  

### **项目结构**  
```  
Vitae_System/  
├── cells.py          # 细胞实体/遗传机制  
├── env.py            # 环境引擎/能量模型  
├── metabolism.py     # 代谢控制系统  
├── random_DNA.py     # DNA序列生成器  
└── __init__.py       # 系统配置与版本管理
```  

---

### **发展路线**  
| 阶段       | 目标                          | 状态       |  
|------------|-----------------------------|-----------|  
| 0.1.x      | 单细胞基础代谢                | 🚧 开发中   |  
| 0.2.x      | 多细胞竞争协作                | ⌛ 计划中  |  
| 0.3.x      | 遗传变异/进化算法集成          | ⌛ 计划中  |  
| 1.0        | 生态系统级演化模拟             | ⏳ 长期目标|  

---

## 运行方法
- 确保安装Python（推荐3.8+）。  
- 克隆本仓库。  
- 运行示例主程序(main.py)

## 项目状态
项目处于​​早期开发阶段​​，核心框架仍在构建中。由于作者学业繁重，开发进度可能较慢。欢迎关注项目，但目前​​不主动征集代码贡献​​。

## 未来方向
- 完善细胞分裂和繁殖机制。
- 引入环境因素（如食物、毒素）。
- 实现自然选择和多代进化模拟。
- 优化性能和可视化。

## 贡献  
> 目前项目不接受外部代码贡献，但欢迎提出建议（通过issue）。未来可能会开放贡献。
### **参与贡献**  

🙏 **当前状态**：  
由于开发者学业限制，暂不接受代码贡献，但欢迎在GitHub提交Issue反馈问题  
### 非代码贡献建议
1. 文献推荐：计算生物学/进化算法相关论文
2. 测试场景：不同环境参数下的模拟用例
3. 教学应用：高中/大学生物课演示案例

> ⚠️ 注意：项目架构可能发生破坏性变更，建议Fork分支进行二次开发  
### **特别致谢**  
- **AI协作**：Kimi & DeepSeek-R1 提供核心算法建议  
- **学术顾问**：SteveZhang08 的高中生物教师  

