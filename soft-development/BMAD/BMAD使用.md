# BMAD 使用指南

> 基于本地仓库 `/home/yuchao/sources/BMAD-METHOD` 当前代码整理。当前 `package.json` 版本为 `bmad-method@6.10.0`。最后整理日期：2026-07-16。

## 1. BMAD 是什么

BMAD（Build More Architect Dreams / BMad Method）是一个面向 AI 辅助软件交付的结构化方法框架。它把“让 AI 写代码”拆成一组可复用的 Agent、Skill 和 Workflow，让 AI 在不同阶段扮演不同角色：业务分析、产品经理、UX、架构师、开发者、技术写作、代码审查等。

BMAD 的核心价值不是多几个提示词，而是为 AI 提供稳定上下文：

- 先把需求、约束、成功标准说清楚，再进入实现。
- 每个阶段产出文件，后续阶段读取这些文件，减少上下文漂移。
- 对小改动提供 Quick Dev，对中大型项目提供完整 PRD + 架构 + Epic/Story 流程。
- 支持多 IDE/CLI 的 Skill 安装方式，例如 Claude Code、Codex、Cursor、GitHub Copilot 等。

## 2. 核心概念速览

| 概念 | 含义 | 常见例子 |
| --- | --- | --- |
| Module | BMAD 的功能包。安装时选择模块，模块提供 Agent、Workflow、Task、Tool | `bmm`、`bmb`、`tea`、`cis`、`gds` |
| Skill | 在 AI IDE 中可直接调用的能力目录，核心文件是 `SKILL.md` | `bmad-help`、`bmad-prd`、`bmad-quick-dev` |
| Agent Skill | 加载某个专业角色，并提供菜单触发码 | `bmad-agent-pm`、`bmad-agent-dev` |
| Workflow Skill | 运行一个结构化流程，通常会读写项目文件 | `bmad-prd`、`bmad-architecture` |
| Task / Tool Skill | 独立工具型能力 | `bmad-shard-doc`、`bmad-index-docs` |
| Artifact | Workflow 产出的上下文文档 | PRD、Architecture、Epic、Story、`project-context.md` |

使用时优先记住两句话：

1. 不确定下一步就调用 `bmad-help`。
2. 每个较大的 workflow 都尽量新开一个 AI 会话，避免上下文互相污染。

## 3. 环境要求

当前仓库 README 和安装器要求：

- Node.js `20.12+`
- Python `3.10+`
- `uv` 包管理器
- Git（强烈建议，用于版本控制和安装外部模块）
- 一个支持项目 Skill / Agent 上下文的 AI 编码工具

常用 AI 工具：

| 工具 ID | 名称 | 项目内 Skill 目录 |
| --- | --- | --- |
| `claude-code` | Claude Code | `.claude/skills/` |
| `codex` | Codex CLI | `.agents/skills/` |
| `cursor` | Cursor | `.agents/skills/` |
| `github-copilot` | GitHub Copilot | `.agents/skills/`，并生成 `.github/agents/` agent 文件 |
| `windsurf` | Windsurf | `.agents/skills/` |

完整工具列表可用安装器查看：

```bash
npx bmad-method install --list-tools
```

如果你在 BMAD 源码仓库本地运行安装器，先安装依赖：

```bash
cd /home/yuchao/sources/BMAD-METHOD
npm ci
node tools/installer/bmad-cli.js install --list-tools
```

## 4. 安装 BMAD

### 4.1 交互式安装

在目标项目根目录执行：

```bash
npx bmad-method install
```

安装器会询问：

1. 安装目录，默认当前目录。
2. 要安装哪些模块，默认会选择 BMad Method（`bmm`）。
3. 外部模块使用 stable / next / pinned 哪个版本渠道。
4. 要集成哪些 AI 工具或 IDE。
5. 用户名、沟通语言、文档输出语言、输出目录等配置。

如果想体验预发布版安装器与内置 core/bmm：

```bash
npx bmad-method@next install
```

### 4.2 非交互式安装

适合 CI、模板项目、批量初始化：

```bash
npx bmad-method install --yes \
  --directory /path/to/project \
  --modules bmm \
  --tools claude-code
```

安装 BMM，并显式设置配置：

```bash
npx bmad-method install --yes \
  --modules bmm \
  --tools codex \
  --set core.communication_language=中文 \
  --set core.document_output_language=中文 \
  --set bmm.user_skill_level=expert \
  --set bmm.project_knowledge=docs
```

查看可配置项：

```bash
npx bmad-method install --list-options
npx bmad-method install --list-options bmm
```

常用参数：

| 参数 | 用途 |
| --- | --- |
| `--yes`, `-y` | 跳过交互，接受默认值或命令行传入值 |
| `--directory <path>` | 指定安装到哪个项目目录 |
| `--modules <a,b>` | 指定完整模块集合；core 会自动包含 |
| `--tools <a,b>` | 指定 AI 工具，例如 `claude-code,codex,cursor` |
| `--list-tools` | 列出支持的工具 ID |
| `--set <module>.<key>=<value>` | 非交互设置模块配置，可重复传入 |
| `--list-options [module]` | 查看可用 `--set` key |
| `--action install|update|quick-update` | 指定对已有安装的动作 |
| `--custom-source <urls>` | 从 Git URL 或本地路径安装自定义模块 |
| `--channel stable|next` | 设置外部模块渠道 |
| `--all-stable` / `--all-next` | 外部模块全部使用 stable 或 next |
| `--next <code>` | 指定某个外部模块使用 main HEAD |
| `--pin <code>=<tag>` | 固定某个外部模块到指定 tag |

注意：`core` 和 `bmm` 是随 `bmad-method` 安装器打包的内置模块，版本由你运行的 npm 包版本决定。`--pin bmm=...` 或 `--next bmm` 对当前架构无效。

## 5. 安装后目录结构

典型项目结构：

```text
your-project/
├── _bmad/                         # BMAD 安装、模块、脚本、配置
│   ├── core/
│   ├── bmm/
│   ├── _config/
│   ├── config.toml                 # 团队级安装配置
│   ├── config.user.toml            # 用户级安装配置
│   └── custom/                     # 自定义覆盖，手动创建或由 bmad-customize 创建
├── _bmad-output/                   # 默认产物目录
│   ├── planning-artifacts/          # PRD、UX、架构、epic 等规划产物
│   ├── implementation-artifacts/    # sprint、story、review、quick-dev 产物
│   └── project-context.md           # 可选，项目级 AI 实现规则
├── .claude/skills/                 # Claude Code 选择时生成
└── .agents/skills/                 # Codex / Cursor / Windsurf 等选择时生成
```

每个 Skill 目录通常形如：

```text
.agents/skills/bmad-help/SKILL.md
.agents/skills/bmad-prd/SKILL.md
.agents/skills/bmad-agent-dev/SKILL.md
```

调用方式通常就是在 AI 工具中输入 Skill 名称，例如：

```text
bmad-help
bmad-prd
bmad-agent-dev
```

## 6. 官方模块

以当前仓库 `bmad-modules.yaml` 为准，BMAD 安装器会提供这些官方模块或外部模块：

| 模块 code | 名称 | 用途 | 默认 |
| --- | --- | --- | --- |
| `core` | BMad Core Module | 所有安装都会包含的共享工具和配置 | 自动包含 |
| `bmm` | BMad Method | 全生命周期敏捷 AI 开发：分析、规划、架构、实现 | 默认选中 |
| `bmad-loop` | BMad Loop | Python 驱动的无人值守开发循环，带对抗式审查 | 可选 |
| `tea` | BMad Test Architect | 企业级质量策略、测试自动化、发布门禁 | 可选 |
| `bmb` | BMad Builder | 从对话创建自定义 Agent、Workflow、Module | 可选 |
| `cis` | Creative Intelligence Suite | 创意、头脑风暴、设计思维、问题解决 | 可选 |
| `gds` | Game Dev Studio | Unity / Unreal / Godot / Phaser 游戏开发工作流 | 可选 |
| `wds` | Whiteport Design Studio | 偏 UX 与 Design-first 的规划方法 | 可选 |
| `automator` | BMad Automator | 已废弃，被 `bmad-loop` 替代 | 不建议 |

安装 `bmad-loop` 后还需要按安装器提示运行 `bmad-loop-setup` 完成项目级 setup。

## 7. 推荐使用路径

### 7.1 新项目最短路径

```bash
mkdir my-project
cd my-project
npx bmad-method install
```

然后在你的 AI IDE 中：

```text
bmad-help 我有一个新项目想法，下一步怎么开始？
```

BMAD 会根据当前安装模块和已存在产物推荐下一步。

### 7.2 小修小改：Quick Flow

适合：bug 修复、小功能、局部重构、依赖升级、配置变更。

```text
bmad-quick-dev 修复登录校验允许空密码的问题
```

Quick Dev 会尽量完成：

1. 澄清意图。
2. 形成小规格或实现边界。
3. 修改代码。
4. 运行测试或验证。
5. 自查与修复。
6. 给出结果和后续建议。

如果你需要无人值守的一轮开发循环，可以使用：

```text
bmad-dev-auto 实现 _bmad-output/implementation-artifacts/spec-xxx.md
```

`bmad-dev-auto` 更适合作为上层 orchestrator 调用。它会读写 spec 状态，可能提交本地 commit，但不会 push。

### 7.3 中大型项目：完整 BMad Method

适合：从 0 到 1 的产品、平台、复杂功能、多人协作、需要可审计规划的工作。

推荐顺序：

```text
bmad-help
可选：bmad-brainstorming / bmad-forge-idea / bmad-market-research / bmad-product-brief / bmad-prfaq
bmad-prd
可选：bmad-ux
bmad-architecture
bmad-create-epics-and-stories
bmad-check-implementation-readiness
bmad-sprint-planning
循环：bmad-create-story -> bmad-dev-story -> bmad-code-review
每个 epic 结束：bmad-retrospective
```

## 8. 四阶段工作流详解

### Phase 1：Analysis（可选）

用于探索问题空间、验证想法、形成上游输入。

| Skill | 何时使用 | 产出 |
| --- | --- | --- |
| `bmad-brainstorming` | 需要结构化发散和创意技法 | `brainstorm.html`、可选 `brainstorm-intent.md` |
| `bmad-forge-idea` | 想对想法做压力测试，判断继续或放弃 | `forge-report.html`、可选 `forged-idea.md` |
| `bmad-market-research` | 研究客户、竞争、市场 | research 文档 |
| `bmad-domain-research` | 研究行业、领域、监管、趋势 | research 文档 |
| `bmad-technical-research` | 研究技术选型、架构模式、集成方案 | research 文档 |
| `bmad-product-brief` | 概念较清楚，想先形成产品简报 | `brief.md`、`addendum.md`、`.memlog.md` |
| `bmad-prfaq` | 用 Working Backwards/PRFAQ 检验产品叙事 | `prfaq-{project}.md` |
| `bmad-document-project` | 给既有项目生成 AI 可读项目文档 | docs / project knowledge |

研究类 workflow 要求能联网检索。若你的 AI 环境不能联网，需要换到支持 web search 的工具或手动提供资料。

### Phase 2：Planning

用于明确要构建什么、为谁构建、成功标准是什么。

| Skill | 何时使用 | 说明 |
| --- | --- | --- |
| `bmad-prd` | 创建、更新、验证 PRD | 当前统一入口，替代旧的 create/edit/validate PRD skills |
| `bmad-ux` | 项目有重要 UI/UX 体验，需要设计规格 | 产出 `DESIGN.md`、`EXPERIENCE.md`、`.memlog.md` |
| `bmad-spec` | 把任意输入压缩成下游可消费的 SPEC contract | 产出 `SPEC.md`、companions、可选 `stories.yaml` |

`bmad-prd` 有三个意图：

- Create：从零创建 PRD。
- Update：根据变更信号更新已有 PRD。
- Validate：用 checklist 审查 PRD，不直接修改。

旧入口仍在仓库中，但已废弃，后续 v7 会移除：

- `bmad-create-prd` -> 转发到 `bmad-prd` create intent
- `bmad-edit-prd` -> 转发到 `bmad-prd` update intent
- `bmad-validate-prd` -> 转发到 `bmad-prd` validate intent

### Phase 3：Solutioning

用于决定如何构建，以及把需求拆成可实现的工作。

| Skill | 何时使用 | 产出 |
| --- | --- | --- |
| `bmad-architecture` | 创建架构 spine / solution design / technical architecture | 默认 `ARCHITECTURE-SPINE.md` 或所需投影形式 |
| `bmad-create-epics-and-stories` | 基于 PRD + 架构拆 Epic 和 Story | epic 文件和 story 列表 |
| `bmad-check-implementation-readiness` | 实现前门禁检查，校验 PRD、UX、架构、Epic/Story 是否一致 | PASS / CONCERNS / FAIL 决策 |
| `bmad-generate-project-context` | 生成 `project-context.md`，记录实现约束和代码规范 | `_bmad-output/project-context.md` |

当前推荐使用 `bmad-architecture`。`bmad-create-architecture` 还存在，但已是兼容旧命令的转发入口，后续 v7 会移除。

### Phase 4：Implementation

用于按 story 实现、审查、跟踪和复盘。

| Skill | 何时使用 | 说明 |
| --- | --- | --- |
| `bmad-sprint-planning` | 初始化或更新 sprint tracking | 产出 `sprint-status.yaml` |
| `bmad-create-story` | 从 epic 准备下一条可实现 story | 产出 `story-[slug].md` |
| `bmad-dev-story` | 根据 story 文件实现代码 | 修改代码并验证 |
| `bmad-code-review` | 对实现做对抗式代码审查 | 批准或要求修复 |
| `bmad-qa-generate-e2e-tests` | 为已有功能生成 API/E2E 测试 | 测试代码 |
| `bmad-sprint-status` | 查看 sprint 状态、风险和下一步 | 状态摘要 |
| `bmad-correct-course` | Sprint 中出现重大变更时调整方向 | Sprint Change Proposal |
| `bmad-retrospective` | Epic 完成后复盘经验 | lessons learned |
| `bmad-checkpoint-preview` | 人类审查某个变更，聚焦关键差异 | review walk-through |

标准 story 循环：

```text
bmad-sprint-planning
bmad-create-story
bmad-dev-story
bmad-code-review
# 下一条 story 重复 create -> dev -> review
bmad-retrospective
```

## 9. 默认 Agent

Agent 可作为 Skill 直接调用，也可以在 Agent 会话内输入菜单触发码。

| Agent | Skill | 角色 | 常见触发码 / 工作 |
| --- | --- | --- | --- |
| Mary | `bmad-agent-analyst` | Business Analyst | `BP` brief、`MR` market research、`DR` domain research、`TR` technical research、`CB` brainstorming、`WB` PRFAQ、`DP` document project |
| John | `bmad-agent-pm` | Product Manager | `PRD`、`CE` create epics、`IR` readiness、`CC` correct course |
| Sally | `bmad-agent-ux-designer` | UX Designer | `CU` create UX |
| Winston | `bmad-agent-architect` | System Architect | `CA` architecture、`IR` readiness |
| Amelia | `bmad-agent-dev` | Senior Software Engineer | `DS` dev story、`QD` quick dev、`QA` tests、`CR` code review、`SP` sprint planning、`CS` create story、`ER` retrospective |
| Paige | `bmad-agent-tech-writer` | Technical Writer | `DP` document project、`WD` write doc、`MG` Mermaid、`VD` validate doc、`EC` explain concept |

两种启动方式：

```text
# 直接调用 workflow skill
bmad-prd

# 先加载 agent，再用菜单码
bmad-agent-pm
PRD
```

如果知道要做什么，直接调用 workflow skill 更快；如果想让某个角色持续参与讨论，先加载 agent。

## 10. Core Skills 常用清单

这些是 core 模块提供的通用能力，通常随任何 BMAD 安装可用。

| Skill | 用途 |
| --- | --- |
| `bmad-help` | 检查项目状态，回答 BMAD 问题，推荐下一步 |
| `bmad-brainstorming` | 结构化头脑风暴 |
| `bmad-party-mode` | 多 Agent 讨论，同一会话中引入多个专家视角 |
| `bmad-forge-idea` | 压力测试想法 |
| `bmad-spec` | 把输入提炼成 SPEC contract |
| `bmad-advanced-elicitation` | 对已有内容做高级追问和迭代增强 |
| `bmad-review-adversarial-general` | 对抗式审查文档、spec、story 或 diff |
| `bmad-review-edge-case-hunter` | 从分支路径和边界条件找未处理 edge case |
| `bmad-review-verification-gap` | 审查行为变更是否缺少可靠验证 |
| `bmad-editorial-review-prose` | 文案清晰度编辑 |
| `bmad-editorial-review-structure` | 文档结构审查、裁剪、合并、移动建议 |
| `bmad-shard-doc` | 将大型 Markdown 按二级标题拆分 |
| `bmad-index-docs` | 为目录生成文档索引 |
| `bmad-customize` | 引导创建和验证 BMAD 自定义覆盖 |

## 11. `project-context.md`：让实现不跑偏

`project-context.md` 是项目级 AI 实现规则，类似“项目宪法”。实现相关 workflow 会自动查找并加载它，尤其适合既有代码库和 Quick Dev。

默认位置：

```text
_bmad-output/project-context.md
```

建议包含：

```markdown
## Technology Stack & Versions

- Node.js 20.x, TypeScript 5.x, React 18
- Testing: Vitest + Playwright
- Styling: Tailwind CSS + design tokens

## Critical Implementation Rules

- API 请求必须使用 `src/lib/apiClient.ts`，不要直接 `fetch`。
- 新组件放在 `src/components/`，测试文件与组件同目录。
- 所有新增逻辑必须有单元测试，关键用户路径补 E2E。
- 禁止引入 Redux，本项目使用 Zustand。
```

创建方式：

```text
# 手动创建
mkdir -p _bmad-output
$EDITOR _bmad-output/project-context.md

# 或由 BMAD 生成
bmad-generate-project-context
```

新项目可以在架构前手动写入技术偏好；既有项目建议先运行 `bmad-generate-project-context`，让 AI 从代码库提取约定。

## 12. 既有项目怎么用 BMAD

推荐流程：

1. 安装 BMAD。
2. 清理已经过期的历史规划文档，避免 AI 误读。
3. 生成或手写 `project-context.md`。
4. 确保 `docs/` 里有当前真实有效的业务规则、架构说明和关键约束。
5. 小改动直接 `bmad-quick-dev`。
6. 大改动走 PRD -> UX（可选）-> Architecture -> Epics/Stories -> Readiness -> Implementation。

示例：

```text
bmad-help 我正在维护一个既有 Rails 应用，想新增订阅计费能力，应该走 quick flow 还是完整 BMAD？
```

如果文档缺失，可以先让 BMAD 生成项目文档：

```text
bmad-document-project
```

## 13. 常见任务范例

### 13.1 从想法到 PRD

```text
bmad-help 我有一个 SaaS 想法，但还没整理需求
bmad-brainstorming 帮我围绕这个想法发散功能和用户场景
bmad-product-brief 根据刚才的结果生成产品简报
bmad-prd 基于 product brief 创建 PRD
```

### 13.2 创建架构和故事

```text
bmad-architecture 基于当前 PRD 创建架构 spine
bmad-create-epics-and-stories 根据 PRD 和架构拆分 epic 和 story
bmad-check-implementation-readiness 检查是否可以进入实现
```

### 13.3 实现下一条 Story

```text
bmad-sprint-planning
bmad-create-story 创建下一条 story
bmad-dev-story 实现刚创建的 story
bmad-code-review 审查刚才的实现
```

### 13.4 快速修 bug

```text
bmad-quick-dev 修复用户登出后刷新页面仍显示已登录状态的问题。请先定位原因，再最小化修改，并运行相关测试。
```

### 13.5 审查变更是否缺测试

```text
bmad-review-verification-gap 请审查当前 git diff，判断行为变化是否有可靠测试覆盖。
```

### 13.6 文档太大需要拆分

```text
bmad-shard-doc docs/architecture.md
bmad-index-docs docs/
```

## 14. 更新、状态、卸载

查看当前安装状态：

```bash
npx bmad-method status
# 或已全局/本地可用时
bmad status
```

更新已有安装：

```bash
npx bmad-method install
```

如果检测到已有 `_bmad/`，交互模式通常会提供：

| 选项 | 作用 |
| --- | --- |
| Quick Update | 保留现有设置，刷新文件，应用 patch/minor stable 更新；不自动做 major 升级 |
| Modify Install | 重新选择模块、工具、配置和渠道 |

非交互 quick update：

```bash
npx bmad-method install --yes --action quick-update
```

添加模块时要传入完整模块集合，而不是增量：

```bash
npx bmad-method install --yes --action update \
  --modules bmm,bmb,cis,gds
```

卸载：

```bash
npx bmad-method uninstall
```

非交互卸载会保留用户产物目录：

```bash
npx bmad-method uninstall --yes --directory /path/to/project
```

## 15. 自定义 BMAD

BMAD v6 推荐通过 override 文件自定义，而不是直接修改安装生成的 Skill 文件。这样升级时不会丢失或覆盖你的改动。

### 15.1 单个 Agent / Workflow 自定义

三层优先级：

```text
优先级 1：_bmad/custom/{skill-name}.user.toml   # 个人覆盖，通常 gitignored
优先级 2：_bmad/custom/{skill-name}.toml        # 团队覆盖，可提交
优先级 3：skill 自带 customize.toml             # 默认值，不要直接改
```

推荐使用：

```text
bmad-customize 我想让 PM agent 在写 PRD 时默认关注合规风险，并且用更直接的中文提问。
```

手写示例：

```toml
# _bmad/custom/bmad-agent-pm.toml

[agent]
communication_style = "直接、审慎、持续追问商业价值和合规风险。"
persistent_facts = [
  "所有 PRD 必须包含合规风险和上线回滚策略。",
  "团队偏好中文沟通，文档面向工程与产品共同评审。",
]
```

### 15.2 全局配置覆盖

跨模块配置合并顺序：

```text
优先级 1：_bmad/custom/config.user.toml
优先级 2：_bmad/custom/config.toml
优先级 3：_bmad/config.user.toml
优先级 4：_bmad/config.toml
```

安装时也可以用 `--set` 直接写配置：

```bash
npx bmad-method install --yes \
  --modules bmm \
  --tools codex \
  --set core.communication_language=中文 \
  --set core.document_output_language=中文
```

## 16. Web Bundles

BMAD v6 还提供 Web Bundles：把部分规划类 Skill 打包成 Gemini Gems 或 ChatGPT Custom GPT 可用的资料包。适合把头脑风暴、PRD、PRFAQ、市场研究等前置规划放到网页端 LLM 订阅中完成，再把产物带回 IDE 实现。

当前仓库的 web bundles：

| Bundle | 用途 |
| --- | --- |
| `brainstorming-coach` | 头脑风暴 |
| `product-brief-coach` | 产品简报 |
| `prfaq-coach` | Working Backwards PRFAQ |
| `prd-coach` | PRD |
| `ux-coach` | UX |
| `market-and-industry-research` | 市场与行业研究 |

使用思路：

1. 在网页端完成前期规划，导出或复制产物。
2. 放入项目的 `_bmad-output/planning-artifacts/` 或 `docs/`。
3. 在 IDE 中用 `bmad-prd`、`bmad-architecture`、`bmad-create-epics-and-stories` 继续。

## 17. BMAD 源码仓库开发说明

如果你要修改 `/home/yuchao/sources/BMAD-METHOD` 这个仓库本身，遵守仓库规则：

- 提交信息使用 Conventional Commits。
- push 前在即将 push 的 checkout 上运行：

```bash
npm ci
npm run quality
```

`quality` 当前包含：

```text
format:check
lint
lint:md
docs:build
test:install
test:urls
test:renderer
validate:refs
validate:skills
docs:validate-sidebar
```

常用源码命令：

| 命令 | 用途 |
| --- | --- |
| `npm run bmad:install` | 本地运行安装器 install |
| `npm run bmad:uninstall` | 本地运行卸载器 |
| `npm run docs:dev` | 启动文档站开发服务 |
| `npm run docs:build` | 构建文档站 |
| `npm run validate:skills` | 校验 skills |
| `npm run validate:refs` | 校验文件引用 |
| `npm run quality` | 仓库完整质量检查 |

Skill 校验规则见：

```text
tools/skill-validator.md
```

## 18. 常见问题和排错

### 18.1 Skill 在 IDE 中不出现

处理顺序：

1. 确认安装时选择了对应工具，例如 `--tools codex`。
2. 检查项目中是否生成了对应目录，例如 `.agents/skills/bmad-help/SKILL.md`。
3. 重启 IDE 或 reload window。
4. 某些工具需要手动启用 Skills / Agents 功能。
5. 重新运行 `npx bmad-method install`。

### 18.2 模块没装全

重新运行安装器，并在 `--modules` 中写完整集合：

```bash
npx bmad-method install --yes --action update \
  --modules bmm,bmb,cis,tea \
  --tools codex
```

### 18.3 GitHub API rate limit

安装外部模块时会访问 GitHub API。共享网络、CI、VPN 下可能触发匿名限流。设置：

```bash
export GITHUB_TOKEN=你的_public_repo_read_PAT
```

### 18.4 已废弃旧命令还能不能用

当前还能用，但建议迁移：

| 旧命令 | 当前推荐 |
| --- | --- |
| `bmad-create-prd` | `bmad-prd` create intent |
| `bmad-edit-prd` | `bmad-prd` update intent |
| `bmad-validate-prd` | `bmad-prd` validate intent |
| `bmad-create-architecture` | `bmad-architecture` |

### 18.5 Quick Dev 适合所有需求吗

不适合。Quick Dev 适合边界清楚的小改动。下面情况建议走完整 BMad：

- 影响多个系统或多个团队。
- 需求本身不清楚，需要 discovery。
- 涉及重要 UX、架构、合规、安全或迁移。
- 需要留存可评审的 PRD / 架构 / Epic / Story。

### 18.6 为什么要新开会话

BMAD workflow 会读取和产出大量上下文。复用旧会话容易导致：

- AI 把上一个 workflow 的假设带到新任务。
- 上下文窗口被无关内容占满。
- Agent persona 或菜单状态混乱。

经验规则：每个 workflow 新开会话；story 实现、代码审查、复盘也尽量分开。

## 19. 快速命令备忘

```text
# 帮助与导航
bmad-help
bmad-help 我刚安装完，下一步做什么？

# 前期分析
bmad-brainstorming
bmad-forge-idea
bmad-market-research
bmad-domain-research
bmad-technical-research
bmad-product-brief
bmad-prfaq

# 规划
bmad-prd
bmad-ux
bmad-spec

# 方案设计
bmad-architecture
bmad-create-epics-and-stories
bmad-check-implementation-readiness
bmad-generate-project-context

# 实现
bmad-quick-dev
bmad-dev-auto
bmad-sprint-planning
bmad-create-story
bmad-dev-story
bmad-code-review
bmad-sprint-status
bmad-correct-course
bmad-retrospective

# 文档与审查工具
bmad-document-project
bmad-shard-doc
bmad-index-docs
bmad-review-adversarial-general
bmad-review-edge-case-hunter
bmad-review-verification-gap
bmad-editorial-review-prose
bmad-editorial-review-structure
bmad-checkpoint-preview
bmad-customize
```

## 20. 推荐阅读源码内文档

```text
README.md
README_CN.md
docs/tutorials/getting-started.md
docs/how-to/install-bmad.md
docs/reference/workflow-map.md
docs/reference/commands.md
docs/reference/agents.md
docs/reference/core-tools.md
docs/explanation/quick-dev.md
docs/explanation/project-context.md
docs/how-to/customize-bmad.md
docs/reference/dev-auto.md
```
