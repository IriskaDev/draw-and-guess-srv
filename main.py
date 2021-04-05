from config_manager import configmgr
from singleton import singleton
import worker

@singleton
class sometestcls:
    def __init__(self):
        pass

if __name__ == "__main__":
    worker.start()


