#!/usr/bin/env python

import asyncio
import websockets
from config_manager import configmgr
from singleton import singleton

async def echo(websocket, path):
    greeting = await websocket.recv()
    print('greeting form client: ', greeting)
    await websocket.send(greeting)


@singleton
class worker:
    def __init__(self):
        pass

    def start(self):
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(echo, 'localhost', configmgr().getport())
        )
        asyncio.get_event_loop().run_forever()



