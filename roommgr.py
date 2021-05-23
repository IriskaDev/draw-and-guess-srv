#!/usr/bin/env python
# -*- coding: utf-8 -*-

from singleton import singleton
from room import room


@singleton
class roommgr:
    def __init__(self):
        # id - room
        self.rooms  = dict()

        # sorted rooms
        # only used in generating room list for client
        # when ROOMS updated, use code below to generate SORTED_ROOMS
        # SORTED_ROOMS = sorted(ROOMS.items(), key=lambda x: x[0])
        # after sorted, we get a list which contains values as shown below
        # [(key, value), (key, value), ...]
        self.sortedrooms = []

    # def createroom(self, name, maxplayers, matchoverscore, pwd=None, onclientdisconnected=None):
    def createroom(self, name, icon, maxplayers, matchoverscore, pwd=None):
        r = room()
        r.name = name
        r.icon = icon
        r.maxplayers = maxplayers
        r.matchoverscore = matchoverscore
        r.pwd = pwd
        # r.onclientdisconnected = onclientdisconnected
        self.rooms[r.id] = r
        self.updatesortedrooms()
        return r

    def updatesortedrooms(self):
        self.sortedrooms.clear()
        self.sortedrooms.extend(sorted(self.rooms.items(), key=lambda x: x[0]))
    
    def roomexists(self, rid):
        return rid in self.rooms

    def getroom(self, rid):
        return self.rooms[rid]
    
    def getjoinalbleroom(self):
        for _, r in self.sortedrooms:
            if not r.isplayerfull() and not r.isinmatch():
                return r
        return None

    def getsortedroomlist(self, sort = None):
        return [i[1].getroombriefinfo() for i in self.sortedrooms]
    
    def removeroom(self, rid):
        if rid not in self.rooms:
            return

        r = self.rooms[rid]
        r.clear()
        del self.rooms[rid]
        self.updatesortedrooms()
    
    def update(self, tickcount, tm):
        # contains rooms that need process on worker after update
        l = []
        for _, r in self.rooms.items():
            needproc = r.update(tickcount, tm)
            if needproc:
                l.append(r)
        return l

