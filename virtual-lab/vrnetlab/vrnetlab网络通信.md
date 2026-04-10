
## 虚拟机宿主机通信

```
 +-----------------------------------------+
 |                                         |
 |    +--------------+                     |
 |    |              |                     |
 |    |              |                     |
 |    |              |                     |
 |    |              |                     |
 |    |              |                     |
 |    |              |                     |                             +-----------------+
 |    |              |  USER               |     VETH                    |                 |
 |    |              | <---->socat <-----> | <---------> BRIDGE <------> |       PC        |
 |    |              |                     |                             |                 |
 |    |              |                     |                             +-----------------+
 |    |              |                     |
 |    |              |                     |
 |    |              |                     |
 |    | QEMU         |                     |
 |    +--------------+                     |
 |                                         |
 |                                         |
 |                                         |
 |                                         |
 |                                         |
 |  Docker                                 |
 +-----------------------------------------+

```

- 宿主机和Docker 通信

  宿主机和Docker 之间通过桥口，接上`veth` 口通信.

  ```bash
  $ brctl show
  bridge name	bridge id		STP enabled	interfaces
  docker0   8000.0242ff0e070c	no		veth979a862
             							vethacf6fc3
  ```

  比较形象的图是这张.

  ```
  宿主机
    docker0: 172.17.0.1
        |
     Linux bridge
     /         \
  veth        veth
   |            |
  容器A        容器B
  eth0         eth0
  172.17.0.2   172.17.0.3
  ```


- Docker和QEMU 通信

  QEMU 通过设置`hostfw` 参数，监听指定端口，将流量转发到虚拟机中.

  可以理解成是通过QEMU 进程做的 NAT 转发.

  技术细节.

  > hostfwd 依赖的是 QEMU 的 user 网络后端，也就是常说的 SLiRP / libslirp
  >
  > - 管理口对应的 QEMU 配置是：
  >     - -device virtio-net-pci,netdev=p00,...
  >     - -netdev user,id=p00,...,hostfwd=...
  > - 也就是：
  >     - virtio-net-pci 是 guest 看到的“网卡设备”
  >     - user,id=p00 是这块网卡背后的网络后端
  >     - hostfwd 是这个后端上的端口转发规则

## 虚拟机虚拟机通信

**TODO**


## 附录

### 待整理

#### 虚拟机宿主机通信

通信网络.

```
  宿主机
    docker0: 172.17.0.1
        |
     Linux bridge
     /         \
  veth        veth
   |            |
  容器A        容器B
  eth0         eth0
  172.17.0.2   172.17.0.3
```


```dockerfile
EXPOSE 22 161/udp 80 830 5000 10000-10099
```

仅仅是说明，说明容器会监听这些端口.



```
  Docker 容器
    |
    +-- /launch.py
    |     |
    |     +-- subprocess.Popen(qemu-system-x86_64)
    |     +-- telnet 127.0.0.1:5000  <-- 串口初始化
    |     +-- telnet 127.0.0.1:4000  <-- QEMU monitor
    |
    +-- socat 22/80/443/830/161
    |     |
    |     +-- 转发到 127.0.0.1:2022/2080/2443/2830/2161
    |
    +-- qemu-system-x86_64
          |
          +-- 使用容器内磁盘文件启动
          +-- 监听 5000 串口
          +-- 监听 4000 monitor
          +-- 监听 10001 业务口 socket
```

```
  容器 22  ->  socat  ->  容器 2022  ->  QEMU hostfwd  ->  OpenWrt 10.0.0.15:22
```

```
  外部进程 -> 连接 QEMU 所在环境的 2022
          -> QEMU/libslirp 接受这个 TCP 连接
          -> libslirp 在 guest 网络里构造一条到 10.0.0.15:22 的连接
          -> 数据通过 QEMU 的网络后端送到 virtio-net-pci
          -> guest 里的网卡驱动收到包
          -> guest 的 TCP/IP 协议栈交给 sshd

  - hostfwd + -netdev user
      - 用户态实现
      - 不需要额外创建 TAP 设备
      - 配置简单
      - 更像 NAT/端口映射
```

#### 虚拟机之间通信

› 给我解释一下 xcon p2p 通信的原理


• Explored
  └ Search vr-xcon|p2p|--p2p|xcon|10001|listen=:10001|connect: in ..
    List ..
    Search vr-xcon|xcon|topology-machine|README.md$
    Read README.md, xcon.py

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• 可以，把 xcon --p2p 理解成“在两个 QEMU 网卡 socket 之间拉一根虚拟网线”。

  先说结论

  - 每个 vrnetlab 路由器容器里的 QEMU，会把业务网口暴露成 TCP 端口，比如：
      - 口 1 -> 10001
      - 口 2 -> 10002
  - vr-xcon --p2p vr1/1--vr2/1 做的事，就是：
      - 连上 vr1:10001
      - 连上 vr2:10001
      - 然后把一边收到的字节流原样转发到另一边
  - 所以它本质上是一个“TCP 层的二层交叉连接器”

  这个设计的基础
  根 README 已经说明了这套思路：

  - ../README.md:150 说所有虚拟路由器的 NIC 都通过 TCP 端口暴露
  - ../README.md:151 说第一块 NIC 对应 10001
  - ../README.md:153 说把两个这样的 TCP socket 接起来，就能 bridge 两块 NIC
  - ../vr-xcon/README.md:10 到 ../vr-xcon/README.md:16 也明确说了，vr-xcon 是把 QEMU 暴露出的 TCP 端口互连起来，形成一个 overlay

  在路由器容器侧，QEMU 是怎么暴露业务口的
  你前面看的 docker/vrnetlab.py 里有这段：

  - gen_nics() 在 docker/vrnetlab.py:239 生成：
      - -netdev socket,id=pXX,listen=:10001

  这表示：

  - QEMU 为某块业务网卡开一个 TCP server
  - 第一块业务网卡监听 10001
  - 第二块监听 10002
  - 以此类推

  所以：

  - vr1/1 实际就是 vr1:10001
  - vr2/3 实际就是 vr2:10003

  xcon 是怎么把 vr1/1--vr2/1 解析出来的
  在 ../vr-xcon/xcon.py 里：

  - add_p2p() 在 ../vr-xcon/xcon.py:238
  - 它会把 vr1/1--vr2/1 拆成左右两个端点
  - hostintf2addr() 在 ../vr-xcon/xcon.py:227
  - 它把 vr1/1 转成：
      - 主机名 vr1
      - 端口 10001
  - 转换规则在 ../vr-xcon/xcon.py:231：
      - "100%02d" % int(interface)

  也就是：

  - 1 -> 10001
  - 2 -> 10002
  - 10 -> 10010

  这里之所以通常配 --link vr1 --link vr2，就是为了让 xcon 容器里能解析到这些容器名。

  xcon p2p 的核心转发逻辑
  TcpBridge 是 --p2p 模式真正干活的类，定义在 ../vr-xcon/xcon.py:219

  它做的事情很直接：

  - 给左端创建一个 TCP socket，连到 vr1:10001
  - 给右端创建一个 TCP socket，连到 vr2:10001
  - 把两个 socket 记成一对
  - 然后进入 select() 循环，谁有数据就读出来，再发给另一边

  关键代码是：

  - 建连接：../vr-xcon/xcon.py:246 到 ../vr-xcon/xcon.py:268
  - 多路复用：../vr-xcon/xcon.py:272 到 ../vr-xcon/xcon.py:279
  - 收数据：../vr-xcon/xcon.py:282
  - 发到对端：../vr-xcon/xcon.py:304

  所以它不是交换机学习 MAC，也不是路由器转发 IP，它只是：

  - 左边来字节
  - 原样送右边
  - 右边来字节
  - 原样送左边

  这就是点到点 cross-connect。

  那这些“字节”到底是什么
  这里有个很关键的细节：

  - QEMU 的 socket 型网卡后端，传的不是“裸 TCP 业务数据”
  - 传的是“以太帧的封装字节流”

  从 Tcp2Tap / Tcp2Raw 的实现可以看出来：

  - ../vr-xcon/xcon.py:184 先读 4 字节长度
  - ../vr-xcon/xcon.py:198 再读完整 payload
  - ../vr-xcon/xcon.py:207 发回去时也会自己加一个 4 字节长度头

  这说明 QEMU 的这类 TCP 网卡连接，流里实际是：

  [4字节长度][二层帧payload][4字节长度][二层帧payload]...

  而 TcpBridge 模式根本不解析这个格式，它只是透明搬运整个 TCP 字节流。因为：

  - 左边 QEMU 发出的格式
  - 右边 QEMU 本来就懂得怎么收

  所以 TcpBridge 可以非常简单，像一根“TCP 管道”。

  整个 p2p 数据路径
  以 vr1/1--vr2/1 为例，链路可以画成这样：

  vr1 内部 OpenWrt/路由器
    -> vr1 的虚拟网卡1
    -> vr1 容器里的 QEMU socket listener :10001
    -> vr-xcon 容器中的左侧 TCP 连接
    -> vr-xcon 把字节流转发到右侧 TCP 连接
    -> vr2 容器里的 QEMU socket listener :10001
    -> vr2 的虚拟网卡1
    -> vr2 内部 OpenWrt/路由器

  所以它模拟的是：

  vr1 的接口1  <------一根虚拟网线------>  vr2 的接口1

  为什么它叫 overlay
  因为它不是在 Linux 内核里真的拉了一根 tap/bridge 二层链路，而是：

  - 跑在 Docker 容器默认网络之上
  - 通过容器之间原本可达的 TCP 网络来承载“内部链路流量”

  也就是：

  - 外层：Docker 网络 / docker0 / overlay 网络
  - 内层：用 TCP 封装承载虚拟路由器的二层帧

  这就是 ../vr-xcon/README.md:12 说的 “It can be seen as an overlay”。

  为什么不直接让两个 QEMU 彼此 connect
  README 也解释了这个设计取舍：

  - ../vr-xcon/README.md:127 到 ../vr-xcon/README.md:133
  - 如果直接用 QEMU 自己点对点互连，拓扑必须在启动前就固定
  - 但 vr-xcon 是“后插”的
  - 虚机先起来，之后再决定怎么连
  - 要改拓扑时，停掉 xcon，换个 --p2p 参数重起就行

  所以它最大的价值不是性能，而是：

  - 拓扑后定义
  - 拓扑可变更
  - 容器间只要网络可达即可互联

  它的局限
  README 也写得很实在：

  - 性能通常不会太好，见 ../vr-xcon/README.md:96
  - 抖动可能比较明显，见 ../vr-xcon/README.md:99
  - 因为它本质上是：
      - QEMU 一次封装
      - Docker 网络再跑一次
      - xcon 用户态再转一次
      - 对端再解封装

  所以它更适合实验、拓扑验证，而不是追求高性能。

  一句话总结
  xcon --p2p 的原理就是：

  - 把 容器名/接口号 映射成 容器IP:1000X
  - 用一个中间容器同时连上两端 QEMU 暴露的 TCP 网卡端口
  - 用 select + recv + send 透明转发两端的二层帧字节流
  - 从而模拟出一条点到点链路

  如果你愿意，我下一步可以继续给你讲：

  1. 为什么 TcpBridge 不需要自己解析以太帧也能工作
  2. vr1/1--vr2/1 这一条链路在你当前的 openwrt1 / openwrt2 上该怎么实际跑起来


› 是通过什么技术实现的呢？


• 如果只看 xcon --p2p，它主要是靠这几项技术实现的：

  - QEMU socket NIC backend
      - 每个业务网口在 QEMU 里都被暴露成一个 TCP 监听端口
      - 比如接口 1 对应 10001，见 docker/vrnetlab.py:239
  - Python socket
      - vr-xcon 用 Python 的 socket 库分别连到两端路由器的 1000X 端口
      - 代码在 ../vr-xcon/xcon.py:246、../vr-xcon/xcon.py:247
  - select 多路复用
      - vr-xcon 用 select.select() 同时监听多条连接，谁来数据就转发谁
      - 代码在 ../vr-xcon/xcon.py:275
  - recv/send 用户态转发
      - 从左边 recv() 到的数据，直接 send() 到右边
      - 代码在 ../vr-xcon/xcon.py:282 和 ../vr-xcon/xcon.py:304
  - Docker 容器网络
      - 两个路由器容器和 vr-xcon 容器之间，本身还是靠 Docker 的容器网络互通
      - vr-xcon 通过容器名解析到对端地址，见 ../vr-xcon/xcon.py:231

  所以，最准确的说法是：

  - xcon p2p 不是用 VXLAN、GRE、Linux bridge 这种内核网络技术做的
  - 它是用“QEMU 暴露的 TCP 网口 + Python 用户态 socket 中继”实现的

  你可以把它理解成：

  QEMU网口TCP端口  <--TCP连接-->  vr-xcon进程  <--TCP连接-->  QEMU网口TCP端口

  vr-xcon 自己本质上就是一个用户态“线缆转接器”。

  再补一个关键点：

  - 在 --p2p 模式下，它通常不创建 tap、不做 Linux bridge
  - tap/原始网卡那套是 --tap-listen / --raw-listen 模式，见 ../vr-xcon/xcon.py:517 和 ../vr-xcon/xcon.py:528
  - --p2p 只用 TCP socket 做透明搬运，核心类就是 TcpBridge，见 ../vr-xcon/xcon.py:219

  如果你愿意，我可以下一步把 vr1/1--vr2/1 这条链路，从容器名解析到最终收发字节，完整按时序给你画出来。

