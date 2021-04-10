
class client:
    def __init__(self, socket):
        self.ws = socket
        self.nickname = None
        self.room = None
