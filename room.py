
class Room:

    def __init__(self):
        self.host = None
        self.players = set()
        self.viewers = set()
        self.answer = None
        self.history = []
    
    def brocastchat(self, content):
        contentpacket = content
        for i in self.players:
            i.send(contentpacket)
        for i in self.viewers:
            i.send(contentpacket)

    def broacastdraws(self, draws):
        pass

    def join_asplayer(self, player):
        self.players.add(player)
        # send join success
        self.sendhistorydraws(player)

    def join_asviewer(self, viewer):
        self.players.add(viewer)
        # send join success
        self.sendhistorydraws(viewer)

    def sendhistorydraws(self, client):
        pass
