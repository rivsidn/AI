
## 构建

### 构建文件

拷贝'image'镜像到目录下.


**openwrt/Makefile**

```make
-include ../makefile-sanity.include
-include ../makefile.include

build: download
	$(MAKE) docker-image
```

**makefile.inclue**

```make
docker-build-common: docker-clean-build docker-pre-build
	@if [ -z "$$IMAGE" ]; then echo "ERROR: No IMAGE specified"; exit 1; fi
	@if [ "$(IMAGE)" = "$(VERSION)" ]; then echo "ERROR: Incorrect version string ($(IMAGE)). The regexp for extracting version information is likely incorrect, check the regexp in the Makefile or open an issue at https://github.com/plajjan/vrnetlab/issues/new including the image file name you are using."; exit 1; fi
	@echo "Building docker image using $(IMAGE) as $(TAG_NAME)"
	cp ../common/* docker/
	$(MAKE) IMAGE=$$IMAGE docker-build-image-copy
	(cd docker; docker build --build-arg http_proxy=$(http_proxy) --build-arg https_proxy=$(https_proxy) --build-arg IMAGE=$(IMAGE) --build-arg VERSION=$(VERSION) -t $(TAG_NAME) .)
```

### dockerfile文件

```dockerfile
FROM debian:bullseye
MAINTAINER Kristian Larsson <kristian@spritelink.net>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
 && apt-get upgrade -qy \
 && apt-get install -y \
    bridge-utils \
    iproute2 \
    python3-ipy \
    socat \
    qemu-kvm \
 && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 161/udp 80 830 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
```

执行Docker构建.

主要功能:

- 执行安装工具
- 拷贝$IMAGE、脚本到镜像
- 设置`launch.py` 为入口点


## 启动

**TODO**

### openwrt启动

### xcon启动


## 附录

### 脚本文件

| 脚本文件       | 说明            |
|----------------|-----------------|
| healthcheck.py | 健康检查        |
| launch.py      | qemu 启动脚本   |
| vrnetlab.py    | vrnetlab 库脚本 |

