#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
from singleton import singleton
from configmgr import configmgr

@singleton
class questionmgr:
    def __init__(self):
        self.dataobj = None
        self.datalen = 0
        self.maxretry = 5
        self.read(configmgr().getquestionfilepath())

    def read(self, path):
        f = open(path, 'r', encoding='utf-8')
        self.dataobj = json.load(f)
        f.close()
        self.datalen = len(self.dataobj)
    
    def getrndquestion(self, avoididx = -1):
        rnd = random.randrange(0, self.datalen)
        retry = 0
        while rnd == avoididx and retry < self.maxretry:
            rnd = random.randrange(0, self.datalen)
            retry += 1
        return self.dataobj[rnd], rnd

    