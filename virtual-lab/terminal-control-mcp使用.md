
## 安装

```bash
sudo apt update
sudo apt install -y pipx tmux
pipx ensurepath
export PATH="$HOME/.local/bin:$PATH"
pipx install terminal-control-mcp
terminal-control-mcp
```

## 配置MCP

### 安装

```bash
sudo apt install -y tmux
codex mcp add terminal-control -- "$(command -v terminal-control-mcp)"
codex mcp list
codex mcp get terminal-control
```

### 删除

```bash
codex mcp remove terminal-control
```

## 使用

| 工具                   | 使用           |
|------------------------|----------------|
| open_terminal          | 开启终端       |
| send_input             | 发送内容到终端 |
| get_screen_content     | 获取屏幕内容   |
| list_terminal_sessions | 查看终端会话   |
| exit_terminal          | 关闭会话       |


