
## 安装


```bash
$ cd project/
$ npx skills@latest add mattpocock/skills

◆  Select skills to install (space to toggle)
  ❯ ▾ ○ Mattpocock Skills
    ├─ ○ ask-matt
    ├─ ○ code-review
    ├─ ○ codebase-design
    ├─ ○ diagnosing-bugs
    ├─ ○ domain-modeling
    ├─ ○ grill-me
    ├─ ○ grill-with-docs
    ├─ ○ grilling
    ├─ ○ handoff
    ├─ ○ implement
    ├─ ○ improve-codebase-architecture
    ├─ ○ prototype
    ├─ ○ research
    ├─ ○ resolving-merge-conflicts
    ├─ ○ setup-matt-pocock-skills
    ├─ ○ tdd
    ├─ ○ teach
    ├─ ○ to-questionnaire
    ├─ ○ to-spec
    ├─ ○ to-tickets
    ├─ ○ triage
    ├─ ○ wait-what
    ├─ ○ wayfinder
    ├─ ○ wizard
    └─ ○ writing-for-agents
    ▾ ○ Other
    ├─ ○ claude-handoff
    ├─ ○ git-guardrails-claude-code
    ├─ ○ loop-me
    ├─ ○ migrate-to-shoehorn
    ├─ ○ scaffold-exercises
    ├─ ○ setup-pre-commit
    ├─ ○ setup-ts-deep-modules
    ├─ ○ writing-beats
    ├─ ○ writing-fragments
    └─ ○ writing-shape
```


### 技能介绍

#### ask-matt

它是这套技能的“导航员”或“总入口”：当你不知道当前任务应该调用哪个技能、或者多个技能该按什么顺序使用时，就先调用它。

它通常会根据场景给你推荐一条工作流：

- 新功能、需求还模糊：grill-with-docs → to-spec → to-tickets → implement
- 小型且明确的功能：直接 implement
- 疑难 Bug：diagnosing-bugs
- 大型且方向模糊的项目：wayfinder
- 收到很多外部 Issue：triage
- 想改善代码结构：improve-codebase-architecture
- 不知道如何跨会话保存上下文：handoff

#### code-review

它用来审查某个分支、PR 或一段尚未提交的修改。它不是简单检查语法或格式，而是把审查拆成两个相互独立的方向。

1. Standards：代码质量与项目规范

检查修改是否符合：

- 仓库里的 CONTRIBUTING.md、CODING_STANDARDS.md 等规范
- 命名是否清楚
- 是否存在重复代码
- 是否过度抽象
- 是否有职责混乱、修改散落等设计问题
- 是否存在不合理的继承、长调用链、中间转发层等代码异味

已经能被 ESLint、Prettier、类型检查器自动发现的问题，它通常不会重复报告。

2. Spec：需求实现是否正确

对照原始 Issue 或需求文档检查：

- 有没有遗漏需求
- 有没有只实现了一部分
- 有没有做需求之外的东西，即范围膨胀
- 表面上实现了，但行为实际不正确

这两个方向会交给两个独立的子 Agent 并行审查，最后分别输出结果，避免“代码写得漂亮”掩盖“功能做错了”，也避免“功能能用”掩盖“代码质量很差”。

#### codebase-design

> codebase 代码库

codebase-design 会指导 Agent 思考：

- 能不能减少公开方法的数量
- 能不能简化函数参数
- 能不能把更多复杂性藏在模块内部
- 模块的接口应该放在哪里
- 哪些依赖应该从外部注入
- 测试应该从哪个接口进入
- 是否真的需要增加抽象层
- 某个模块是否只是无意义地转发调用

一句话概括：codebase-design 教 Agent 把复杂性藏进设计良好的模块中，让调用方只面对一个小而稳定的接口。

#### diagnosing-bugs

它是一套严格的 Bug 诊断流程，适合处理：

- 难以定位的 Bug
- 偶发失败、并发问题
- 性能回退
- 某次版本更新后才出现的问题
- Agent 看了很多代码却一直在猜原因的情况

它的核心原则是：

> 在提出原因假设之前，必须先建立一个能够稳定复现 Bug 的快速反馈循环。

也就是说，它不会一上来就读代码然后猜“可能是这里有问题”，而是先寻找一条命令，让这条命令能够准确表现用户描述的故障。

一句话概括：diagnosing-bugs 要求先制造一个稳定亮红灯的故障信号，再用实验逐步定位根因，最后用回归测试锁住修复。


#### domain-modeling

它用于建立和维护项目的“领域语言”：让用户、开发者和 Agent 对业务概念使用一致、精确的词汇。

一句话概括：domain-modeling 帮团队建立一套精确、统一的业务语言，并让需求、代码和文档都围绕这套语言表达。

#### grill-me


- grilling：真正负责多轮访谈和决策树推进的底层技能。
- grill-me：让用户可以主动启动 grilling 的快捷入口。

因此，如果你勾选 grill-me，建议同时勾选 grilling。只安装 grill-me 而不安装 grilling，它可能找不到真正要执行的底层技能。

和 grill-with-docs 的区别

grill-me 是无状态访谈：

- 不维护 CONTEXT.md
- 不创建 ADR
- 不把结论自动保存到项目
- 适合项目之外的想法、方案、写作和个人决策

grill-with-docs 是项目内访谈：

- 会检查现有代码和文档
- 会维护领域词汇
- 会更新 CONTEXT.md
- 必要时会创建 ADR
- 适合真实代码仓库中的功能设计

一句话概括：grill-me 会启动一场多轮、无状态的深度访谈，把你的想法沿决策树逐层问清楚，但不会保存文档或直接开始实施。

#### grill-with-docs。

  它可以理解为：

  grill-me
  + 项目代码调查
  + 领域术语整理
  + CONTEXT.md
  + ADR

  它会对你的功能构想或技术方案进行多轮“盘问”，同时把已经确认的重要结论写进项目文档。作者把它作为代码仓库内设计新功能时的推荐起点。

#### grilling

它是这套技能里的“深度访谈引擎”，负责把一个想法、计划或设计拆成决策树，然后按依赖关系逐轮提问。

前面两个技能其实都是它的包装：

grill-me
└── grilling

grill-with-docs
├── grilling
└── domain-modeling

所以：

- grilling 决定“怎么问”
- grill-me 提供无状态访谈入口
- grill-with-docs 在访谈之外增加项目文档维护

#### handoff

它用来把当前对话压缩成一份可移交的 Markdown 文档，让另一个全新的 Agent、会话或工作环境能够继续当前工作。


它明确要求把交接文件保存到操作系统的临时目录，而不是当前代码仓库。

Linux 上通常会是类似：

/tmp/handoff-xxxx.md

这样不会无意中污染仓库或被提交进 Git。

不过临时目录可能被系统清理。如果这份交接需要长期保存，生成后应明确要求将它移动到一个持久位置，或者把重要结论正式写入 Spec、Issue、ADR 等项目文档。

#### implement

一句话概括：implement 接收一份明确的 Spec 或 Ticket，以 TDD 方式逐步实现，持续验证，完成双轴代码审查，并把结果提交到当前 Git 分支。

#### improve-codebase-architecture

它是一个“架构体检与候选方案发现”技能：扫描代码库中阻碍理解、测试和修改的结构，找出可以把“浅模块”改造成“深模块”的地方，然后生成一份带图的 HTML 架构报告供你选择。

#### prototype

一句话概括：prototype 用最低工程成本做一个可以亲手操作的实验，回答状态模型或 UI 设计中的一个具体问题；结论进入正式代码，原型本身留在独立分支作为历史证据。

#### research

它用于把一个需要查资料的问题交给后台子 Agent，让它从高可信的一手来源中调查，并将带引用的结论写成 Markdown 文件保存在当前仓库中。

#### resolving-merge-conflicts

一句话概括：resolving-merge-conflicts 会追溯冲突双方的原始意图，逐个 hunk 合并兼容目标，运行项目检查，并把当前 merge/rebase 一直完成；它不会简单选择某一侧，也不会中途执行 --abort。


#### setup-matt-pocock-skills

  这是整套 Matt Pocock 工程技能的“项目初始化向导”。它不是全局安装器，而是为当前代码仓库建立一组约定，让 to-spec、to-tickets、triage、code-
  review、wayfinder 等技能知道：

  - Issue 和 Spec 应该保存在哪里
  - 应该怎样读取、创建和关闭 Issue
  - Triage 使用哪些标签
  - 项目的领域词汇与 ADR 放在哪里
  - Agent 开始工作前应该读取哪些文档

  作者明确建议：安装技能后，在每个实际项目中第一次使用工程流程之前，先运行一次它。


  一句话概括：setup-matt-pocock-skills 会调查当前仓库，和你确认 Issue Tracker、Triage 标签与领域文档布局，然后把这些约定写进 Agent 指令和 docs/agents/，供整套工程技能共同使用。

#### tdd

它用于让 Agent 按测试驱动开发方式实现功能或修复 Bug。核心循环是：

Red：先写一个会失败的测试
→ Green：只写刚好让测试通过的代码
→ 再处理下一个行为

这套技能特别强调：TDD 不只是“先写测试”，还必须把测试写在正确的接口上，并确保测试验证的是业务行为，而不是内部实现。

一句话概括：tdd 先和你确认值得测试的公共接缝，再按“一条失败测试、一份最小实现”的垂直切片推进；测试只验证外部行为，Mock 仅用于真正的系统边界，重构则留到代码审查阶段。

#### teach

它用于把当前目录变成一个长期、可持续的“个人教学工作区”。和普通的一问一答不同，它会记录你的学习目标、已有知识、学习进度、资料来源和每一节课，使下一次全新 Codex 会话也能继续教学。

它不仅能教编程，也可以用于：

- 数学、物理等知识型主题
- 外语
- 写作
- 健身、瑜伽等技能型主题
- 某个行业或业务领域
- 一套工具或工作方法

#### to-questionnaire

它用于把“你自己无法回答、必须找某个特定的人确认”的事项，整理成一份结构化 Markdown 问卷，让对方异步填写，或者在会议中一起完成。

核心思想是：

不要继续盘问用户不掌握的内容，
而是确认问卷要发给谁、需要从对方那里得到什么。

#### to-spec

它用于把当前对话中已经讨论清楚的内容整理成正式 Spec，并发布到项目配置好的 Issue Tracker。

最重要的定位是：

它负责总结，不负责继续访谈。

所以应该在需求已经基本明确之后调用，而不是在只有一个模糊想法时调用。

典型流程是：

grill-with-docs
→ 需求与决策讨论清楚
→ to-spec
→ to-tickets
→ implement

#### to-tickets

它用于把一份 Spec、计划或当前对话拆成多个可以独立执行的 Ticket，并明确每个 Ticket 被哪些其他 Ticket 阻塞。

它最核心的两个概念是：

垂直切片
+
阻塞关系

最终不是简单生成一份待办清单，而是生成一张可以按依赖顺序执行、也可以安全并行的任务图。

#### triage

  它用于把外部进入项目的 Issue，必要时也包括外部 PR/MR，按照一个明确的状态机进行分诊：先确认它是什么，再验证描述是否成立，补齐信息，最后决定
  交给 Agent、交给人，或者关闭。

  它主要处理的是“别人提交进来的原始请求”，例如：

  - 用户报告的 Bug
  - 客户提出的功能请求
  - 社区提交的 Issue
  - 外部贡献者提交的 PR
  - 信息不完整、尚未确认是否值得做的请求

  它不用于处理 to-tickets 生成的 Ticket，因为那些 Ticket 已经被整理成 ready-for-agent，不需要再分诊一次。

  ## 两类分类标签

  每个被分诊的 Issue 都应该有且只有一个类别：

  bug
  enhancement

  含义分别是：

  - bug：已有行为损坏、不符合承诺或发生回退
  - enhancement：新增功能、改进或改变现有行为

  ## 五种状态

  每个 Issue 还应该有且只有一个状态：

   状态               含义
  ━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   needs-triage       等待维护者评估
  ─────────────────  ──────────────────────────────────
   needs-info         等待报告者补充信息
  ─────────────────  ──────────────────────────────────
   ready-for-agent    信息完整，可以交给无人值守 Agent
  ─────────────────  ──────────────────────────────────
   ready-for-human    需要人工判断、权限或操作
  ─────────────────  ──────────────────────────────────
   wontfix            决定不处理


  一句话概括：triage 把外部 Issue/PR 经过分类、代码验证、补充询问和维护者确认，流转到 ready-for-agent、ready-for-human、needs-info 或
  wontfix，并为结果留下可持续使用的记录。


可以理解成是分诊台.


#### wait-what

它是一个“我刚才没听懂，请换种说法”的快捷技能。

它会把上一条消息重新讲一遍，并遵循三点：

- 补上理解所需的少量上下文
- 使用更简单、直接的技术英语表达
- 如果项目有 CONTEXT.md，优先使用其中已经定义的业务术语

一句话概括：wait-what 会用更少术语、更完整上下文，把 Agent 刚才没有讲明白的内容重新说清楚。

#### wayfinder

一句话概括：wayfinder 将一个超大且路径不清的目标变成一张由“决策 Ticket”构成的共享地图；每次只解决一个前沿决定，逐步驱散迷雾，直到可以安全交给 Spec、Ticket 和实现流程。

#### wizard

它用于生成一个可交互的 Bash 向导脚本，带着人一步一步完成“只有人能做”的操作，例如：

- 在第三方后台创建项目、密钥或 Webhook
- 获取 API Key、OAuth Client Secret 等凭据
- 将本地环境变量写入 .env
- 将 CI 所需值写入 GitHub Actions Secrets 或 Variables
- 引导完成一次性数据迁移或切换
- 操作一个 Agent 无法登录、无法点击、无法确认的网页后台

#### writing-for-agents

它不会直接替你写文件

writing-for-agents 更像持续生效的写作标准和审稿原则。


### others

#### claude-handoff

一句话概括：claude-handoff 会把当前上下文直接交给一个新启动的 Claude 后台 Agent，让它在当前目录立即继续工作；它不是通用 Codex 技能，且要注意并发修改同一工作区的风险。


#### git-guardrails-claude-code

一句话概括：git-guardrails-claude-code 通过 Claude Code 的 PreToolUse Hook，在常见危险 Git 命令执行前进行拦截；它是防误操作护栏，不是完整安全边界，并且只适用于 Claude Code。

#### loop-me





## 附录

• 这个仓库是给 Claude Code、Codex 等编程 Agent 用的技能集合。作者对 Codex 推荐使用 skills.sh 安装器，不需要手动 clone 仓库。

  在你想使用这些技能的项目根目录执行：

  cd /你的项目目录
  npx skills@latest add mattpocock/skills

  安装器会交互式询问：

  1. 安装哪些技能
  2. 安装给哪个 Agent——选择 Codex
  3. 安装到当前项目还是用户级目录

  选择技能时，务必包含：

  setup-matt-pocock-skills

  安装结束后，重新开始一个 Codex 会话或进入下一轮对话，让新技能被发现，然后运行：

  /setup-matt-pocock-skills

  如果 Codex 界面使用 $技能名 的调用形式，则运行：

  $setup-matt-pocock-skills

  它会配置问题跟踪方式、工单标签以及文档保存位置。

  你当前环境已经满足条件：

  - Node.js：v22.22.1
  - npm/npx：10.9.4
  - 当前目录：/home/yuchao/tmp/chat_channel

  不过当前目录看起来不像代码项目，所以不建议直接在这里执行，除非你就是想把技能装到这个目录。建议先进入实际项目根目录再安装。

  另外，这套技能中有 tdd、code-review、diagnosing-bugs 等，和你已有的部分 superpowers 技能可能重叠。安装器允许按需勾选，不必全部安装，也不要
  同时使用 Claude 插件版和 npx skills 版，否则会出现重复技能。



