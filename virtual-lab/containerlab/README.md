
- 搭建测试实验室

- 执行测试用例


## TODO

- 通过容器安装 containerlab



## 附录

### 名词解释

| 名词 | 英文解释                  | 解释         |
|------|---------------------------|--------------|
| NOS  | Network Operating Systems | 网络操作系统 |
| CI   | Continuous Integration    | 持续集成     |
| CD   | Continuous Deployment     | 持续部署     |


### AI

#### GitLab CI/CD

GitLab 本身就内置了 CI/CD 能力，所以“持续集成、持续部署 与 GitLab 结合”本质上就是：

把你的自动化流程写进 GitLab，让它在你每次提交代码时自动执行。

最核心的几个东西是：

- GitLab 仓库：存放代码
- .gitlab-ci.yml：定义自动化流程的配置文件
- GitLab Runner：真正执行任务的执行器
- Pipeline：一次完整的自动化流程
- Job：流程中的某一步，比如测试、构建、部署

你可以把它理解成这条链路：

1. 开发者把代码 push 到 GitLab
2. GitLab 检测到代码变更
3. 按 .gitlab-ci.yml 创建一条 pipeline
4. Runner 按顺序执行各个 job
5. 先做 CI：测试、检查、构建
6. 再做 CD：发布到测试环境或生产环境

简单说：

- CI 在 GitLab 里负责“验证代码没问题”
- CD 在 GitLab 里负责“把代码发到目标环境”

一个很常见的结合方式是：

- 提交代码后自动运行单元测试
- 测试通过后自动构建 Docker 镜像
- 构建完成后自动部署到测试环境
- 如果是生产环境，可以设置成手动批准后再部署

一个最基础的 .gitlab-ci.yml 例子：

stages:
  - test
  - build
  - deploy

test_job:
  stage: test
  script:
    - echo "运行测试"
    - pytest

build_job:
  stage: build
  script:
    - echo "构建镜像"
    - docker build -t myapp:$CI_COMMIT_SHORT_SHA .

deploy_job:
  stage: deploy
  script:
    - echo "部署到服务器"
    - ssh user@server "docker pull myapp:$CI_COMMIT_SHORT_SHA && docker restart myapp"
  only:
    - main

这段配置的意思是：

- test 阶段：跑测试
- build 阶段：构建镜像
- deploy 阶段：如果是 main 分支，就执行部署

如果你问“具体怎么落地”，一般是这 5 步：

- 在 GitLab 创建项目并上传代码
- 编写 .gitlab-ci.yml
- 安装并注册 GitLab Runner
- 在 GitLab 里配置 CI/CD Variables，比如服务器密码、SSH Key、镜像仓库账号
- 每次提交代码后观察 pipeline 是否成功

实际工作里，GitLab 里通常这样分工：

- CI
    - 代码格式检查
    - 静态扫描
    - 单元测试
    - 构建产物
- CD
    - 发布制品到镜像仓库
    - 部署到测试环境
    - 手动批准后部署到生产环境

你还会经常看到这些 GitLab 功能：

- Runner：执行任务的机器
- Variables：保存密钥、密码、Token
- Environments：区分 dev、test、prod
- Manual jobs：生产部署前人工点击确认
- Artifacts：保存构建结果
- Tags：把任务分配给指定 Runner

一个很实用的理解方式是：

- GitLab = 平台
- .gitlab-ci.yml = 流程说明书
- Runner = 干活的人
- Pipeline = 一次完整执行
- CI/CD = 这套自动化执行的目标

如果你是初学者，我建议先这样接 GitLab：

1. 先只做 CI：提交代码后自动测试
2. 再加 build：自动打包或构建镜像
3. 最后加 CD：先部署测试环境，再考虑生产环境

如果你愿意，我可以下一步直接给你一份：

1. 最小可用的 GitLab CI/CD 配置
2. Node.js 项目的 GitLab CI/CD 示例
3. Docker 项目的 GitLab CI/CD 示例

你回复一个编号，我直接给你现成模板。


