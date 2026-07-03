
## Eraser / DiagramGPT

• 可以，结论是：可以从 Codex 后台调用，但不是 Codex 内置能力，需要通过 Eraser 的 API / MCP / Agent Skill 接入。

  支持方式

  - REST API 方式：Eraser 有官方 Diagramming API，可以从后端服务、脚本、CI、Codex 执行环境里直接 HTTP 调用。
  - MCP Server 方式：Eraser 官方提供 MCP Server，地址是 https://app.eraser.io/api/mcp，用于让 AI coding agents 调用 Eraser。
  - Agent Skills 方式：Eraser 也提供 eraserlabs/eraser-io skills，面向 Claude Code、Cursor、Windsurf 以及其他支持 skills 的 agent。
  - Codex 是否能用：如果你的 Codex 环境能配置 MCP，或者能运行脚本发 HTTP 请求，就可以接；但需要你自己的 Eraser 账号授权/API Token。

  官方 API 能力
  Eraser 的 API 里有一个自然语言生成图的接口：

  POST https://app.eraser.io/api/render/prompt

  它支持传入：

  - text：自然语言 prompt，比如“画一个总部-分支机构组网图……”
  - diagramType：图类型，可选 cloud-architecture-diagram、flowchart-diagram、sequence-diagram、entity-relationship-diagram、bpmn-diagram、freeform-diagram
  - mode：standard 或 premium
  - attachments：可传 PNG、JPEG、PDF 作为上下文
  - gitContexts：可把 Git 仓库作为上下文
  - returnImageAsFile：是否直接返回图片文件
  - fileOptions：是否直接创建 Eraser 文件

  官方文档来源：
  https://docs.eraser.io/reference/generate-diagram-from-prompt

  注意限制

  - API 需要 Bearer Token。
  - DiagramGPT 页面写明：API 只对 Starter、Business、Enterprise Plan teams 开放。
    来源：https://www.eraser.io/diagramgpt

  - Eraser 文档还写到：API calls 需要启用 usage-based pricing。
    来源：https://docs.eraser.io/docs/usage-based-pricing

  - API 的 diagramType 里没有单独的 network-diagram 类型；做组网图通常用 cloud-architecture-diagram 或 freeform-diagram，然后在 prompt 里明确“network topology / firewall / switch /
    router / VLAN / subnet”。

  Codex 后台调用示例

  如果只是让 Codex 或你自己的后端调一次，可以类似这样：

  curl --request POST \
    --url https://app.eraser.io/api/render/prompt \
    --header "Authorization: Bearer $ERASER_API_TOKEN" \
    --header "Content-Type: application/json" \
    --data '{
      "text": "Create a network topology diagram: Internet connects to firewall, firewall connects to core switch, core switch connects to DMZ, office LAN, server VLAN, and database
      VLAN. Label VLAN IDs and subnets.",
      "diagramType": "cloud-architecture-diagram",
      "mode": "premium",
      "theme": "light",
      "imageQuality": 2
    }'

  如果要接到 Codex 工作流里
  我建议有三种方案：

  1. 最简单：Codex 生成 prompt + curl 调 Eraser API
     适合先验证效果。

  2. 更工程化：写一个本地脚本 generate-network-diagram.ts/py
     Codex 负责读取配置、生成 prompt、调用 Eraser API、保存图片 URL 或返回的文件。

  3. 更 Agent 化：配置 Eraser MCP Server
     Eraser 官方 MCP 文档说它可以让 AI coding agents 生成、创建、读取、搜索、更新 Eraser workspace 里的文件、图、文件夹、preset。
     来源：https://docs.eraser.io/docs/mcp

  所以答案是：支持后台调用，也适合接 Codex；但要看你是想“调用 API 出图”，还是想“把 Eraser 作为 Codex 的长期绘图工具/MCP 工具”。




## 附录

### AI 文字生成组网图

  - Eraser / DiagramGPT：专门有 AI Network Diagram Generator，可用英文描述或代码片段生成网络图，生成后能在 Eraser 里继续编辑，也支持 diagram-as-code 和付费 API。适合工程团队、技术文档。
    来源：Eraser 官网说明可从 plain English / code 生成并编辑网络图。https://www.eraser.io/ai/network-diagram-generator

  - Cloudairy：明确主打 AI Network Diagram Generator，描述服务器、交换机、路由器、防火墙等拓扑，自动生成 LAN/WAN/云/混合网络图。适合快速出方案图、教学图、IT 文档。https://cloudairy.com/ai/ai-network-diagram-generator

  - MockFlow AI Cisco Network Diagram：偏 Cisco 风格，描述 routers、switches、firewalls、VLAN、WAN links，AI 生成 Cisco-style 拓扑图，还强调 Cisco 图标、协议标签、网络分区。https://
    mockflow.com/ai/cisco-network-diagram-generator/

  - ChatDiagram：有 Free AI Network Diagram Maker，支持先免费生成 3 张，描述网络或上传文件后生成，可拖拽调整。https://www.chatdiagram.com/tool/network-diagram-maker
  - Miro AI Diagram Generator：不是专门网络图工具，但官网 FAQ 写明支持 network diagrams，并且 AI 生成内容可在 Miro 画布上完全编辑。适合协作评审、方案讨论。https://miro.com/ai/diagram-
    ai/ai-diagramming-generator-from-text/

  - Lucidchart / Lucid AI：可把复杂描述转成结构化图，也有成熟的网络图模板和协作能力。适合企业文档、跨团队协作。https://www.lucidchart.com/pages/use-cases/diagram-with-AI
  - EdrawMax AI：文本转图，支持在线生成、编辑、下载，官网称支持 210+ 类图。适合偏办公/通用制图。https://www.edrawmax.com/app/ai-diagram/
  - draw.io / diagrams.net：现在也有 Generate 功能，可在模板库或菜单里输入 prompt 生成图；此外还支持 Mermaid、CSV、From Text 等方式自动生成图。适合你想保留 draw.io 生态或 .drawio 文件流
    转。https://www.drawio.com/docs/best-practice/write-query-generate-diagram/

  - Excalidraw：有 Text to Diagram AI，更偏手绘风格架构图，不是最标准的网络设备图，但做方案草图很快。https://plus.excalidraw.com/use-cases/software-architecture-diagram
  - next-ai-draw-io：开源项目，把 AI 和 draw.io 集成，可以用自然语言创建、修改、增强 draw.io 图。适合二次开发或参考实现。https://github.com/DayuanJiang/next-ai-draw-io




