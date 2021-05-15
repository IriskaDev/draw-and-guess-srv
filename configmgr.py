
import json
from singleton import singleton


@singleton
class configmgr:
    dataobj = None

    def __init__(self):
        pass

    def read(self, path):
        f = open(path, 'r')
        self.dataobj = json.load(f)
        f.close()

    def getport(self):
        if self.dataobj is None:
            return 0
        return self.dataobj['srv-port']

    def getip(self):
        if self.dataobj is None:
            return "localhost"
        return self.dataobj['srv-ip']
    
    def gettickinterval(self):
        if self.dataobj is None:
            return 1
        return float(self.dataobj["tick-interval"])
    

