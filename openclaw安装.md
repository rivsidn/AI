## 前期准备

### 升级node

```bash
proxychains curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh > nvm_install.sh

bash nvm_install.sh

nvm install 22

nvm alias default 22

```

## 安装

```bash
# 安装
proxychains npm install -g openclaw@latest

# 查看
npm list

# 卸载
npm uninstall -g openclaw

```

### 配置

文件 `/home/yuchao/.openclaw/openclaw.json`.

```json
{
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "<Token>",
      "proxy": "http://127.0.0.1:1081"
    }
  },
  "models": {
    "providers": {
      "crs": {
        "baseUrl": "http://127.0.0.1:3000/openai",
        "apiKey": "<Key>",
        "api": "openai-responses",
        "models": [
          {
            "id": "gpt-5.4",
            "name": "gpt-5.4",
            "api": "openai-responses",
            "reasoning": true,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 32768
          }
        ]
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "<Token>"
    }
  },
  "meta": {
    "lastTouchedVersion": "2026.4.11",
    "lastTouchedAt": "2026-04-13T11:03:20.392Z"
  }
}
```

### 连接telegram

```
  openclaw plugins enable telegram

  1. 在 Telegram 里找 @BotFather，执行 /newbot，拿到 bot token（形如 123456:ABC...）。
  2. 在本机配置频道账号：

  openclaw channels add --channel telegram --token "<省略>"

  3. 确认已添加成功：

  openclaw channels list

  4. 启动网关（你已经修好 gateway.mode=local）：

  proxychains  openclaw gateway --verbose

  5. 在 Telegram 里先给你的 Bot 发一条消息，然后查看是否有配对请求：

  openclaw pairing list telegram

  6. 批准配对（把 <配对码> 换成上一步看到的 code）：

  openclaw pairing approve telegram <省略>

```


## 启动

```bash
# 调试时候用--verbose模式
openclaw gateway --verbose
```

## 附录

### 问题解决

添加代理，解决模型不通问题.

```bash
"channels":{
  "telegram": {
    "enabled": true,
    "botToken": "...",
    "proxy": "http://127.0.0.1:1081"
  }
}
```


