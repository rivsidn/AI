
## vrnetlab

vrnetlab 是把各厂商的虚拟路由器镜像放进 Docker 容器里，在容器内用 QEMU/KVM 跑起来，再用启动脚本自动完成首启配置、管理口开放和拓扑互联。

它是干什么的。

- 用 Docker 统一封装不同厂商的虚拟路由器，方便做实验、自动化测试、CI。
- 主要支持思路是“程序化起路由器 + 程序化连拓扑”，不是 GNS3 那种偏图形界面的交互式玩法。
- 仓库里每个子目录基本就是一种平台适配器，比如 xrv/、xrv9k/、vmx/、vqfx/、nxos9kv/、openwrt/、routeros/ 等。


  docker run -d --name vr-xcon --link vr1 --link vr2 vr-xcon --p2p vr1/1--vr2/1

  逐段解释：

  - docker run
      - 启动一个新容器。
  - -d
      - 后台运行，命令执行后直接返回，不占当前终端。
  - --name vr-xcon
      - 给这个容器起名叫 vr-xcon。
      - 这个容器的职责不是跑路由器，而是“连线”。
  - --link vr1 --link vr2
      - 把已有的两个容器 vr1、vr2 连接到 vr-xcon 这个容器可见的网络里。
      - 这样 vr-xcon 容器内部就能通过名字 vr1、vr2 找到这两个容器。
      - 在这个项目里，vr-xcon 需要访问 vr1、vr2 暴露出来的 TCP 端口，才能把它们桥接起来。
  - vr-xcon
      - 这里是镜像名，表示用 vr-xcon 这个 Docker 镜像启动容器。
      - 如果你是自己在仓库里构建的，镜像通常就叫这个名字；如果从仓库或远端拉取，也可能是 vrnetlab/vr-xcon。
  - --p2p vr1/1--vr2/1
      - 这是传给 vr-xcon 容器内部程序的参数。
      - p2p = point-to-point，点对点链路。
      - vr1/1--vr2/1 的意思是：
          - 把 vr1 的接口 1
          - 连到 vr2 的接口 1


› docker run -d --name vr-xcon --link vr1 --link vr2 vr-xcon --p2p vr1/1--vr2/1

  这种类似的docker 可以启多个么？--name 都是 vr-xcon 可以么


• 可以启多个，但 --name 不能都叫 vr-xcon。

  结论

  - vr-xcon 这个“镜像”可以启动很多个容器。
  - 但 Docker 容器名必须唯一。
  - 所以：
      - 可以启动多个 vr-xcon 容器
      - 不可以都用 --name vr-xcon

  为什么不行
  --name 是容器名，不是镜像名。
  Docker 里同一时刻，甚至很多情况下包括“已停止但还存在”的容器，名字都不能重复。

  如果你已经有一个叫 vr-xcon 的容器，再执行一次：

  docker run -d --name vr-xcon ...

  通常会报“名字冲突”，因为 /vr-xcon 已经被占用了。

  正确做法
  给每个 vr-xcon 容器不同名字，比如：

  docker run -d --name vr-xcon-1 --link vr1 --link vr2 vr-xcon --p2p vr1/1--vr2/1
  docker run -d --name vr-xcon-2 --link vr1 --link vr3 vr-xcon --p2p vr1/2--vr3/1
  docker run -d --name vr-xcon-3 --link vr2 --link vr3 vr-xcon --p2p vr2/2--vr3/2

  在 vrnetlab 里，通常有两种用法

  - 一个 vr-xcon 容器连多条链路
      - 例如：

    docker run -d --name vr-xcon --link vr1 --link vr2 --link vr3 vr-xcon --p2p vr1/1--vr2/1 vr1/2--vr3/1
      - 优点：少起几个容器，简单。
      - 缺点：这个 vr-xcon 挂了，里面所有链路都一起受影响。
  - 多个 vr-xcon 容器，每个负责一条或一组链路
      - 这是完全可行的，vr-xcon 的 README 也提到过可以“一条链路一个 xcon 进程/容器”。
      - 优点：隔离更好，改某条链路时不影响别的链路。
      - 缺点：容器数量会更多。

  所以你这个问题的直接答案是

  - “类似的 docker 可以启多个么？”
      - 可以。
  - “--name 都是 vr-xcon 可以么？”
      - 不可以，必须换成不同的名字。

  一个小建议
  如果你想做稍复杂一点的拓扑，命名可以按链路来取，比如：

  --name xcon-vr1-1-vr2-1
  --name xcon-vr1-2-vr3-1

  这样一看名字就知道它连的是哪两个端口。



## srl-labs vrnetlab





## 附录

### 仓库地址

- [vrnetlab](https://github.com/vrnetlab/vrnetlab)
- [srl-labs-vrnetlab](https://github.com/srl-labs/vrnetlab)
- [Vrnetlab: Emulate networks using KVM and Docker](https://brianlinkletter.com/2019/03/vrnetlab-emulate-networks-using-kvm-and-docker/)


### AI

#### vr1 虚拟机创建好之后，它的网口有几个，是不是固定的

• 不是“统一固定”的，要分两层看：

  先说结论

  - 对整个 vrnetlab 来说：网口数不是固定的，不同厂商/平台不一样。
  - 对某一个已经启动的 vr1 来说：它启动时网口数基本就定下来了，运行中不会动态增减；想改通常要换启动参数后重建容器。

  vrnetlab 里的网口其实分两类

  - 1 个管理口
      - 这是框架统一加的，在 common/vrnetlab.py:195 的 gen_mgmt() 里创建。
      - 它主要用来 SSH / NETCONF / SNMP 管理。
  - N 个业务口
      - 由每个平台自己的 launch.py 里 self.num_nics 决定，在 common/vrnetlab.py:215 的 gen_nics() 里批量生成。
      - vr1/1、vr1/2 这种编号，说的就是这些业务口，不包含管理口。

  所以严格说，某台虚拟路由器的总网口数通常是：

  1 个管理口 + N 个业务口

  是不是固定，取决于平台
  几个例子：

  - XRv：128 个业务口，见 xrv/docker/launch.py:41
  - OpenWRT：1 个业务口，见 openwrt/docker/launch.py:38
  - RouterOS：31 个业务口，见 routeros/docker/launch.py:39
  - XRv9k：默认 24 个业务口，但可以用 --num-nics / NUM_NICS 改，见 xrv9k/docker/launch.py:227
  - NXOS9Kv：默认也是 24 个业务口，可调，见 nxos9kv/docker/launch.py:146

  所以你的 vr1 有几个口，关键看它是什么类型
  比如如果你的 vr1 是这样起的：

  docker run -d --name vr1 --privileged vr-xrv:5.3.3

  那它通常就是：

  - 1 个管理口
  - 128 个业务口

  而如果是 vr-openwrt，那就可能只有：

  - 1 个管理口
  - 1 个业务口

  再补一条很容易混淆的点
  当你写：

  vr1/1

  这里的 1 不是“第 1 个总网口”，而是“第 1 个业务口”。

  也就是说：

  - 管理口是单独的一套逻辑
  - vr-xcon 连接的是业务口，不是管理口

  你可以把它简单理解成

  - 管理口：给你登设备、做自动化配置
  - 业务口：给你拿来组拓扑、跑协议、互连设备

  如果你愿意，我可以下一条直接结合 XRv 给你画一下：

  - 管理口
  - vr1/1
  - vr1/2
  - vr1/3
    分别在 vrnetlab 里是怎么映射到 QEMU TCP 端口的。

#### 这里的 "原生容器化" 如何理解呢？

› vrnetlab 不是把路由器“原生容器化”，而是把各厂商的虚拟路由器镜像放进 Docker 容器里，在容器内用 QEMU/KVM 跑起来，再用启动脚本自动完成首启配置、管理口开放和拓扑互联。

  这里的 "原生容器化" 如何理解呢？

• 这里的“原生容器化”，可以理解成：

  不是“把一台完整虚拟机塞进容器里跑”，而是“这个软件本身就是按容器方式运行的”。

  更具体一点，分两种看：

  1. 真正意义上的原生容器化

  - 容器里跑的主进程，就是应用本身，直接用宿主机 Linux 内核。
  - 不需要在容器里再起一层 QEMU/KVM、BIOS、虚拟硬盘、虚拟网卡。
  - 容器技术提供的是进程隔离、文件系统隔离、网络 namespace、cgroup 资源限制。
  - 启动通常很快，往往是秒级。
  - 资源开销相对更小，因为没有“容器里再套一个 VM”。

  比如：

  - 普通 Web 服务放进 Docker
  - nginx、redis
  - FRRouting 这类 Linux 路由软件做成容器

  这类都算比较“原生容器化”。

  2. vrnetlab 这种方式

  - 容器里真正跑的主程序，其实是 qemu-system-x86_64。
  - 路由器操作系统本体仍然是厂商提供的虚拟机镜像，比如 vmdk、qcow2。
  - Docker 在这里更像“VM 的包装盒”和“统一启动入口”。
  - 所以它本质上是：
    Docker 容器 -> QEMU/KVM -> 厂商虚拟路由器 OS

  也就是说，路由器 OS 并没有被改造成一个直接跑在容器里的 Linux 进程集合，它仍然是一个完整 VM。

  为什么说它“不是原生容器化”
  因为原生容器化通常意味着：

  - 应用直接跑在容器里
  - 直接共享宿主机内核
  - 不再依赖完整客体 OS + 虚拟硬件模拟

  而 vrnetlab：

  - 仍依赖完整客体系统镜像
  - 仍需要虚拟硬件
  - 仍经常需要 --privileged
  - 仍依赖 /dev/kvm
  - 启动时还要像操作真实虚拟机一样，通过串口/console 做首配

  这更像：

  - “VM in container”
  - “用容器封装虚拟机”
  - “把虚拟路由器包装成类似容器的交付形式”

  用一个类比

  - 原生容器化：像把“发动机”直接装进车架，结构就是为这辆车设计的。
  - vrnetlab：像把“整辆小车”装进一节货箱里运输；货箱是 Docker，小车是 QEMU 里的虚拟路由器。

  在网络设备领域，这个区别尤其明显
  很多传统网络 OS 最初就是给专用硬件或虚拟机设计的，不是给容器设计的，所以很难真正“原生容器化”。
  于是常见方案就变成：

  - 厂商如果支持容器版 NOS，那才更接近“原生容器化”
  - 如果只提供 VM 镜像，就只能像 vrnetlab 这样“容器包 VM”

  你可以用几个判断标准快速区分
  如果一个“容器化网络设备”：

  - 需要 QEMU/KVM
  - 需要 vmdk/qcow2
  - 需要串口自动化首配
  - 网卡是虚拟 NIC，不是容器原生 veth 为主

  那它大概率不是原生容器化，而是“容器封装虚拟机”。

  如果它：

  - 直接是容器镜像
  - 主进程就是 NOS 或其守护进程
  - 不需要 KVM
  - 启动很快
  - 直接接 Docker / namespace / veth

  那就更接近原生容器化。

  你要是愿意，我可以下一步继续给你讲：

  1. vrnetlab 和 containerlab 的差别
  2. 为什么网络厂商的 NOS 很难真正原生容器化
  3. 结合 common/vrnetlab.py 画一张“容器 -> QEMU -> 路由器”的结构图

#### 给我介绍一下这个仓库的如何使用，主要工作原理 https://github.com/vrnetlab/vrnetlab

• 我看了这个仓库的 README 和几个关键源码文件。简单说：

  vrnetlab 不是把路由器“原生容器化”，而是把各厂商的虚拟路由器镜像放进 Docker 容器里，在容器内用 QEMU/KVM 跑起来，再用启动脚本自动完成首启配置、管理口开放和拓扑互联。

  它是干什么的

  - 用 Docker 统一封装不同厂商的虚拟路由器，方便做实验、自动化测试、CI。
  - 主要支持思路是“程序化起路由器 + 程序化连拓扑”，不是 GNS3 那种偏图形界面的交互式玩法。
  - 仓库里每个子目录基本就是一种平台适配器，比如 xrv/、xrv9k/、vmx/、vqfx/、nxos9kv/、openwrt/、routeros/ 等。

  怎么用
  以 xrv 为例，典型流程是：

  # 1. 进入某个平台目录
  cd xrv

  # 2. 把厂商原始镜像放进当前目录
  # 例如 iosxrv*.vmdk

  # 3. 构建 Docker 镜像
  make docker-image

  # 4. 启动路由器
  docker run -d --privileged --name vr1 vr-xrv:5.3.3
  docker run -d --privileged --name vr2 vr-xrv:5.3.3

  启动后：

  # 查容器 IP
  docker inspect --format '{{.NetworkSettings.IPAddress}}' vr1

  # SSH 登录
  ssh -l vrnetlab <容器IP>
  # 默认密码：VR-netlab9

  # NETCONF
  ssh -l vrnetlab <容器IP> -p 830 -s netconf

  # 串口
  telnet <容器IP> 5000

  两台路由器互联：

  docker run -d --name vr-xcon --link vr1 --link vr2 vr-xcon --p2p vr1/1--vr2/1

  复杂拓扑可以用 topology-machine：

  - 先写高层 JSON 拓扑
  - topo --build hltopo.json > lltopo.json
  - 再 topo --run lltopo.json

  它的 JSON 主要有 3 段：

  - routers
  - p2p
  - fullmeshes

  主要工作原理

  - Docker 只是外壳，真正跑路由器的是容器里的 qemu-system-x86_64；如果宿主机有 /dev/kvm，就启用 KVM 加速，所以容器要 --privileged。
  - 每次启动 VM 时，vrnetlab 会基于原始磁盘镜像先创建一个 qcow2 overlay，真正写入都落在 overlay 上，不直接改原镜像。
  - 管理面和数据面分开处理：
      - 管理口：用 QEMU user-mode networking，加端口转发；外部连容器的 22/830/161/...，再经 socat 转到虚拟路由器管理口。
      - 数据口：每个业务网卡会暴露成一个 TCP 监听端口，通常是 10001-10099。vr-xcon 的职责就是把这些 TCP 端口两两桥接起来，形成链路。
  - 每个平台都有自己的 launch.py，因为不同厂商首启流程不一样：
      - 有的要等串口出现提示符
      - 有的要创建初始用户
      - 有的要生成 SSH key
      - 有的要开启 NETCONF / SSH
      - 有的要给管理接口配置地址
        所以仓库结构才会是“一个平台一个目录 + 一套启动脚本”。
  - 以 xrv 为例，启动脚本会监听串口输出，等系统起来后自动：
      - 创建用户
      - 生成 RSA key
      - 开 SSH / NETCONF
      - 给管理口配 10.0.0.15/24
        然后才把容器标记为健康可用。
  - topology-machine 本质上是编排器：把你写的“高层拓扑”展开成具体链路和接口编号，再替你生成/执行 docker run 和 vr-xcon 命令。

  为什么不用 Docker 原生网络直接做

  - 这个项目的设计目标是：路由器先启动，拓扑可以后定义、后修改。
  - Docker 原生网络更适合普通应用容器，且多接口、多链路、运行后再改拓扑不够顺手。
  - 所以它选了“QEMU socket NIC + xcon 桥接”的方案，灵活但不算优雅。

  这个仓库的几个核心优缺点

  - 优点
      - 不同厂商启动方式被统一了，自动化很好做
      - 很适合 CI、回归测试、程序化实验
      - 拓扑可脚本化生成
  - 限制
      - 必须是 Linux + Docker + KVM
      - 基本要 --privileged
      - 资源占用并不会比直接跑 KVM 更省，甚至可能略高
      - 默认是“无状态”的：停掉/删除后配置通常不保留
      - 启动慢，很多虚拟路由器要几分钟

  如果你把它当成一句话理解

  - vrnetlab = Docker 打包 + QEMU/KVM 跑厂商虚拟路由器 + 启动脚本自动首配 + vr-xcon 拼链路 + topology-machine 编排拓扑

  我建议你先看这几个入口

  - 总览 README：https://github.com/vrnetlab/vrnetlab/blob/master/README.md
  - 通用运行框架：https://github.com/vrnetlab/vrnetlab/blob/master/common/vrnetlab.py
  - XRv 示例说明：https://github.com/vrnetlab/vrnetlab/blob/master/xrv/README.md
  - XRv 启动脚本：https://github.com/vrnetlab/vrnetlab/blob/master/xrv/docker/launch.py
  - 链路互联组件：https://github.com/vrnetlab/vrnetlab/blob/master/vr-xcon/README.md
  - 拓扑编排工具：https://github.com/vrnetlab/vrnetlab/blob/master/topology-machine/README.md

  如果你愿意，我下一步可以直接给你一份：

  1. “在 Linux 机器上从零跑起 XRv 的实操步骤”
  2. “这个仓库源码结构导读”
  3. “vr-xcon / topology-machine 的工作流程图”


#### 介绍一下这个仓库的功能和用法 https://github.com/srl-labs/vrnetlab

• 可以，把它理解成一个“把 VM 版网络设备/通用系统封装成容器镜像”的工具仓库就行。

  它是干什么的

  - srl-labs/vrnetlab 是 plajjan/vrnetlab 的一个 fork，目标很明确：让“基于 QEMU/KVM 的 VM 镜像”能够以容器镜像的形式运行，并且能被 containerlab 正常编排。
  - 它不是把虚拟机“改写成原生容器”，而是“容器里启动 QEMU/KVM”。所以本质仍然是 VM，只是交付和编排方式变成了容器。
  - 它的核心价值是把这些麻烦事统一掉：
      - 磁盘镜像打包成 Docker 镜像
      - 启动 QEMU/KVM
      - 首次启动初始化
      - 管理口/业务口映射
      - 让 containerlab 能像管理普通容器一样管理这些 VM 节点

  这个 fork 相比 upstream 最大的变化

  - upstream vrnetlab 原来更偏“用 Docker 跑虚拟路由器”，节点互联依赖单独的 vr-xcon 容器去拼接 TCP socket。
  - srl-labs/vrnetlab 加了 connection-mode，让容器接口可以更“容器原生”地映射进 VM，适配 containerlab 的连线模型。
  - 对 containerlab 来说，默认最重要的是 tc/tc-mirred 方式；这样 eth1+ 这些容器接口可以透明映射到 VM 里的网卡，不再依赖 vr-xcon 这种老模式。
  - 这也是为什么 containerlab 文档明确说：想和 containerlab 配合，应该用 srl-labs/vrnetlab，不要用 upstream 去构建镜像。

  它大概能做什么

  - 支持把多种 VM 版 NOS/系统封装成镜像运行，比如：
      - Cisco XRv / XRv9k / CSR / Nexus / FTDv
      - Juniper vMX / vSRX / vJunos*
      - Nokia SR OS
      - Ubuntu / FreeBSD / OpenBSD
      - 还有 OpenWRT、Fortigate、SONiC 等目录实现
  - 提供多种数据面连接模式：
      - tc-mirred
      - bridge
      - ovs-bridge
      - macvtap
  - 提供两类管理口模式：
      - 默认的 host-forwarded 管理口
      - 透明管理口，可通过 CLAB_MGMT_PASSTHROUGH=true 让 VM 直接拿到 containerlab 分配的管理 IP
  - 还支持一些运维功能：
      - 通过容器内 /reset 触发 VM reset
      - 通过 /snapshot-save 保存运行态快照，后续恢复到同一状态

  仓库怎么组织

  - 从目录结构看，它基本是“每个平台一个目录”的设计：
      - ubuntu/
      - openwrt/
      - cisco/...
      - juniper/...
      - nokia/...
      - common/
  - 每个子目录通常会有：
      - README.md：说明镜像来源、构建方法、默认账号等
      - Makefile：负责构建镜像
      - docker/：放启动脚本/镜像构建内容
      - 有些开源系统还带下载脚本，比如 ubuntu/download.sh、openwrt/download.py

  典型用法

  - 通用流程基本都是这 5 步：
      1. 克隆仓库
      2. 进入目标系统目录
      3. 准备厂商/发行版的磁盘镜像（通常是 qcow2，有些支持 vmdk）
      4. 执行 make / make build / make docker-image
      5. 用 docker run --privileged 直接启动，或者在 containerlab 拓扑里引用生成的镜像

  两个最容易理解的例子

  - Ubuntu：
      - 目录里有下载脚本，可以拉 Ubuntu cloud image
      - 构建一般就是：

  git clone https://github.com/srl-labs/vrnetlab
  cd vrnetlab/ubuntu
  ./download.sh
  make

  - 产物类似：vrnetlab/vr-ubuntu:jammy
  - OpenWRT：
      - 可以自动下载公开镜像并构建

  cd vrnetlab/openwrt
  make build

  - 产物类似：vrnetlab/openwrt_openwrt:<version>

  构建完怎么运行

  - 直接用 Docker 跑：

  docker run -d --privileged --name node1 vrnetlab/vr-ubuntu:jammy

  - 或者给 containerlab 用：

  name: lab
  topology:
    nodes:
      vm1:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
      vm2:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
    links:
      - endpoints: ["vm1:eth1", "vm2:eth1"]

  - 一般规则是：
      - eth0 是管理口
      - eth1+ 是业务口
  - 对 generic_vm 这类 Linux VM，containerlab 只负责“把线连上”，业务口地址还要你进 VM 自己配。

  使用时最重要的限制

  - 必须有 Linux + KVM；如果宿主本身还是虚拟机，通常还要开 nested virtualization
  - 容器通常要 --privileged 才能跑起来
  - 它并不会比直接跑 VM 更省资源；因为里面本来就在跑 QEMU/KVM
  - 商业路由器镜像通常不能预构建分发，所以多数场景都要你自己从厂商拿镜像再 build
  - 如果你是给 containerlab 用，最好先看 containerlab 和 vrnetlab 的版本兼容矩阵

  我主要参考了这些官方资料：

  - 仓库主页：https://github.com/srl-labs/vrnetlab
  - 根 README：https://github.com/srl-labs/vrnetlab/blob/master/README.md
  - Containerlab 的 vrnetlab 集成说明：https://containerlab.dev/manual/vrnetlab/
  - Generic VM 文档：https://containerlab.dev/manual/kinds/generic_vm/
  - Ubuntu 目录说明：https://github.com/srl-labs/vrnetlab/tree/master/ubuntu
  - OpenWRT 目录说明：https://github.com/srl-labs/vrnetlab/tree/master/openwrt




