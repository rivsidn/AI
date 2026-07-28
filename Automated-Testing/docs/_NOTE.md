
也就是说，目前完整流程是：

人工或其他初始化工具下发 OSPF 基线
              |
              v
pytest 启动测试
              |
              v
Nornir 检查 OSPF 邻居和路由
              |
              v
Netmiko 关闭 R1-R3 接口
              |
              v
检查备用路径和 Ping
              |
              v
Netmiko 恢复 R1-R3 接口




  pytest：测试负责人，决定测什么、怎么测、什么算通过
  Nornir：设备调度员，决定操作哪些设备并并发执行
  Netmiko：设备操作员，通过 SSH 执行具体 CLI 命令
