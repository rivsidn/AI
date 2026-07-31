
## 功能概述

**需要：python 3.8 支持.**

用 YAML 文件（Playbook）描述“要对哪些设备做什么动作”，Ansible 负责执行。

- 定义设备
- 编排任务

  Ansible Playbook = 用 YAML 描述“测试步骤 + 执行动作 + 验证结果”的自动化脚本。

- 模块

  真正执行任务的组件。


## 定义设备

```yaml
DUTS:                                   # 主机组名(自定义)
  vars:                                 # 关键字
    ansible_port: 51022                 # 主机名(自定义)
    ansible_user: tester                # IP名称
    ansible_password: passwd
  hosts:
    r1:
      ansible_host: 172.20.20.3
    r2:
      ansible_host: 172.20.20.4
    r3:
      ansible_host: 172.20.20.2
```

## 编排任务

```yaml
- name: My first play
  hosts: DUTS
  tasks:
    # 测试连通性(需要升级python到python3.8)
    - name: Ping my hosts
      ansible.builtin.ping:

    - name: Print message
      ansible.builtin.debug:
        msg: Hello world

    # 执行bash 命令
    - name: Test raw command
      ansible.builtin.raw: echo Hello > "test.txt"
```

### 执行任务

```bash
ansible-playbook -i inventory.yaml playbook.yaml
```

可以参数传递。


- play 与 play 之间是顺序执行
- 同一个 play 内部，task 也是按顺序执行
- 但同一个 task 会并发地在多个 hosts 上执行


## 应用实例(一)

配置IP 地址，查看是否能r1 --> r3 是否能ping 通.

```yaml
- name: 配置 r1 到 r2 的直连链路 IP
  hosts: r1
  gather_facts: false
  tasks:
    - name: 配置 r1 eth1 地址
      ansible.builtin.raw: ip addr replace 10.10.12.1/24 dev eth1

    - name: 启用 r1 eth1
      ansible.builtin.raw: ip link set eth1 up

    - name: 放通 r1 本机入方向流量
      ansible.builtin.raw: iptables -C INPUT -j ACCEPT 2>/dev/null || iptables -I INPUT -j ACCEPT

    - name: 配置 r1 到 r3 网段的路由
      ansible.builtin.raw: ip route replace 10.10.23.0/24 via 10.10.12.2 dev eth1

- name: 配置 r2 两侧链路 IP
  hosts: r2
  gather_facts: false
  tasks:
    - name: 配置 r2 eth1 地址
      ansible.builtin.raw: ip addr replace 10.10.12.2/24 dev eth1

    - name: 启用 r2 eth1
      ansible.builtin.raw: ip link set eth1 up

    - name: 配置 r2 eth2 地址
      ansible.builtin.raw: ip addr replace 10.10.23.2/24 dev eth2

    - name: 启用 r2 eth2
      ansible.builtin.raw: ip link set eth2 up

    - name: 放通 r2 本机入方向流量
      ansible.builtin.raw: iptables -C INPUT -j ACCEPT 2>/dev/null || iptables -I INPUT -j ACCEPT

    - name: 放通 r2 转发流量
      ansible.builtin.raw: iptables -I FORWARD -j ACCEPT

    - name: 开启 r2 IPv4 转发
      ansible.builtin.raw: echo 1 > /proc/sys/net/ipv4/ip_forward

- name: 配置 r3 到 r2 的直连链路 IP
  hosts: r3
  gather_facts: false
  tasks:
    - name: 配置 r3 eth2 地址
      ansible.builtin.raw: ip addr replace 10.10.23.3/24 dev eth2

    - name: 启用 r3 eth2
      ansible.builtin.raw: ip link set eth2 up

    - name: 放通 r3 本机入方向流量
      ansible.builtin.raw: iptables -C INPUT -j ACCEPT 2>/dev/null || iptables -I INPUT -j ACCEPT

    - name: 配置 r3 到 r1 网段的回程路由
      ansible.builtin.raw: ip route replace 10.10.12.0/24 via 10.10.23.2 dev eth2

- name: 测试 r1 经 r2 到 r3 的连通性
  hosts: r1
  gather_facts: false
  tasks:
    - name: 从 r1 ping r3
      ansible.builtin.raw: ping 10.10.23.3 3
      register: ping_r3_result
      changed_when: false
      failed_when: false

    - name: 打印 r1 到 r3 的 ping 输出
      ansible.builtin.debug:
        var: ping_r3_result.stdout_lines

    - name: 判断 r1 到 r3 是否 ping 通
      ansible.builtin.fail:
        msg: r1 ping 10.10.23.3 未看到 ICMP 回包，请检查接口、路由、转发和防火墙规则。
      when: >
        'bytes from' not in (ping_r3_result.stdout | lower) and
        'icmp_seq' not in (ping_r3_result.stdout | lower) and
        'ttl' not in (ping_r3_result.stdout | lower)
```

### 执行任务

```bash
ansible-playbook -i inventory.yaml playbook-case.yaml
```

