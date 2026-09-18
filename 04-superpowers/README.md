# 04 · Superpowers 级通用技能精选

> 收录 9 个 GitHub 上**顶级通用 Claude Code / Agent 技能**，覆盖 AI 工程、UI/UX 设计、科研、营销、写作、浏览器自动化、上下文工程等方向。
> 全部为 **MIT 许可**，各技能子目录已**全量收录**（SKILL.md + references/scripts/data + LICENSE；个别 CLI 型技能仅收录 SKILL.md），可离线查阅与二次改造。
>
> 命名致敬 [obra/superpowers](https://github.com/obra/superpowers)（288k ⭐ 的 Agent 技能框架标杆）——本目录收录的是与之同级的**独立顶级技能**，并非 superpowers 本身。

---

## 技能总览

| 技能 | 来源仓库 | ⭐ | 说明 | 规模 |
|------|----------|----|------|------|
| **ui-ux-pro-max-skill** | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 129k | UI/UX 设计智能：风格/配色/字体/图表/技术栈本地检索库 | 7 子技能 |
| **agent-skills** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 96k | 生产级 AI 编码代理工程技能集 | 25 子技能 |
| **planning-with-files** | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27k | 持久化文件式规划（Manus 风格三文件） | 单技能 |
| **agent-skills-for-context-engineering** | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18k | 上下文工程 / 多智能体架构技能集 | 17 子技能 |
| **obsidian-skills** | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | 48.5k | Obsidian 笔记/知识库（CLI、JSON Canvas、Bases） | 6 子技能 |
| **scientific-agent-skills** | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 45.4k | 科研技能库（生物/化学/医学/药物发现） | 166 子技能 |
| **marketingskills** | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 50.7k | 营销技能集（CRO/文案/SEO/增长） | 50 子技能 |
| **dev-browser** | [SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) | 6.6k | 给 agent 浏览器自动化能力（CLI 驱动） | 单技能 |
| **humanizer** | [blader/humanizer](https://github.com/blader/humanizer) | 49.7k | 去除文本中 AI 生成痕迹 | 单技能 |

> ⭐ 数据由本仓库的 GitHub Action（`.github/scripts/update_stars.py`）自动刷新。

---

## 1. ui-ux-pro-max-skill（UI/UX 设计智能）

把「设计总监」级别的品味内置为可检索的本地数据库，做界面时自动调用。

- **能力**：79 种 UI 风格（50 激活）、192 套产品配色、74 组字体配对、119 条 UX 准则、105 图标、17 GSAP 预设、25 图表类型、22 个技术栈（React/Next.js/Vue/SwiftUI/Flutter/shadcn 等）。
- **子技能（7）**：`ui-ux-pro-max`（主）、`design`、`design-system`、`banner-design`、`brand`、`slides`、`ui-styling`。
- **安装**：`npm install -g uipro-cli && uipro init --ai claude`（需 Python 3）。
- 已收录：**完整 7 个子技能**（`skills/` 目录，260 文件，含 `data/` 风格·配色库与 `scripts/` 检索脚本）、`README.md`、`LICENSE`。

## 2. agent-skills（生产级 AI 编码代理技能集）

Addy Osmani（Google Chrome 团队）出品，面向真实工程场景的成套技能。

- **子技能（25）**：`api-and-interface-design`、`browser-testing-with-devtools`、`ci-cd-and-automation`、`code-review-and-quality`、`code-simplification`、`constraint-driven-development`、`context-engineering`、`debugging-and-error-recovery`、`deprecation-and-migration`、`documentation-and-adrs`、`doubt-driven-development`、`frontend-ui-engineering`、`git-workflow-and-versioning`、`idea-refine`、`incremental-implementation`、`interview-me`、`observability-and-instrumentation`、`performance-optimization`、`planning-and-task-breakdown`、`security-and-hardening`、`shipping-and-launch`、`source-driven-development`、`spec-driven-development`、`test-driven-development`、`using-agent-skills`。
- **安装**：`git clone https://github.com/addyosmani/agent-skills && cp -r agent-skills/skills/* ~/.claude/skills/`
- 已收录：**完整 25 个子技能**（`skills/` 目录，含 SKILL.md + references/scripts）、`README.md`、`LICENSE`。

## 3. planning-with-files（持久化文件式规划）

Manus 风格三文件规划，解决上下文易失 / 目标漂移 / 隐藏错误。

- **核心**：`task_plan.md`（阶段与进度）+ `findings.md`（调研） + `progress.md`（会话日志）；「上下文 = 内存（易失），文件系统 = 磁盘（持久）」。
- **特性**：`/clear` 与压缩后自动恢复、SHA-256 计划校验防篡改、完成门禁。
- **安装**：`npm install -g planning-with-files`，或通过 Claude Code 插件市场 / `npx skills` 安装。
- 已收录：`SKILL.md`、`examples.md`、`reference.md`、`scripts/`（22 个 sh/ps1/py 脚本）、`templates/`（7 个模板）、`LICENSE`。

## 4. agent-skills-for-context-engineering（上下文工程技能集）

上下文工程 / 治理 / 多智能体架构的完整技能库。

- **子技能（17）**：`context-fundamentals`、`context-compression`、`context-degradation`、`context-optimization`、`filesystem-context`、`memory-systems`、`latent-briefing`、`long-horizon-prompting`、`multi-agent-patterns`、`harness-engineering`、`hosted-agents`、`bdi-mental-states`、`advanced-evaluation`、`evaluation`、`tool-design`、`project-development`、`self-improvement-loops`。
- **安装**：`git clone https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering && cp -r Agent-Skills-for-Context-Engineering/skills/* ~/.claude/skills/`
- 已收录：**完整 17 个子技能**（`skills/` 目录，57 文件，含 SKILL.md + references）、`README.md`、`LICENSE`。

## 5. obsidian-skills（Obsidian 笔记 / 知识库）

让 agent 使用 Obsidian CLI 与开放格式（Markdown、Bases、JSON Canvas）。

- **子技能（6）**：`obsidian-cli`、`obsidian-markdown`、`obsidian-bases`、`json-canvas`、`knap`（卡片式笔记）、`defuddle`（网页正文提取）。
- **安装**：`git clone https://github.com/kepano/obsidian-skills && cp -r obsidian-skills/skills/* ~/.claude/skills/`
- 已收录：**完整 6 个子技能**（`skills/` 目录，11 文件，含 SKILL.md + references）、`README.md`、`LICENSE`。

## 6. scientific-agent-skills（科研技能库）

> 你列表中的「claude-scientific-skills」在 GitHub 上无单一高星仓库，本目录收录其最匹配的权威版本 **K-Dense-AI/scientific-agent-skills**（科学领域 #1 技能库）。

- **能力**：165+ 科研技能 + 100+ 科学数据库，覆盖生物学 / 化学 / 医学 / 药物发现（RNA-seq、AlphaGenome、UniProt、BLAST 等）。
- **代表子技能（前 30，共 166）**：`alphagenome`、`biopython`、`bulk-rnaseq`、`cellxgene-census`、`clinical-reports`、`cobrapy`、`datamol`、`deepchem`、`depmap`、`diffdock`、`esm`、`experimental-design`、`exploratory-data-analysis`、`anndata`、`astropy`、`bids`、`cirq`、`dask`、`citation-management`、`datalad`、`flowio` ……
- **安装**：`git clone https://github.com/K-Dense-AI/scientific-agent-skills && cp -r scientific-agent-skills/skills/* ~/.claude/skills/`
- 已收录：**完整 166 个子技能**（`skills/` 目录，2068 文件，含 SKILL.md + references/scripts）、`README.md`、`LICENSE.md`。

## 7. marketingskills（营销技能集）

CRO、文案、SEO、分析、增长工程等全套营销技能。

- **子技能（50）**：`copywriting`、`copy-editing`、`cro`、`ai-seo`、`seo-audit`、`programmatic-seo`、`schema`、`site-architecture`、`content-strategy`、`ab-testing`、`analytics`、`attribution`、`revops`、`sales-enablement`、`product-marketing`、`pricing`、`offers`、`paywalls`、`popups`、`signup`、`onboarding`、`churn-prevention`、`cold-email`、`emails`、`sms`、`prospecting`、`lead-magnets`、`ads`、`ad-creative`、`social`、`video`、`image`、`influencer-marketing`、`community-marketing`、`co-marketing`、`referrals`、`public-relations`、`events`、`directory-submissions`、`competitors`、`competitor-profiling`、`customer-research`、`marketing-plan`、`marketing-ideas`、`marketing-psychology`、`marketing-loops`、`marketing-council`、`launch`、`free-tools`、`aso`。
- **安装**：`git clone https://github.com/coreyhaines31/marketingskills && cp -r marketingskills/skills/* ~/.claude/skills/`
- 已收录：**完整 50 个子技能**（`skills/` 目录，279 文件，含 SKILL.md + references）、`README.md`、`LICENSE`。

## 8. dev-browser（浏览器自动化）

通过 `dev-browser` CLI 让 agent 具备持久化命名页面的浏览器自动化能力。

- **能力**：导航网站、填表单、截图、抓取网页数据、测试 Web 应用、登录、自动化浏览器工作流。
- **触发词**：`go to [url]`、`click on`、`fill out the form`、`take a screenshot`、`scrape`、`automate`、`log into`、`open the browser`。
- **安装**：`git clone https://github.com/SawyerHood/dev-browser && cp -r dev-browser/skills/dev-browser ~/.claude/skills/`（需 Bun）。
- 已收录：`SKILL.md`、`LICENSE`。

## 9. humanizer（去除 AI 生成痕迹）

消除文本中 AI 生成的痕迹，让输出更像人写的。

- **能力**：识别并改写 AI 常见表达模式、句式与用词，提升文本自然度。
- **安装**：把 `SKILL.md` 与 `scripts/` 拷贝到 `~/.claude/skills/humanizer/`。
- 已收录：`SKILL.md`、`LICENSE`（`scripts/` 请从上游仓库取）。

---

## 安装方式（通用）

每个技能目录整体拷贝到项目的 `.claude/skills/<技能名>/` 即可自动加载；全局用 `~/.claude/skills/`。带 CLI / npm 分发方式的（ui-ux-pro-max、planning-with-files）见上文各自说明。

## 许可

9 个上游仓库均为 **MIT 许可**，本目录收录的 SKILL.md / README / LICENSE 均保留原始版权声明，二次使用请遵循 MIT 许可。
