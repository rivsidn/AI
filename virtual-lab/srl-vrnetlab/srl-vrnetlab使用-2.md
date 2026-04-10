

'ubuntu' 为例。


## 创建镜像

- 拷贝'jammy-ubuntu-cloud.qcow2' 到ubuntu 目录

- 制作镜像
  ```bash
  make docker-image
  ```

## 搭建组网环境

### 配置文件

'ubuntu-demo.yml' 配置文件.

```yaml
name: ubuntu-demo
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

### 启动

```bash
# 部署
sudo containerlab deploy -t ubuntu-demo.yml
# 查看
sudo containerlab inspect -t ubuntu-demo.yml
# 查看组网
sudo containerlab graph -t ubuntu-demo.yml
```

### 销毁

```bash
sudo containerlab destroy -t ubuntu-demo.yml --cleanup
```

## 访问

### 串口访问

```bash
telnet 172.20.20.2 5000

telnet 172.20.20.3 5000
```

| 用户名 | 密码     |
|--------|----------|
| clab   | clab@123 |


