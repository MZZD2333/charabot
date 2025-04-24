import chara


if __name__ == '__main__':
    # from chara.core import WorkerProcess
    
    main = chara.initialize('./config.yaml')
    
    # 添加额外的子进程
    # custom_process = WorkerProcess()
    # main.add_worker(custom_process)
    
    main.run()


