#!/usr/bin/env python
# -*- coding: utf-8 -*-

from singleton import singleton

@singleton
class clientidgenerator:
    def __init__(self):
        self.current = 0

    def getnewid(self):
        newid = self.current + 1000000
        self.current = self.current + 1 % 1000000
        return str(newid)


class client:
    def __init__(self, socket):
        self.id = clientidgenerator().getnewid()
        self.ws = socket
        self.name = None
        self.icon = None
        self.room = None
    
    def getinfo(self):
        obj = {
            'ID': self.id,
            'NAME': self.name,
            'ICON': self.icon,
        }
        return obj

    def printinfo(self):
        print(self.id, self.name, self.icon, self.room)
