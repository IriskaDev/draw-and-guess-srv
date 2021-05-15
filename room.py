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
        self.name = ""
        # container of client object
        self.maxscore = 0
        self.players = set()
        # container of client object
        self.viewers = set()
        self.maxplayers = 0
        self.maxviewers = 9999999
        self.answer = None
        self.history = []
        # container of client object
        self.correctplayers = []
        self.roundstarted = False
    
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
    
    def clientisviewer(self, c):
        return c in self.viewers
    
    def roundstart(self, answer):
        self.correctplayers = []
        self.answer = answer
        self.roundstarted = True

    def isinround(self):
        return self.roundstarted

    def roundover(self):
        self.roundstarted = False

    def playeranswercorrect(self, player):
        if player not in self.players:
            return
        if player in self.correctplayers:
            return
        
        self.correctplayers.append(player)

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
        player.room = self.id

    def joinasviewer(self, viewer):
        if viewer in self.viewers:
            return
        if viewer in self.players:
            return
        self.viewers.add(viewer)
        viewer.room = self.id
        # send join success
        # don't do it here, do it outside
        # await self.sendhistorydraws(viewer)
    
    def gethistorydraws(self):
        pass

    def setanswer(self, answer):
        self.answer = answer

    def setpwd(self, pwd):
        self.pwd = pwd

    def quitroom(self, c):
        c.room = None
        if c in self.players:
            self.players.remove(c)
        if c in self.viewers:
            self.viewers.remove(c)
        if c in self.correctplayers:
            self.correctplayers.remove(c)

    def getplayerinfolist(self):
        l = []
        for i in self.players:
            l.append(i.getinfo())
        return l

    def getviewerinfolist(self):
        l = []
        for i in self.viewers:
            l.append(i.getinfo())
        return l
    
    def getcorrectplayerinfolist(self):
        l = []
        for i in self.correctplayers:
            l.append(i.getinfo())
        return l

    def getbroadcastclientlist(self):
        l = []
        for i in self.viewers:
            l.append(i)
        for i in self.players:
            l.append(i)
        return l

    def getroominfo(self):
        obj = {
            'ID': self.id,
            'NAME': self.name,
            'PLAYERS': self.getplayerinfolist(),
            'VIEWERS': self.getviewerinfolist(),
            'HISTORYDRAWS': None,
            'ISINROUND': self.roundstarted,
        }
        return obj

    def getroombriefinfo(self):
        obj = {
            'ID': self.id,
            'NAME': self.name,
            'PLAYERCOUNT': self.playercount(),
            'VIEWERCOUNT': self.viewercount(),
            'MAXPLAYER': self.maxplayers,
            'MAXVIEWER': self.maxviewers,
            'NEEDPWD': self.pwd is not None,
        }
        return obj

    def isempty(self):
        return (self.playercount() + self.viewercount()) <= 0
    
    def clear(self):
        self.players = set()
        self.viewer = set()
        self.correctplayers = []
        self.history = []
        self.roundstarted = False
        self.answer = None
