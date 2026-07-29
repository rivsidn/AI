
Robot Framework = 用自然语言编写自动化测试流程的平台.

可以传参数，Robot Framework 的设计就是让 .robot 管流程、Python Library 管逻辑，参数在两者之间流动.

Robot Framework 的核心思想就是：底层能力封装成 Library，上层通过 .robot 文件自由组合测试流程。


```
        测试场景层
      (*.robot)
           |
           |
        业务关键字层
     (Upgrade / HA / Check)
           |
           |
        设备驱动层
 (Python + Netmiko + API)
           |
           |
        被测设备
```

```
                test.robot
        （测试流程 + 组合逻辑）
                    |
                    v
           Robot Framework
                    |
        -----------------------
        |                     |
  Robot Keyword        Python Library
  (流程封装)          (具体实现)
                              |
                    ----------------
                    |              |
                 Netmiko        API/SSH
                    |
                    v
             网络设备/服务器
```

## 示例程序(一) - 映射关系

### Robot

```Robot
*** Settings ***
Library    NetworkDevice.py


*** Test Cases ***
Test Switch
    Connect Device
    Show Version
```

### Python

```Python
class NetworkDevice:

    def connect_device(self):
        print("SSH connect")

    def show_version(self):
        print("display version")
```

Robot 文件关键字和 python 函数之间存在一一对应关系:

- 空格变下划线
- 大小字不敏感


## 示例程序(二) - 传入参数

### Robot

```Robot
*** Settings ***
Library    NetworkDevice.py


*** Test Cases ***
Connect Test
    Connect Device    192.168.1.1    admin    123456
```

### Python

```Python
class NetworkDevice:

    def connect_device(self, ip, username, password):
        print("IP:", ip)
        print("User:", username)
        print("Password:", password)
```
