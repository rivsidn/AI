

## TODO

- 如何从更高层次，复盘我们执行的任务



## 附录

### 学习资料

#### 官方文档

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

#### 仓库

- [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/zh/)
- [deusyu/harness-engineering](https://github.com/deusyu/harness-engineering)
- [awesome-harness-engineering](https://github.com/walkinglabs/awesome-harness-engineering)


#### AI

• 我会查官方资料来确认“harness”在 Agent/Codex 语境中的说法，优先用 OpenAI 官方来源。

• 有。官方资料里确实出现了 “harness” 这个说法，尤其是在 OpenAI Codex / Agents SDK 语境中。不过要注意：它更像一个工程术语，不是一个统一行业标准规范。

  官方对 harness 的核心定义

  OpenAI 在 Codex 相关文章中把 Codex harness 描述为：

  - 支撑 Codex 各种产品形态的底层 agent 运行逻辑；
  - 负责 agent loop，也就是“用户输入 → 模型推理 → 工具调用 → 工具结果回传 → 继续推理/完成任务”；
  - 负责执行逻辑、上下文管理、工具执行、权限控制、线程生命周期等；
  - 简单说：harness 就是把 LLM 能力变成真实可执行 agent 的运行外壳。

  最重要的官方资料

  - OpenAI：Unrolling the Codex agent loop
    https://openai.com/index/unrolling-the-codex-agent-loop/
    这篇最适合理解 harness 的底层循环。OpenAI 明确说 Codex harness 提供了 Codex 体验背后的核心 agent loop 和执行逻辑。文章解释了 agent loop 如何编排用户、模型和工具。
  - OpenAI：Unlocking the Codex harness: how we built the App Server
    https://openai.com/index/unlocking-the-codex-harness/
    这篇更直接讲 “Codex harness”。它说明 Codex Web、CLI、IDE 插件、macOS App 背后都由同一个 Codex harness 驱动。里面还列出了 harness 内部包含的部分：thread 生命周期、持久化、配置、认
    证、工具执行、MCP、skills、沙箱策略等。
  - OpenAI：The next evolution of the Agents SDK
    https://openai.com/index/the-next-evolution-of-the-agents-sdk/
    这篇讲 Agents SDK 的新版方向，里面使用了 “model-native harness” 的说法。它强调 harness 负责让 agent 在文件、工具、系统、沙箱环境中工作，并包含 memory、sandbox-aware orchestration、
    filesystem tools、MCP、skills、AGENTS.md、shell、apply patch 等能力。
  - OpenAI Agents SDK 文档
    https://openai.github.io/openai-agents-python/agents/
    这不是直接用 “harness” 作为标题，但它讲的就是 harness 的 SDK 化实现：Agent + Runner 帮你管理 turns、tools、guardrails、handoffs、sessions。如果你想自己掌控 loop，就直接用 Responses
    API。

  用中文概括

  你可以把 harness 理解成：

  模型本身只会生成输出；
  harness 负责把模型输出变成行动。

  更工程化一点：

  Agent Harness =
    Prompt / Instructions 管理
  + Agent Loop
  + Tool Registry
  + Tool Execution
  + Context / Memory
  + State / Thread Persistence
  + Guardrails / Permission
  + Sandbox
  + Trace / Logs
  + Eval / Retry
  + Human Approval

  和 Agent Framework 的区别

  - LLM API：只负责模型生成。
  - Agent Loop：负责一轮轮调用模型和工具。
  - Harness：负责完整运行环境，包括 loop、工具、状态、安全、日志、沙箱、权限等。
  - Agent SDK / Framework：把 harness 封装成你能直接用的库。

  所以你要学 “AI Agent harness”，官方最推荐从这两条线看：

  1. Codex harness：理解真实生产级 coding agent 怎么跑。
  2. Agents SDK：理解如何自己构建 agentic app。

  建议阅读顺序

  1. 先看 Unrolling the Codex agent loop，理解 agent loop。
  2. 再看 Unlocking the Codex harness，理解 harness 里还有什么。
  3. 再看 OpenAI Agents SDK 文档，学习怎么用 SDK 实现。
  4. 最后看 The next evolution of the Agents SDK，理解 sandbox、MCP、skills、AGENTS.md 这些生产级能力。

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› claude code 公司没有harness 的文档说明么


• Searching the web

• Searched site:docs.anthropic.com Claude Code harness documentation

• Searching the web

• Searched site:anthropic.com/engineering harness design long-running application development Anthropic

• Searching the web

• Searched https://docs.anthropic.com/en/docs/claude-code/sdk

• Searching the web

• Searched https://code.claude.com/docs/en/agent-sdk/agent-loop

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• 有，Anthropic / Claude Code 官方是有讲 “harness” 的，而且现在讲得比早期更明确。只是它不是一本叫《Claude Code Harness Spec》的完整内部实现文档，而是分散在：

  - Claude Code / Agent SDK 文档
  - Claude Code agent loop 文档
  - Anthropic Engineering Blog
  - Managed Agents 架构文章
  - Settings / Permissions / Monitoring / Sessions 等产品文档

  最直接的官方说法

  Anthropic 在 Managed Agents 架构文章里给了一个很清楚的定义：

  session = 发生过的一切的 append-only 日志
  harness = 调用 Claude 并把 Claude 的工具调用路由到相关基础设施的循环
  sandbox = Claude 可以运行代码和编辑文件的执行环境

  也就是说，Anthropic 官方语境里的 harness，核心就是：

  调用模型 + 工具路由 + 上下文管理 + 会话/状态 + 权限/沙箱 + 可观测性

  来源：
  https://www.anthropic.com/engineering/managed-agents

  Claude Code / Agent SDK 官方文档

  这是最值得看的官方入口：

  - Claude Agent SDK Overview
    https://code.claude.com/docs/en/agent-sdk/overview
    官方说 Agent SDK 提供了和 Claude Code 相同的 tools、agent loop、context management。它可以让你在 Python / TypeScript 里构建能读文件、跑命令、搜索、改代码的生产级 agent。
  - How the agent loop works
    https://code.claude.com/docs/en/agent-sdk/agent-loop
    这页就是 harness 的核心运行循环。官方流程大致是：
      1. 接收 prompt、system prompt、工具定义、历史记录
      2. Claude 判断下一步
      3. 如果需要工具，SDK 执行工具
      4. 工具结果返回给 Claude
      5. 重复直到没有工具调用
      6. 返回最终结果、token、cost、session id
  - Sessions
    https://code.claude.com/docs/en/agent-sdk/sessions
    学 session 续跑、恢复上下文、fork 会话。
  - Permissions
    https://code.claude.com/docs/en/agent-sdk/permissions
    学工具权限、允许/拒绝工具、审批机制。
  - Monitoring / OpenTelemetry
    https://code.claude.com/docs/en/monitoring-usage
    学 Claude Code 的使用量、成本、工具活动、日志、trace 监控。

  Anthropic Engineering 里的 harness 文章

  这几篇很关键：

  - Effective harnesses for long-running agents
    https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
    这是官方专门讲 long-running agent harness 的文章。它说 Claude Agent SDK 是一个通用 agent harness，适合编码和其他需要工具、上下文收集、规划、执行的任务。文章重点讲：长任务不能只靠一
    个大 prompt，需要 initializer agent、coding agent、结构化产物、跨 session 交接。
  - Harness design for long-running application development
    https://www.anthropic.com/engineering/harness-design-long-running-apps
    这篇更偏高级架构。它讲 planner、generator、evaluator 三 Agent 架构，用 evaluator 反复评审 generator 的结果，适合长时间自动开发完整应用。
  - Building agents with the Claude Agent SDK
    https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
    这篇讲怎么用 Claude Agent SDK 构建 agent，并提到 Claude Code 常见循环：收集上下文 → 执行动作 → 验证工作 → 重复。

  但它没有公开什么？

  Anthropic 官方明确说过：

  - Claude Code 的内部 system prompt 不公开；
  - 你可以用 CLAUDE.md 或 --append-system-prompt 增加自定义行为；
  - Claude Code 的完整内部 harness 实现细节不是完整公开规范。

  来源：
  https://code.claude.com/docs/en/settings

  所以答案是：

  有官方 harness 说明；
  但不是公开完整 Claude Code 内部实现。
  官方主要通过 Agent SDK、agent loop、permissions、sessions、monitoring、engineering blog 来解释 harness。

  建议你按这个顺序读

  1. Agent SDK overview：先理解 Claude Code harness 能力边界
     https://code.claude.com/docs/en/agent-sdk/overview
  2. How the agent loop works：理解核心循环
     https://code.claude.com/docs/en/agent-sdk/agent-loop
  3. Configure permissions：理解为什么 harness 必须管权限
     https://code.claude.com/docs/en/agent-sdk/permissions
  4. Work with sessions：理解长任务怎么恢复和续跑
     https://code.claude.com/docs/en/agent-sdk/sessions
  5. Effective harnesses for long-running agents：理解长任务设计模式
     https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  6. Harness design for long-running application development：理解多 Agent harness
     https://www.anthropic.com/engineering/harness-design-long-running-apps

  一句话总结：Claude Code 的官方 harness 资料是有的，关键词不要只搜 harness，还要搜 Agent SDK、agent loop、sessions、permissions、sandbox、managed agents。


