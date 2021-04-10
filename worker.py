#!/usr/bin/env python

import asyncio
import websockets
from config_manager import configmgr
from singleton import singleton
from room import room
from client import client

# ws - client
CLIENTS = dict()
# id - room
ROOMS = dict()

async def onconnected(ws):
    print('register ws: ', ws)
    c = client(ws)
    CLIENTS[ws] = c

async def ondisconnected(ws):
    print('unregister ws: ', ws)
    c = CLIENTS[ws]
    if c.room is not None:
        r = ROOMS[c.room]
        r.client_exit(c)

    del CLIENTS[ws]

async def onmessage(ws, msg):
    c = CLIENTS[ws]
    print('onmessage:\n ', c, "\n", msg)
    await ws.send(msg)

async def handler(ws, uri):
    await onconnected(ws)
    try:
        while True:
            msg = await ws.recv()
            await onmessage(ws, msg)
            # print('msg from client: ', msg)
            # await ws.send(msg)
    finally:
        await ondisconnected(ws)

def start():
    configmgr().read('./config.json')
    port = int(configmgr().getport())
    ip = configmgr().getip()
    print (ip, port)
    srv = websockets.serve(handler, ip, port=port, ping_interval=10)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        srv
    )
    loop.run_forever()

