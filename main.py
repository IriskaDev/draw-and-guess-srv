from config_manager import configmgr
from singleton import singleton
from worker import worker

@singleton
class sometestcls:
    def __init__(self):
        pass

if __name__ == "__main__":
    # configmgr().read("./config.json")
    # print(configmgr().getport())
    worker().start()


