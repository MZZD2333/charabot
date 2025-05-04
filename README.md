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
## 插件制作
### 目录(最小)
```
plugin_directory
  ├── __init__.py
  └── plugin.yaml
```

### 引入文件`plugin.yaml`
```yaml
name: simple-plugin
# 确保唯一即可无格式要求
uuid: 1
description: this is a simple plugin to xxx.
authors:
  - author A
  - author B
version: 版本
#文件类型(.jpeg, .png, .gif, .webp, ...)
icon: icon.png 
#文件类型(.md)
docs: README.md
```