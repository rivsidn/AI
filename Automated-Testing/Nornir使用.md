
Nornir 主要用于并发操作多台网络设备，侧重于网络自动化运维。

## 定义设备

```yaml
sw1:
  hostname: 10.0.0.1
  username: admin
  password: 123456
  platform: ios

sw2:
  hostname: 10.0.0.2
  username: admin
  password: 123456
  platform: ios
```

```python
from nornir import InitNornir

nr = InitNornir(
    config_file="config.yaml"
)

nr.run(
    task=show_version
)
```

show_version() 通常是用户自己写的 Python Task，也可以是别人写好的 Task。Nornir 不定义网络命令，它只负责调度这些 Task。


```
Nornir = 加载设备信息 + 管理任务执行 + 并发调度 + 结果收集

              用户 Python 程序
                    |
                    |
                 Nornir
        -------------------------
        |          |            |
   Inventory    Task       Scheduler
   设备信息     任务管理    并发执行
        |
        |
   Netmiko/Scrapli/NAPALM
        |
        |
       SSH/API
        |
        |
    网络设备
```

其中并发执行是核心功能.
