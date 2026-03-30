# GNS3 使用文档

更新时间：2026-03-20

本文按 Linux 本机部署整理，重点覆盖：

- 安装 GNS3
- 完成本地 server 的基本配置
- 跑通一个最小 demo
- 补充一个和 QEMU 相关的扩展示例

本文主要依据 GNS3 官方文档整理，适合先把环境搭起来，再逐步导入更复杂的网络镜像或虚拟机。

## 1. GNS3 是什么

GNS3 可以理解为一个网络实验拓扑平台，核心由三部分组成：

- `GNS3 GUI`：图形界面，负责画拓扑、连线、启动/停止节点
- `gns3server`：后台服务，负责调度节点和链路
- 后端运行时：例如 `QEMU/KVM`、`Docker`、`Dynamips`、`ubridge`

在 Linux 上，GNS3 可以直接在本机运行 QEMU/KVM 和 Docker；在 Windows/macOS 上，官方更常见的做法是配合 `GNS3 VM` 使用。

如果你的目标是让虚拟机、路由器镜像、交换节点在一个拓扑里统一管理，GNS3 是比手工写一堆 QEMU 启动参数更省事的方案。

## 2. 安装

### 2.1 安装前准备

建议先确认：

- CPU 已开启硬件虚拟化：Intel `VT-x` 或 AMD `AMD-V`
- BIOS/UEFI 中没有禁用虚拟化
- 当前用户后续可以加入 `kvm`、`libvirt`、`ubridge` 等组

Linux 下可用下面的命令做一个快速检查：

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

输出大于 `0`，通常说明 CPU 支持硬件虚拟化。

### 2.2 Ubuntu / Ubuntu 系安装

官方文档给出的安装方式是使用 PPA：

```bash
sudo add-apt-repository ppa:gns3/ppa
sudo apt update
sudo apt install gns3-gui gns3-server
```

安装过程中如果出现权限相关提示，通常会涉及这些组：

- `ubridge`
- `libvirt`
- `kvm`
- `wireshark`
- `docker`

如果你主要跑 QEMU/KVM，至少建议把当前用户加入下面这些组：

```bash
sudo usermod -aG ubridge,libvirt,kvm,wireshark $USER
```

如果你还准备在 GNS3 里用 Docker 节点，再加上：

```bash
sudo usermod -aG docker $USER
```

执行后退出当前会话并重新登录，否则新组权限不会生效。

### 2.3 Debian 系安装

官方文档对 Debian 给出的方式分为系统包和 `pipx` 组合安装。对于需要较新版本的环境，常见做法是：

```bash
sudo apt update
sudo apt install python3 python3-pip pipx python3-pyqt6 \
  python3-pyqt6.qtwebsockets python3-pyqt6.qtsvg qemu-kvm qemu-utils \
  libvirt-clients libvirt-daemon-system virtinst ca-certificates curl gnupg2

pipx install gns3-server
pipx install gns3-gui
pipx inject gns3-gui gns3-server PyQt6
```

随后同样把用户加入相关权限组并重新登录。

### 2.4 Windows / macOS 说明

如果宿主机不是 Linux，而是 Windows 或 macOS，建议优先参考官方安装页并配合 `GNS3 VM`。很多 appliance 和复杂场景在这两类系统上通过 `GNS3 VM` 会更稳定。

### 2.5 安装后验证

可以先做两个简单检查：

```bash
gns3 --version
gns3server --version
```

然后启动图形界面：

```bash
gns3
```

如果 GUI 可以正常打开，并且能连接本地 server，说明基础安装已经完成。

## 3. 基本配置

### 3.1 首次启动建议

首次启动 GNS3 时，会进入 setup wizard。对 Linux 本机场景，建议优先选择本地模式：

- 选择 `Run appliances on my local computer`
- `Host binding` 使用 `127.0.0.1`
- 端口保持默认即可

如果你只是单机使用，不要把本地 server 直接绑定到公网地址。

### 3.2 关键配置项

首次进 GUI 后，建议先看这几个位置：

- `Edit -> Preferences -> Server -> Local server`
  - 确认本地 server 状态正常
- `Edit -> Preferences -> QEMU VMs`
  - 管理 QEMU 虚拟机模板
- `Edit -> Preferences -> Console applications`
  - 选择打开 console 的终端程序
- `File -> Import Appliance`
  - 导入官方或社区 appliance 模板

如果你之后要在 GNS3 里跑 Linux/路由器镜像，`QEMU VMs` 和 `Import Appliance` 是最常用的两个入口。

### 3.3 关于 QEMU 的建议

如果你希望拓扑便于迁移、复制和分享，官方文档通常更推荐优先考虑 `QEMU`，而不是把实验强绑定到 `VMware` 或 `VirtualBox`。

这也是 GNS3 很适合做 QEMU 组网实验的原因之一：拓扑、节点和连线都能在一个项目里统一管理。

### 3.4 常见问题

- 装完后启动失败：通常是组权限没有生效，重新登录一次
- QEMU/KVM 跑不起来：优先检查 BIOS 虚拟化、`kvm` 组和 `libvirt` 状态
- 找不到镜像：GNS3 只管理模板和拓扑，不会替你提供商业厂商镜像
- 远程连接失败：先确认本地模式跑通，再考虑 remote server

## 4. 简单 Demo：两台 VPCS 通过交换机互通

这是最适合第一次验证环境是否正常的 demo，因为它不依赖额外的虚拟机镜像。

### 4.1 拓扑

```text
PC1 ---- Ethernet switch ---- PC2
```

### 4.2 操作步骤

1. 打开 GNS3，创建一个新项目，例如 `demo-vpcs`
2. 从左侧节点列表拖入：
   - 1 个 `Ethernet switch`
   - 2 个 `VPCS`
3. 使用连线工具把 `PC1` 和 `PC2` 接到交换机
4. 点击启动按钮，启动全部节点
5. 分别打开 `PC1` 和 `PC2` 的 console

### 4.3 配置 IP

在 `PC1` 中执行：

```bash
ip 10.10.10.1 255.255.255.0
```

在 `PC2` 中执行：

```bash
ip 10.10.10.2 255.255.255.0
```

然后在 `PC1` 中测试：

```bash
ping 10.10.10.2
```

如果能 ping 通，建议顺手保存一次 VPCS 配置：

```bash
save
```

然后说明以下几件事已经正常：

- GNS3 GUI 正常
- 本地 server 正常
- ubridge 链路正常
- console 正常
- 基本二层互联正常

这个 demo 是整个环境的最小健康检查。

## 5. 扩展示例：两台 QEMU Linux 虚拟机互联

如果你的重点是 QEMU 虚拟机组网，可以在最小 demo 通过后做这个扩展。

### 5.1 准备内容

你需要准备一个可启动的 QEMU 磁盘镜像，例如：

- `qcow2`
- `img`
- `vmdk`（不如 `qcow2` 常用）

建议优先使用体积较小、启动快的 Linux 镜像，比如 Alpine、TinyCore 或其他你熟悉的轻量系统。

### 5.2 创建 QEMU 模板

在 GNS3 中进入：

`Edit -> Preferences -> QEMU VMs -> New`

建议按下面思路创建：

- 名称：例如 `linux-qemu`
- 运行位置：本地 Linux server
- 二进制：通常是 `qemu-system-x86_64`
- 内存：先从 `512 MB` 或 `1024 MB` 开始
- 网卡数量：`1` 或 `2`
- 磁盘镜像：选择你的 `qcow2` 文件

完成后，左侧节点栏里会出现这个 QEMU 模板。

### 5.3 组网步骤

1. 把 `linux-qemu` 拖两次到画布中，得到两台虚拟机
2. 再拖一个 `Ethernet switch`
3. 将两台虚拟机都连到这个交换机
4. 启动全部节点
5. 分别打开两台虚拟机 console

### 5.4 虚拟机内配置

进入每台 Linux 虚拟机后，先查看网卡名：

```bash
ip link
```

常见网卡名可能是：

- `eth0`
- `ens3`
- `enp0s3`

假设第一台网卡名是 `eth0`，可以这样配置：

第一台：

```bash
sudo ip addr add 10.10.20.1/24 dev eth0
sudo ip link set eth0 up
```

第二台：

```bash
sudo ip addr add 10.10.20.2/24 dev eth0
sudo ip link set eth0 up
```

然后测试：

```bash
ping 10.10.20.2
```

如果能互通，说明你已经在 GNS3 里跑通了最基本的 QEMU 虚拟机二层组网。

### 5.5 这个扩展示例适合什么场景

这个示例适合你后续继续做这些事情：

- 把单台 QEMU 扩展到多台
- 在虚拟机之间插入交换机、路由器、防火墙节点
- 观察不同链路和拓扑变化的影响
- 为后续的自动化测试或网络实验准备可视化拓扑

## 6. 推荐的学习顺序

如果你是第一次使用 GNS3，建议按这个顺序：

1. 先跑通 `VPCS + Ethernet switch` 的最小 demo
2. 再导入一个轻量 Linux QEMU 镜像
3. 验证两台 QEMU 虚拟机互通
4. 再考虑加入路由器、NAT、云节点、Docker 节点或远程 server

这样排错最简单，也最容易区分问题到底出在：

- GNS3 自身
- 链路层
- QEMU 模板
- 客户机网络配置

## 7. 参考资料

以下为本文整理时使用的官方资料：

- GNS3 Linux 安装文档：
  - https://docs.gns3.com/docs/getting-started/installation/linux/
- GNS3 本地 server 向导：
  - https://docs.gns3.com/docs/getting-started/setup-wizard-local-server/
- GNS3 第一个拓扑：
  - https://docs.gns3.com/docs/getting-started/your-first-gns3-topology/
- GNS3 appliance 导入说明：
  - https://docs.gns3.com/docs/using-gns3/beginners/import-gns3-appliance
- GNS3 官方站点：
  - https://www.gns3.com/

## 8. 一句话总结

如果你的目标是“用图形方式管理 QEMU 虚拟机组网”，最实用的起步路径就是：

先在 Linux 上装好 `GNS3 GUI + gns3server`，跑通 `VPCS` 最小 demo，再把自己的 `QEMU qcow2` 镜像导入成模板做扩展实验。
