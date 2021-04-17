from singleton import singleton

@singleton
class roomidgenerator:
    def __init__(self):
        self.current = 0

    def getnewid(self):
        newid = self.current + 1000000
        self.current = self.current + 1 % 1000000
        return str(newid)



class room:

    def __init__(self):
        self.id = roomidgenerator().getnewid()
        self.pwd = None
        self.host = None
        self.name = ""
        self.players = set()
        self.viewers = set()
        self.maxplayers = 0
        self.maxviewers = 0
        self.answer = None
        self.history = []
    
    def playercount(self):
        return len(self.players)
    
    def viewercount(self):
        return len(self.viewers)

    def isplayerfull(self):
        return len(self.players) >= self.maxplayers

    def isviewerfull(self):
        return len(self.viewers) >= self.maxviewers

    def clientinroom(self, c):
        return c in self.viewers or c in self.players

    def brocastchat(self, content):
        contentpacket = content
        for i in self.players:
            i.send(contentpacket)
        for i in self.viewers:
            i.send(contentpacket)

    def broacastdraws(self, draws):
        pass

    def joinasplayer(self, player):
        if player in self.players:
            return
        if player in self.viewers:
            return
        self.players.add(player)
        player.roomid = self.id
        # send join success
        # don't do it here, do it outside
        # self.sendhistorydraws(player)

    async def joinasviewer(self, viewer):
        if viewer in self.viewers:
            return
        if viewer in self.players:
            return
        self.viewers.add(viewer)
        viewer.roomid = self.id
        # send join success
        # don't do it here, do it outside
        # await self.sendhistorydraws(viewer)

    async def sendhistorydraws(self, client):
        pass

    def setanswer(self, answer):
        self.answer = answer

    def setpwd(self, pwd):
        self.pwd = pwd

    def quitroom(self, c):
        c.roomid = None
        if c in self.players:
            self.players.remove(c)
        if c in self.viewers:
            self.viewers.remove(c)
