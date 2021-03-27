
from singleton import singleton
import json


@singleton
class configmgr:
    dataobj = None

    def __init__(self):
        pass

    @classmethod
    def read(self, path):
        f = open(path, 'r')
        self.dataobj = json.load(f)
        f.close()

    def getport(self):
        if self.dataobj is None:
            return 0
        return self.dataobj['srv-port']


