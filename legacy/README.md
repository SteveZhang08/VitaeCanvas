# legacy —— 历史界面代码封存区

本目录存放**已废弃的界面代码**，仅作历史留存与设计参考，**不参与主项目运行，不要 import**。

## 内容

| 路径 | 说明 | 时期 |
|---|---|---|
| `gui_cell.py` | tkinter 单细胞数据面板（创建细胞、看蛋白质序列/代谢率/颜色统计）。`dist/中文/3.安装指南.md` 曾把它当作"项目的 GUI"。 | 2025-10 ~ 2026-02 |
| `sim.py` | `main.py` 的**非阻塞版本**（把原来的 `while True` 拆成 `SimulationController.run()`），供 `aigui/` 各原型 import。 | 2026-04-26 |
| `new_gui/` | tkinter 控制面板 + pygame 渲染窗口的双窗口方案。`main.py` 为入口，`tkinter_control.py`（1058 行）为控制面板，`simulation_controller.py` 含代谢线程，`old.py` 是拆分前的单体版本。 | 2026-01-11 |
| `window_gui/` | tkinter 纯 MVC 分层实现（views / controllers / models / utils）。含 `SimulationThread` 定步长 60 Hz 线程模型与 `EventBus` 事件总线。**架构最完整的一套，但代码停留在旧 API，从未真正跑通。** 重构时的事件总线设计可参考此目录。 | 2026-01-01 |

## 已删除（未保留）

以下界面代码在 2026 年重构清理中直接删除，未封存（仍可在 git 历史 `9e8d2f5` 中找到）：

- `gui/`、`aigui/` —— DearPyGUI 2.2 两批界面原型
- `gui.py` —— pygame 网格可视化
- `tools/gui.py` —— tkinter + pygame + matplotlib + Pillow 缝合调试面板
- `tools/Protein_structure_show_by_turtle.py` —— 基于 `turtle` 的蛋白质结构预览

## 当前保留的工具（非界面）

`tools/DNA_Generation.py`、`tools/GUI_DNA_Generation.py`（密码子工具）、`tools/Protein_structure_show.py`（matplotlib 出图）保留在主目录，被视为工具而非界面。
