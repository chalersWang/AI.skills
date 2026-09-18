# 02 · 芯片研发 / 验证（本地技能，已收录）

> 本目录收录的是**本地自建/自用的芯片验证技能**（原位于 `~/.claude/skills` 与 `~/.agents/skills`），打包上传以便团队共享与版本管理。
> 相比 GitHub 上稀缺的芯片 EDA 技能，这 7 个技能质量更高、更贴合实际验证流程，建议作为主力使用。

---

## 技能清单

| 技能 | 说明 | 关键内容 |
|------|------|----------|
| **chip-verif-reviewer** | 验证测试点评审：按 ST/IT/BT/UT 分层审查测试点、补充 checklist | `references/`（AXI checklist、验证层级）、`test/` 示例 |
| **dv_skills** | 芯片前端验证技能库（RTL 仿真 + UVM + EDA 工具） | `references/` 14 篇：UVM/覆盖率/CDC/低功耗/RAL/AMBA/DDR/VIP/约束/BVA |
| **sva-coverage** | SVA 断言 + 功能覆盖率：immediate/concurrent、property/sequence、covergroup/coverpoint、交叉覆盖率 | 单文件 SKILL.md |
| **uvm-verification** | UVM 测试平台：agent/driver/monitor/scoreboard/sequence/factory/TLM/寄存器模型 | 单文件 SKILL.md |
| **vcs-simulation** | VCS 编译仿真 + Verdi 调试：编译选项、波形 dump、覆盖率、debug flags | 单文件 SKILL.md |
| **systemverilog** | SystemVerilog 开发规范：模块化设计、验证、时序优化 | 单文件 SKILL.md |
| **claude-skill-verilog** | Verilog/SystemVerilog 编码风格 + Verilator 工作流 | 单文件 SKILL.md |

## 使用方式

将需要的技能目录（如 `dv_skills/`）整体拷贝到项目的 `.claude/skills/` 下即可自动加载：

```bash
# 例如在本仓库克隆后
cp -r 02-chip/verification/dv_skills  你的项目/.claude/skills/dv_skills
cp -r 02-chip/verification/sva-coverage 你的项目/.claude/skills/sva-coverage
```

## 覆盖的技术方向

- **验证方法学**：UVM、覆盖率驱动验证（CDV）、验证计划、测试点分层评审
- **协议**：AMBA（AXI/AHB/APB）、DDR
- **专项**：CDC 检查、低功耗验证、寄存器模型（RAL）、VIP 使用、边界值分析
- **语言**：SystemVerilog、SVA 断言、Verilog 编码风格
- **工具链**：VCS / Verdi / Verilator
