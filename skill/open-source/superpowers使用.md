
## 安装

### codex 安装

- 搜索插件

  ```codex
  › /plugins
    /plugins  browse plugins
  ```

- 输入名称查找插件

  ```codex
    Plugins
    Browse plugins from available marketplaces.
    Installed 1 of 29 available plugins.
   
    [All Plugins]  Installed (1)  OpenAI Curated  Workspace  Shared with me  Add Marketplace
   
    Type to search plugins
  › [-] Superpowers                   Installed   Space to disable; Enter view details.
    [-] Boltz                         Available · OpenAI Curated · Predict structures, screen molecules and proteins, and design binders
    [-] Build macOS Apps              Available · OpenAI Curated · Build, debug, instrument, and implement macOS apps with SwiftUI and AppKit guidance
    [-] Build Web Apps                Available · OpenAI Curated · Build frontend-focused web apps with generated assets, browser testing, payments, and databases
    [-] Build Web Data Visualization  Available · OpenAI Curated · Design, build, test, and export web data visualizations
    [-] CircleCI                      Available · OpenAI Curated · Build, test, and deploy any application
    [-] CodeRabbit                    Available · OpenAI Curated · Run AI-powered code review for your current changes
    [-] Codex Security                Available · OpenAI Curated · Security scanning for your codebase
  ```

- 安装插件

  ```codex
  Plugins
  Superpowers · Installed · OpenAI Curated
  An agentic skills framework & software development methodology that works: planning, TDD, debugging, and collaboration workflows.
 
› 1. Back to plugins   Return to the plugin list.
  2. install plugin    Install this plugin now.
     Source            Local
     Auth              Auth on install
     Version           local 5.1.3
     Skills            superpowers:brainstorming, superpowers:dispatching-parallel-agents, superpowers:executing-plans, superpowers:finishing-a-development-branch,
                       superpowers:receiving-code-review, superpowers:requesting-code-review, superpowers:subagent-driven-development, superpowers:systematic-debugging,
                       superpowers:test-driven-development, superpowers:using-git-worktrees, superpowers:using-superpowers, superpowers:verification-before-completion,
                       superpowers:writing-plans, superpowers:writing-skills
     Hooks             No plugin hooks.
     Apps              No plugin apps.

  ```

### 安装确认

安装好之后的插件地址为:

```bash
$HOME/.codex/plugins/cache/openai-api-curated/superpowers/11c74d6b/skills
```

```bash
$ ls -al 
total 64
drwxrwxr-x 16 yuchao yuchao 4096 Jul 14 09:45 .
drwxrwxr-x  5 yuchao yuchao 4096 Jul 14 09:45 ..
drwxrwxr-x  4 yuchao yuchao 4096 Jul 14 09:45 brainstorming
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 dispatching-parallel-agents
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 executing-plans
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 finishing-a-development-branch
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 receiving-code-review
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 requesting-code-review
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 subagent-driven-development
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 systematic-debugging
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 test-driven-development
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 using-git-worktrees
drwxrwxr-x  4 yuchao yuchao 4096 Jul 14 09:45 using-superpowers
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 verification-before-completion
drwxrwxr-x  3 yuchao yuchao 4096 Jul 14 09:45 writing-plans
drwxrwxr-x  4 yuchao yuchao 4096 Jul 14 09:45 writing-skills
```

## 插件使用

包含这四类skill:

- Meta
- Testing
- Debugging
- Collaboration

| 技能                           | 分类          | 说明                                             |
|--------------------------------|---------------|--------------------------------------------------|
| writing-skills                 | Meta          | 按照最佳实践方法培养新技能                       |
| using-superpowers              | Meta          | 技能系统介绍                                     |
| test-driven-development        | Testing       | 测试驱动开发                                     |
| systematic-debugging           | Debugging     | 系统性调试                                       |
| verification-before-completion | Debugging     | 在完成之前进行验证                               |
| brainstorming                  | Collaboration | 头脑风暴，设计优化                               |
| writing-plans                  | Collaboration | 写作计划(详细的实施方案)                         |
| executing-plans                | Collaboration | 执行计划(批量执行并支持检查点功能)               |
| dispatching-parallel-agents    | Collaboration | 派遣并行代理——并发的子代理工作流                 |
| requesting-code-review         | Collaboration | 请求代码审核 - 预审核检查清单                    |
| receiving-code-review          | Collaboration | 接收反馈 - 对反馈作出回应                        |
| using-git-worktrees            | Collaboration | 创建git wroktre                                  |
| finishing-a-development-branch | Collaboration | 完成开发分支的合并                               |
| subagent-driven-development    | Collaboration | 子代理驱动的开发模式——通过两阶段的评审来快速迭代 |


## 基本工作流

- brainstorming

  头脑风暴，通过提问的方式，完善想法，生成设计文档.

- using-git-worktrees

  创建worktree.

- writing-plans

  编写实现计划.

- executing-plans

  执行计划.

- test-driven-development

  测试驱动开发.

- requesting-code-review

  代码review.

- finishing-a-development-branch

  完成开发分支.


