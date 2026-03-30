# Emacs Shell 操作记录

## 1. 在 `M-x term` 后如何切换到其他窗口

在 `term` buffer 中，先从 **char mode** 切到 **line mode**，再切换窗口：

1. `C-c C-j`（进入 line mode）
2. `C-x o`（切到其他窗口，或使用你自己的切窗快捷键）
3. 需要回到终端直通输入时，按 `C-c C-k`（回 char mode）

核心点：`char mode` 下很多按键会直接发给 shell，所以要先 `C-c C-j`。

## 2. 在 buffer 中查看文件列表并打开其他文件

可使用 Emacs 内置 `dired`：

1. `C-x d`
2. 输入目录（例如 `.` 表示当前目录）并回车
3. 在文件列表中用方向键或 `n`/`p` 移动
4. `RET` 打开文件
5. `^` 返回上级目录

补充常用命令：

- `C-x C-f`：直接输入文件名打开
- `C-x b`：切换已打开的 buffer
- `C-x C-b`：查看 buffer 列表
