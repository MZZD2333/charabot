from typing import Optional, Union
from chara.config import GlobalConfig, load_config
from chara.typing import PathLike


def initialize(config_or_path: Optional[Union[PathLike, GlobalConfig]] = None):
    '''
    ## 初始化
    
    ---
    ### 参数
    - _config: 配置或配置文件路径
    '''
    from multiprocessing import current_process
    
    from chara.config import DEFAULT_GLOBAL_CONFIG
    from chara.log import C256, logger
    from chara.core import Core

    current_process().name = 'chara'

    log_msg = C256.f_ef5b9c('Config')
    if config_or_path is None:
        config = load_config()
        with open('./config.yaml', 'w', encoding='UTF-8') as f:
            f.write(DEFAULT_GLOBAL_CONFIG)
        log_msg += C256.f_009ad6('[Default]') + C256.f_00a6ac('[./config.yaml]')
        logger.success(log_msg + ' 已生成.')
        logger.info('请修改配置文件后再次启动.')
        exit(0)
    
    elif isinstance(config_or_path, GlobalConfig):
        config = config_or_path
        log_msg += C256.f_fcaf17('[Custom]') + C256.f_6f60aa('[memory]')
    
    else:
        log_msg += C256.f_fcaf17('[Custom]') + C256.f_00a6ac(f'[{config_or_path}]')
        try:
            config = load_config(config_or_path)
        except Exception:
            logger.exception(log_msg + ' 加载失败!')
            exit(0)
    
    logger.success(log_msg  + ' 加载成功!')
    logger.set_level(config.log.level)
    core = Core(config)
    
    return core

