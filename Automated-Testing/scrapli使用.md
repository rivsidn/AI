

scrapli 的核心作用就是: 通过程序自动登录网络设备，并在设备 CLI（命令行）上执行命令或下发配置。

scrapli 就是让 Python 像一个网络工程师一样 SSH 登录设备，然后自动执行 CLI 命令、读取结果、修改配置。


支持的厂商:

| 厂商        | 设备系统 / Platform | 示例设备                                       |
|-------------|---------------------|------------------------------------------------|
| Cisco       | IOS / IOS-XE        | Catalyst 2960/3560/3850/9300、ISR、ASR 等      |
| Cisco       | NX-OS               | Nexus 3000/5000/7000/9000                      |
| Cisco       | IOS-XR              | ASR 9000、NCS 系列                             |
| Cisco       | ASA                 | 防火墙设备（部分场景）                         |
| Arista      | EOS                 | Arista 7050/7280/7500 等交换机                 |
| Juniper     | Junos               | MX、SRX、EX 系列                               |
| Nokia       | SR OS               | 7750 SR、7250 IXR 等                           |
| Huawei      | VRP                 | S 系列交换机、AR 路由器（通常需自定义 driver） |
| HPE / Aruba | Comware / ArubaOS   | 部分交换机                                     |
| Linux/Unix  | Shell               | Linux 服务器、Bash 环境                        |
| Generic     | Generic Network OS  | 未内置的平台可扩展                             |
