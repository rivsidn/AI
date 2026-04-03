
## pytest + scrapli 

• 可以，下面给你一个可直接跑的 pytest + scrapli 示例。

  这个示例会做 4 件事：

  - 通过 SSH 连接设备
  - 执行 show buildsvn
  - 获取命令输出
  - 把输出保存到本地 artifacts/ 目录

  我这里做成了 pytest 风格，并且支持通过 CLI 传参，这样更适合你后面接自动化和 CI。

  目录结构

  your_project/
  ├── conftest.py
  └── tests/
      └── test_show_buildsvn.py

  安装依赖

  pip install pytest scrapli

  如果你的环境不方便用系统 ssh，也可以装 paramiko transport：

  pip install "scrapli[paramiko]" pytest

  conftest.py
  ```python
  from pathlib import Path

  import pytest
  from scrapli import Scrapli
  from scrapli.driver import GenericDriver

  def pytest_addoption(parser):
      group = parser.getgroup("network")
      group.addoption("--host", action="store", required=True, help="设备 IP 或主机名")
      group.addoption("--port", action="store", type=int, default=22, help="SSH 端口，默认 22")
      group.addoption("--username", action="store", required=True, help="SSH 用户名")
      group.addoption("--password", action="store", required=True, help="SSH 密码")
      group.addoption(
          "--platform",
          action="store",
          default="generic",
          help="scrapli 平台名，例如 cisco_iosxe / cisco_nxos / generic",
      )
      group.addoption(
          "--pager-off-cmd",
          action="store",
          default="",
          help="关闭分页命令；generic 平台常需要，例如 'terminal length 0'",
      )


  @pytest.fixture(scope="session")
  def device(pytestconfig):
      return {
          "host": pytestconfig.getoption("host"),
          "port": pytestconfig.getoption("port"),
          "username": pytestconfig.getoption("username"),
          "password": pytestconfig.getoption("password"),
          "platform": pytestconfig.getoption("platform"),
          "pager_off_cmd": pytestconfig.getoption("pager_off_cmd"),
      }


  @pytest.fixture(scope="session")
  def artifact_dir():
      path = Path("artifacts")
      path.mkdir(parents=True, exist_ok=True)
      return path


  @pytest.fixture(scope="function")
  def conn(device, artifact_dir):
      common_kwargs = {
          "host": device["host"],
          "port": device["port"],
          "auth_username": device["username"],
          "auth_password": device["password"],
          "auth_strict_key": False,
          "channel_log": str(artifact_dir / f"{device['host']}_channel.log"),
      }

      if device["platform"] == "generic":
          driver = GenericDriver(**common_kwargs)
      else:
          driver = Scrapli(platform=device["platform"], **common_kwargs)

      with driver as connection:
          if device["pager_off_cmd"]:
              connection.send_command(device["pager_off_cmd"])
          yield connection

  tests/test_show_buildsvn.py

  from datetime import datetime

  COMMAND = "show buildsvn"

  def test_show_buildsvn(conn, device, artifact_dir):
      response = conn.send_command(COMMAND)
      output = response.result.strip()

      assert output, f"{COMMAND} 没有返回内容"

      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      safe_host = str(device["host"]).replace(":", "_").replace("/", "_")
      output_file = artifact_dir / f"{safe_host}_show_buildsvn_{timestamp}.txt"

      header = (
          f"host: {device['host']}\n"
          f"platform: {device['platform']}\n"
          f"command: {COMMAND}\n"
          f"time: {timestamp}\n"
          f"{'-' * 60}\n"
      )

      output_file.write_text(header + response.result, encoding="utf-8")

      print(f"\n命令输出已保存到: {output_file}")
  ```

  怎么运行

  如果你的设备平台不在 scrapli 的 core 平台里，先用 generic：

  pytest -s tests/test_show_buildsvn.py \
    --host 192.168.1.10 \
    --username admin \
    --password 'your_password' \
    --platform generic \
    --pager-off-cmd 'terminal length 0'

  如果你知道设备属于 scrapli core 平台，比如 Cisco IOS XE：

  pytest -s tests/test_show_buildsvn.py \
    --host 192.168.1.10 \
    --username admin \
    --password 'your_password' \
    --platform cisco_iosxe

  运行后会得到什么

  - 命令输出文件，例如：
      - artifacts/192.168.1.10_show_buildsvn_20260403_153000.txt
  - SSH 通道日志：
      - artifacts/192.168.1.10_channel.log

  几点说明

  - show buildsvn 是设备相关命令，不是所有厂商/平台都支持
  - 如果设备会分页，generic 模式下通常要手动传 --pager-off-cmd
      - Cisco 常见是 terminal length 0
      - 华为常见是 screen-length 0 temporary
      - H3C/Comware 常见是 screen-length disable
  - 如果设备需要先进入特权模式，generic 模式下你要自己补这一步；而 core 平台驱动会比 generic 更懂设备 CLI 语义
  - 示例里用了 auth_strict_key=False 是为了方便演示；生产环境更建议启用 SSH host key 校验

  为什么这样写

  - scrapli 官方建议：已知 core 平台优先用对应平台驱动或 Scrapli factory；非 core 平台可以用 GenericDriver
  - GenericDriver 和 core drivers 都支持 send_command
  - pytest 用 fixture 管理连接生命周期最自然，适合后面扩展成更多测试用例

  参考资料

  - scrapli Basic Usage: https://carlmontanari.github.io/scrapli/user_guide/basic_usage/
  - scrapli Advanced Usage / GenericDriver: https://carlmontanari.github.io/scrapli/user_guide/advanced_usage/
  - pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html

  如果你愿意，我下一条可以继续直接给你两种增强版中的一种：

  1. 支持从 devices.yaml 批量读取多台设备并循环保存输出
  2. 支持用户名/密码从环境变量读取，避免明文出现在命令行里

  你回我 1 或 2 就行。


## pytest + Netmiko

› 给我提供一个示例，链接ssh，执行show buildsvn 命令，获取输出并保存输出到文件中


• 可以，下面先给你一个最容易跑起来的 Netmiko 示例。它会：

  - 通过 SSH 连接网络设备
  - 执行 show buildsvn
  - 获取命令输出
  - 把输出保存到本地文件
  - 同时保留一份 SSH 会话日志，便于排错

  ```python
  # get_buildsvn.py
  import os
  from datetime import datetime
  from pathlib import Path

  from netmiko import ConnectHandler
  from netmiko.exceptions import (
      NetmikoAuthenticationException,
      NetmikoTimeoutException,
  )

  COMMAND = "show buildsvn"

  def main():
      # 创建目录
      Path("logs").mkdir(exist_ok=True)
      Path("output").mkdir(exist_ok=True)

      device = {
          "device_type": "cisco_ios",   # 按你的设备实际类型修改
          "host": os.environ["NET_HOST"],
          "username": os.environ["NET_USER"],
          "password": os.environ["NET_PASS"],
          "port": int(os.getenv("NET_PORT", "22")),
          "session_log": "logs/ssh_session.log",
      }

      conn = None
      try:
          conn = ConnectHandler(**device)

          # 如果你的设备需要 enable 模式，可以打开下面两行
          # conn.enable()
          # 或者在 device 里增加 "secret": "你的enable密码"

          output = conn.send_command(COMMAND, read_timeout=30)

          ts = datetime.now().strftime("%Y%m%d_%H%M%S")
          output_file = Path("output") / f"{device['host']}_buildsvn_{ts}.txt"
          output_file.write_text(output, encoding="utf-8")

          print(f"命令执行成功: {COMMAND}")
          print(f"输出已保存到: {output_file}")
          print()
          print(output)

      except NetmikoAuthenticationException as e:
          print(f"认证失败: {e}")
          raise
      except NetmikoTimeoutException as e:
          print(f"连接超时: {e}")
          raise
      finally:
          if conn:
              conn.disconnect()

  if __name__ == "__main__":
      main()
  ```

  运行前先安装依赖：

  pip install netmiko

  再设置环境变量：

  export NET_HOST=192.168.1.10
  export NET_USER=admin
  export NET_PASS='your_password'
  export NET_PORT=22

  然后运行：

  python get_buildsvn.py

  几点说明：

  - device_type 要按你的设备改，不同厂商不一样
      - Cisco IOS/IOS XE：cisco_ios
      - H3C/Comware：hp_comware
      - Huawei VRP：huawei
  - show buildsvn 是设备相关命令，如果你的设备不支持，就换成实际命令
  - 如果命令返回慢，把 read_timeout=30 调大一点，比如 60
  - 原始 SSH 交互日志会保存在 logs/ssh_session.log
  - 命令输出会保存在 output/ 目录下的时间戳文件里

  如果你想把它改成 pytest 版本，我也可以直接给你一个：

  - conftest.py 负责 SSH 连接
  - tests/test_buildsvn.py 负责执行命令并保存输出

  你要的话我下一条直接给你完整目录结构。







## 附录

### 学习资料



### AI

#### pytest

• 可以。pytest 可以理解成一个“Python 测试运行器 + 测试框架”。
  它最核心的价值是：用很少的样板代码，把测试的编写、组织、执行、筛选、报告、调试都串起来。

  按官方文档，pytest 的主要功能可以概括成下面这些。

  核心能力

  - 自动发现测试
      - 默认会递归查找当前目录及子目录里符合规则的测试文件，比如 test_*.py 和 *_test.py，并收集其中的测试函数/测试类来执行
      - 这让你通常只需要写好文件和函数命名，直接跑 pytest 就行
  - 断言很简洁，而且失败信息很强
      - 直接用 Python 原生 assert，不必记 self.assertEqual、self.assertTrue 这一类 API
      - pytest 会做“断言内省”，失败时给出更详细的比较信息，比如左右值分别是什么、哪一层不匹配
  - fixture 机制
      - 这是 pytest 最重要的功能之一
      - 你可以把测试前准备、测试后清理、共享资源初始化都写成 fixture
      - 测试函数只要把 fixture 名字写在参数里，就能“注入”进来
      - 支持不同作用域：function、class、module、package、session
      - 支持 yield 做 teardown，也支持 fixture 依赖 fixture
      - 很适合管理数据库连接、临时目录、浏览器会话、网络设备 SSH 连接这类资源
  - 参数化测试
      - 同一个测试逻辑，可以用多组输入反复跑
      - 官方提供 @pytest.mark.parametrize(...)
      - 也可以参数化 fixture
      - 这对“同一检查跑多台设备 / 多个命令 / 多组配置”特别适合
  - 标记与筛选
      - 可以给测试打标签，例如 smoke、slow、destructive
      - 官方内置常见 marks 包括：
          - skip
          - skipif
          - xfail
          - usefixtures
          - parametrize
      - 运行时可以用 -m 按 marker 选测试，用 -k 按名字表达式筛选
      - 这对大项目和 CI 非常重要
  - 跳过和“预期失败”
      - skip / skipif：不满足条件时跳过
      - xfail：已知问题先标成“预期失败”，避免它把整轮结果变成意外红灯
      - 很适合处理平台差异、已知 bug、实验功能

  运行与报告

  - 输出捕获
      - pytest 默认会捕获 stdout 和 stderr
      - 测试失败时，会把相关输出和 traceback 一起展示
      - 还能通过 capsys、capfd 这类 fixture 在测试内部读取输出
      - 对调试命令行程序、子进程、脚本输出很实用
  - 日志捕获
      - 默认会捕获 WARNING 及以上级别日志
      - 失败时会把日志单独显示
      - 还能通过 caplog fixture 断言日志内容
      - 如果你在测自动化脚本、网络巡检程序、后台任务，这个能力很好用
  - JUnit XML 等报告输出
      - 可以生成 JUnit XML，方便接 Jenkins、GitLab CI、GitHub Actions 等系统
      - 这就是为什么很多团队会说“pytest 很适合接 CI/CD”
  - 调试支持
      - 可以用 --pdb 在失败后直接进调试器
      - 还支持控制 traceback、失败后停止等常见调试选项
      - 对排查复杂测试很方便

  测试辅助能力

  - 临时目录/临时文件
      - 提供 tmp_path、tmp_path_factory
      - 每个测试都能拿到隔离的临时目录
      - 适合测试生成配置文件、导出日志、缓存文件等逻辑
  - monkeypatch
      - 这是 pytest 很实用的内置测试工具
      - 可以安全地修改/删除：
          - 对象属性
          - 字典项
          - 环境变量
          - sys.path
          - 当前工作目录
      - 测试结束后会自动恢复
      - 特别适合 mock 环境变量、替换 API 调用、屏蔽真实网络访问
  - 异常/警告断言
      - 可以很方便地断言某段代码会不会抛异常、会不会发 warning
      - 比手写 try/except 更清晰

  兼容与扩展

  - 能直接运行 unittest 测试
      - 官方明确支持直接跑基于 unittest.TestCase 的测试
      - 所以老项目迁移时，可以先把运行器换成 pytest，再逐步把测试改成 pytest 风格
  - 插件生态很强
      - 官方首页提到有上千个外部插件
      - 常见扩展方向包括：
          - 并行执行
          - 覆盖率统计
          - 重试 flaky tests
          - HTML 报告
          - Django / Flask / asyncio / Playwright 等生态集成
      - 一个很实用的点：很多你以为是“pytest 自带”的高级能力，实际上常常是插件提供的
        比如并行执行通常是 pytest-xdist，不是核心内置功能
  - 可配置性强
      - 可以通过 pytest.ini、pyproject.toml 等配置默认参数、markers、日志格式、测试路径等
      - 适合团队统一约定

  放到你前面说的“网络设备 CLI 自动化测试”里，pytest 最常见的用法是

  - 用 fixture 管理 SSH/Telnet 连接生命周期
  - 用 parametrize 跑多设备、多命令、多场景
  - 用 marker 区分：
      - smoke
      - read_only
      - config
      - destructive
  - 用 --junitxml 把测试结果接到 CI
  - 用 caplog / 输出捕获辅助排错
  - 再配合 scrapli 或 Netmiko 发命令和收结果

  一个很小的例子：

  import pytest

  @pytest.fixture(scope="module")
  def conn():
      c = connect_to_device()
      yield c
      c.close()

  @pytest.mark.smoke
  @pytest.mark.parametrize("cmd", ["show version", "show clock"])
  def test_show_commands(conn, cmd):
      output = conn.send_command(cmd)
      assert output

  这个例子里就同时用了 3 个核心功能：

  - fixture：管理连接
  - parametrize：同一条测试跑多条命令
  - mark：把它标成 smoke 测试

  如果你只想记住 pytest 的 5 个最核心关键词，我建议记这五个：

  - assert
  - fixture
  - parametrize
  - mark
  - report

  官方文档

  - 总文档: https://docs.pytest.org/en/stable/
  - 使用 fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
  - 参数化: https://docs.pytest.org/en/stable/how-to/parametrize.html
  - 标记 tests: https://docs.pytest.org/en/stable/how-to/mark.html
  - 捕获 stdout/stderr: https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
  - 日志管理: https://docs.pytest.org/en/stable/how-to/logging.html
  - monkeypatch: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
  - tmp_path: https://docs.pytest.org/en/stable/how-to/tmp_path.html
  - unittest 兼容: https://docs.pytest.org/en/stable/how-to/unittest.html

  如果你愿意，我下一条可以继续给你讲两种更贴近实战的内容：

  1. pytest 在网络设备自动化测试里怎么组织项目目录
  2. pytest 里 fixture / parametrize / marker 三者到底怎么配合用

  你回我 1 或 2 就行。







