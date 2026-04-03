



› 请简单介绍 JSON-RPC 2.0 协议


• JSON-RPC 2.0 是一种基于 JSON 的远程过程调用协议，用来让一端通过发送 JSON 消息，请另一端执行某个“方法”，再返回结果。

  你可以把它理解成：

  - 本地调用：add(1, 2)
  - JSON-RPC：把这个调用包装成一条 JSON 消息发出去

  它的核心特点

  - 消息格式简单，易读
  - 与传输层无关
      - 可以跑在 HTTP、WebSocket、stdio、TCP 等之上
  - 以“方法调用”为中心
  - 支持请求、响应、通知、批量调用

  一个最基本的请求

  {
    "jsonrpc": "2.0",
    "method": "add",
    "params": [1, 2],
    "id": 1
  }

  含义：

  - jsonrpc: 固定写 "2.0"
  - method: 要调用的方法名
  - params: 参数，可以是数组，也可以是对象
  - id: 请求 ID，用来匹配返回结果

  对应响应

  {
    "jsonrpc": "2.0",
    "result": 3,
    "id": 1
  }

  表示调用成功，结果是 3。

  调用失败时

  {
    "jsonrpc": "2.0",
    "error": {
      "code": -32601,
      "message": "Method not found"
    },
    "id": 1
  }

  这里的 error 表示出错了，比如方法不存在。

  通知（Notification）

  如果一条消息没有 id，那它就是通知，不要求对方返回结果。

  {
    "jsonrpc": "2.0",
    "method": "log",
    "params": {
      "level": "info",
      "message": "task started"
    }
  }

  这类消息常用于：

  - 状态更新
  - 事件上报
  - 日志推送

  批量调用

  JSON-RPC 2.0 支持一次发多个请求：

  [
    {
      "jsonrpc": "2.0",
      "method": "sum",
      "params": [1, 2],
      "id": 1
    },
    {
      "jsonrpc": "2.0",
      "method": "subtract",
      "params": [5, 3],
      "id": 2
    }
  ]

  服务端可以返回对应的一组响应。

  它常被用在哪

  - AI 协议和工具调用协议
  - 编辑器 / IDE 与语言服务通信
  - 前后端或进程间通信
  - 区块链节点接口
  - 本地客户端和后台服务通信

  一句话总结

  JSON-RPC 2.0 就是：
  用 JSON 表达“调用哪个方法、传什么参数、返回什么结果”的一套轻量 RPC 协议。

  如果你愿意，我可以下一条继续讲：

  1. JSON-RPC 2.0 和 REST API 的区别
  2. MCP 为什么要基于 JSON-RPC 2.0
  3. 用代码写一个最小 JSON-RPC 示例

› {
      "jsonrpc": "2.0",
      "result": 3,
      "id": 1
    }

    表示调用成功，结果是 3。

    调用失败时

    {
      "jsonrpc": "2.0",
      "error": {
        "code": -32601,
        "message": "Method not found"
      },
      "id": 1
    }

  这些格式是固定的么？还是自己可以自由定义？


• 不是完全自由定义。
  更准确地说：JSON-RPC 2.0 的“外层协议结构”是固定的，里面承载的“业务内容”可以自定义。

  固定的部分

  成功响应必须长这样的一类结构：

  {
    "jsonrpc": "2.0",
    "result": ...,
    "id": 1
  }

  失败响应必须长这样的一类结构：

  {
    "jsonrpc": "2.0",
    "error": {
      "code": -32601,
      "message": "Method not found"
    },
    "id": 1
  }

  这些规则是协议规定的：

  - jsonrpc 必须存在，而且值必须是 "2.0"
  - 成功时要有 result
  - 失败时要有 error
  - result 和 error 不能同时出现
  - id 用来对应请求和响应
  - error.code 必须是整数
  - error.message 必须是字符串

  可以自定义的部分

  这些内容通常由你的业务自己定义：

  - method 的名字，例如 "add"、"getUser"
  - params 的内容和结构
  - result 的内容和结构
  - error.data 的内容
  - 一部分业务错误码和错误消息

  例如这个就是合法的自定义成功结果：

  {
    "jsonrpc": "2.0",
    "result": {
      "userId": 12,
      "name": "Alice"
    },
    "id": 1
  }

  这个也是合法的自定义错误扩展：

  {
    "jsonrpc": "2.0",
    "error": {
      "code": 10001,
      "message": "User not found",
      "data": {
        "userId": 12
      }
    },
    "id": 1
  }

  一句话记忆

  - 外层壳子：固定
  - 里面的数据：你定义

  补充两个容易混的点

  - error.code 不是随便乱写的全部都行。协议保留了一些标准错误码，比如 -32601 表示方法不存在。
  - 顶层最好不要随便加额外字段，除非通信双方明确约定；否则会影响兼容性。

  如果你愿意，我可以下一条继续给你整理一份 JSON-RPC 2.0 的“固定字段清单”，一眼就能看懂。

