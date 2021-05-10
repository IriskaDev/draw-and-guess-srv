import asyncio
from client import client
from room import room
import worker

class fakews:
    def __init__(self):
        pass

    async def send(self, msg):
        print("fakewssend: ", msg)


async def fill():
    for i in range(30):
        ws = fakews()
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

    for k in worker.CLIENTS:
        worker.CLIENTS[k].printinfo()


def run():
    # asyncio.run(fill())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fill())