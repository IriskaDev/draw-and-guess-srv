#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from room import room
from client import client
from roommgr import roommgr
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

    player0 = worker.CLIENTS[wslist[0]]
    await worker.oncreateroom(player0, {
        'PROTO': 'REQ_CREATE_ROOM',
        'NAME': 'ROOM_1',
        'ICON': '10001',
        'MAXPLAYERS': 5,
        'MATCHOVERSCORE': 20
    })
    player0.printinfo()
    # printallclientinfo()

    r0 = roommgr().getroom("1000000")


    player1 = worker.CLIENTS[wslist[1]]
    await worker.getroomlist(player1, {})
    await worker.joinroom_asplayer(player1, {
        'PROTO': 'REQ_JOIN_ROOM_AS_PLAYER',
        'ROOMID': "1000000"
    })
    player1.printinfo()

    viewer0 = worker.CLIENTS[wslist[2]]
    await worker.joinroom_asviewer(viewer0, {
        'PROTO': 'REQ_JOIN_ROOM_AS_VIEWER',
        'ROOMID': "1000000"
    })
    viewer0.printinfo()

    player2 = worker.CLIENTS[wslist[3]]
    await worker.joinroom_asplayer(player2, {
        'PROTO': 'REQ_JOIN_ROOM_AS_PLAYER',
        'ROOMID': "1000000"
    })
    player2.printinfo()
    await worker.quitroom(player2, {})

    player3 = worker.CLIENTS[wslist[4]]
    # await worker.joinroom_asplayer(player3, {
    #     'PROTO': 'REQ_JOIN_ROOM_AS_PLAYER',
    #     'ROOMID': "1000000"
    # })
    await worker.joinrandomroom(player3, {
        'PROTO': 'REQ_JOIN_RANDOM_ROOM',
    })

    await worker.onreadyforplay(player0, {'PROTO': 'REQ_READY_FOR_PLAY'})
    await worker.onreadyforplay(player1, {'PROTO': 'REQ_READY_FOR_PLAY'})
    await worker.oncancelready(player1, {'PROTO': 'REQ_CANCEL_PLAY'})
    await worker.onreadyforplay(player1, {'PROTO': 'REQ_READY_FOR_PLAY'})

    # await worker.onreadyforplay(viewer0, {'PROTO': 'REQ_READY_FOR_PLAY'})

    await worker.onreadyforplay(player2, {'PROTO': 'REQ_READY_FOR_PLAY'})
    await worker.onreadyforplay(player3, {'PROTO': 'REQ_READY_FOR_PLAY'})


    await worker.startround(player0, {'PROTO': 'REQ_START_ROUND'})
    await worker.send_answer(player3, {
        'PROTO': 'REQ_SEND_ANSWER',
        'ANSWER': r0.answer
    })

    await worker.send_answer(player1, {
        'PROTO': 'REQ_SEND_ANSWER',
        'ANSWER': r0.answer
    })

    await worker.startround(player1, {'PROTO': 'REQ_START_ROUND'})
    await worker.send_answer(player3, {
        'PROTO': 'REQ_SEND_ANSWER',
        'ANSWER': r0.answer
    })
    await worker.send_answer(player0, {
        'PROTO': 'REQ_SEND_ANSWER',
        'ANSWER': r0.answer
    })

    # await worker.getroomlist(player2, {})
    # printallclientinfo()
    # printallclientinfo()


def run():
    # asyncio.run(fill())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())