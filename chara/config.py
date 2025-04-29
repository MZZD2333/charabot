from pathlib import Path
from typing import Optional, Union

import yaml

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class _BaseConfig(BaseModel):
    model_config = ConfigDict(extra='ignore')


class DataConfig(_BaseConfig):
    directory: Path    

    @field_validator('directory', mode='before')
    def _field_validator_directory(cls, raw_path: str) -> Path:
        return Path(raw_path)


class BotConfig(_BaseConfig):
    uin: int
    name: str
    nicknames: list[str]
    superusers: list[int]
    
    http_host: str
    http_port: int


class WebSocketConfig(_BaseConfig):
    path: str


class WebUIConfig(_BaseConfig):
    enable: bool
    path: str
    assets: Path
    static: Path
    index: str

    @field_validator('assets', mode='before')
    def _field_validator_assets(cls, raw_path: str) -> Path:
        return Path(raw_path)

    @field_validator('static', mode='before')
    def _field_validator_static(cls, raw_path: str) -> Path:
        return Path(raw_path)

    @model_validator(mode='after')
    def _(self) -> 'WebUIConfig':
        self.static = self.assets / self.static
        return self


class ServerConfig(_BaseConfig):
    host: str
    port: int

    websocket: WebSocketConfig
    webui: WebUIConfig


class PluginGroupConfig(_BaseConfig):
    group_name: str
    directory: Path

    @field_validator('directory', mode='before')
    def _field_validator_directory(cls, raw_path: str) -> Path:
        return Path(raw_path)


class FastAPIConfig(_BaseConfig):
    enable_docs: bool


class UvicornConfig(_BaseConfig):
    log_level: str
    loop: str


class ModuleConfig(_BaseConfig):
    fastapi: FastAPIConfig
    uvicorn: UvicornConfig


class LogConfig(_BaseConfig):
    level: str


class GlobalConfig(_BaseConfig):
    '''全局设置'''
    data: DataConfig
    bots: list[BotConfig]
    server: ServerConfig
    plugins: list[PluginGroupConfig]
    module: ModuleConfig
    log: LogConfig


def _load_default_config() -> GlobalConfig:
    data = yaml.safe_load(DEFAULT_GLOBAL_CONFIG)
    return GlobalConfig(**data)

def load_config(path: Optional[Union[str, Path]] = None) -> GlobalConfig:
    if path is None:
        return _load_default_config()

    path = Path(path)
    with open(path, 'rb') as f:
        data = yaml.safe_load(f)
    config = GlobalConfig(**data)
    return config


DEFAULT_GLOBAL_CONFIG = '''\
# 默认配置文件

# 数据存储目录
data:
  directory: ./data

# 接入bot配置, 可配置多个
bots:
  - uin: 12345678
    name: chara_chan
    nicknames:
      - chara
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
    enable: true
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


'''

