#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configmgr import configmgr
from singleton import singleton
import worker

import testroutine

@singleton
class sometestcls:
    def __init__(self):
        pass

if __name__ == "__main__":
    configmgr().read('./config.json')
    testroutine.run()
    worker.start()



