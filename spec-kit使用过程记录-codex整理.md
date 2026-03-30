• 下面给你一套针对 KeyScriptor 的最小落地流程。

  1. 进入项目目录并初始化（用你正在用的 AI 助手，这里按 codex 举例）

  cd /home/yuchao/AI_ask/KeyScriptor
  specify init --here --ai codex --force
  specify check

  2. 在你的 AI 助手里按 spec-kit 流程依次执行

  /speckit.constitution
  /speckit.specify
  /speckit.plan
  /speckit.tasks
  /speckit.implement

  3. 每一步建议写的内容（按 KeyScriptor 场景）
  4. constitution：先定规则

  - 配置文件驱动（YAML/JSON）
  - 默认只允许白名单按键
  - 必须有 dry-run（只打印不执行）
  - 必须支持紧急停止键（如 Esc）
  - 所有自动输入都要有日志与可追踪性

  2. specify：写需求

  - 输入：配置文件路径
  - 输出：按配置顺序模拟键盘输入
  - 能力：延时、组合键、重复、条件停止
  - 非功能：跨平台优先级（先 Linux），错误提示清晰

  3. plan：写技术方案

  - 模块划分：config_loader、validator、executor、logger
  - 键盘库选型：如 Python 的 pynput/keyboard（按平台取舍）
  - 配置 schema 与校验策略
  - 安全机制：黑名单窗口、速率限制、最大执行时长

  4. tasks：拆可执行任务

  - CLI 骨架
  - 配置解析与 schema 校验
  - 执行引擎（单键/组合键/延时/循环）
  - dry-run 与日志
  - 单元测试与示例配置

  5. implement：按任务实现并跑测试
  6. 你可以直接先用的首版命令（示例）

  # 假设后续实现为 Python CLI
  python -m keyscriptor run -c examples/demo.yaml --dry-run
  python -m keyscriptor run -c examples/demo.yaml
