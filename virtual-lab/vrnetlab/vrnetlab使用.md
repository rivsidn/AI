
`vrnetlab` 这个仓库有两个，分别为:

- [vrnetlab](https://github.com/srl-labs/vrnetlab)
- [srl-labs vrnetlab](https://github.com/srl-labs/vrnetlab)

其中后一个是前一个的`fork` 分支.

此处我们着重分析前者，以 `openwrt` 为例.


## 构建镜像

```bash
cd openwrt

wget https://downloads.openwrt.org/releases/18.06.9/targets/x86/64/openwrt-18.06.9-x86-64-combined-ext4.img.gz

# 解压
gzip -d openwrt-18.06.9-x86-64-combined-ext4.img.gz

```

构建镜像.

```bash
docker pull debian:bullseye
make docker-image
```

`docker` 执行过程中需要将`docker` 科学上网。

## 容器运行

```bash
# 运行
$ docker run -d --privileged --name openwrt1 vrnetlab/vr-openwrt:18.06.9
e2dd66e8d5fd3a262823b9556fab30802ad2c271292fe50f6742b71b3dbb63fa
$ docker run -d --privileged --name openwrt2 vrnetlab/vr-openwrt:18.06.9
d8320945f51cda5531699373568bcf604f0dd5d22c5c951c18c4628a2e11f674

# 查看
$ docker ps 
CONTAINER ID   IMAGE                         COMMAND        CREATED        STATUS                  PORTS                                                         NAMES
d8320945f51c   vrnetlab/vr-openwrt:18.06.9   "/launch.py"   18 hours ago   Up 18 hours (healthy)   22/tcp, 80/tcp, 830/tcp, 5000/tcp, 10000-10099/tcp, 161/udp   openwrt2
e2dd66e8d5fd   vrnetlab/vr-openwrt:18.06.9   "/launch.py"   18 hours ago   Up 18 hours (healthy)   22/tcp, 80/tcp, 830/tcp, 5000/tcp, 10000-10099/tcp, 161/udp   openwrt1

# 访问
docker exec -it openwrt1 bash
docker exec -it openwrt2 bash

```

## 设备访问

### 查看IP地址

```bash
$ docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt1
172.17.0.2
$ docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt2
172.17.0.3
```

### 串口登陆

```bash
# 获取openwrt1 IP地址并登陆串口
telnet $(docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt1) 5000

# 获取openwrt2 IP地址并登陆串口
telnet $(docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt2) 5000
```

### SSH登陆

```bash
# 登陆SSH
zssh -oHostKeyAlgorithms=+ssh-rsa -oPubkeyAcceptedAlgorithms=+ssh-rsa vrnetlab@$(docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt2)

# 登陆SSH
zssh -oHostKeyAlgorithms=+ssh-rsa -oPubkeyAcceptedAlgorithms=+ssh-rsa vrnetlab@$(docker inspect --format '{{.NetworkSettings.IPAddress}}' openwrt2)
```

默认密码为'VR-netlab9'。


## 设备互联

### 构建镜像

```bash
# 进入vr-xcon 目录
cd .. && cd vr-xcon

make
```

### 设备互联

```bash
docker run -d --name vr-xcon --link openwrt1 --link openwrt2 vrnetlab/vr-xcon --p2p openwrt1/2--openwrt2/2
```

### 地址配置

```bash
# openwrt1

# openwrt2

```


## 附录

### 参考资料

- [vrnetlab](https://github.com/vrnetlab/vrnetlab)
- [srl-labs-vrnetlab](https://github.com/srl-labs/vrnetlab)
- [Vrnetlab: Emulate networks using KVM and Docker](https://brianlinkletter.com/2019/03/vrnetlab-emulate-networks-using-kvm-and-docker/)


