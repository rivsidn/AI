

## TODO

- [harness](https://github.com/harness/harness)
- [OpenHarness](https://github.com/HKUDS/OpenHarness)

- [superpowers](https://github.com/obra/superpowers)


### 敏捷开发

• 我搜了一圈 GitHub 后，最符合你说的“敏捷开发 + skills 框架 + 方便迭代”的，是：

  推荐：Smart SDLC

  - GitHub：superMLdev/smart-sdlc
    https://github.com/superMLdev/smart-sdlc

  - npm：@supermldev/smart-sdlc
    https://www.npmjs.com/package/@supermldev/smart-sdlc

  它比 superpowers 更适合你这个诉求，原因是：

  - 它明确定位为 “AI-driven agile development framework”，不是单纯的提示词集合。
  - 每个 skill 就是一个 SKILL.md，结构简单，适合 fork 后快速改。
  - 覆盖完整敏捷/SDLC 流程：relearn、analysis、planning、solutioning、implementation、QA、release、modernization。
  - 有 persona：BA、PM、Architect、Developer、Team Lead、QA、Release 等。
  - 支持 GitHub Copilot、Claude、Cursor，以及“any AI coding assistant”，理论上也容易适配 Codex。
  - 安装后生成 _superml/skills/，你可以把它当成自己的 skill 仓库来迭代。
  - 支持 JIRA、Confluence、GitHub、GitLab、Azure DevOps 等集成思路。

  快速试用：

  npx @supermldev/smart-sdlc init
  npx @supermldev/smart-sdlc persona

  它的 README 里说明 skill 形态就是：

  _superml/skills/<phase>/<skill>/SKILL.md

  比如 PRD skill：

  skills/2-planning/create-prd/SKILL.md
  skills/2-planning/create-prd/workflow.md
  skills/2-planning/create-prd/steps/...

  这点很关键：它不是强绑定一个复杂 runtime，而是“Markdown skill + workflow + step files”，更方便你本地改、删、拆、重组。

  备选对比

   项目                                 结论                                              适合场景
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   superMLdev/smart-sdlc                最像你要的 agile skill framework                  想 fork 一套可迭代的敏捷开发 skills
  ───────────────────────────────────  ────────────────────────────────────────────────  ───────────────────────────────────────────────
   bmad-code-org/BMAD-METHOD            很成熟，但偏重型                                  想要完整 AI 敏捷开发方法论和社区生态
  ───────────────────────────────────  ────────────────────────────────────────────────  ───────────────────────────────────────────────
   microsoft/agentic-agile-template     很敏捷，但不是 skill 框架                         想把 GitHub Issues / PR / wave 执行流程标准化
  ───────────────────────────────────  ────────────────────────────────────────────────  ───────────────────────────────────────────────
   buildermethods/agent-os              轻量、规范驱动，但不算 agile skill 框架           想管理 standards、specs、产品规划
  ───────────────────────────────────  ────────────────────────────────────────────────  ───────────────────────────────────────────────
   github/spec-kit                      很强的 spec-driven 工具链，但不是 agile skills    想用规格驱动开发替代 vibe coding
  ───────────────────────────────────  ────────────────────────────────────────────────  ───────────────────────────────────────────────
   levnikolaevich/claude-code-skills    skills 结构很干净，但不是敏捷开发框架             想参考“简洁 skill 仓库”的组织方式

  我的建议

  如果你的目标是替代 superpowers，并且重点是“后续方便自己迭代”，我会选：

  1. 用 smart-sdlc 作为主框架。
  2. fork 后保留它的目录结构：skills/<phase>/<skill>/SKILL.md。
  3. 删除你不需要的企业集成和重流程。
  4. 引入 microsoft/agentic-agile-template 的 backlog、acceptance criteria、wave execution 思路。
  5. 参考 levnikolaevich/claude-code-skills 的简洁风格，把每个 skill 写短、写硬、写可测试。

  一句话：
  Smart SDLC 是最接近“敏捷开发 skill 框架”的现成项目；BMAD 更成熟但更重，Agentic Agile 更像流程模板，Spec Kit 更像规格驱动工具链。

