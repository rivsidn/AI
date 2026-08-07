
## 安装

```bash
npm install -g @fission-ai/openspec@latest
```


## 终端命令

### init

```bash
openspec init
```

### config

```bash
# 配置选项:
# 
# delivery      OpenSpec 能力要以什么载体(skill/command)交付给 AI 工具
# workflows     启用哪些动作 / 命令

openspec config profile

```


## 工作流

### 默认模式

```bash
/opsx:explore ──► /opsx:propose ──► /opsx:apply ──► /opsx:sync ──► /opsx:archive
  (optional)
```

| 命令          | 说明                                 |
|---------------|--------------------------------------|
| /opsx:explore | 不知道要干什么的时候，先探索当前工程 |
| /opsx:propose | 知道要干什么的时候，直接开始设计     |
| /opsx:apply   | 开始实现                             |
| /opsx:sync    | Merge delta specs into main specs    |
| /opsx:archive | 结束修改                             |

### 快速模式

```bash
/opsx:new ──► /opsx:ff ──► /opsx:apply ──► /opsx:verify ──► /opsx:archive
```

| 命令          | 说明                              |
|---------------|-----------------------------------|
| /opsx:new     | 创建一个新的change 所需要的脚手架 |
| /opsx:ff      | 快速创建完所有的文档              |
| /opsx:apply   | 开始实现                          |
| /opsx:verify  | 确认文档和实现是否一致            |
| /opsx:archive | 结束并归档                        |


### 拓展模式(二)

```bash
/opsx:explore ──► /opsx:new ──► /opsx:continue ──► ... ──► /opsx:apply
```

| 命令           | 说明                              |
|----------------|-----------------------------------|
| /opsx:explore  | 开始探索                          |
| /opsx:new      | 创建一个新的change 所需要的脚手架 |
| /opsx:continue | 一次性创建一个文档                |
| /opsx:apply    | 开始实现                          |


## 附录

### 地址

- [openspec](https://github.com/Fission-AI/openspec)

### 名词解释

- schema

  OpenSpec 里的 schema = 描述一个 change 应该经历哪些规划产物、按什么顺序生成、每个产物怎么写的工作流定义.


