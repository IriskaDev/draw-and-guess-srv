import asyncio
from client import client
from room import room
import worker

class fakews:
    def __init__(self):
        pass

    async def send(self, msg):
        name = worker.CLIENTS[self].name
        print("sending to fake client: " + name + "; msg: " + msg)


def printallclientinfo():
    for k in worker.CLIENTS:
        worker.CLIENTS[k].printinfo()

async def test():
    wslist = []
    for i in range(30):
        ws = fakews()
        wslist.append(ws)
        c = client(ws)
        worker.CLIENTS[ws] = c
        # c.name = "CLIENT" + i
        # c.icon = i % 10
    i = 0
    for k in worker.CLIENTS:
        i = i + 1
        c = worker.CLIENTS[k]
        name = 'CLIENT_' + str(i)
        req = {
            'PROTO': 'REQ_REGISTER',
            'NAME': name,
            'ICON': i % 10
        }
        await worker.onregister(c, req)

    printallclientinfo()

    c0 = worker.CLIENTS[wslist[0]]
    await worker.oncreateroom(c0, {
        'PROTO': 'REQ_CREATE_ROOM',
        'NAME': 'ROOM_1'
    })
    c0.printinfo()
    # printallclientinfo()

    c1 = worker.CLIENTS[wslist[1]]
    await worker.getroomlist(c1, {})
    await worker.joinroom_asplayer(c1, {
        'PROTO': 'REQ_JOIN_ROOM_AS_PLAYER',
        'ROOMID': "1000000"
    })
    c1.printinfo()

    c2 = worker.CLIENTS[wslist[2]]
    await worker.joinroom_asviewer(c2, {
        'PROTO': 'REQ_JOIN_ROOM_AS_VIEWER',
        'ROOMID': "1000000"
    })
    c2.printinfo()

    c3 = worker.CLIENTS[wslist[3]]
    await worker.joinroom_asplayer(c3, {
        'PROTO': 'REQ_JOIN_ROOM_AS_PLAYER',
        'ROOMID': "1000000"
    })
    c3.printinfo()

    await worker.quitroom(c3, {})

    await worker.getroomlist(c3, {})

    printallclientinfo()

    # printallclientinfo()



def run():
    # asyncio.run(fill())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())