
NAPALM 为不同厂商网络设备提供了一层统一的 Python 操作接口，使上层自动化程序可以
用相同的方法管理 Cisco、Juniper、Arista 等设备。


```
             自动化程序
                 |
              NAPALM API
                 |
    +------------+------------+
    |            |            |
 Cisco IOS    Junos        EOS
 Driver       Driver       Driver
    |            |            |
 Cisco设备    Juniper设备   Arista设备
```
