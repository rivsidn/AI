
'openwrt' 失败，暂时忽略。

## 安装镜像

```bash
# 下载
wget https://downloads.openwrt.org/releases/25.12.2/targets/x86/64/openwrt-25.12.2-x86-64-generic-ext4-combined.img.gz

# 解压
gzip -d openwrt-25.12.2-x86-64-generic-ext4-combined.img.gz

# 安装镜像
make docker-image
```

### 镜像安装确认

```bash
yuchao@yuchao:~/sources/srl-labs-vrnetlab$ docker image ls 
REPOSITORY                  TAG        IMAGE ID       CREATED         SIZE
vrnetlab/openwrt_openwrt    25.12.2    2bffaa81244f   3 minutes ago   618MB

#...
```

## 搭建组网环境

### 配置文件

`client-server.yml`

```yaml
name: client-server
topology:
  nodes:
    node1:
      kind: generic_vm
      image: vrnetlab/openwrt_openwrt:25.12.2
    node2:
      kind: generic_vm
      image: vrnetlab/openwrt_openwrt:25.12.2
  links:
    - endpoints: ["node1:eth2", "node2:eth2"]
```

### 启动

```bash
# 部署
sudo containerlab deploy -t client-server.yml
# 查看
sudo containerlab inspect -t client-server.yml
# 查看组网
sudo containerlab graph -t client-server.yml
```

### 销毁

```bash
sudo containerlab destroy -t client-server.yml --cleanup
```

## 访问

```bash
telnet clab-client-server-node1 5000

telnet clab-client-server-node2 5000

```

