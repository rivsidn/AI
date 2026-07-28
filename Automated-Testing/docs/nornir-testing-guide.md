# Nornir 多设备网络自动化测试实战

## 1. Nornir 是什么

Nornir 是一个以 Python 为核心的网络自动化框架，主要负责设备清单管理、设备筛选、并发任务执行和结果汇总。它本身不模拟网络设备，也不生成测试流量，而是通过 Netmiko、Scrapli、NAPALM、NETCONF 等插件连接真实或虚拟网络设备。

在网络设备功能测试平台中，Nornir 通常处于设备编排层：

```text
pytest 测试编排与断言
          |
          v
Nornir 设备筛选、并发执行、结果汇总
          |
          v
Netmiko / Scrapli / NAPALM / NETCONF
          |
          v
交换机、路由器、防火墙和虚拟 NOS
```

Nornir 适合以下场景：

- 同时操作多台网络设备。
- 按厂商、角色、站点或拓扑筛选设备。
- 批量下发配置并采集运行状态。
- 编排配置、检查、故障注入、收敛等待和环境恢复流程。
- 将设备操作直接集成到 pytest 测试用例。

Nornir 不是完整的测试产品。测试断言和报告通常由 pytest、Allure 等工具负责，数据面流量则由 Scapy、TRex、PTF、Ixia 或 Spirent 等工具负责。

## 2. 核心概念

| 概念 | 作用 |
| --- | --- |
| Inventory | 保存设备地址、平台、分组和自定义属性 |
| Task | 定义需要在设备上执行的操作 |
| Runner | 决定任务的并发执行方式和并发数量 |
| Plugin | 提供 SSH、NETCONF、库存、日志等扩展能力 |
| Result | 保存每台设备的输出、异常和成功/失败状态 |

相比以 YAML Playbook 为主的 Ansible，Nornir 更像一个可以嵌入项目的 Python 库。复杂的状态轮询、条件分支、故障恢复和测试框架集成通常更容易用 Python 表达。

## 3. 完整测试用例目标

本例使用三台 Cisco IOS 路由器组成三角形 OSPF 网络，验证 R1 到 R3 的主链路发生故障后，业务能否切换到经过 R2 的备用路径。

测试流程如下：

1. 并发检查三台设备的 OSPF 邻居是否全部达到 `FULL` 状态。
2. 检查 R1 到 R3 Loopback0 的路由是否使用直连主路径。
3. 从 R1 的 Loopback0 Ping R3 的 Loopback0，确认故障前业务正常。
4. 关闭 R1 到 R3 的接口，模拟主链路故障。
5. 轮询 R1 路由表，等待路由切换到经过 R2 的备用下一跳。
6. 再次执行 Ping，验证故障后的业务连通性。
7. 无论用例成功还是失败，都恢复被关闭的接口。
8. 恢复后再次检查全部 OSPF 邻居，避免污染后续测试。

> 本例以 Cisco IOS/IOSv 命令为准。其他厂商只需替换平台名称、接口命令、查询命令和输出解析逻辑，Nornir 与 pytest 的整体结构可以保持不变。

## 4. 测试拓扑

```text
                    10.0.12.0/30
              Gi0/1             Gi0/1
       Lo0 1.1.1.1      R1 ----- R2      Lo0 2.2.2.2
                         |         |
                   Gi0/2 |         | Gi0/2
                         |         |
          10.0.13.0/30   |         |   10.0.23.0/30
                         |         |
                   Gi0/2 +--- R3 --+ Gi0/1
                              Lo0 3.3.3.3
```

链路与地址规划：

| 设备 | 接口 | 地址 | 对端 | 用途 |
| --- | --- | --- | --- | --- |
| R1 | Loopback0 | 1.1.1.1/32 | - | Router ID 与 Ping 源地址 |
| R1 | GigabitEthernet0/1 | 10.0.12.1/30 | R2 Gi0/1 | 备用路径 |
| R1 | GigabitEthernet0/2 | 10.0.13.1/30 | R3 Gi0/2 | 主路径、故障注入点 |
| R2 | Loopback0 | 2.2.2.2/32 | - | Router ID |
| R2 | GigabitEthernet0/1 | 10.0.12.2/30 | R1 Gi0/1 | 备用路径 |
| R2 | GigabitEthernet0/2 | 10.0.23.1/30 | R3 Gi0/1 | 备用路径 |
| R3 | Loopback0 | 3.3.3.3/32 | - | 测试目的地址 |
| R3 | GigabitEthernet0/1 | 10.0.23.2/30 | R2 Gi0/2 | 备用路径 |
| R3 | GigabitEthernet0/2 | 10.0.13.2/30 | R1 Gi0/2 | 主路径 |

示例管理地址使用文档专用网段 `192.0.2.0/24`。运行前必须替换成实验室中真实可达的管理地址。

## 5. 前置条件

- Python 3.10 或更高版本。
- 三台设备已开启 SSH，并且测试主机能够访问管理地址。
- 三台设备已完成下述 OSPF 基线配置。
- 测试账号具备进入配置模式和执行接口 `shutdown` 的权限。
- 接口名称与设备实际名称一致。
- 测试期间没有其他任务操作同一组设备。

### 5.1 R1 基线配置

```text
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/1
 description TO-R2-Gi0/1
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description TO-R3-Gi0/2
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 passive-interface Loopback0
 network 1.1.1.1 0.0.0.0 area 0
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.13.0 0.0.0.3 area 0
```

### 5.2 R2 基线配置

```text
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
!
interface GigabitEthernet0/1
 description TO-R1-Gi0/1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description TO-R3-Gi0/1
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 passive-interface Loopback0
 network 2.2.2.2 0.0.0.0 area 0
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
```

### 5.3 R3 基线配置

```text
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
interface GigabitEthernet0/1
 description TO-R2-Gi0/2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description TO-R1-Gi0/2
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 3.3.3.3
 passive-interface Loopback0
 network 3.3.3.3 0.0.0.0 area 0
 network 10.0.23.0 0.0.0.3 area 0
 network 10.0.13.0 0.0.0.3 area 0
```

## 6. 示例项目目录

```text
nornir-ospf-failover/
├── config.yaml
├── pytest.ini
├── requirements.txt
├── inventory/
│   ├── defaults.yaml
│   ├── groups.yaml
│   └── hosts.yaml
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── nornir_helpers.py
    └── test_ospf_failover.py
```

## 7. 依赖文件

`requirements.txt`：

```text
nornir>=3.4,<4
nornir-netmiko>=1.0,<2
pytest>=8,<9
```

安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 8. Nornir 配置

`config.yaml`：

```yaml
inventory:
  plugin: SimpleInventory
  options:
    host_file: inventory/hosts.yaml
    group_file: inventory/groups.yaml
    defaults_file: inventory/defaults.yaml

runner:
  plugin: threaded
  options:
    num_workers: 10

logging:
  enabled: true
  level: INFO
  log_file: nornir.log
  to_console: false
```

线程 Runner 会并发执行设备任务。示例只有三台设备，`num_workers` 设置为 10 已足够；大型测试床应根据设备承载能力、跳板机限制和 AAA 限速调整。

## 9. Inventory 配置

### 9.1 设备清单

`inventory/hosts.yaml`：

```yaml
r1:
  hostname: 192.0.2.11
  groups:
    - ios
  data:
    router_id: 1.1.1.1
    expected_neighbors:
      - 2.2.2.2
      - 3.3.3.3
    primary_interface: GigabitEthernet0/2
    primary_next_hop: 10.0.13.2
    backup_next_hop: 10.0.12.2

r2:
  hostname: 192.0.2.12
  groups:
    - ios
  data:
    router_id: 2.2.2.2
    expected_neighbors:
      - 1.1.1.1
      - 3.3.3.3

r3:
  hostname: 192.0.2.13
  groups:
    - ios
  data:
    router_id: 3.3.3.3
    expected_neighbors:
      - 1.1.1.1
      - 2.2.2.2
```

### 9.2 设备分组

`inventory/groups.yaml`：

```yaml
ios:
  platform: cisco_ios
  port: 22
  connection_options:
    netmiko:
      extras:
        conn_timeout: 10
        auth_timeout: 10
        banner_timeout: 15
        fast_cli: false
  data:
    commands:
      ospf_neighbors: show ip ospf neighbor
      route: show ip route {prefix}
      ping: ping {target} source {source} repeat {count} timeout 1
```

### 9.3 默认配置

`inventory/defaults.yaml`：

```yaml
data:
  site: lab-a
```

用户名和密码不写入 Inventory，而是通过环境变量注入：

```bash
export LAB_USERNAME='lab-user'
export LAB_PASSWORD='replace-with-real-password'
```

生产环境建议进一步接入 Vault、企业密码管理系统或 CI 的 Secret Variables，避免密码出现在 Shell 历史和日志中。

## 10. pytest 配置

`pytest.ini`：

```ini
[pytest]
addopts = -ra -v
testpaths = tests
markers =
    network: requires access to the physical or virtual network lab
```

## 11. Nornir Fixture

`tests/conftest.py`：

```python
import os
from pathlib import Path

import pytest
from nornir import InitNornir


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def nr():
    """初始化 Nornir，并从环境变量注入测试账号。"""
    username = os.environ.get("LAB_USERNAME")
    password = os.environ.get("LAB_PASSWORD")
    if not username or not password:
        pytest.fail("必须设置 LAB_USERNAME 和 LAB_PASSWORD 环境变量")

    nornir = InitNornir(config_file=str(PROJECT_ROOT / "config.yaml"))
    for host in nornir.inventory.hosts.values():
        host.username = username
        host.password = password

    yield nornir

    nornir.close_connections()
```

该 Fixture 在整个 pytest 会话中只初始化一次 Nornir，并在测试结束时关闭所有连接。Inventory 文件中不需要保存密码。

## 12. 公共任务与轮询函数

`tests/nornir_helpers.py`：

```python
import re
import time
from collections.abc import Callable

from nornir.core.filter import F
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config


def _failure_details(multi_result) -> str:
    details = []
    for item in multi_result:
        if item.failed:
            details.append(str(item.exception or item.result))
    return "; ".join(details) or "unknown error"


def run_show(nr, host_name: str, command: str) -> str:
    """在一台设备执行查询命令，失败时给出设备级错误。"""
    target = nr.filter(F(name=host_name))
    if not target.inventory.hosts:
        raise KeyError(f"Inventory 中不存在设备 {host_name}")

    aggregated = target.run(
        task=netmiko_send_command,
        command_string=command,
        on_failed=True,
    )
    multi_result = aggregated[host_name]
    nr.data.reset_failed_hosts()

    if multi_result.failed:
        raise RuntimeError(
            f"{host_name} 执行 {command!r} 失败: "
            f"{_failure_details(multi_result)}"
        )
    return str(multi_result[-1].result)


def run_config(nr, host_name: str, commands: list[str]) -> None:
    """在一台设备执行配置命令。"""
    target = nr.filter(F(name=host_name))
    if not target.inventory.hosts:
        raise KeyError(f"Inventory 中不存在设备 {host_name}")

    aggregated = target.run(
        task=netmiko_send_config,
        config_commands=commands,
        on_failed=True,
    )
    multi_result = aggregated[host_name]
    nr.data.reset_failed_hosts()

    if multi_result.failed:
        raise RuntimeError(
            f"{host_name} 下发配置失败: {_failure_details(multi_result)}"
        )


def collect_ospf_state(task: Task) -> Result:
    """采集单台设备的 OSPF FULL 邻居，供 Nornir 并发执行。"""
    command = task.host["commands"]["ospf_neighbors"]
    command_result = task.run(
        task=netmiko_send_command,
        command_string=command,
    )
    output = str(command_result.result)

    full_neighbors = set()
    for line in output.splitlines():
        match = re.match(r"^\s*(\d+\.\d+\.\d+\.\d+)\s+", line)
        if match and "FULL" in line.upper():
            full_neighbors.add(match.group(1))

    expected = set(task.host["expected_neighbors"])
    return Result(
        host=task.host,
        result={
            "ready": expected.issubset(full_neighbors),
            "expected": sorted(expected),
            "full_neighbors": sorted(full_neighbors),
            "missing": sorted(expected - full_neighbors),
        },
    )


def wait_for_all_ospf_neighbors(
    nr,
    timeout: float = 60,
    interval: float = 3,
) -> dict:
    """等待所有设备达到预期邻居状态，超时后返回最后现场。"""
    deadline = time.monotonic() + timeout
    last_state = {}

    while time.monotonic() < deadline:
        aggregated = nr.run(task=collect_ospf_state, on_failed=True)
        current_state = {}

        for host_name in nr.inventory.hosts:
            if host_name not in aggregated:
                current_state[host_name] = {"error": "task was not executed"}
                continue

            multi_result = aggregated[host_name]
            if multi_result.failed:
                current_state[host_name] = {
                    "error": _failure_details(multi_result)
                }
            else:
                current_state[host_name] = multi_result[-1].result

        nr.data.reset_failed_hosts()
        last_state = current_state

        if current_state and all(
            state.get("ready", False) for state in current_state.values()
        ):
            return current_state

        time.sleep(interval)

    raise TimeoutError(
        f"等待 OSPF 邻居超时，最后状态: {last_state}"
    )


def wait_until(
    predicate: Callable[[], bool],
    timeout: float,
    interval: float = 2,
) -> None:
    """轮询条件，避免使用无法反映真实收敛时间的固定等待。"""
    deadline = time.monotonic() + timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            if predicate():
                return
        except RuntimeError as exc:
            last_error = exc
        time.sleep(interval)

    message = f"条件在 {timeout} 秒内未满足"
    if last_error:
        message += f"，最后错误: {last_error}"
    raise TimeoutError(message)


def route_uses_next_hop(
    nr,
    host_name: str,
    prefix: str,
    next_hop: str,
) -> bool:
    command_template = nr.inventory.hosts[host_name]["commands"]["route"]
    output = run_show(
        nr,
        host_name,
        command_template.format(prefix=prefix),
    )
    pattern = rf"\bvia\s+{re.escape(next_hop)}(?:,|\s)"
    return re.search(pattern, output) is not None


def ping_success_rate(
    nr,
    host_name: str,
    target: str,
    source: str,
    count: int = 20,
) -> int:
    command_template = nr.inventory.hosts[host_name]["commands"]["ping"]
    command = command_template.format(
        target=target,
        source=source,
        count=count,
    )
    output = run_show(nr, host_name, command)
    match = re.search(r"Success rate is\s+(\d+)\s+percent", output)
    if not match:
        raise ValueError(f"无法解析 {host_name} 的 Ping 输出: {output}")
    return int(match.group(1))
```

这里有两个重要设计：

- `collect_ospf_state` 由 Nornir 同时在所有设备执行，体现多设备并发采集能力。
- 收敛检查采用轮询和超时，不使用固定 `sleep 30`。协议提前收敛时测试可以立即继续，未收敛时也能保留最后一次状态。

## 13. 完整 pytest 测试用例

`tests/test_ospf_failover.py`：

```python
import pytest

from tests.nornir_helpers import (
    ping_success_rate,
    route_uses_next_hop,
    run_config,
    wait_for_all_ospf_neighbors,
    wait_until,
)


R1 = "r1"
TARGET_PREFIX = "3.3.3.3/32"
PING_SOURCE = "Loopback0"
PING_TARGET = "3.3.3.3"


@pytest.fixture
def primary_link_guard(nr):
    """测试前确保接口开启，测试后无条件恢复接口和邻居。"""
    interface = nr.inventory.hosts[R1]["primary_interface"]
    recovery_commands = [f"interface {interface}", "no shutdown"]

    run_config(nr, R1, recovery_commands)
    wait_for_all_ospf_neighbors(nr, timeout=60)

    yield interface

    # teardown 即使用例断言失败也会执行，防止测试床保持故障状态。
    run_config(nr, R1, recovery_commands)
    wait_for_all_ospf_neighbors(nr, timeout=60)


@pytest.mark.network
def test_ospf_primary_link_failover(nr, primary_link_guard):
    primary_next_hop = nr.inventory.hosts[R1]["primary_next_hop"]
    backup_next_hop = nr.inventory.hosts[R1]["backup_next_hop"]

    # 1. 前置状态：所有 OSPF 邻居必须正常。
    ospf_state = wait_for_all_ospf_neighbors(nr, timeout=60)
    assert all(state["ready"] for state in ospf_state.values())

    # 2. 故障前应使用 R1-R3 直连主路径。
    wait_until(
        lambda: route_uses_next_hop(
            nr, R1, TARGET_PREFIX, primary_next_hop
        ),
        timeout=30,
    )

    # 3. 故障前端到端业务必须完全可达。
    before_rate = ping_success_rate(
        nr,
        R1,
        target=PING_TARGET,
        source=PING_SOURCE,
        count=10,
    )
    assert before_rate == 100, f"故障前 Ping 成功率仅为 {before_rate}%"

    # 4. 关闭 R1-R3 主链路，注入故障。
    run_config(
        nr,
        R1,
        [f"interface {primary_link_guard}", "shutdown"],
    )

    # 5. 等待路由切换到 R1-R2-R3 备用路径。
    wait_until(
        lambda: route_uses_next_hop(
            nr, R1, TARGET_PREFIX, backup_next_hop
        ),
        timeout=30,
        interval=1,
    )

    # 6. 故障后允许少量收敛丢包，但最终成功率不得低于 95%。
    after_rate = ping_success_rate(
        nr,
        R1,
        target=PING_TARGET,
        source=PING_SOURCE,
        count=20,
    )
    assert after_rate >= 95, f"倒换后 Ping 成功率仅为 {after_rate}%"
```

## 14. 执行测试

在项目根目录执行：

```bash
export LAB_USERNAME='lab-user'
export LAB_PASSWORD='replace-with-real-password'
pytest -m network -v -s
```

只执行当前用例：

```bash
pytest tests/test_ospf_failover.py::test_ospf_primary_link_failover -v -s
```

正常情况下将看到类似结果：

```text
tests/test_ospf_failover.py::test_ospf_primary_link_failover PASSED
========================= 1 passed =========================
```

同时会生成 `nornir.log`，用于排查设备连接和任务执行问题。不要在日志中记录密码、Token 或完整认证响应。

## 15. 用例判定标准

| 检查点 | 通过标准 |
| --- | --- |
| 初始 OSPF 状态 | 每台设备的预期邻居均处于 `FULL` |
| 初始路由 | R1 到 `3.3.3.3/32` 使用 `10.0.13.2` |
| 故障前连通性 | Ping 成功率为 100% |
| 路由倒换 | 30 秒内切换到 `10.0.12.2` |
| 故障后连通性 | 20 次 Ping 成功率不低于 95% |
| 环境恢复 | R1 Gi0/2 恢复开启，全部 OSPF 邻居重新达到 `FULL` |

## 16. 为什么清理逻辑很重要

故障注入测试会主动改变测试床状态。如果测试在关闭接口后因为断言、超时或解析异常退出，而没有执行恢复操作，后续用例可能全部失败。

本例使用 pytest 的 `yield fixture` 管理恢复逻辑：

```text
Fixture setup：确保主链路开启并检查邻居
       |
       v
执行测试：关闭主链路并验证倒换
       |
       v
Fixture teardown：无条件开启主链路并等待邻居恢复
```

如果 teardown 本身失败，pytest 会单独报告清理错误，提醒测试人员人工检查测试床。

## 17. 常见问题

### 17.1 无法登录设备

检查以下内容：

- 管理地址是否已替换为真实地址。
- 测试主机到管理网是否可达。
- `LAB_USERNAME` 和 `LAB_PASSWORD` 是否设置。
- 账号是否支持 SSH 和配置模式。
- `platform: cisco_ios` 是否与 Netmiko 设备类型一致。
- 是否存在堡垒机、首次登录提示或 AAA 并发限制。

### 17.2 OSPF 邻居一直不满足

手工执行 `show ip ospf neighbor`，确认输出中邻居 ID 和 `FULL` 是否在同一行。不同设备版本的 CLI 格式可能不同，需要相应调整 `collect_ospf_state` 的解析表达式。

正式项目建议使用 TextFSM、TTP、Genie Parser、NETCONF 或 gNMI 将输出转换为结构化数据，减少字符串格式变化造成的误判。

### 17.3 路由下一跳不符合预期

检查以下内容：

- 三条链路的 OSPF Cost 是否使 R1-R3 直连链路成为主路径。
- 是否存在静态路由、其他 OSPF 进程或路由重分发。
- `show ip route 3.3.3.3` 的输出格式是否包含 `via <next-hop>`。
- 设备是否启用了 ECMP，导致同时出现多个下一跳。

如果实验室链路带宽不同，可以显式配置 OSPF Cost，保证路径选择确定：

```text
interface GigabitEthernet0/2
 ip ospf cost 10
```

需要在 R1-R3 主链路两端设置较低 Cost，并确保经 R2 的总 Cost 更高。

### 17.4 Ping 解析失败

本例解析 Cisco IOS 的以下输出：

```text
Success rate is 100 percent (20/20)
```

其他厂商可能输出 `packet loss`、`received` 等字段，应修改 `ping_success_rate`。更严谨的数据面测试可以接入 Scapy、TRex 或专业测试仪，避免依赖设备 CLI Ping。

## 18. 向生产级测试平台演进

该示例可以继续扩展：

- 将命令模板按厂商拆分，实现多厂商适配。
- 使用 Pydantic 定义设备、链路和预期结果的数据模型。
- 使用 NetBox 管理设备、端口、地址和线缆关系。
- 增加测试床预约与资源锁，阻止并发任务相互干扰。
- 接入 TRex、Ixia 或 Spirent，测量精确丢包和收敛时间。
- 使用 Allure 附加设备输出、抓包、拓扑和失败现场。
- 在 Jenkins 或 GitLab CI 中执行每日回归和版本准入。
- 接入串口服务器和 PDU，处理 SSH 不可达和设备异常重启。

推荐保持职责分离：pytest 负责用例和断言，Nornir 负责设备并发编排，Netmiko/Scrapli 负责连接，流量工具负责数据面验证，资源管理系统负责测试床生命周期。
