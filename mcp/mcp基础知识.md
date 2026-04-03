
## 交互协议

- [JSON-RPC 2.0](JSON-RPC_2-0.md)

## 传输方式

- [标准输入输出(stdio)](标准输入输出.md)
- [流式HTTP(Streamable HTTP)](流式HTTP.md)

## 能力定义

- 工具(Tools)
- 资源(Resources)

- 提示词(Prompts)

  暂时不搞这个.


## 附录

• 官方规范已经查过了。我接下来会把它拆成“是什么、怎么工作、有哪些核心概念、安全吗、怎么上手”几部分，尽量用工程视角讲清楚。

• 这里先按 AI 领域里的 MCP = Model Context Protocol 来讲。

  MCP 是什么

  MCP 可以理解成“AI 应用连接外部世界的通用协议”。
  它的目标，是把 AI 与文件系统、数据库、GitHub、Slack、内部业务系统等的连接方式标准化，避免每个客户端都为每个系统单独写一套集成。

  官方在 2024 年 11 月 25 日公开了这个协议；截至我现在查到的官方文档，当前协议版本页显示的版本是 2025-11-25。它的版本号直接用日期表示。
  参考：Anthropic 介绍 (https://www.anthropic.com/news/model-context-protocol)、官方版本说明 (https://modelcontextprotocol.io/specification/)

  为什么它重要

  没有 MCP 时，AI 工具接一个新系统，通常要单独写适配层。
  有了 MCP 后，关系会变成：

  - AI 客户端按统一协议对接
  - 外部系统通过 MCP Server 暴露能力
  - 双方靠标准能力协商、消息格式、认证方式通信

  所以它本质上是一个“标准接口层”，不是模型，也不是 RAG 本身，更不是某个特定厂商私有 API。

  核心架构

  MCP 采用 Host / Client / Server 的结构：

  - Host：面向用户的 AI 应用，比如桌面端、IDE、代码助手
  - Client：Host 内部负责和某个 MCP Server 建连的组件
  - Server：真正提供能力的一端

  协议分两层：

  - 数据层：基于 JSON-RPC 2.0，定义请求、响应、通知、能力协商
  - 传输层：负责怎么传消息

  官方当前重点传输方式是：

  - stdio：本地进程间通信，适合本地 MCP Server
  - Streamable HTTP：适合远程 Server

  旧的 HTTP+SSE 已被新传输方式取代，只保留兼容说明。
  参考：架构概览 (https://modelcontextprotocol.io/docs/learn/architecture)、传输层 (https://modelcontextprotocol.io/specification/draft/basic/transports)

  最核心的 3 个服务端能力

  - Tools：可执行动作
    例如查数据库、调 API、创建 issue、运行某个操作
  - Resources：可提供上下文
    例如文件、日志、数据库 schema、文档内容
  - Prompts：可复用提示模板
    更像“预设工作流入口”或“标准化 prompt 模板”

  可以简单理解为：

  - Resources 是“给模型看的东西”
  - Tools 是“让模型做的事”
  - Prompts 是“帮用户快速触发某种交互方式”

  参考：Tools (https://modelcontextprotocol.io/specification/2025-06-18/server/tools)、Resources (https://modelcontextprotocol.io/specification/2025-06-18/server/resources)、Prompts
  (https://modelcontextprotocol.io/specification/draft/server/prompts)

  客户端侧的重要能力

  MCP 不只是“Server 给 Client 提供工具”。

  它还支持一些反向能力：

  - Sampling：Server 可以请求 Client 代为调用大模型
  - Elicitation：Server 可以通过 Client 向用户索取额外信息

  这很关键，因为它意味着：

  - Server 不一定自己持有模型 API Key
  - 复杂工作流里，Server 可以在中途向用户补问信息
  - 某些场景可以做更完整的 agent 交互链路

  截至官方 2025-11-25 版本，Elicitation 还增加了 URL 模式，适合授权、支付、外部页面确认这类必须跳出客户端处理的流程。
  参考：Sampling (https://modelcontextprotocol.io/specification/2025-11-25/client/sampling)、Elicitation (https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)

  一次 MCP 连接大概怎么工作

  1. Client 先发 initialize
  2. 双方协商协议版本和能力
  3. Server 声明自己支持哪些能力，比如 tools/resources/prompts
  4. Client 决定把这些能力怎样呈现给用户或模型
  5. 运行过程中双方继续发请求、响应和通知
  6. 结束时正常关闭连接

  官方把这个生命周期明确分成：

  - Initialization
  - Operation
  - Shutdown

  参考：Lifecycle (https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)

  一个直观例子

  假设你在 IDE 里接了一个 GitHub MCP Server：

  - Resources 可以暴露仓库文件、PR 信息、Issue 列表
  - Tools 可以创建 issue、评论 PR、查工作流状态
  - Prompts 可以暴露“代码审查”“生成发布说明”这种模板

  于是你对 AI 说一句“帮我分析这个 PR，并把潜在风险建成 issue”，它就不只是聊天，而是能在受控前提下读取上下文并执行动作。

  安全是 MCP 的重点

  MCP 很强，但风险也不低，尤其是本地 Server。

  官方安全文档强调的点，最值得记住的是：

  - 本地 MCP Server 本质上是在你的机器上运行代码
  - 用户应当能看见将要执行的精确启动命令
  - 工具调用最好始终保留人工确认能力
  - 远程场景建议走 OAuth / 标准授权流程
  - 最小权限原则非常重要
  - 本地运行最好做沙箱隔离，限制文件系统和网络访问

  简单说：
  MCP 的价值来自“能动真系统”，所以安全边界必须单独设计，不能把它当普通插件。

  参考：安全最佳实践 (https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)、授权规范
  (https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)

  生态现状

  截至我查到的官方资料：

  - 官方 MCP Registry 已在 2025 年 9 月 8 日以 preview 形式推出
  - 它的目标是做 MCP Server 的官方发现入口
  - 也允许社区或企业在其上构建自己的子注册表

  参考：MCP Registry 公告 (https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/)、Registry (https://registry.modelcontextprotocol.io/)

  如果你要学 MCP，建议顺序

  - 先理解 Tools / Resources / Prompts
  - 再理解 Host / Client / Server
  - 然后看 stdio 和 Streamable HTTP
  - 最后补 Authorization 和 Security

  如果你愿意，我下一条可以继续给你讲这几种内容中的任意一种：

  1. 用通俗例子讲 MCP
  2. 讲 MCP 和 function calling / plugin / RAG 的区别
  3. 手把手写一个最小 MCP Server
  4. 讲 MCP 的安全风险和落地建议

  如果你说的 MCP 不是 Model Context Protocol，我也可以改讲别的 MCP。





