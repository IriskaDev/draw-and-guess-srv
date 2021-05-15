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

    def createroom(self, name, maxplayers, maxscore, pwd):
        r = room()
        r.name = name
        r.maxplayers = maxplayers
        r.maxscore = maxscore
        r.pwd = pwd
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

    def getsortedroomlist(self, sort = None):
        return [i[1].getroombriefinfo() for i in self.sortedrooms]
    
    def removeroom(self, rid):
        if rid not in self.rooms:
            return

        r = self.rooms[rid]
        r.clear()
        del self.rooms[rid]
        self.updatesortedrooms()
