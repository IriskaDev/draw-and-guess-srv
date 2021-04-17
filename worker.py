#!/usr/bin/env python

import sys
import asyncio
import websockets
import json
import math
import respassembler
from config_manager import configmgr
from singleton import singleton
from room import room
from client import client

# ws - client
CLIENTS = dict()
# id - room
ROOMS = dict()

# sorted rooms
# only used in generating room list for client
# when ROOMS updated, use code below to generate SORTED_ROOMS
# SORTED_ROOMS = sorted(ROOMS.items(), key=lambda x: x[0])
# after sorted, we get a list which contains values as shown below
# [(key, value), (key, value), ...]
SORTED_ROOMS = []


def updatesortedroom():
    SORTED_ROOMS.clear()
    SORTED_ROOMS.extend(sorted(ROOMS.items(), key=lambda x: x[0]))

async def onregister(c, req):
    if 'NAME' not in req:
        await c.ws.send(respassembler.get_resp_register(1))
        return

    c.nickname = req['NAME']
    await c.ws.send(respassembler.get_resp_register(0))

async def getroomlist(c, req):
    # sortby = "BYID"
    # if 'SORT' in req:
        # sortby = req['sort']
    infolist = []
    for i in SORTED_ROOMS:
        info = {
            'ROOMID': i.id,
            'NAME': i.name,
            'HOSTNAME': i.host.nickname,
            'PLAYERCOUNT': i.playercount(),
            'VIEWERCOUNT': i.viewercount(),
            'MAXPLAYER': i.maxplayers,
            'MAXVIEWER': i.maxviewers,
            'NEEDPWD': i.pwd is not None,
        }
        infolist.append(info)
    await c.ws.send(respassembler.get_resp_get_room_list(0, infolist))

async def oncreateroom(c, req):
    if 'NAME' not in req:
        await c.ws.send(respassembler.get_resp_create_room(1))
        return

    if c.room is not None:
        await c.ws.send(respassembler.get_resp_create_room(2))
        return
    
    r = room()
    r.host = c
    r.name = req['NAME']
    c.room = r.id
    if 'PWD' in req:
        r.pwd = req['PWD']
    ROOMS[r.id] = r
    updatesortedroom()
    await c.ws.send(respassembler.get_resp_create_room(0, r.id))


async def joinroom_asplayer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(respassembler.get_resp_join_room_as_player(1))
        return
    roomid = req['ROOMID']
    if roomid not in ROOMS:
        await c.ws.send(respassembler.get_resp_join_room_as_player(2))
        return
    r = ROOMS[roomid]
    if r.isplayerfull():
        await c.ws.send(respassembler.get_resp_join_room_as_player(3))
        return

    if r.clientinroom(c):
        await c.ws.send(respassembler.get_resp_join_room_as_player(4))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(respassembler.get_resp_join_room_as_player(5))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(respassembler.get_resp_join_room_as_player(5))
            return
    
    r.joinasplayer(c)
    await c.ws.send(respassembler.get_resp_join_room_as_player(0, roomid))
    await r.sendhistorydraws(c)

async def joinroom_asviewer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(respassembler.get_resp_join_room_as_viewer(1))
        return
    roomid = req['ROOMID']
    if roomid not in ROOMS:
        await c.ws.send(respassembler.get_resp_join_room_as_viewer(2))
        return
    r = ROOMS[roomid]
    if r.isviewerfull():
        await c.ws.send(respassembler.get_resp_join_room_as_viewer(3))
        return
    if r.clientinroom(c):
        await c.ws.send(respassembler.get_resp_join_room_as_viewer(4))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(respassembler.get_resp_join_room_as_viewer(5))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(respassembler.get_resp_join_room_as_viewer(5))
            return
    
    r.joinasviewer(c)
    await c.ws.send(respassembler.get_resp_join_room_as_viewer(0, roomid))
    await r.sendhistorydraws(c)

async def quitroom(c, req):
    if c.room is None:
        await c.ws.send(respassembler.get_resp_quit_room(1))
        return
    
    if c.room not in ROOMS:
        await c.ws.send(respassembler.get_resp_quit_room(2))
        return
    
    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(respassembler.get_resp_quit_room(1))
        return
    
    if c == r.host:
        for i in r.viewers:
            try:
                await i.ws.send(respassembler.get_resp_quit_room(0))
            except websockets.exceptions.ConnectionClosed:
                ondisconnected(i.ws, False)
            except:
                pass
        for i in r.players:
            try:
                await i.ws.send(respassembler.get_resp_quit_room(0))
            except websockets.exceptions.ConnectionClosed:
                ondisconnected(i.ws, False)
            except:
                pass
        # delete room here
        del ROOMS[c.room]
        updatesortedroom()
        return
    
    r.quitroom(c)
    await c.ws.send(respassembler.get_resp_quit_room(0))

async def heartbeat(c, req):
    await c.ws.send(respassembler.get_resp_heartbeat())

HANDLERS = {
    'REQ_REGISTER':             onregister,
    'REQ_GET_ROOM_LIST':        getroomlist,
    'REQ_CREATE_ROOM':          oncreateroom,
    'REQ_JOIN_ROOM_AS_PLAYER':  joinroom_asplayer,
    'REQ_JOIN_ROOM_AS_VIEWER':  joinroom_asviewer,
    'REQ_QUIT_ROOM':            quitroom,



    'REQ_HEARTBEAT':            heartbeat,
}

async def onconnected(ws):
    print('register ws: ', ws)
    if ws in CLIENTS:
        return
    c = client(ws)
    CLIENTS[ws] = c

async def ondisconnected(ws, quitroom=True):
    print('unregister ws: ', ws)
    if ws not in CLIENTS:
        return
    if quitroom:
        c = CLIENTS[ws]
        if c.room is not None:
            r = ROOMS[c.room]
            if r.host == c:
                # need to delete room and notify players and viewers in the room
                for i in r.viewers:
                    try:
                        await i.ws.send(respassembler.get_resp_quit_room(0))
                    except websockets.exceptions.ConnectionClosed:
                        ondisconnected(i.ws, False)
                    except:
                        pass
                for i in r.players:
                    try:
                        await i.ws.send(respassembler.get_resp_quit_room(0))
                    except websockets.exceptions.ConnectionClosed:
                        ondisconnected(i.ws, False)
                    except:
                        pass
                del ROOMS[c.room]
                updatesortedroom()
            else:
                r.quitroom(c)

    del CLIENTS[ws]

async def onmessage(ws, msg):
    print(ws, msg)
    try:
        c = CLIENTS[ws]
        if c.nickname is not None:
            print(c.nickname)
        req = json.loads(msg)
        if type(req['PROTO']) is not str:
            raise Exception('PROTO not found in incoming message')
    
        if req['PROTO'] not in HANDLERS:
            raise Exception('PROTO handler not found, PROTO -> [{proto}]'.format(req['PROTO']))
        
        await HANDLERS[req['PROTO']](c, req)
    except websockets.exceptions.ConnectionClosed:
        ondisconnected(ws)
    except:
        await ws.send(respassembler.get_resp_handle_req_failed())
        print('handle message failed: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])

    

async def handler(ws, uri):
    await onconnected(ws)
    try:
        while True:
            msg = await ws.recv()
            await onmessage(ws, msg)
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

