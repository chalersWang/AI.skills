# 02 · 芯片研发

芯片设计 / 验证 / 中后端 + 硬件语言 + Synopsys 工具链。

> ⚠️ **现状说明**：GitHub 上专门的芯片 / EDA 方向 Claude Skill 目前非常稀缺、星数普遍偏低（几十~几百）。以下为当前能找到的相对靠前者；**你本地已装的一整套芯片技能质量更高，建议作为主力**（见文末「本地技能」）。

---

## 2.1 芯片设计 · 验证 · 中后端
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **verilog-generator** | [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) | 293 | Verilog-2001 RTL 生成 + FPGA 设计流程 |
| **30-days-of-verilog** | [Akashtailor-exe/30-days-of-verilog](https://github.com/Akashtailor-exe/30-days-of-verilog) | 75 | 30 天 Verilog 数字电路练习（门级→FSM） |
| **108-RTL-Projects** | [Abhishekvlsi/108-RTL-Projects](https://github.com/Abhishekvlsi/108-RTL-Projects) | 64 | 108 个 RTL 设计项目 |
| **RTL-ASS** | [liujianyu20021122/RTL-ASS](https://github.com/liujianyu20021122/RTL-ASS) | 63 | 开源工具链的 RTL 编码 + 验证技能 |
| **veriflow-cc** | [bjwanneng/veriflow-cc](https://github.com/bjwanneng/veriflow-cc) | 51 | 架构→综合（iVerilog/Yosys）RTL 流水线 |
| **rtl-skills** | [phamcuong21478/rtl-skills](https://github.com/phamcuong21478/rtl-skills) | 14 | 全 RTL 流程：架构/RTL/lint/仿真/回归/综合/文档 |

> cpu / gpu / npu / riscv / noc / pcie / lpddr / 3d-dram / c2c / d2d 等细分方向，GitHub 上暂无成体系的公开 skill，需以通用 RTL/验证技能 + 本地技能组合实现。

## 2.2 语言类（VHDL / Verilog / SV / UVM / Coverage / SVA / C / C++ / Python / Tcl / Makefile）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **verilog-generator** | [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) | 293 | Verilog RTL |
| **RTL-ASS** | [liujianyu20021122/RTL-ASS](https://github.com/liujianyu20021122/RTL-ASS) | 63 | Verilog / SystemVerilog |
| **awesome-formal-verification-skill** | [gokeshenzhen/awesome-formal-verification-skill](https://github.com/gokeshenzhen/awesome-formal-verification-skill) | 34 | SVA / FPV（JasperGold，含 TCL） |
| **veriloga-skills** | [Arcadia-1/veriloga-skills](https://github.com/Arcadia-1/veriloga-skills) | 34 | Verilog-A 模拟建模 |

> C / C++ / Python / Tcl / Makefile 建议复用主流通用编程 skill；芯片专用封装少。

## 2.3 工具（Synopsys 全流程：VCS / Verdi / Formality / PrimeTime / SpyGlass）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **awesome-formal-verification-skill** | [gokeshenzhen/awesome-formal-verification-skill](https://github.com/gokeshenzhen/awesome-formal-verification-skill) | 34 | FPV/SVA/TCL 工作流 |
| **vcs-simulation**（本地） | 你本地已装 | — | VCS 编译/仿真流程 |

> 专门的 VCS / Verdi / Formality / PrimeTime / SpyGlass 等 Synopsys 全流程 skill 在 GitHub 上基本空白。**建议**以本地技能为主力，按需二次封装成团队 skill。

---

## 📦 本地芯片技能（已收录到本仓库）

这 7 个本地自建技能已打包上传到 [`verification/`](./verification/) 目录：

| 技能 | 用途 |
|------|------|
| `dv_skills` | 芯片前端验证技能库（UVM/覆盖率/CDC/低功耗/RAL/AMBA/DDR/VIP，14 篇 reference） |
| `chip-verif-reviewer` | 验证测试点分层评审（ST/IT/BT/UT） |
| `uvm-verification` | UVM 验证平台开发 |
| `sva-coverage` | SVA 断言 + 功能覆盖率 |
| `vcs-simulation` | VCS 编译仿真 + Verdi 调试 |
| `systemverilog` | SystemVerilog 开发规范 |
| `claude-skill-verilog` | Verilog 编码风格 + Verilator |

> 详见 [`verification/README.md`](./verification/README.md)。
