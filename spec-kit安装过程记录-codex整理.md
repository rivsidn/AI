# spec-kit 安装过程记录

- 时间：2026-03-13
- 目标：在当前环境安装 `github/spec-kit` 的 `specify` 命令
- 结果：安装成功，命令可用

## 操作时间线

1. 检查基础环境

```bash
which uv && uv --version && which specify || true
```

- 结果：`uv` 可用（`uv 0.7.20`），`specify` 尚未安装。

2. 首次尝试（`uv tool install`）

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

- 失败原因：`specify-cli==0.2.1` 需要 `Python>=3.11`，当前解析到 `3.10.18`，依赖不可满足。

3. 指定 Python 3.11 再试

```bash
uv tool install --python 3.11 specify-cli --from git+https://github.com/github/spec-kit.git
```

- 失败原因：`uv` 下载/解压 `cpython-3.11.13` 时网络超时（I/O timeout）。

4. 单独安装 Python 3.11

```bash
uv python install 3.11
```

- 失败原因：下载 `python-build-standalone` 资源超时。

5. 检查系统 Python 与替代路径

```bash
which python3.11 && python3.11 --version || true
which conda || true; which mamba || true; which pyenv || true; python3 --version
```

- 结果：无 `python3.11`/`conda`/`mamba`/`pyenv`，但系统有 `Python 3.13.3`。

6. 改为 `uv` 使用系统 Python

```bash
uv tool install --python python3 specify-cli --from git+https://github.com/github/spec-kit.git
```

- 过程问题：仍触发 `uv` 下载独立 `cpython-3.11.13`，网络环境下有超时风险。

7. 改用 `pip --user` 直装（失败）

```bash
python3 -m pip install --user --upgrade git+https://github.com/github/spec-kit.git#subdirectory=specify_cli
```

- 失败原因：系统启用 PEP 668（externally-managed-environment），禁止该安装方式。

8. 改为独立虚拟环境安装（首轮失败）

```bash
python3 -m venv /home/yuchao/.local/venvs/specify-cli
/home/yuchao/.local/venvs/specify-cli/bin/pip install --upgrade pip
/home/yuchao/.local/venvs/specify-cli/bin/pip install git+https://github.com/github/spec-kit.git#subdirectory=specify_cli
```

- 失败原因：下载 `pip` 及部分依赖时超时。

9. 切换清华镜像并修正安装路径

先尝试：
```bash
/home/yuchao/.local/venvs/specify-cli/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout 120 'git+https://github.com/github/spec-kit.git#subdirectory=specify_cli'
```

- 失败原因：仓库不存在 `specify_cli` 子目录（根目录才是 Python 包）。

确认包结构：
```bash
tmpdir=$(mktemp -d) && git clone --depth 1 https://github.com/github/spec-kit.git "$tmpdir/spec-kit" && find "$tmpdir/spec-kit" -maxdepth 4 \( -name pyproject.toml -o -name setup.py \)
```

- 结果：`pyproject.toml` 在仓库根目录。

10. 最终成功安装

```bash
/home/yuchao/.local/venvs/specify-cli/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout 120 'git+https://github.com/github/spec-kit.git'
mkdir -p /home/yuchao/.local/bin
ln -sf /home/yuchao/.local/venvs/specify-cli/bin/specify /home/yuchao/.local/bin/specify
```

- 结果：`specify-cli 0.2.1` 安装成功，依赖安装完成。

11. 验证命令

```bash
which specify && specify --help | sed -n '1,40p'
```

- 结果：
  - 可执行文件：`/home/yuchao/.local/bin/specify`
  - 命令可用：`specify --help` 正常
  - 版本查看方式：`specify version`（而非 `--version`）

## 当前可用命令

```bash
specify --help
specify version
specify check
specify init --here --ai copilot
```

