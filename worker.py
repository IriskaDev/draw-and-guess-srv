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

async def register(ws):
    print('register ws: ', ws)
    c = client(ws)
    CLIENTS[ws] = c

async def unreister(ws):
    print('unregister ws: ', ws)
    c = CLIENTS[ws]
    if c.room is not None:
        r = ROOMS[c.room]
        r.client_exit(c)

    del CLIENTS[ws]

async def handler(ws, uri):
    await register(ws)
    try:
        while True:
            msg = await ws.recv()
            print('msg from client: ', msg)
            await ws.send(msg)
    finally:
        await unreister(ws)

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

