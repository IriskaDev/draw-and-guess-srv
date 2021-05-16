#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import websockets
from singleton import singleton
from questionsmgr import questionmgr

@singleton
class roomidgenerator:
    def __init__(self):
        self.current = 0

    def getnewid(self):
        newid = self.current + 1000000
        self.current = self.current + 1 % 1000000
        return str(newid)

class playerstatus:
    def __init__(self, player):
        self.player = player
        self.isready = False
        self.score = 0
        self.entertm = time.time()

    def setready(self, val):
        self.isready = val
    
    def getisready(self):
        return self.isready

    def getinfo(self):
        infoobj = {
            'PLAYER': self.player.getinfo(),
            'SCORE': self.score,
            'ISREADY': self.isready,
            'ENTERTM': self.entertm
        }
        return infoobj
    
    def addscore(self, score):
        self.score += score
    
    def getscore(self):
        return self.score


class room:
    def __init__(self):
        self.id = roomidgenerator().getnewid()
        self.pwd = None
        self.name = ""
        # container of client object
        self.maxscore = 0
        # player - playerstatus
        self.players = dict()
        self.playersequence = []
        self.currentdraweridx = 0
        self.rank = []
        # container of client object
        self.viewers = set()
        self.maxplayers = 0
        self.maxviewers = 9999999
        self.answer = None
        self.hint = None
        self.lastquestionidx = -1
        self.history = []
        self.roundstarted = False
        self.roundstarttm = 0
        self.roundcorrectplayers = []
        self.drawerroundscore = 0
        self.ismatchover = False
        # self.onclientdisconnected = None
    
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
    
    def clientisdrawer(self, c):
        stat = self.playersequence[self.currentdraweridx%len(self.playersequence)]
        return stat.player.id == c.id
    
    def refreshrank(self):
        self.rank = [stat for _, stat in self.players.items()].sort(key=lambda x: x.score, reverse=True)

    def updateplayersequence(self):
        self.playersequence = [v for _, v in self.players.items()]
        self.playersequence.sort(key=lambda x: x.entertm)
    
    def roundstart(self):
        # select an answer
        self.roundstarted = True
        self.roundstarttm = time.time()
        self.roundcorrectplayers.clear()
        self.drawerroundscore = 0
        question, self.lastquestionidx = questionmgr().getrndquestion(self.lastquestionidx)
        self.answer = question['title']
        self.hint = question['hint']

    def isinround(self):
        return self.roundstarted

    def roundover(self):
        self.roundstarted = False
        self.currentdraweridx += 1
        self.refreshrank()
        self.history.clear()
        self.roundstarttm = 0
        for _, player in self.players.items():
            player.setready(False)
    
    def matchover(self):
        self.ismatchover = True

    def playeranswercorrect(self, player):
        if player not in self.players:
            return
        if player in self.roundcorrectplayers:
            return
        self.roundcorrectplayers.append(player)
        playerstat = self.players[player]
        correctplayernum = len(self.roundcorrectplayers)
        gains = 0
        if correctplayernum == 0:
            gains = 10
        elif correctplayernum == 1:
            gains = 7
        elif correctplayernum == 2:
            gains = 4
        else:
            gains = 1
        playerstat.addscore(gains)
        s = playerstat.getscore()
        if self.maxscore < s:
            self.maxscore = s
        drawergains = 0
        self.drawerroundscore += 2
        drawergains = 2
        if self.drawerroundscore > 10:
            drawergains -= self.drawerroundscore - 10
            self.drawerroundscore = 10
        drawerstat = self.getdrawerstat()
        drawerstat.addscore(drawergains)
        s = drawerstat.getscore()
        if self.maxscore < s:
            self.maxscore = s
        self.refreshrank()
    
    def getroundcorrectplayerstatlist(self):
        return [self.players[i].getinfo() for i in self.roundcorrectplayers]

    def joinasplayer(self, player):
        if player in self.players:
            return
        if player in self.viewers:
            return
        self.players[player] = playerstatus(player)
        player.room = self.id
        self.updateplayersequence()

    def joinasviewer(self, viewer):
        if viewer in self.viewers:
            return
        if viewer in self.players:
            return
        self.viewers.add(viewer)
        viewer.room = self.id
    
    def gethistorydraws(self):
        pass

    def getanswer(self):
        return self.answer

    def setpwd(self, pwd):
        self.pwd = pwd
    
    def setplayerready(self, player, ready):
        status = self.players[player]
        status.setready(True)
        allready = True
        for _, s in self.players.items():
            if not s.getisready():
                allready = False
                break
        if allready:
            self.roundstart()
        return allready
    
    def quitroom(self, c):
        c.room = None
        if c in self.players:
            del self.players[c]
            self.updateplayersequence()
        if c in self.viewers:
            self.viewers.remove(c)

    def getplayerstat(self, c):
        if c not in self.players:
            return None
        return self.players[c]

    def getdrawerstat(self):
        print ("curretndraweridx: ", self.currentdraweridx)
        print ("len: ", len(self.playersequence))
        player = self.playersequence[self.currentdraweridx%len(self.playersequence)]
        stat = self.players[player]
        return stat
        
    def getplayerinfolist(self):
        l = []
        for _, stats in self.players.items():
            l.append(stats.getinfo())
        return l

    def getviewerinfolist(self):
        l = []
        for i in self.viewers:
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
        obj = None
        if not self.isinround:
            obj = {
                'ID': self.id,
                'NAME': self.name,
                'PLAYERSTATS': self.getplayerinfolist(),
                'HISTORYDRAWS': None,
                'ISINROUND': self.roundstarted,
                'ROUNDINFO': self.getcurrentroundinfo(),
            }
        else:
            obj = {
                'ID': self.id,
                'NAME': self.name,
                'PLAYERSTATS': self.getplayerinfolist(),
                'HISTORYDRAWS': None,
                'ISINROUND': self.roundstarted,
                'ROUNDINFO': None
            }
        return obj

    def getroombriefinfo(self):
        obj = {
            'ID': self.id,
            'NAME': self.name,
            'PLAYERCOUNT': self.playercount(),
            'VIEWERCOUNT': self.viewercount(),
            'MAXPLAYER': self.maxplayers,
            'NEEDPWD': self.pwd is not None,
        }
        return obj
    
    def getcurrentroundinfo(self):
        obj = {
            'STARTTM': self.roundstarttm,
            'DRAWER': self.getdrawerstat().getinfo(),
            'HINT': self.hint
        }
        return obj

    def getrankinfo(self):
        return [stat.getinfo() for stat in self.rank]

    def isempty(self):
        return (self.playercount() + self.viewercount()) <= 0

    def update(self, tickcount, tm):
        if not self.roundstarted:
            return False
        
        t = tm - self.roundstarttm
        if t >= 120:
            self.roundover()
            return True
        return False
    
    # async def broadcastmsg(self, msg):
    #     l = self.getbroadcastclientlist()
    #     for c in l:
    #         try:
    #             await c.ws.send(msg)
    #         except websockets.exceptions.ConnectionClosed:
    #             self.ondisconnected(c.ws, False)
    #         except:
    #             pass
    
    def clear(self):
        self.players = set()
        self.viewer = set()
        self.roundcorrectplayers.clear()
        self.history = []
        self.roundstarted = False
        self.answer = None
