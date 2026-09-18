# 03 · 管理类（项目管理 · 进度 · 汇报）

> GitHub 上「项目管理 / 进度 / 汇报」方向的专用 Claude Skill 同样稀缺，`ccpm` 是当前最成熟的标杆。其余需求可结合文档类技能（`docx`/`xlsx`/`pptx`）与本地 `feishu-reader` 组合实现。

---

## 3.1 项目管理 · 进度 · 汇报
| 技能 | 来源 | ⭐ | 说明 |
|------|------|----|------|
| **ccpm** | [automazeio/ccpm](https://github.com/automazeio/ccpm) | 8.4k | 项目管理 skill 系统：用 GitHub Issues + git worktree 并行执行 agent 任务 |

## 组合方案（汇报 / 周报 / 进度）

| 需求 | 推荐技能组合 |
|------|--------------|
| 项目进度跟踪 | `ccpm`（GitHub Issues 工作流） |
| 周报 / 汇报材料 | 文档类 `docx` + `pptx` |
| 数据报表 | 文档类 `xlsx` |
| 飞书文档 / 知识库 | 本地 `feishu-reader` |
| 项目复盘 / 评审 | 本地 `chip-verif-reviewer`（芯片场景） |
