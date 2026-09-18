# AI.skills — Claude Code Skills 精选合集

> 从 GitHub 收集**排名靠前**的 Claude Code / Agent Skills，按「文档 / 芯片研发 / 管理」三大类整理。
> 每个技能标注来源仓库、星数与一句话说明，附获取方式。星数来自 GitHub 实时数据（2026-09 整理）。

Skills 是「文件夹 + SKILL.md」形式的指令包，Claude Code 等 agent 按需动态加载，用来教会 agent 完成特定任务（文档、EDA、项目管理等）。本仓库是一个**分类索引**，并对核心技能附上其 SKILL.md 正文，方便离线查阅与二次改造。

---

## 目录

| 大类 | 子类 | 链接 |
|------|------|------|
| **1. 文档类** | PDF / Word / Excel / PPT / 画图·流程图 | [01-documents](./01-documents/) |
| **2. 芯片研发** | 设计·验证·中后端 / 语言 / Synopsys 工具 | [02-chip](./02-chip/) |
| **3. 管理类** | 项目管理 / 进度 / 汇报 | [03-management](./03-management/) |

---

## 1. 文档类（读取 & 编辑）

> 📦 官方文档技能（pdf/docx/xlsx/pptx）已收录**完整本地版本**（含 scripts 脚本）；另收录本地技能 `doc-coauthoring`（文档协作）、`feishu-reader`（飞书文档，已脱敏）。

### 1.1 PDF
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **pdf**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pdf) | 官方 | PDF 读取、表单提取、文本抽取，Claude 官方文档技能 |
| **graphify** | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 119k | 把代码库 + 文档 + SQL + PDF 变成可查询知识图谱 |
| **book-to-skill** | [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) | 31.1k | 把技术书 PDF 一键转成 Claude Code skill |
| **Skill_Seekers** | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | 15k | 文档站 / GitHub 仓库 / PDF → skill，含冲突检测 |

### 1.2 Word（docx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **docx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/docx) | 官方 | .docx 创建与编辑，Claude 官方文档技能 |
| **genoffice** | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 7.1k | 本地创建/编辑真实 .docx/.xlsx/.pptx，免费开源 |
| **SoftwareCopyright-Skill** | [Fokkyp/SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | 5.5k | 自动生成全套软著申请 .docx 材料（中文） |
| **claude-office-skills** | [tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) | 828 | PPTX/DOCX/XLSX/PDF 全套工作流 |

### 1.3 Excel（xlsx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **xlsx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/xlsx) | 官方 | .xlsx 创建、公式、数据分析，Claude 官方文档技能 |
| **genoffice** | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 7.1k | 本地创建/编辑 .xlsx（含公式） |
| **claude-office-skills** | [tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) | 828 | XLSX 工作流自动化 |

### 1.4 PPT（pptx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **pptx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pptx) | 官方 | .pptx 生成与编辑，Claude 官方文档技能 |
| **dashi-ppt-skill** | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | 8.4k | 多视觉主题、浏览器可编辑的演示，导出 HTML/PDF/PPTX |
| **codex-ppt-skill** | [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | 6k | 基于图片的 PowerPoint 生成 |
| **GordenPPTSkill** | [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | 3.1k | 17 套中文 PPTX 模板 + 非破坏性文字编辑 |

### 1.5 画图 · 流程图
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **drawio-skill** | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) | 9.4k | 自然语言/代码 → 可编辑 draw.io 架构图（含 Mermaid/PPTX 导出） |
| **architecture-diagram-generator** | [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) | 7.3k | 深色主题系统架构图，输出 HTML/SVG |
| **excalidraw-diagram-skill** | [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | 4.8k | 生成美观实用的 Excalidraw 图 |
| **axton-obsidian-visual-skills** | [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills) | 3.6k | 文本 → Canvas / Excalidraw / Mermaid |
| **Pretty-mermaid-skills** | [imxv/Pretty-mermaid-skills](https://github.com/imxv/Pretty-mermaid-skills) | 1.2k | Mermaid 图 → SVG / 终端 ASCII，15 主题 6 类图 |
| **svg-diagram** | [bybit-exchange/svg-diagram](https://github.com/bybit-exchange/svg-diagram) | 566 | 架构/流程/时序/数据流图，手绘级 SVG |
| **mermaid-skill** | [WH-2099/mermaid-skill](https://github.com/WH-2099/mermaid-skill) | 280 | 全类型 Mermaid 图生成 |

---

## 2. 芯片研发

> ⚠️ **现状说明**：GitHub 上专门的芯片 / EDA 方向 Claude Skill 目前非常稀缺、星数普遍偏低（多在几十~几百）。下方列出的是当前能找到的**相对靠前**者；你本地已装的一整套芯片技能（见「本地技能」）质量更高，建议作为主力。

### 2.1 芯片设计 · 验证 · 中后端
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **verilog-generator** | [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) | 287 | Verilog-2001 RTL 生成 + FPGA 设计流程 |
| **30-days-of-verilog** | [Akashtailor-exe/30-days-of-verilog](https://github.com/Akashtailor-exe/30-days-of-verilog) | 75 | 30 天 Verilog 数字电路练习（门级→FSM） |
| **108-RTL-Projects** | [Abhishekvlsi/108-RTL-Projects](https://github.com/Abhishekvlsi/108-RTL-Projects) | 64 | 108 个 RTL 设计项目（简单电路→复杂系统） |
| **RTL-ASS** | [liujianyu20021122/RTL-ASS](https://github.com/liujianyu20021122/RTL-ASS) | 63 | 开源工具链的 RTL 编码 + 验证技能 |
| **veriflow-cc** | [bjwanneng/veriflow-cc](https://github.com/bjwanneng/veriflow-cc) | 51 | 架构→综合（iVerilog/Yosys）的 RTL 流水线 |
| **rtl-skills** | [phamcuong21478/rtl-skills](https://github.com/phamcuong21478/rtl-skills) | 14 | 全 RTL 流程：架构/RTL/lint/仿真/回归/综合/文档 |

> cpu / gpu / npu / riscv / noc / pcie / lpddr / 3d-dram / c2c / d2d 等细分方向，GitHub 上暂无成体系的公开 skill，主要依赖本地技能与上述通用 RTL/验证技能组合使用。

### 2.2 语言类（VHDL / Verilog / SV / UVM / Coverage / SVA / C / C++ / Python / Tcl / Makefile）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **verilog-generator** | [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) | 287 | Verilog RTL |
| **RTL-ASS** | [liujianyu20021122/RTL-ASS](https://github.com/liujianyu20021122/RTL-ASS) | 63 | Verilog / SystemVerilog |
| **awesome-formal-verification-skill** | [gokeshenzhen/awesome-formal-verification-skill](https://github.com/gokeshenzhen/awesome-formal-verification-skill) | 34 | SVA / FPV 形式验证（JasperGold） |
| **veriloga-skills** | [Arcadia-1/veriloga-skills](https://github.com/Arcadia-1/veriloga-skills) | 34 | Verilog-A（模拟建模） |

> C / C++ / Python / Tcl / Makefile 等通用语言，建议复用主流通用编程 skill（如 anthropics 官方示例与第三方 coding skill），芯片专用封装较少。

### 2.3 工具（Synopsys 全流程：VCS / Verdi / Formality / PrimeTime / SpyGlass）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **awesome-formal-verification-skill** | [gokeshenzhen/awesome-formal-verification-skill](https://github.com/gokeshenzhen/awesome-formal-verification-skill) | 34 | FPV/SVA/TCL 工作流（JasperGold 形式验证，含 TCL 脚本） |
| **vcs-simulation**（已收录） | [verification/vcs-simulation](./02-chip/verification/vcs-simulation/) | 本地 | VCS 仿真流程技能 |

> 专门的 VCS / Verdi / Formality / PrimeTime / SpyGlass 等 Synopsys 全流程 skill 在 GitHub 上基本空白，本仓库已收录本地自建的 7 个芯片技能作为主力（见下方）。

### 📦 本地芯片技能（已收录到 `verification/`）
| 技能 | 用途 |
|------|------|
| `dv_skills` | 芯片前端验证技能库（UVM/覆盖率/CDC/低功耗/RAL/AMBA/DDR/VIP，14 篇 reference） |
| `chip-verif-reviewer` | 验证测试点分层评审（ST/IT/BT/UT） |
| `uvm-verification` | UVM 验证平台开发 |
| `sva-coverage` | SVA 断言 + 功能覆盖率 |
| `vcs-simulation` | VCS 编译仿真 + Verdi 调试 |
| `systemverilog` | SystemVerilog 开发规范 |
| `claude-skill-verilog` | Verilog 编码风格 + Verilator |

> 详见 [`02-chip/verification/README.md`](./02-chip/verification/README.md)。

---

## 3. 管理类

### 3.1 项目管理 · 进度 · 汇报
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **ccpm** | [automazeio/ccpm](https://github.com/automazeio/ccpm) | 8.4k | 项目管理 skill 系统：用 GitHub Issues + git worktree 并行执行 agent 任务 |

> 项目管理 / 进度 / 汇报方向的专用 skill 在 GitHub 上同样稀缺，`ccpm` 是当前最成熟的标杆。其余需求建议结合本地 `feishu-reader`（飞书文档/知识库）、`docx`/`xlsx`/`pptx`（周报/汇报材料）组合实现。

---

## 使用方式

**快速安装（官方文档技能）：**
```bash
# 在 Claude Code 中注册官方 marketplace
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

**安装第三方技能：** 将仓库中的 `SKILL.md`（及配套脚本）放入项目的 `.claude/skills/<技能名>/` 目录即可被自动加载；或 `git clone` 后按需拷贝。

**本仓库结构：** 每个子类目录下附有该子类核心技能的 `SKILL.md` 正文，供离线查阅与二次改造。

---

## 数据来源与更新

- 星数通过 GitHub Search API 实时抓取（`sort=stars`），整理日期 2026-09-17。
- ⚖️ **许可说明**：`anthropics/skills` 的文档技能（pdf/docx/xlsx/pptx）为 source-available（专有许可，仅供参考），已收录的 SKILL.md 均标注原始出处与作者；其余社区技能遵循各自仓库的开源许可。二次使用时请遵循上游许可。
- 主要参考：[anthropics/skills](https://github.com/anthropics/skills)（官方）、[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)、[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)。
