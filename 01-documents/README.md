# 01 · 文档类（读取 & 编辑）

涵盖 PDF、Word、Excel、PPT，以及画图 / 流程图（draw.io / Mermaid / Excalidraw / SVG）。

> 目录内已收录：官方文档技能 `pdf/`、`docx/`、`xlsx/`、`pptx/`（**完整本地版本，含 scripts 脚本与 LICENSE**）、`doc-coauthoring`（文档协作）、`feishu-reader`（飞书文档，**已脱敏**），以及 `diagram/` 社区画图技能。其余以链接形式索引。

---

## 1.1 PDF
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **pdf**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pdf) | 官方 | PDF 读取、表单提取、文本抽取，Claude 官方文档技能 |
| **graphify** | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 118k | 代码库 + 文档 + SQL + PDF → 可查询知识图谱 |
| **book-to-skill** | [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) | 31k | 技术书 PDF 一键转 Claude Code skill |
| **Skill_Seekers** | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | 15k | 文档站 / GitHub 仓库 / PDF → skill，含冲突检测 |

**官方 PDF 技能安装：**
```bash
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

## 1.2 Word（docx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **docx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/docx) | 官方 | .docx 创建与编辑，Claude 官方文档技能 |
| **genoffice** | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 7.0k | 本地创建/编辑真实 .docx/.xlsx/.pptx，免费开源 |
| **SoftwareCopyright-Skill** | [Fokkyp/SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | 5.4k | 自动生成全套软著申请 .docx（中文） |
| **claude-office-skills** | [tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) | 827 | PPTX/DOCX/XLSX/PDF 全套工作流 |

## 1.3 Excel（xlsx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **xlsx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/xlsx) | 官方 | .xlsx 创建、公式、数据分析 |
| **genoffice** | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 7.0k | 本地创建/编辑 .xlsx（含公式） |
| **claude-office-skills** | [tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) | 827 | XLSX 工作流自动化 |

## 1.4 PPT（pptx）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **pptx**（官方） | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pptx) | 官方 | .pptx 生成与编辑，Claude 官方文档技能 |
| **dashi-ppt-skill** | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | 8.3k | 多主题、浏览器可编辑演示，导出 HTML/PDF/PPTX |
| **codex-ppt-skill** | [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | 6.0k | 基于图片的 PowerPoint 生成 |
| **GordenPPTSkill** | [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | 3.1k | 17 套中文 PPTX 模板 + 非破坏性文字编辑 |

## 1.6 文档协作 · 知识库阅读（本地技能）
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **doc-coauthoring** | [本地收录](./doc-coauthoring/) | 本地 | 结构化文档协作工作流（上下文收集→迭代精炼→读者验证） |
| **feishu-reader** | [本地收录（已脱敏）](./feishu-reader/) | 本地 | 读取/操作飞书文档与知识库（需自行填入应用凭据） |

---

## 1.5 画图 · 流程图
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **drawio-skill** | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) | 9.4k | 自然语言/代码 → 可编辑 draw.io 架构图 |
| **architecture-diagram-generator** | [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) | 7.3k | 深色主题架构图，输出 HTML/SVG |
| **excalidraw-diagram-skill** | [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | 4.8k | 生成美观实用的 Excalidraw 图 |
| **axton-obsidian-visual-skills** | [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills) | 3.6k | 文本 → Canvas / Excalidraw / Mermaid |
| **Pretty-mermaid-skills** | [imxv/Pretty-mermaid-skills](https://github.com/imxv/Pretty-mermaid-skills) | 1.2k | Mermaid → SVG / 终端 ASCII，15 主题 |
| **svg-diagram** | [bybit-exchange/svg-diagram](https://github.com/bybit-exchange/svg-diagram) | 562 | 架构/流程/时序/数据流 SVG |
| **mermaid-skill** | [WH-2099/mermaid-skill](https://github.com/WH-2099/mermaid-skill) | 279 | 全类型 Mermaid 图生成 |
