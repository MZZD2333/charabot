# CharaBot

<br/>
<div align="center">
  <a href="https://github.com/MZZD2333/charabot/blob/main/">
    <img src="assets/static/img/logo.webp" alt="" style="width: 120px; height: 120px">
  </a>
  <p align="center">基于Onebot 11协议的QQ bot, 支持插件多进程(分组),可同时管理多个bot.</p>
  <a href="https://github.com/MZZD2333/charabot/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/MZZD2333/charabot?style=flat-square
    " alt="">
  </a>
  <a href="https://www.python.org">
      <img src="https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/network/members">
    <img src="https://img.shields.io/github/forks/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/stargazers">
    <img src="https://img.shields.io/github/stars/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/issues">
    <img src="https://img.shields.io/github/issues/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/commits">
    <img src="https://img.shields.io/github/commit-activity/m/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/releases">
    <img src="https://img.shields.io/github/v/release/MZZD2333/charabot?style=flat-square" alt="">
  </a>
  <a href="https://github.com/MZZD2333/charabot/releases">
    <img src="https://img.shields.io/github/downloads/MZZD2333/charabot/total?style=flat-square" alt="">
  </a>
</div>

## 安装
```bash
git clone https://github.com/MZZD2333/charabot.git
cd charabot
pip install -r requirements.txt
```

## 配置文件
```yaml
# 数据存储目录
data:
  directory: ./data

# 接入bot配置, 可配置多个
bots:
  - uin: 12345678
    name: chara
    nicknames:
      - chara_chan
    superusers:
      - 23456789
    
    # Http服务配置
    http_host: 127.0.0.1
    http_port: 12001

# 服务器配置
server:
  host: 127.0.0.1
  port: 12000
  
  websocket:
    path: /chara/ws

  webui:
    path: /web-ui
    assets: ./assets
    # static 需在 assets 目录下
    static: static
    index: index.html

# 插件配置
plugins:
  # 每个插件组会作为一个单独的子进程运行
  - group_name: core
    directory: ./plugins/core

# 其他模块配置
module:
  fastapi:
    enable_docs: false
  
  uvicorn:
    log_level: error
    loop: auto

# 日志配置
log:
  level: info
```

## 插件制作
### 目录(最小)
```
plugin_directory
  ├── __init__.py
  └── plugin.yaml
```

### 引入文件 `plugin.yaml`
```yaml
name: simple-plugin
# 确保唯一即可无格式要求
uuid: 1
description: this is a simple plugin to xxx.
authors:
  - author A
  - author B
version: 版本
# 图标 文件类型(.jpeg, .png, .gif, .webp, ...) [可选]
icon: icon.png 
# 说明文档 文件类型(.md) [可选]
docs: README.md
```