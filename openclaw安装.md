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

```
{
  "meta": {
    "lastTouchedVersion": "2026.3.8",
    "lastTouchedAt": "2026-03-11T08:20:36.837Z"
  },
  "wizard": {
    "lastRunAt": "2026-03-11T06:53:09.895Z",
    "lastRunVersion": "2026.3.8",
    "lastRunCommand": "doctor",
    "lastRunMode": "local"
  },
  "models": {
    "providers": {
      "crs": {
        "baseUrl": "http://45.147.48.41:3030/openai",
        "apiKey": "<省略>",
        "api": "openai-responses",
        "models": [
          {
            "id": "gpt-5.3-codex",
            "name": "gpt-5.3-codex",
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
          },
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
  "agents": {
    "defaults": {
      "model": {
        "primary": "crs/gpt-5.3-codex",
        "fallbacks": [
          "crs/gpt-5.4"
        ]
      },
      "models": {
        "crs/gpt-5.3-codex": {
          "params": {
            "transport": "sse"
          },
          "streaming": true
        },
        "crs/gpt-5.4": {
          "params": {
            "transport": "sse"
          },
          "streaming": true
        }
      },
      "compaction": {
        "mode": "safeguard"
      },
      "thinkingDefault": "minimal",
      "timeoutSeconds": 120,
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    }
  },
  "tools": {},
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing",
      "botToken": "<省略>",
      "groupPolicy": "open",
      "streaming": "partial",
      "timeoutSeconds": 120,
      "accounts": {
        "default": {
          "dmPolicy": "pairing",
          "groupPolicy": "open",
          "streaming": "partial",
          "timeoutSeconds": 120
        }
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "<省略>"
    }
  },
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      }
    }
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
http_proxy=http://127.0.0.1:1081 openclaw gateway --verbose
```


