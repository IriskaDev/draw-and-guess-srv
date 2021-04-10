
class room:

    def __init__(self):
        self.id = 0
        self.pwd = ""
        self.host = None
        self.name = ""
        self.players = set()
        self.viewers = set()
        self.maxplayers = 0
        self.maxviewers = 0
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

    def set_answer(self, answer):
        pass

    def set_pwd(self, pwd):
        pass

    def client_exit(self, client):
        pass

    def room_close(self):
        pass
