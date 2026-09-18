---
name: dv_skills
version: "1.0.0"
description: |
  芯片前端验证工程师技能库。面向芯片前端验证（RTL仿真 + UVM + EDA工具）。

  触发场景：
  (1) UVM验证环境搭建、sequence/sequencer/driver编写
  (2) SystemVerilog约束随机、覆盖率模型设计
  (3) AMBA协议验证（AXI/AHB/APB）
  (4) 寄存器模型（RAL）构建与验证
  (5) CDC跨时钟域验证
  (6) EDA工具使用（VCS/Questa/Verdi）
  (7) 芯片验证测试点评审、覆盖率收敛
---

# DV Skills - 芯片前端验证工程师技能库

## 核心定位

芯片前端验证（RTL级验证）技能沉淀，聚焦 **UVM + SystemVerilog + EDA工具**。

## 知识结构

```
dv_skills/
├── references/
│   ├── boundary_value_analysis.md    # 边界值分析（已存在）
│   ├── coverage_model_design.md      # 覆盖模型设计（已存在）
│   ├── verification_methodology.md   # 验证方法论（已存在）
│   ├── vip_usage.md                 # VIP使用（已存在）
│   ├── amba_verification.md          # AMBA协议验证（已存在）
│   ├── ddr_verification.md           # DDR验证（已存在）
│   ├── low_power_verification.md     # 低功耗验证（已存在）
│   ├── uvm_verification.md           # UVM基础（已存在）
│   ├── sv_constraints.md             # SV约束随机 ← 新增
│   ├── uvm_advanced.md              # UVM进阶 ← 新增
│   ├── coverage_convergence.md       # 覆盖率收敛 ← 新增
│   ├── ral_verification.md          # 寄存器RAL验证 ← 新增
│   ├── cdc_verification.md          # CDC跨时钟域 ← 新增
│   └── eda_tool_guide.md            # EDA工具指南 ← 新增
```

## 快速索引

| 场景 | 参考文件 |
|------|---------|
| UVM component/sequence/factory 基础 | `references/uvm_verification.md` |
| 约束随机技巧（权重/条件/solve before） | `references/sv_constraints.md` |
| UVM进阶（phase/objection/config_db/layered sequence） | `references/uvm_advanced.md` |
| 覆盖组/coverpoint/cross/收敛策略 | `references/coverage_convergence.md` |
| RAL模型构建、mirror/predict/update | `references/ral_verification.md` |
| 异步FIFO/握手同步/CDC检查清单 | `references/cdc_verification.md` |
| VCS/Questa编译/仿真/覆盖率/调试 | `references/eda_tool_guide.md` |
| AMBA AXI/AHB/APB协议验证 | `references/amba_verification.md` |
| 边界值分析/覆盖模型设计 | `references/coverage_model_design.md` |

## 验证流程（参考）

```
规划 → 环境构建 → 执行 → Sign-off
```

### 覆盖模型设计原则

1. **分层覆盖**：系统级 → 集成级 → 模块级
2. **覆盖点**：单项 + 交叉 + 过渡 + 序列
3. **收敛策略**：定向 → 随机扩展 → 缺口填补 → 边界强化

### 覆盖率目标（参考）

| 类型 | 目标 | 说明 |
|------|------|------|
| 行覆盖 | >95% | 核心路径 |
| 分支覆盖 | >90% | 所有分支 |
| FSM覆盖 | 100% | 状态机全状态 |
| 功能覆盖 | 100% | 所有功能点 |

## 评审能力

配合 `chip-verif-reviewer` skill 可对测试点进行分层评审（ST/IT/BT/UT），
补充完善验证 checklist，参考 `skills/chip-verif-reviewer/SKILL.md`。

---
*持续学习，持续验证*
