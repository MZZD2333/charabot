import chara


if __name__ == '__main__':
    # from chara.core.workers import WorkerProcess
    
    core = chara.initialize()
    
    # 添加额外的子进程
    # custom_process = WorkerProcess(core.config, 'extra')
    # core.wm.add(custom_process)
    
    core.run()


