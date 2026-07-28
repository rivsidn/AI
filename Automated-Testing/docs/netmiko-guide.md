# Netmiko 网络设备自动化指南

## 1. Netmiko 是什么

Netmiko 是一个专门面向网络设备的 Python 连接与操作库，主要通过 SSH 登录交换机、路由器、防火墙等设备，然后执行查询命令或下发配置。

它建立在 Paramiko 等底层 SSH 能力之上，但针对网络设备 CLI 做了大量适配，例如：

- 自动识别设备命令提示符。
- 处理配置模式、特权模式和分页。
- 等待命令执行完成。
- 处理不同厂商的换行符和命令回显。
- 支持进入 `enable` 模式。
- 批量下发配置命令。
- 保存配置。
- 通过 TextFSM、TTP 等方式解析命令输出。
- 支持文件传输和配置替换等扩展操作。

## 2. Netmiko 的定位

可以把 Netmiko 理解为网络设备专用的 SSH 驱动：

```text
测试脚本 / 自动化平台
          |
          v
       Netmiko
          |
          v
       SSH/CLI
          |
          v
交换机、路由器、防火墙
```

Netmiko 主要解决“如何可靠地登录设备并执行 CLI 命令”，但不负责：

- 管理大规模设备清单。
- 编排多设备并发任务。
- 组织 pytest 测试用例。
- 生成专业测试流量。
- 模拟网络拓扑。
- 提供完整的 Web 管理平台。

因此，在多设备测试平台中，Netmiko 经常和 Nornir 配合：

```text
pytest：测试步骤和断言
Nornir：设备清单、筛选、并发和结果汇总
Netmiko：SSH 登录、执行命令、下发配置
TRex/Scapy：数据面流量验证
```

## 3. Netmiko 和 Paramiko 的区别

Paramiko 是通用 SSH 库，Netmiko 是针对网络设备封装的 SSH 库。

如果直接使用 Paramiko，通常需要自行处理：

- 什么时候命令执行完成。
- 如何识别设备提示符。
- 如何进入配置模式。
- 如何关闭分页。
- 如何进入特权模式。
- 不同设备的命令回显差异。
- 命令执行时间过长时如何等待。
- 如何判断设备当前处于哪个 CLI 模式。

Netmiko 已经为常见网络设备实现了这些逻辑。例如，使用 Paramiko 操作设备时，往往需要不断读取 SSH Channel 并判断输出；使用 Netmiko 时只需：

```python
output = connection.send_command("show ip interface brief")
```

## 4. 支持的设备类型

Netmiko 支持大量网络设备平台，包括常见的：

- Cisco IOS、IOS XE、NX-OS、IOS XR、ASA。
- Huawei VRP。
- H3C Comware。
- Juniper Junos。
- Arista EOS。
- Nokia SR OS。
- Fortinet FortiOS。
- Palo Alto PAN-OS。
- F5。
- Linux。
- SONiC。
- MikroTik RouterOS。

不同平台通过 `device_type` 区分，例如：

```python
"cisco_ios"
"cisco_nxos"
"huawei"
"hp_comware"
"juniper_junos"
"arista_eos"
"fortinet"
```

具体名称需要根据项目实际使用的 Netmiko 版本确定。

## 5. 安装 Netmiko

```bash
python -m pip install netmiko
```

查看安装版本：

```bash
python -c "import netmiko; print(netmiko.__version__)"
```

## 6. 最简单的查询示例

```python
from netmiko import ConnectHandler


device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.11",
    "username": "lab-user",
    "password": "example-password",
}

with ConnectHandler(**device) as connection:
    output = connection.send_command("show ip interface brief")
    print(output)
```

`with` 代码块结束后，Netmiko 会主动关闭 SSH 连接。

生产代码中不要直接写入真实密码，应该从环境变量或密码管理系统读取：

```python
import os

from netmiko import ConnectHandler


device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.11",
    "username": os.environ["LAB_USERNAME"],
    "password": os.environ["LAB_PASSWORD"],
}

with ConnectHandler(**device) as connection:
    output = connection.send_command("show version")
    print(output)
```

## 7. 下发配置

使用 `send_config_set()` 可以下发多条配置：

```python
from netmiko import ConnectHandler


device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.11",
    "username": "lab-user",
    "password": "example-password",
}

commands = [
    "interface GigabitEthernet0/1",
    "description TEST-LINK",
    "no shutdown",
]

with ConnectHandler(**device) as connection:
    output = connection.send_config_set(commands)
    print(output)
```

对于 Cisco IOS，Netmiko 会自动处理进入和退出配置模式。是否需要进入 `enable` 模式取决于设备和账号权限。如果需要 enable 密码：

```python
device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.11",
    "username": "lab-user",
    "password": "login-password",
    "secret": "enable-password",
}

with ConnectHandler(**device) as connection:
    connection.enable()
    output = connection.send_config_set(commands)
```

## 8. 保存配置

下发配置并不一定代表设备已经将配置写入启动配置。部分平台可以使用：

```python
with ConnectHandler(**device) as connection:
    connection.send_config_set(commands)
    connection.save_config()
```

需要注意：

- 不同平台的保存方式不同。
- 测试用例中的临时配置不一定应该保存。
- 故障注入命令通常不应写入启动配置。
- 批量保存前应确认不会永久改变实验室环境。

## 9. 查询命令和配置命令

Netmiko 常用的两个方法是 `send_command()` 和 `send_config_set()`。

### 9.1 `send_command()`

用于执行查询类命令：

```python
output = connection.send_command("show ip ospf neighbor")
```

它通常根据设备提示符判断命令什么时候执行完成，适合大多数 `show` 或 `display` 命令。

### 9.2 `send_config_set()`

用于进入配置模式并执行配置：

```python
output = connection.send_config_set([
    "interface GigabitEthernet0/1",
    "shutdown",
])
```

不要使用 `send_command()` 下发需要进入配置模式的命令。

## 10. 处理执行时间较长的命令

某些命令执行时间较长，例如：

- 大量路由查询。
- 多次 Ping。
- 软件升级。
- 保存大配置。
- 诊断命令。
- 大量日志输出。

可以调整读取超时：

```python
output = connection.send_command(
    "show tech-support",
    read_timeout=120,
)
```

如果命令的结束条件不适合基于提示符判断，可以考虑 `send_command_timing()`：

```python
output = connection.send_command_timing(
    "ping 10.0.0.1 repeat 100",
    read_timeout=120,
)
```

两者的主要区别：

- `send_command()` 通常根据设备提示符或期望字符串判断完成。
- `send_command_timing()` 主要根据输出读取时序判断完成。

对于交互式命令，可以分步处理设备的确认提示：

```python
output = connection.send_command_timing("delete flash:test.txt")

if "confirm" in output.lower():
    output += connection.send_command_timing("\n")
```

交互命令可能产生删除、重启、升级等高风险操作，必须提前确认命令和目标设备。

## 11. 将 CLI 输出转换为结构化数据

原始 CLI 输出通常是字符串：

```text
Interface              IP-Address      OK? Method Status Protocol
GigabitEthernet0/1     10.0.12.1       YES manual up     up
```

可以尝试使用 TextFSM 解析：

```python
result = connection.send_command(
    "show ip interface brief",
    use_textfsm=True,
)

print(result)
```

解析成功时可能返回：

```python
[
    {
        "interface": "GigabitEthernet0/1",
        "ip_address": "10.0.12.1",
        "status": "up",
        "proto": "up",
    }
]
```

然后可以进行结构化断言：

```python
assert result[0]["status"] == "up"
assert result[0]["proto"] == "up"
```

需要注意：

- 是否能解析取决于平台、命令和模板。
- 没有匹配模板时，可能仍然返回原始字符串。
- 不同模板版本的字段名可能发生变化。
- 测试代码应先检查返回值类型和字段是否存在。

例如：

```python
result = connection.send_command(
    "show ip interface brief",
    use_textfsm=True,
)

if not isinstance(result, list):
    raise RuntimeError(f"命令没有被结构化解析: {result}")
```

## 12. 完整的接口状态检查示例

```python
import os

from netmiko import ConnectHandler


def get_interface_status(host: str, interface: str) -> dict:
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": os.environ["LAB_USERNAME"],
        "password": os.environ["LAB_PASSWORD"],
    }

    with ConnectHandler(**device) as connection:
        result = connection.send_command(
            "show ip interface brief",
            use_textfsm=True,
        )

    if not isinstance(result, list):
        raise RuntimeError(f"{host} 的命令输出无法解析: {result}")

    for item in result:
        if item["interface"] == interface:
            return {
                "host": host,
                "interface": interface,
                "status": item["status"],
                "protocol": item["proto"],
            }

    raise LookupError(f"{host} 不存在接口 {interface}")


status = get_interface_status(
    host="192.0.2.11",
    interface="GigabitEthernet0/1",
)

assert status["status"] == "up"
assert status["protocol"] == "up"
```

## 13. Netmiko 与 Nornir 的关系

Netmiko 和 Nornir 不是竞争关系，它们解决的问题不同。

| 能力 | Netmiko | Nornir |
| --- | --- | --- |
| SSH 连接设备 | 核心能力 | 通常通过插件实现 |
| 执行 CLI 命令 | 核心能力 | 调用 Netmiko 等插件 |
| 进入配置模式 | 支持 | 依赖连接插件 |
| 设备清单 | 简单字典或自行实现 | 核心能力 |
| 设备分组和筛选 | 需要自行实现 | 核心能力 |
| 多设备并发 | 需要自行编写 | Runner 原生支持 |
| 任务编排 | 基础 | 核心能力 |
| 结果按设备汇总 | 需要自行处理 | 核心能力 |
| pytest 集成 | 可以 | 更适合统一编排 |

单独使用 Netmiko 时：

```python
for device in devices:
    with ConnectHandler(**device) as connection:
        print(connection.send_command("show version"))
```

这种写法默认顺序执行。设备较多时，需要自行使用线程池、异常处理和结果汇总。

使用 Nornir 配合 Netmiko 时：

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command


nr = InitNornir(config_file="config.yaml")

result = nr.run(
    task=netmiko_send_command,
    command_string="show version",
)
```

Nornir 负责选择设备和并发运行，Netmiko 负责实际 SSH 交互。

## 14. 与其他工具的区别

| 工具 | 主要定位 | 特点 |
| --- | --- | --- |
| Netmiko | 多厂商 CLI 自动化 | 生态成熟、设备支持广、容易上手 |
| Scrapli | CLI/NETCONF 连接驱动 | 结构清晰、性能较好、异步能力更突出 |
| NAPALM | 多厂商统一 API | 提供统一 Getter 和配置操作，但厂商覆盖程度不同 |
| Paramiko | 通用 SSH 库 | 灵活，但需要自行处理网络设备 CLI 细节 |
| Nornir | 自动化编排框架 | 管理 Inventory、并发任务和结果，不是底层 SSH 驱动 |

如果大量工作是执行传统 CLI，Netmiko 通常是很实用的起点。

## 15. 在网络功能测试中的典型用途

Netmiko 可以覆盖测试流程中的控制面操作：

```text
1. 登录全部设备
2. 检查软件版本和接口状态
3. 下发测试基线配置
4. 检查 OSPF/BGP 邻居
5. 关闭接口，注入链路故障
6. 轮询路由表，等待协议收敛
7. 恢复接口
8. 收集日志和故障现场
9. 恢复测试基线
```

数据面验证最好交给专门工具。例如：

- 用 Netmiko 关闭接口、查询路由状态。
- 用 TRex 持续发送测试流量。
- 用 pytest 判断收敛时间和丢包率。
- 用 Allure 保存设备输出与测试报告。

## 16. 使用时需要注意的问题

### 16.1 凭据安全

不要把真实用户名、密码或 enable 密码提交到 Git。优先使用：

- 环境变量。
- CI Secret Variables。
- HashiCorp Vault。
- 企业密码管理系统。
- 临时凭据。

### 16.2 命令超时

不同命令执行时间差异很大，应分别设置合理的 `read_timeout`，不要使用一个无限大的统一超时。

### 16.3 输出解析

尽量使用结构化解析，不要只判断某个字符串是否出现。CLI 格式可能随设备型号和版本变化。

### 16.4 环境恢复

执行 `shutdown`、修改路由策略或重启进程后，应使用 pytest Fixture 或 `try/finally` 保证恢复。

### 16.5 并发限制

大量设备并发登录可能触发：

- AAA 限流。
- 堡垒机连接数限制。
- 设备 VTY 数量不足。
- CPU 突增。
- SSH 握手超时。

应限制并发数量，并为失败设备提供有限重试。

### 16.6 日志脱敏

不要把以下信息写入普通测试日志：

- 登录密码。
- enable 密码。
- SSH 私钥。
- API Token。
- 完整认证报文。

## 17. 是否适合多设备组网测试

对于多台网络设备组网功能测试，Netmiko 很适合作为设备连接层，尤其是在以下情况下：

- 设备主要通过 CLI 管理。
- 涉及多个设备厂商。
- 需要快速实现查询和配置操作。
- 设备没有稳定的 NETCONF、RESTCONF 或 gNMI 接口。
- 希望与 Nornir、pytest 组合使用。

推荐的整体结构是：

```text
pytest
  └── Nornir
        └── Netmiko
              └── 多台网络设备
```

其中 pytest 定义测试用例，Nornir 负责多设备编排，Netmiko 负责每台设备的 SSH/CLI 操作。这三个工具组合起来，适合搭建第一版网络设备自动化功能测试框架。
