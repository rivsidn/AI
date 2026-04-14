
## 安装

### 安装

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### 更新

```bash
# 更新spec-kit
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# 项目更新
specify init --here --force --ai <your-agent>
```

其中'X.Y.Z' 对应版本号，查询版本号地址 [release](https://github.com/github/spec-kit/releases).

## 简单示例

### 初始化

```bash
$ specify init --ai codex --script sh sendto-kindle
$ cd sendto-kindle
```

开启`codex` 之后，可以通过 **"Prompt: 显示当前可用的skill"** ，查看`spec-kit` 是
否正式可用.


### 建立约束

```codex
› $speckit-constitution 当前是一个空项目目录，请帮我生成代码约束，侧重用户使用便捷性
› $speckit-git-commit
```

### 明确任务

```codex
› $speckit-specify 我希望能够有一个程序，能够监听邮箱的收件，收到之后能够将这个网址的内容转
  换成epub格式，发送到我的kindle 邮箱.
› $speckit-git-commit
```

聚焦 **干什么、为什么干？** 不涉及技术栈.

### 实现计划

```codex
› $speckit-plan
› $speckit-git-commit
```

### 任务列表

```codex
› $speckit-tasks
› $speckit-git-commit
```

### 开始实现

```codex
› $speckit-implement
```

## 附录

### TODO

- 已经存在的项目如何使用`speckit`？

- 插件如何安装？如何使用？

### 常见问题

- Selected model is at capacity. Please try a different model.

  模型异常，重新执行即可.


### 参考资料

- [github spec-kit](https://github.com/github/spec-kit)

