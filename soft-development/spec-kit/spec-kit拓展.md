

## 查看拓展

```bash
$ specify extension list

Installed Extensions:

  ✓ Git Branching Workflow (v1.0.0)
     git
     Feature branch creation, numbering (sequential/timestamp), validation, and Git remote
detection
     Commands: 5 | Hooks: 18 | Priority: 10 | Status: Enabled
```


### Commands(命令)


**拓展目录**

```bash
~/AI/spec-kit/topo-kit/.specify/extensions/git/commands$ ls
speckit.git.commit.md   speckit.git.initialize.md  speckit.git.validate.md
speckit.git.feature.md  speckit.git.remote.md
```

**skill目录**

```bash
~/AI/spec-kit/topo-kit/.agents/skills$ ls
speckit-analyze       speckit-git-commit      speckit-git-validate  speckit-tasks
speckit-checklist     speckit-git-feature     speckit-implement     speckit-taskstoissues
speckit-clarify       speckit-git-initialize  speckit-plan
speckit-constitution  speckit-git-remote      speckit-specify
```

**实际使用**

```bash
› $speckit-git

  speckit-git-commit      [Skill] Auto-commit changes after a Spec Kit command completes
  speckit-git-feature     [Skill] Create a feature branch with sequential or timestamp numb…
  speckit-git-initialize  [Skill] Initialize a Git repository with an initial commit
  speckit-git-remote      [Skill] Detect Git remote URL for GitHub integration
  speckit-git-validate    [Skill] Validate current branch follows feature branch naming con…
```


### Hooks(钩子)


```AI
• 这里的 Hooks 指的是扩展挂到 Spec Kit 主流程里的“钩子事件”，不是 Git 里的 .git/hooks。

  - Commands: 5 表示这个扩展提供了 5 个可调用命令，比如 speckit.git.feature、
    speckit.git.commit
  - Hooks: 18 表示这个扩展注册了 18 个“在某个时机自动触发”的事件处理
  - 这些时机通常是 before_* 或 after_*，比如：
      - before_specify：在执行 specify 前先跑 speckit.git.feature
      - after_plan：在执行 plan 后可触发 speckit.git.commit
  - 所以它的意思更接近“生命周期回调”/“自动挂载点”，不是你手动敲的命令

  你这个仓库里定义也很清楚：

  - 扩展文档里专门列了 Hooks 表：.specify/extensions/git/README.md:25
  - 扩展元数据里定义了 18 个 hook：.specify/extensions/git/extension.yml:42
  - 当前项目启用了自动执行 hooks：.specify/extensions.yml:3

  按你现在这个 Git 扩展来看，18 个 hook 基本就是：

  - 2 个必选 hook：初始化 Git、创建 feature branch
  - 16 个可选 hook：在 clarify/plan/tasks/implement/checklist/analyze/taskstoissues 的前后自
    动提交

  如果你愿意，我可以顺手把这 18 个 hook 全部翻成中文表给你看。
```

### 优先级

```AI
• 这里的 Priority 可以理解成“解析优先级 / 生效先后级”，不是“重要程度评分”。

  - 这套实现里写得很明确：lower priority number = higher precedence，也就是数字越小，优先级
    越高，越先被检查 /home/yuchao/.local/share/uv/tools/specify-cli/lib/python3.11/site-
    packages/specify_cli/extensions.py:480
  - 安装扩展时默认就是 10，所以你现在看到的 Priority: 10 基本就是“默认优先级” /home/
    yuchao/.local/share/uv/tools/specify-cli/lib/python3.11/site-packages/specify_cli/
    extensions.py:1024
  - 你这个项目里当前 git 扩展的优先级确实存成了 10：.specify/extensions/.registry:9

  怎么理解最实用：

  - 如果将来装了多个扩展，而它们都提供某些可解析资源，priority 决定“先看谁、谁先赢”
  - 在当前代码里，最直接的用途是模板解析：扩展提供的模板会按 priority 顺序遍历，数字小的先尝
    试 /home/yuchao/.local/share/uv/tools/specify-cli/lib/python3.11/site-packages/
    specify_cli/presets.py:1770
  - 如果 priority 一样，就按扩展 ID 字母序稳定排序 /home/yuchao/.local/share/uv/tools/
    specify-cli/lib/python3.11/site-packages/specify_cli/extensions.py:481

  另外有两个容易误解的点：

  - 它不是“这个扩展更重要”的意思，只是“冲突/解析时谁先被采用”
  - 它看起来也不是 hook 执行顺序控制项；hook 是注册到 .specify/extensions.yml 里，然后按事件
    下已有列表取出来，没有看到按 priority 再排序 /home/yuchao/.local/share/uv/tools/specify-
    cli/lib/python3.11/site-packages/specify_cli/extensions.py:2247 /home/yuchao/.local/
    share/uv/tools/specify-cli/lib/python3.11/site-packages/specify_cli/extensions.py:2317

  放到你现在这个仓库里：

  - 目前只有一个 git 扩展，所以 Priority: 10 几乎没有实际差别
  - 只有当你以后再装别的扩展，而且它们在“模板/资源解析”上可能重叠时，这个值才会明显影响结果

  如果你想改它，可以用：

  specify extension set-priority git 5

  这会把 git 的优先级调高，因为数字更小了。
  如果你愿意，我也可以继续帮你举一个“两个扩展同时存在时，priority 到底怎么影响结果”的具体例
  子。

```



