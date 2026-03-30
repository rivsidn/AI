

- terminal-control-mcp 熟悉



## 附录

### AI

• 截至 2026-03-30，我搜到的结果是：有现成工程，但“AI 直接通过 tmux 管传统虚拟机”的成熟开源成品不多。更常见的是三类：tmux 控制层、SSH/运维终端、VM/沙箱层。

  最贴近你需求

  - terminal-control-mcp (https://github.com/wehnsdaefflae/terminal-control-mcp)：MCP + tmux/libtmux，AI 可管理持久终端 session，README 明确写了支持 SSH 连接，并带命令过滤、审计日志、W
    eb 旁路接管。很适合做 AI -> tmux -> ssh -> VM。
  - nickgnd/tmux-mcp (https://github.com/nickgnd/tmux-mcp)：给 AI 读写 tmux session/pane 的 MCP 服务，能列 session、抓 pane、执行命令。
  - lox/tmux-mcp-server (https://github.com/lox/tmux-mcp-server)：更轻量，提供 start_session、send_commands、view_session、list_sessions 这些接口，适合原型。
  - jonrad/tmux-mcp (https://github.com/jonrad/tmux-mcp)：也是 tmux MCP，但作者自己标了 POC，更适合参考，不建议直接上生产。
  - TmuxAI (https://github.com/alvinunreal/tmuxai)：AI 直接“住在” tmux 里，读取 pane 内容，在单独 exec pane 执行命令，还带确认机制。它不是专门做 VM 管理，但交互形态非常接近你的目标。最
    新 release 是 v2.1.2，日期 2026-03-18。

  更偏 SSH / 运维

  - Chaterm (https://github.com/chaterm/Chaterm)：开源 AI terminal + SSH client，面向服务器、Kubernetes、多集群运维，更像“AI 运维终端”而不是 tmux 工具。最新 release 是 v0.9.4，日期 202
    6-03-24。
  - SSHTMux (https://github.com/scjorge/sshtmux)：tmux + SSH 管理器，支持多主机、批量命令、snippet/playbook。它本身不带 AI，但很适合做你的 host/session 层。

  更偏多 Agent / 编排

  - Claude Squad (https://github.com/smtg-ai/claude-squad)：明确写了底层用 tmux + git worktrees 管多个 AI terminal agent。适合“一台 VM/一类任务一个 agent”的模式。最新 release 是 v1.0.1
    7，日期 2026-03-12。
  - Tmux-Orchestrator (https://github.com/Jedward23/Tmux-Orchestrator)：直接演示 agent 间通过 tmux session/window 通信和自调度，概念很接近，但成熟度明显低一些。

  如果你其实更想要“AI 管隔离虚拟环境”

  - E2B Sandbox MCP (https://github.com/HeurisTech/e2b-sandbox-mcp)：AI 创建和控制 Ubuntu 虚拟桌面。
  - trycua/cua (https://github.com/trycua/cua)：开源 computer-use 基础设施，包含 macOS/Linux VM 管理。最新 release 页面显示到 2026-03-27。
  - agent-sandbox (https://github.com/kubernetes-sigs/agent-sandbox)：Kubernetes 方向的 agent runtime sandbox。
  - Arrakis (https://github.com/abshkbh/arrakis)：自托管 MicroVM sandbox。
  - VibeVM (https://github.com/Phala-Network/VibeVM)：运行在 Confidential VM 里的 agent sandbox。

  结论
  按我这轮搜索，我没搜到一个已经很成熟、主流、开箱即用、专门针对 virsh/Proxmox/VMware，并且底层就是 tmux 的头部开源项目。现在最现实的路线仍然是：

  AI -> tmux/SSH 会话层 -> 你自己的 VM 控制器(API / virsh / Proxmox)

  如果你要自建，这些项目里最值得先看的通常是：
  terminal-control-mcp、TmuxAI、Chaterm。

  另外，如果你准备自己实现，tmux 官方的 Control Mode (https://github.com/tmux/tmux/wiki/Control-Mode) 比单纯 send-keys 更稳。

  如果你愿意，我可以下一步继续帮你专门搜一轮 Proxmox / libvirt(virsh) / VMware 方向，把最适合改造成你需求的仓库筛出来。



