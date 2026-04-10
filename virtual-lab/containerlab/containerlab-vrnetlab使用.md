
## 安装

### containerlab安装

```bash
# 安装
curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"

# 检查是否正确安装
docker version
clab version
```

### vrnetlab安装

```bash
git clone https://github.com/srl-labs/vrnetlab.git
```

## 构建镜像

### 下载

```bash
cd ubuntu
bash download.sh
```

### 构建

```bash
make

# 查看docker镜像
docker images | grep vr-ubuntu
```

## 使用

### 配置

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

| 成员               | 说明                         |
|--------------------|------------------------------|
| `name`             | 实验名                       |
| `nodes`            | 定义节点                     |
| `kind: generic_vm` | 说明这是 VM 类型节点         |
| `image`            | 指定 `vrnetlab` 打包好的镜像 |
| `links`            | 定义节点间的链路             |

### 管理组网

#### 部署拓扑

```bash
sudo containerlab deploy -t demo.yml
```

#### 查看节点

```bash
sudo containerlab inspect -t demo.yml
```

#### 查看图形拓扑

```bash
sudo containerlab graph -t demo.yml
```

通过显示的后台地址查看拓扑图.

#### 销毁拓扑

```bash
sudo containerlab destroy -t demo.yml --cleanup
```

### 访问

#### 查看容器

查看拓扑。

```bash
$ sudo containerlab inspect -t demo.yml
[sudo] password for yuchao: 
10:35:13 INFO Parsing & checking topology file=demo.yml
╭─────────────────┬─────────────────────────────────┬───────────┬───────────────────╮
│       Name      │            Kind/Image           │   State   │   IPv4/6 Address  │
├─────────────────┼─────────────────────────────────┼───────────┼───────────────────┤
│ clab-demo-node1 │ generic_vm                      │ running   │ 172.20.20.2       │
│                 │ vrnetlab/canonical_ubuntu:jammy │ (healthy) │ 3fff:172:20:20::2 │
├─────────────────┼─────────────────────────────────┼───────────┼───────────────────┤
│ clab-demo-node2 │ generic_vm                      │ running   │ 172.20.20.3       │
│                 │ vrnetlab/canonical_ubuntu:jammy │ (healthy) │ 3fff:172:20:20::3 │
╰─────────────────┴─────────────────────────────────┴───────────┴───────────────────╯
```

会将name 添加到`/etc/hosts` 中.

```bash
$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 yuchao

###### CLAB-demo-START ######
172.20.20.3	clab-demo-node2 2be529c5f2c3	# Kind: generic_vm
172.20.20.2	clab-demo-node1 fd1a30eb8c64	# Kind: generic_vm
3fff:172:20:20::3	clab-demo-node2 2be529c5f2c3	# Kind: generic_vm
3fff:172:20:20::2	clab-demo-node1 fd1a30eb8c64	# Kind: generic_vm
###### CLAB-demo-END ######
```

查看容器启动COMMAND，可以获取启动的用户名和密码。

```bash
$ docker ps --no-trunc
CONTAINER ID                                                       IMAGE                             COMMAND                                                                                          CREATED        STATUS                  PORTS                               NAMES
fd1a30eb8c64dcf18dd209792d1186c3c4b3fc19ee4d10b423c5fbe279eaaa88   vrnetlab/canonical_ubuntu:jammy   "/launch.py --username clab --password clab@123 --hostname node1 --connection-mode tc --trace"   16 hours ago   Up 16 hours (healthy)   22/tcp, 5000/tcp, 10000-10099/tcp   clab-demo-node1
2be529c5f2c3bf14e06b6ead1c0e67b4dbecf88305464b12b1551725f1c7a939   vrnetlab/canonical_ubuntu:jammy   "/launch.py --username clab --password clab@123 --hostname node2 --connection-mode tc --trace"   16 hours ago   Up 16 hours (healthy)   22/tcp, 5000/tcp, 10000-10099/tcp   clab-demo-node2
```

#### docker访问容器

```bash
docker exec -it <容器名或ID> bash
```

执行exit 退出.

#### CONSOLE访问

```bash
# 访问node1
telnet 172.20.20.2 5000
telnet clab-demo-node1 5000

# 访问node2
telnet 172.20.20.3 5000
telnet clab-demo-node2 5000
```

#### SSH访问

```bash
# 访问node1
zssh clab@172.20.20.2
zssh clab@clab-demo-node1

# 访问node2
zssh clab@172.20.20.3
zssh clab@clab-demo-node2

```

密码为`clab@123`。


## 附录

### FAQ

- docker 构建失败

  ```
  (cd docker; docker build --build-arg http_proxy= --build-arg HTTP_PROXY= --build-arg https_proxy= --build-arg HTTPS_PROXY= --build-arg IMAGE=jammy-ubuntu-cloud.qcow2 --build-arg VERSION=jammy --label "vrnetlab-version=$(git log -1 --format=format:"Commit: %H from %aD")" -t vrnetlab/canonical_ubuntu:jammy .)
  ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
  ```

  ```bash
  sudo systemctl daemon-reload
  sudo systemctl reset-failed docker.socket docker.service
  sudo systemctl restart docker.socket
  sudo systemctl restart docker
  systemctl status docker docker.socket --no-pager
  docker info
  ```

### AI

#### 我当前有一个img 文件，如何使用这个img 文件创建组网环境？

• 可以，但关键点是：

  - 不能把 .img 直接写进 containerlab 的拓扑文件里就启动
  - containerlab 在拓扑里引用的是“容器镜像名”
  - 如果你要跑的是 VM 类节点，通常流程是：.img/磁盘镜像 -> qcow2 -> 用 srl-labs/vrnetlab 包装成 Docker 镜像 -> 在 clab.yml 里用这个镜像起多个节点组网

  最常见的做法有 3 条路。

  - generic_vm：适合通用 Linux VM，官方文档说明这条路通常需要 qcow2 镜像
  - 厂商/系统专用 kind：比如 openwrt、vyosnetworks_vyos、各家虚拟路由器，优先走对应的构建方式
  - 外部 VM + bridge：如果你的 .img 很特殊，不想折腾 vrnetlab，也可以先用 qemu/libvirt 单独启动 VM，再用 containerlab 的 bridge 把它们接进来

  如果先按“你这个 .img 是一个可启动的 Linux/网络设备磁盘镜像”来讲，步骤通常是这样。

  1. 先确认镜像格式

  qemu-img info your.img
  file your.img

  - 如果它是 raw 格式的 .img，通常先转成 qcow2
  - 如果它本来就是 qcow2，只是扩展名叫 .img，也最好改成 .qcow2，因为官方 vrnetlab/ubuntu 的 Makefile 默认匹配 *.qcow2

  例如把 raw 转成 qcow2：

  qemu-img convert -f raw -O qcow2 your.img your.qcow2

  2. 用 vrnetlab 把它打包成容器镜像

  这里要注意两点：

  - 要用 srl-labs/vrnetlab 这个 fork，不要用 upstream vrnetlab/vrnetlab，containerlab 官方文档明确说 upstream 构出来的镜像不保证兼容
  - 如果你的镜像是 Ubuntu/cloud image，这条路最顺；如果是“任意自定义 img”，通常要参考现有目录自己适配一下打包脚本

  如果你的镜像本质上是 Ubuntu cloud image，最简单的官方路径大致是：

  git clone https://github.com/srl-labs/vrnetlab
  cd vrnetlab/ubuntu
  cp /path/to/your.qcow2 ./jammy-ubuntu-cloud.qcow2
  make

  构建完成后会得到类似这样的镜像名：

  vrnetlab/vr-ubuntu:jammy

  3. 在 containerlab 里定义多个节点，引用同一个镜像

  比如最小两节点直连：

  name: mylab

  topology:
    nodes:
      vm1:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
        env:
          QEMU_MEMORY: "2048"
          QEMU_SMP: "2"

      vm2:
        kind: generic_vm
        image: vrnetlab/vr-ubuntu:jammy
        env:
          QEMU_MEMORY: "2048"
          QEMU_SMP: "2"

    links:
      - endpoints: ["vm1:eth1", "vm2:eth1"]

  然后部署：

  sudo containerlab deploy -t mylab.clab.yml

  这里有两个很重要的细节：

  - generic_vm 里 eth0 是管理口，不要拿来做业务链路
  - 业务接口从 eth1 开始，在拓扑里也只能写 eth1、eth2 这种名字

  4. 进 VM 里配置业务口 IP

  containerlab 只帮你把线连上，generic_vm 不会自动帮你把业务口 IP 配好。
  官方示例里 Ubuntu 的第二块网卡是 ens2，你可以类似这样配：

  vm1

  sudo ip addr add 192.168.10.1/24 dev ens2
  sudo ip link set ens2 up

  vm2

  sudo ip addr add 192.168.10.2/24 dev ens2
  sudo ip link set ens2 up

  然后互 ping。

  还有几个现实限制你最好提前知道：

  - 如果宿主机本身是虚拟机，通常要开 nested virtualization/KVM
  - generic_vm 官方文档偏向“通用 Linux VM”场景
  - 如果你的 .img 是 OpenWrt、VyOS、Juniper/Cisco 之类，通常用对应 kind 会比硬塞进 generic_vm 更省事
  - 如果你的 .img 很“野”，最省时间的办法可能反而是：先用 qemu/libvirt 单独起 VM，再用 containerlab bridge 把外部 VM 接进来

  一句话总结：

  - containerlab 不能直接消费裸 .img
  - 最标准的路径是先把它包装成 vrnetlab 容器镜像，再在拓扑里起多个节点
  - 如果是通用 Linux VM，优先看 generic_vm
  - 如果是厂商虚机镜像，优先找对应 kind
  - 如果镜像很特殊，考虑“外部 VM + bridge”

  参考资料：

  - generic_vm 文档：https://containerlab.dev/manual/kinds/generic_vm/
  - vrnetlab 集成文档：https://containerlab.dev/manual/vrnetlab/
  - generic_vm 官方示例：https://containerlab.dev/lab-examples/generic_vm01/
  - srl-labs/vrnetlab 仓库：https://github.com/srl-labs/vrnetlab
  - vrnetlab/ubuntu 目录：https://github.com/srl-labs/vrnetlab/tree/master/ubuntu

  如果你愿意，把这个 .img 的具体类型告诉我，例如：

  - Ubuntu/OpenWrt/VyOS？
  - qemu-img info 的输出是什么？
  - x86_64 还是 arm64？

  我可以直接给你写一份能跑的 clab.yml 和对应的构建命令。


#### 还是没明白，我为什么一定要使用vrnetlab 呢？

• 不是“一定要用 vrnetlab”，而是你需要一个“适配层”把裸 .img 变成 containerlab 能管理的节点。

  你可以把这 4 个东西分开看：

  - .img：只是磁盘文件
  - qemu/KVM：真正负责把这块磁盘启动成 VM
  - vrnetlab：把 qemu/KVM + 网卡映射 + 管理口 + 启动脚本 封装成一个容器镜像
  - containerlab：负责“拉线”和编排节点，不负责替你为任意 .img 设计启动方案

  所以关键不是“vrnetlab 神圣不可替代”，而是：

  - containerlab 不能直接拿一个裸 .img 当节点用
  - 你必须告诉它：这个 VM 怎么启动、几块网卡、管理口怎么接、业务口怎么映射、什么时候算启动完成
  - vrnetlab 只是官方最常见、最省事的一种实现方式

  为什么裸 .img 不够：

  - .img 只是一块“硬盘”，不包含启动命令
  - 它没有告诉 containerlab 要用什么 qemu 参数
  - 它没有告诉 containerlab 怎么把拓扑里的 eth1/eth2 映射到 VM 里的网卡
  - 它没有告诉 containerlab 管理接口、串口、日志怎么处理

  更直白一点：

  - containerlab 擅长的是“组网编排”
  - vrnetlab 擅长的是“把 VM 包装成一个像容器一样可编排的节点”
  - 如果没有 vrnetlab，那你就得自己做这层包装

  所以你其实有 3 条路：

  - 用 vrnetlab：最省心，适合想把 VM 直接写进 clab.yml，然后 deploy/destroy 一把梭
  - 自己写一套等价封装：自己做 Docker image + entrypoint + qemu 启动参数 + tap/网卡映射；可行，但本质上你是在“手搓 vrnetlab”
  - 完全不用 vrnetlab：先用 qemu/libvirt 在外面把 VM 启起来，再用 containerlab 的 bridge/ovs-bridge 把它们接进拓扑

  所以结论是：

  - 不是必须用 vrnetlab
  - 但如果你想“把一个现成 .img 直接作为 containerlab 节点”并且“还想在一个拓扑文件里统一管理”，vrnetlab 往往是最自然的办法
  - 如果你只是想“把几台现成 VM 连起来做实验”，其实“外部 qemu/libvirt + bridge”反而更直接

  你可以这样选：

  - 想要统一生命周期管理：选 vrnetlab/generic_vm
  - 想最快复用现有 .img：选外部 qemu/libvirt + bridge
  - 想完全自定义：自己写 qemu wrapper

  containerlab 官方资料也基本是这个思路：

  - generic_vm 说明它本身就是基于 vrnetlab 来启动通用 VM：https://containerlab.dev/manual/kinds/generic_vm/
  - VM 集成文档说明：不用 vrnetlab 时，也可以通过 bridge/ovs-bridge 把外部 VM 接入 lab：https://containerlab.dev/manual/vrnetlab/
  - bridge 用法：https://containerlab.dev/manual/kinds/bridge/
  - kinds 总览：https://containerlab.dev/manual/kinds/

  如果你愿意，我下一条可以直接给你画两种方案的最小示意：

  1. img -> vrnetlab -> containerlab
  2. img -> qemu/libvirt -> Linux bridge -> containerlab

  然后告诉你在你这个场景下哪条更简单。

