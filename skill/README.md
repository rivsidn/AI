

- cli-anything 使用


## 附录

### AI

#### skill学习资料

• 我这次按 skill-creator 的思路来整理，因为你想学的应该是 OpenAI / Codex 这套基于 SKILL.md 的 skill 机制。

  我先给你一个结论：

  - 学 skill，最有效的路径不是“先找书”，而是“先看官方文档 -> 再看 cookbook -> 再抄 1 个简单真实实现 -> 最后自己写一个最小 skill”。
  - 如果你想看“标准 + 简单”的现成实现，你本机里就已经有两个非常适合入门的例子：/home/yuchao/.codex/skills/.system/skill-installer/SKILL.md 和 /home/yuchao/.codex/skills/.system/openai-
    docs/SKILL.md。

  学习资料

  - 官方总文档，先读这个
      - OpenAI Developers / Agent Skills
        链接：https://developers.openai.com/codex/skills
      - 这是最核心的一篇。它讲清楚了：
          - skill 是什么
          - SKILL.md 的最小结构
          - scripts/、references/、assets/、agents/openai.yaml 的作用
          - skill 如何触发：显式调用 + 隐式匹配
          - skill 放在哪些目录会被 Codex 发现
  - 官方 cookbook，最适合“照着做一遍”
      - OpenAI Cookbook / Skills in OpenAI API
        链接：https://developers.openai.com/cookbook/examples/skills_in_api
      - 这篇最有用的地方是给了一个完整、可运行的 csv_insights_skill 示例，适合你第一次真正“看懂一个 skill 怎么落地”。
      - 它还讲了：
          - skill 上传方式
          - hosted / local shell 如何挂载 skill
          - 版本管理
          - skill script 应该像“小 CLI”一样设计
  - 官方博客，最适合学“怎么写得像工程化项目”
      - OpenAI Blog / Using skills to accelerate OSS maintenance
        链接：https://developers.openai.com/blog/skills-agents-sdk
      - 这篇不是入门语法，而是实战经验：
          - skill 的 description 应该怎么写，才能更容易被正确路由
          - 什么逻辑放 SKILL.md，什么逻辑下沉到 scripts/
          - 真正的大仓库是怎么把 skill 和 AGENTS.md 配合起来用的
      - 里面还点名了很多真实 skill，例如：
          - code-change-verification
          - docs-sync
          - pr-draft-summary
          - openai-knowledge
  - 官方 Academy，最适合零基础建立概念
      - OpenAI Academy / Skills
        链接：https://academy.openai.com/public/resources/skills
      - 这篇偏“概念 + 场景 + 使用方式”，讲得很平实，适合先建立直觉：
          - 什么任务适合做成 skill
          - 为什么 skill 比重复贴 prompt 更好
          - skill 和 GPT / project 的区别
      - 如果你是第一次接触，这篇建议放在最前面或第二篇读。
  - 官方技能目录，最适合找现成实现
      - GitHub / openai/skills
        链接：https://github.com/openai/skills
      - 这是 OpenAI 的技能目录仓库，里面有 curated / experimental skill。
      - 很适合拿来做“案例库”，看别人怎么命名、怎么写 description、怎么组织 scripts/。
  - 真实仓库里的 skill 集合
      - OpenAI Agents SDK for Python
        链接：https://github.com/openai/openai-agents-python/tree/main/.agents/skills
      - OpenAI Agents SDK for JS
        链接：https://github.com/openai/openai-agents-js/tree/main/.agents/skills
      - 这两个仓库不是教程，但它们是非常好的“真实工程案例”。

  视频 / 演示

  - 这块我先说实话：截至 2026-04-16，我没有检到一套“专门系统讲 Codex Skill”的官方完整视频课。
  - 目前最接近“视频化入门”的官方资源，还是：
      - OpenAI Academy / Skills
        https://academy.openai.com/public/resources/skills
  - 如果你想继续找官方视频入口，可以看：
      - Codex Videos
        https://developers.openai.com/codex/videos
  - 但就“学习效率”来说，这个主题目前还是文档和示例仓库远比视频更值。

  书籍

  - 这个领域我不建议你优先找书。
  - 原因很简单：skill / agent workflow 变化太快，书很容易过时。
  - 截至 2026-04-16，我没有看到 OpenAI 官方专门围绕 Codex / ChatGPT skill 的书籍路线。
  - 所以我的建议是：
      - 不要先买书
      - 先把官方 docs + cookbook + 真实 skill 例子吃透
      - 这比看书更快、更准

  我建议你的学习顺序

  - 第 1 步：读 OpenAI Academy 的 Skills，先建立概念
  - 第 2 步：读 OpenAI Developers 的 Agent Skills
  - 第 3 步：读 cookbook 的 Skills in OpenAI API
  - 第 4 步：看你本机的 skill-installer 和 openai-docs
  - 第 5 步：再去看 openai/skills 和 Agents SDK 仓库里的复杂案例

  已有实现：标准 + 简单

  先给你“最好抄”的 3 个。

  - 最推荐 1：skill-installer
      - 文件：/home/yuchao/.codex/skills/.system/skill-installer/SKILL.md
      - 这是我最建议你先看的。
      - 原因：
          - 很短，只有约 58 行
          - 结构标准
          - 同时展示了 skill 如何配合 scripts/
      - 你还能顺手看这些配套文件：
          - /home/yuchao/.codex/skills/.system/skill-installer/agents/openai.yaml
          - /home/yuchao/.codex/skills/.system/skill-installer/scripts/list-skills.py
          - /home/yuchao/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py
  - 最推荐 2：openai-docs
      - 文件：/home/yuchao/.codex/skills/.system/openai-docs/SKILL.md
      - 这个也很适合入门，大约 69 行。
      - 适合学的点：
          - 如何把 skill 的触发范围写清楚
          - 如何约束信息来源
          - 如何把“工具优先级”和“fallback 逻辑”写在 skill 里
  - 最推荐 3：官方 curated skills 仓库
      - 仓库：https://github.com/openai/skills
      - 这个仓库里有很多标准实现。
      - 我更建议你先从目录里挑“职责边界很窄”的 skill 看，而不是一上来挑特别大的。
      - 从目录名字看，适合先扫的包括：
          - openai-docs
          - doc
          - speech
          - spreadsheet
          - cli-creator

  更完整但不算“简单”的实现

  - project-constitution-generator
      - 文件：/home/yuchao/.codex/skills/project-constitution-generator/SKILL.md
      - 这个更像“进阶例子”
      - 适合学：
          - 多阶段 workflow 怎么写
          - skill 如何引用 references/
          - 大一点的 skill 如何做“按需加载”
  - OpenAI Agents SDK 仓库中的技能
      - https://github.com/openai/openai-agents-python/tree/main/.agents/skills
      - https://github.com/openai/openai-agents-js/tree/main/.agents/skills
      - 适合学：
          - skill 怎么跟真实 repo 的验证、发布、PR 流程结合
          - AGENTS.md 怎么强制某些场景必须调用 skill

  什么叫“标准”的 skill

  按官方文档，一个标准 skill 至少要满足这些：

  - 目录里必须有 SKILL.md
  - SKILL.md frontmatter 里至少要有：
      - name
      - description
  - 可选目录：
      - scripts/
      - references/
      - assets/
      - agents/openai.yaml
  - description 不能只写“它做什么”，最好还要写“什么时候该触发、什么时候不该触发”
  - 一个 skill 最好只做一件事
  - 能用文字说明解决，就先不要急着上脚本
  - 如果有脚本，最好像小 CLI：
      - 输入清楚
      - 输出清楚
      - 失败时有明确报错
      - 结果写到固定路径

  一个最小可学模板

  这个不是官方现成仓库文件，而是我根据官方文档整理出来的“最小可用骨架”，你可以拿它当练习模板：

  ---
  name: my-first-skill
  description: 当用户需要把输入按固定流程处理成标准输出时触发；如果只是一次性随手处理，就不要触发。
  ---

  # My First Skill

  ## 何时使用
  - 用户给出明确输入
  - 需要稳定流程
  - 需要固定输出格式

  ## 不要使用
  - 闲聊
  - 一次性小任务
  - 没有明确输入输出约束的场景

  ## 输入
  - 用户提供的原始材料

  ## 输出
  - 一个固定格式的结果

  ## 步骤
  1. 检查输入是否完整
  2. 按固定步骤处理
  3. 用约定格式输出
  4. 输出前做一次自检

  如果你只想先看 1 个例子，我建议这样选

  - 想看“最简单真实 skill”：/home/yuchao/.codex/skills/.system/skill-installer/SKILL.md
  - 想看“最标准官方教程”：https://developers.openai.com/codex/skills
  - 想看“完整 runnable 示例”：https://developers.openai.com/cookbook/examples/skills_in_api
  - 想看“真实工程怎么用 skill”：https://developers.openai.com/blog/skills-agents-sdk

  如果你愿意，我下一条可以直接继续给你这 3 个内容里的任意一个：

  1. 逐行讲解 skill-installer 这个 skill
  2. 给你手写一个“最小可运行”的练习 skill
  3. 按“入门 -> 进阶 -> 实战”给你排一份 7 天学习计划

