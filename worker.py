#!/usr/bin/env python

import asyncio
import websockets
from config_manager import configmgr
from singleton import singleton
from room import Room

CLIENTS = set()
ROOM_MAP = dict()

async def handler(websocket, path):
    greeting = await websocket.recv()
    print('greeting form client: ', greeting)
    await websocket.send(greeting)

def start():
    configmgr().read('./config.json')
    port = int(configmgr().getport())
    ip = configmgr().getip()
    print (ip, port)
    srv = websockets.serve(handler, ip, port=port)
    asyncio.get_event_loop().run_until_complete(
        srv
    )
    asyncio.get_event_loop().run_forever()




