from chara.config import GlobalConfig, load_config
from chara.typing import PathLike as _PathLike


def initialize(_config: _PathLike | GlobalConfig | None = None):
    '''
    ## 初始化
    
    ---
    ### 参数
    - _config: 配置或配置文件路径
    '''
    from multiprocessing import current_process
    
    from chara.config import DEFAULT_GLOBAL_CONFIG
    from chara.log import set_logger_config, style, logger
    from chara.core import MainProcess

    current_process().name = 'chara'

    log_msg = style.c('Config')
    if _config is None:
        config = load_config()
        with open('./default-config.yaml', 'w', encoding='UTF-8') as f:
            f.write(DEFAULT_GLOBAL_CONFIG)
        log_msg += style.ly('[Default]') + style.lc('[./default-config.yaml]')
        logger.success(log_msg + ' 已生成.')
    
    elif isinstance(_config, GlobalConfig):
        config = _config
        log_msg += style.ly('[Custom]') + style.lc('[memory]')
    
    else:
        log_msg += style.ly('[Custom]') + style.lc(f'[{_config}]')
        try:
            config = load_config(_config)
        except Exception:
            logger.exception(log_msg + ' 加载失败!')
            exit(0)
    
    set_logger_config(config.log)
    logger.success(log_msg  + ' loaded successfully!')
    main = MainProcess(config)
    
    return main

