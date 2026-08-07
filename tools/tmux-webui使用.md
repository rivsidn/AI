
### 安装

```bash
# 下载安装脚本
$ proxychains wget -fsSL https://raw.githubusercontent.com/operonlab/tmux-webui/main/install.sh

# 执行安装脚本
$ proxychains bash install.sh 

  ProxyChains-3.1 (http://proxychains.sf.net)
  ==> platform: linux/amd64
  ==> tmux found: tmux 3.5a
  ==> resolving install method (brew -> release -> source)
    brew: not installed — skipping
  ==> looking up GitHub release (latest)
  ==> downloading tmux-webui_0.1.0_linux_amd64.tar.gz
  |DNS-request| github.com 
  |S-chain|-<>-127.0.0.1:10810-<><>-4.2.2.2:53-<><>-OK
  |DNS-response| github.com is 140.82.116.3
  |S-chain|-<>-127.0.0.1:10810-<><>-140.82.116.3:443-<><>-OK
  |DNS-request| release-assets.githubusercontent.com 
  |S-chain|-<>-127.0.0.1:10810-<><>-4.2.2.2:53-<><>-OK
  |DNS-response| release-assets.githubusercontent.com is 185.199.111.133
  |S-chain|-<>-127.0.0.1:10810-<><>-185.199.111.133:443-<><>-OK
  ==> sha256 verified
  
  ==> installed: tmux-webui 0.1.0 (195ad23, 2026-07-08T02:03:50Z)
  ==> config dir: /home/yuchao/.config/tmux-webui (config.json is optional — defaults apply when absent)
      key reference: https://github.com/operonlab/tmux-webui/blob/main/docs/config-reference.md
  
  next steps:
      /home/yuchao/.local/bin/tmux-webui serve            # local:  http://127.0.0.1:9527
      /home/yuchao/.local/bin/tmux-webui serve --lan      # phone:  prints a QR + token URL
      /home/yuchao/.local/bin/tmux-webui daemon install   # run as a login service (launchd/systemd)
```

### 卸载

```bash
tmux-webui uninstall -y
```
