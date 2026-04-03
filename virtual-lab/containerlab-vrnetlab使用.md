# containerlab + vrnetlab 使用文档

本文面向 Linux 主机，目标是用 `containerlab` 编排实验拓扑，用 `vrnetlab` 打包 QEMU/KVM 虚拟机镜像，在一台机器上快速搭建可重复的虚拟网络实验环境。

适用场景：

- 需要声明式地描述实验拓扑
- 需要把 QEMU/KVM 虚拟机接入同一个可编排网络
- 需要后续方便地增删节点、重建实验、自动化部署

不太适合的场景：

- 宿主机没有 KVM 能力
- 运行环境本身又是虚拟机，但没有开启 nested virtualization
- 只想临时手工启动 1 到 2 台 QEMU，不需要实验编排

## 1. 组件关系

这套方案里有三层：

- `containerlab`：负责读取拓扑 YAML，创建节点、连线、管理生命周期
- `vrnetlab`：把 VM 镜像封装成容器镜像，内部实际仍由 QEMU/KVM 启动虚拟机
- `generic_vm`：`containerlab` 中承载 VM 节点的一种类型，常和 `vrnetlab` 镜像配合使用

可以把它理解为：

`containerlab` 负责“怎么组网”，`vrnetlab` 负责“怎么把虚拟机装进容器里并跑起来”。

## 2. 安装

以下步骤以 Ubuntu/Debian 类 Linux 为主。`containerlab` 官方安装方式可能随版本调整，本文基于 2026-03-20 可访问的官方文档整理；如果命令失效，优先以官方页面为准。

### 2.1 环境要求

- Linux 宿主机
- 已开启硬件虚拟化：Intel `VT-x` 或 AMD `SVM`
- `Docker` 可用
- 对 `vrnetlab` 节点来说，最好具备 `/dev/kvm`
- 如果宿主机本身又跑在虚拟机里，需要开启 nested virtualization

建议先检查：

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
lsmod | grep kvm
test -e /dev/kvm && echo "/dev/kvm ok" || echo "/dev/kvm missing"
```

如果这里检查失败，后面的 `vrnetlab` 虚拟机通常无法正常启动。

### 2.2 安装 containerlab

官方提供一键安装脚本。最省事的方式是：

```bash
curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"
```

这会按官方脚本安装 `Docker`、`containerlab` 等组件。

安装完成后检查：

```bash
docker version
clab version
```

如果当前用户还不能直接使用 `docker`，重新登录一次 shell，或者确认自己已加入 `docker` 组。

### 2.3 获取 vrnetlab

`containerlab` 官方文档当前更常引用的是 `srl-labs/vrnetlab`。建议直接用这个仓库。

```bash
sudo apt-get update
sudo apt-get install -y git make
git clone https://github.com/srl-labs/vrnetlab.git
cd vrnetlab
```

### 2.4 构建一个可用的 Ubuntu VM 镜像

为了做一个最小可运行 demo，这里用 `vrnetlab` 自带的 Ubuntu 定义来构建镜像。

```bash
cd ubuntu
bash download.sh
make
```

构建成功后，本地应能看到类似镜像：

```bash
docker images | grep vr-ubuntu
```

通常会得到：

```text
vrnetlab/vr-ubuntu   jammy
```

说明：

- `download.sh` 会下载 Ubuntu cloud image
- `make` 会把这个镜像封装成 `vrnetlab` 可运行的 VM 容器镜像
- 这一过程会占用较多磁盘和网络流量

## 3. 基本配置

### 3.1 拓扑文件结构

`containerlab` 的核心是一个拓扑 YAML。最常见的结构如下：

```yaml
name: demo
topology:
  nodes:
    node1:
      kind: generic_vm
      image: vrnetlab/vr-ubuntu:jammy
    node2:
      kind: generic_vm
      image: vrnetlab/vr-ubuntu:jammy
  links:
    - endpoints: ["node1:eth1", "node2:eth1"]
```

含义：

- `name`：实验名
- `nodes`：定义节点
- `kind: generic_vm`：说明这是 VM 类型节点
- `image`：指定 `vrnetlab` 打包好的镜像
- `links`：定义节点间的链路

### 3.2 接口命名要点

在拓扑文件中你会写 `eth1`、`eth2` 这样的端口名，但进入 guest 之后，Linux 虚拟机里的接口名往往不是 `eth1`，而可能是：

- `ens2`
- `ens3`
- `enpXsY`

所以在 guest 内部配置 IP 前，先执行：

```bash
ip link
```

找到实际的数据口名称再继续。

通常可以这样理解：

- 管理口由 `containerlab` 自动接到管理网络
- 你在拓扑里声明的第一个业务口 `eth1`，进入 Ubuntu guest 后常对应 `ens2`

这不是绝对规则，最终以 `ip link` 输出为准。

### 3.3 常用生命周期命令

部署拓扑：

```bash
sudo containerlab deploy -t demo.clab.yml
```

查看节点：

```bash
sudo containerlab inspect -t demo.clab.yml
```

查看图形拓扑：

```bash
sudo containerlab graph -t demo.clab.yml
```

销毁拓扑：

```bash
sudo containerlab destroy -t demo.clab.yml --cleanup
```

## 4. 简单 Demo：两台 Ubuntu VM 直连

下面这个 demo 是基于官方 `generic_vm` 用法整理出来的一个最小版本，目的是验证：

- `containerlab` 能正确部署拓扑
- `vrnetlab` 镜像能启动 QEMU/KVM 虚拟机
- 两台 VM 能通过 `containerlab` 声明的链路互通

### 4.1 新建实验目录

```bash
mkdir -p ~/clab-labs/ubuntu2
cd ~/clab-labs/ubuntu2
```

### 4.2 编写拓扑文件

创建 `ubuntu2.clab.yml`：

```yaml
name: ubuntu2
topology:
  nodes:
    u1:
      kind: generic_vm
      image: vrnetlab/vr-ubuntu:jammy
    u2:
      kind: generic_vm
      image: vrnetlab/vr-ubuntu:jammy
  links:
    - endpoints: ["u1:eth1", "u2:eth1"]
```

### 4.3 部署拓扑

```bash
sudo containerlab deploy -t ubuntu2.clab.yml
```

确认节点起来了：

```bash
sudo containerlab inspect -t ubuntu2.clab.yml
docker ps
```

### 4.4 登录虚拟机

参考 containerlab 官方 `generic_vm` 示例，Ubuntu 22.04 VM 通常需要大约 1 分钟完成启动，再额外等待约 30 秒让 SSH 密码登录可用。

可以先看启动日志：

```bash
docker logs -f clab-ubuntu2-u1
docker logs -f clab-ubuntu2-u2
```

节点名通常会映射为类似下面的实例名：

- `clab-ubuntu2-u1`
- `clab-ubuntu2-u2`

优先尝试直接 SSH：

```bash
ssh clab-ubuntu2-u1
ssh clab-ubuntu2-u2
```

如果你使用的是 `vrnetlab/vr-ubuntu:jammy` 默认镜像，密码通常是：

```text
clab@123
```

如果 `ssh clab-ubuntu2-u1` 这种主机别名在你的环境里不可用，就执行：

```bash
sudo containerlab inspect -t ubuntu2.clab.yml
```

查看管理地址后，再用管理 IP 进行 SSH。

### 4.5 配置业务口地址

进入 `u1` 后，先找接口名：

```bash
ip link
```

假设业务口是 `ens2`，则执行：

```bash
sudo ip link set ens2 up
sudo ip addr add 192.168.10.1/24 dev ens2
```

进入 `u2` 后同样处理：

```bash
ip link
sudo ip link set ens2 up
sudo ip addr add 192.168.10.2/24 dev ens2
```

### 4.6 验证联通性

在 `u1` 上执行：

```bash
ping 192.168.10.2
```

在 `u2` 上执行：

```bash
ping 192.168.10.1
```

如果互通，说明这个最小实验已经成功。

### 4.7 清理实验

```bash
sudo containerlab destroy -t ubuntu2.clab.yml --cleanup
```

## 5. 常见问题

### 5.1 节点起不来，日志里提示 KVM 或 QEMU 相关错误

优先检查：

- `/dev/kvm` 是否存在
- 宿主机 BIOS/UEFI 是否开启 VT-x/AMD-V
- 如果宿主机本身是虚拟机，是否开启 nested virtualization

如果没有 KVM，`vrnetlab` 虚拟机大概率会启动很慢甚至失败。

### 5.2 拓扑文件里写了 `eth1`，guest 里却看不到同名接口

这是正常现象。`containerlab` 里的端口名和 guest 内部的网卡命名不是一回事。进入 guest 后以 `ip link` 的结果为准。

### 5.3 容器起来了，但 SSH 不通

优先检查：

- 节点是否真的 boot 完成
- 管理网络是否正常
- guest 内部的 SSH 服务是否已经启动
- 该镜像是否使用了你预期的默认用户名和认证方式

### 5.4 在 VirtualBox 里再跑这套环境可不可以

可以尝试，但关键限制是 nested virtualization。没有这一层，`vrnetlab` 里的 QEMU/KVM 往往无法正常工作。你前面问到的“QEMU 组网环境”如果最终要在二层虚拟化里跑，这一点是第一优先级检查项。

## 6. 进阶建议

- 如果你要频繁改连线，不要直接依赖 QEMU 的 `socket` 直连，优先让 `containerlab` 管理链路
- 如果后续要接入厂商网络操作系统镜像，可以在 `vrnetlab` 里为对应 NOS 构建镜像，再通过 `containerlab` 接入统一拓扑
- 实验规模扩大后，建议把拓扑、初始化脚本、地址规划都纳入 Git 管理

## 7. 参考资料

- containerlab 安装文档：https://containerlab.dev/install/
- containerlab vrnetlab 集成说明：https://containerlab.dev/manual/vrnetlab/
- containerlab `generic_vm` 节点说明：https://containerlab.dev/manual/kinds/generic_vm/
- containerlab 官方 `generic_vm` 示例：https://containerlab.dev/lab-examples/generic_vm01/
- `srl-labs/vrnetlab` 仓库：https://github.com/srl-labs/vrnetlab
- `vrnetlab` Ubuntu README：https://raw.githubusercontent.com/srl-labs/vrnetlab/master/ubuntu/README.md


## 附录

### AI

```
› 这个工具，有办法配置虚拟机的管理IP地址么？


• 我核对一下 containerlab 官方文档里管理网络和 mgmt-ipv4 的配置方式，确认能不能给 VM 节点指
  定管理 IP。

• Searched site:containerlab.dev containerlab management network mgmt-ipv4 official

────────────────────────────────────────────────────────────────────────────────────────────

• 有。containerlab 支持给节点指定管理 IP，包括 generic_vm 这类基于 vrnetlab 的虚拟机节点。官
  方文档里对应的是管理网络配置 mgmt，以及节点级别的 mgmt-ipv4 / mgmt-ipv6。
  来源：
  https://containerlab.dev/manual/network/
  https://containerlab.dev/manual/nodes/
  https://containerlab.dev/manual/kinds/generic_vm/

  最常见的写法是这样：

  name: ubuntu2

  mgmt:
    network: custom_mgmt
    ipv4-subnet: 172.100.100.0/24
    ipv6-subnet: 3fff:172:100:100::/80

  topology:
    nodes:
      u1:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
        mgmt-ipv4: 172.100.100.11
      u2:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
        mgmt-ipv4: 172.100.100.12
    links:
      - endpoints: ["u1:eth1", "u2:eth1"]

  几点要注意：

  - mgmt-ipv4 必须落在你定义的 mgmt.ipv4-subnet 里。
  - 官方文档建议：如果你要在同一个管理网里用静态管理 IP，最好这个网里的所有节点都显式指定，
    避免地址冲突。
  - 对 generic_vm 来说，管理口是 eth0，进入 Ubuntu guest 后通常映射成 enp1s0，这个地址由
    containerlab 自动下发。
  - 业务口 eth1+ 的 IP 还是要你自己进虚拟机配置。

  如果你问的是“实验已经 running 了，能不能直接改管理 IP”：

  - 实际上这是容器/管理网络层的地址分配，通常不是 containerlab 运行中热改的常规路径。
  - 稳妥做法是改拓扑 YAML 后重新 deploy / destroy+deploy。

  如果你要，我可以直接把你刚才那份 /home/yuchao/Documents/workspace/2026.03.18-AI_coding-虚
  拟机/containerlab-vrnetlab使用.md 补一节“静态管理 IP 配置示例”。

```
