from multiprocessing import Process

from chara.config import GlobalConfig


class ChildProcess(Process):
    _start_method = 'spawn'

    def __init__(self, global_config: GlobalConfig) -> None:
        super().__init__(name='unnamed-process')
        self.global_config = global_config

    def main(self) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        import signal
        
        signal.signal(signal.SIGFPE, signal.SIG_IGN)
        
        from chara.log import logger, set_logger_config

        set_logger_config(self.global_config.log)
        logger.success(f'子进程开启 [PID: {self.pid}].')
        try:
            self.main()
        except KeyboardInterrupt:
            pass
        except InterruptedError:
            pass
        except:
            logger.exception('子进程捕获到异常.')
        
        logger.success(f'子进程关闭 [PID: {self.pid}].')
    
    def new(self) -> 'ChildProcess':
        raise NotImplementedError()
