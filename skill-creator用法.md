









## 附录


### AI

#### skill-creator 使用

• $skill-creator 是一个“教你怎么做 skill”的元技能。它不直接帮你处理某类业务，而是指导你新建或更新一个可复用的 Codex skill。定义在 SKILL.md。

  什么时候用

  - 你想新建一个 skill
  - 你想补全现有 skill 的 SKILL.md
  - 你想给 skill 增加 scripts/、references/、assets/
  - 你想生成或修复 agents/openai.yaml

  基本用法

  1. 先明确 skill 的使用场景和触发语句。
     例如：用户会怎么说，skill 要解决什么问题，边界是什么。
  2. 规划哪些内容应该沉淀成可复用资源。
     例如：重复逻辑放 scripts/，详细文档放 references/，模板素材放 assets/。
  3. 如果是新 skill，用初始化脚本建骨架。

  python3 /home/yuchao/.codex/skills/.system/skill-creator/scripts/init_skill.py my-skill --path /home/yuchao/.codex/skills

  4. 编辑 SKILL.md。
     前言区只写 name 和 description；description 要把“做什么”和“什么时候触发”写清楚。
  5. 生成或更新 agents/openai.yaml。

  python3 /home/yuchao/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py /path/to/skill --interface 'display_name=My Skill' --interface 'short_description=...'
  --interface 'default_prompt=Use $my-skill to ...'

  6. 跑校验。

  python3 /home/yuchao/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/skill

  7. 用真实任务试一遍，再迭代。

  这个 skill 的核心原则

  - SKILL.md 要短，别把大段资料都塞进去
  - 触发条件写在 frontmatter 的 description，不要只写在正文
  - 详细资料尽量拆到 references/
  - 需要稳定执行的重复操作尽量写成 scripts/
  - 不要额外生成 README.md、CHANGELOG.md 这类无关文件

  最小目录结构

  my-skill/
  ├── SKILL.md
  ├── agents/
  │   └── openai.yaml
  ├── scripts/        # 可选
  ├── references/     # 可选
  └── assets/         # 可选

  如果你愿意，我下一步可以直接按 $skill-creator 的流程，帮你从 0 到 1 创建一个新 skill。

› 你上边的描述中，没有说明何时在codex 内部调用这个skill 啊


• 对，这一层我刚才没讲清楚。

  $skill-creator 在 Codex 里不是“你手动调用的函数”，而是“当请求命中条件时，Codex 自动加载的一套指令”。在当前这套规则里，它的内部调用时机是这样的：

  1. Codex 先只看到每个 skill 的元数据：name 和 description。
  2. 当用户请求满足下面任一条件时，就应触发 skill-creator：
      - 用户显式提到 $skill-creator
      - 用户虽然没写技能名，但需求明显是在“新建或更新一个 skill”
  3. 一旦触发，Codex 才去读这个 skill 的 SKILL.md 正文，并按里面的流程执行。
  4. 如果 SKILL.md 又引用了 references/、scripts/，再按需继续读，不会一开始全加载。
  5. 这个触发只对当前轮有效；下一轮如果用户没再提，默认不会继续沿用。

  对 skill-creator 来说，典型触发语句是：

  - “帮我创建一个新 skill”
  - “帮我完善这个 skill 的 SKILL.md”
  - “给这个 skill 增加 scripts/references/assets”
  - “帮我生成 agents/openai.yaml”
  - “这个 skill 写得太模板化了，重构一下”

  不触发的情况通常是：

  - 用户只是让你分析代码、修 bug、写功能
  - 用户讨论的是某个业务问题，而不是“做一个 skill”

  所以更准确地说，$skill-creator 的“内部调用时机”就是：
  “当用户显式点名，或任务语义明显是在创建/更新 skill 时，Codex 必须加载它。”

  如果你要，我可以继续给你画一张“Codex 内部 skill 触发流程图”，把“元数据匹配 -> 读 SKILL.md -> 按需读 references -> 执行任务”这条链说明白。


