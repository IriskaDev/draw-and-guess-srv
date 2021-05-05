#!/usr/bin/env python

import sys
import asyncio
import websockets
import json
import math
import protoassembler
from config_manager import configmgr
from singleton import singleton
from room import room
from client import client

# ws - client
CLIENTS = dict()
# NAMES = set()
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

async def broadcastmsg(clientlist, msg):
    for c in clientlist:
        try:
            await c.ws.send(msg)
        except websockets.exceptions.ConnectionClosed:
            ondisconnected(c.ws, False)
        except:
            pass

async def onregister(c, req):
    if 'NAME' not in req:
        await c.ws.send(protoassembler.get_resp_register(1))
        return

    if 'ICON' not in req:
        await c.ws.send(protoassembler.get_resp_register(2))

    # if req['NAME'] in NAMES:
        # await c.ws.send(protoassembler.get_resp_register(2))
        # return

    c.name = req['NAME']
    await c.ws.send(protoassembler.get_resp_register(0))

async def getroomlist(c, req):
    # sortby = "BYID"
    # if 'SORT' in req:
        # sortby = req['sort']
    infolist = []
    for i in SORTED_ROOMS:
        info = i.getroombriefinfoobject()
        infolist.append(info)
    await c.ws.send(protoassembler.get_resp_get_room_list(0, infolist))

async def oncreateroom(c, req):
    if 'NAME' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(1))
        return

    if c.room is not None:
        await c.ws.send(protoassembler.get_resp_create_room(2))
        return
    
    r = room()
    r.host = c
    r.name = req['NAME']
    c.room = r.id
    if 'PWD' in req:
        r.pwd = req['PWD']
    ROOMS[r.id] = r
    updatesortedroom()
    await c.ws.send(protoassembler.get_resp_create_room(0, r.getroombreifinfoobejct()))


async def joinroom_asplayer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(protoassembler.get_resp_join_room_as_player(1))
        return
    roomid = req['ROOMID']
    if roomid not in ROOMS:
        await c.ws.send(protoassembler.get_resp_join_room_as_player(2))
        return
    r = ROOMS[roomid]
    if r.isplayerfull():
        await c.ws.send(protoassembler.get_resp_join_room_as_player(3))
        return

    if r.clientinroom(c):
        await c.ws.send(protoassembler.get_resp_join_room_as_player(4))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(protoassembler.get_resp_join_room_as_player(5))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(protoassembler.get_resp_join_room_as_player(5))
            return
    
    l = r.getbroadcastwslist()
    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_join_room_as_player(0, r.getroominfoobject()))
    await broadcastmsg(l, protoassembler.get_broadcast_player_joined(c))

async def joinroom_asviewer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(1))
        return
    roomid = req['ROOMID']
    if roomid not in ROOMS:
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(2))
        return
    r = ROOMS[roomid]
    if r.isviewerfull():
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(3))
        return
    if r.clientinroom(c):
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(4))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(protoassembler.get_resp_join_room_as_viewer(5))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(protoassembler.get_resp_join_room_as_viewer(5))
            return
    
    l = r.getbroadcastwslist()
    r.joinasviewer(c)
    await c.ws.send(protoassembler.get_resp_join_room_as_viewer(0, r.getroominfoobject()))
    await broadcastmsg(l, protoassembler.get_broadcast_viewer_joined(c))

async def quitroom(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_quit_room(1))
        return
    
    if c.room not in ROOMS:
        c.room = None
        await c.ws.send(protoassembler.get_resp_quit_room(2))
        return
    
    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_quit_room(1))
        return
    
    if c == r.host:
        for viewer in r.viewers:
            viewer.room = None
        await broadcastmsg(r.viewers, protoassembler.get_resp_quit_room(0))
        for player in r.players:
            player.room = None
        await broadcastmsg(r.players, protoassembler.get_resp_quit_room(0))
        # delete room here
        del ROOMS[c.room]
        updatesortedroom()
        return
    
    isviewer = r.clientisviewer(c)
    r.quitroom(c)
    await c.ws.send(protoassembler.get_resp_quit_room(0))
    if isviewer:
        await broadcastmsg(r.getbroadcastwslist(), protoassembler.get_broadcast_viewer_exit(c))
    else:
        await broadcastmsg(r.getbroadcastwslist(), protoassembler.get_broadcast_player_exit(c))

async def get_room_player_list(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_get_room_player_list(1, None))
        return
    
    if c.room not in ROOMS:
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_player_list(2, None))
        return

    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_player_list(3, None))
        return
    
    await c.ws.send(protoassembler.get_resp_get_room_player_list(0, r.getplayerinfolist()))
    
async def get_room_viewer_list(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(1, None))
        return
    
    if c.room not in ROOMS:
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(2, None))
        return
    
    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(3, None))
        return
    
    await c.ws.send(protoassembler.get_resp_get_room_viewer_list(0, r.getviewerinfolist()))

async def send_chat(c, req):
    if c.room is None:
        return

    if c.room not in ROOMS:
        return

    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        return
    
    msg = req['MSG']
    if type(msg) is not str:
        return
    if len(msg) <= 0:
        return
    
    await broadcastmsg(r.getbroadcastwslist(), msg)
    

async def send_answer(c, req):
    if c.room is None:
        c.ws.send(protoassembler.get_resp_send_answer(1, False))
        return

    if c.room not in ROOMS:
        c.room = None
        c.ws.send(protoassembler.get_resp_send_answer(2, False))
        return
    
    r = ROOMS[c.room]
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_send_answer(3, False))
        return

    if r.clientisviewer(c):
        await c.ws.send(protoassembler.get_resp_send_answer(4, False))
        return
    
    if not r.isinround():
        await c.ws.send(protoassembler.get_resp_send_answer(5, False))
    
    if r.answer is None:
        await c.ws.send(protoassembler.get_resp_send_answer(6, False))
        return

    answer = req['ANSWER']
    if answer != r.answer:
        await c.ws.send(protoassembler.get_resp_send_answer(0, False))
    else:
        r.playeranswercorrect(c)
        await c.ws.send(protoassembler.get_resp_send_answer(0, True))

async def roundstart(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_roundstart(1))
        return

    if c.room not in ROOMS:
        await c.ws.send(protoassembler.get_resp_roundstart(2))
        return

    r = ROOMS[c.room]
    if r.host != c:
        await c.ws.send(protoassembler.get_resp_roundstart(3))
        return

    answer = req['ANSWER']
    if type(answer) is not str:
        await c.ws.send(protoassembler.get_resp_roundstart(4))
        return
    
    if len(answer) <= 0:
        await c.ws.send(protoassembler.get_resp_roundstart(5))
        return
    
    r.roundstart(answer)
    await c.ws.send(protoassembler.get_resp_roundstart(0))
    l = r.getbroadcastwslist()
    broadcastmsg(l, protoassembler.get_broadcast_roundstart())

async def roundover(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_roundover(1))
        return
    
    if c.room not in ROOMS:
        await c.ws.send(protoassembler.get_resp_roundover(2))
        return
    
    r = ROOMS[c.room]
    if r.host != c:
        await c.ws.send(protoassembler.get_resp_roundover(3))
        return
    
    r.roundover()
    await c.ws.send(protoassembler.get_resp_roundover(0))
    l = r.getbroadcastwslist()
    broadcastmsg(l, protoassembler.get_broadcast_roundover(r.getcorrectplayerinfolist()))

async def draw(c, req):
    pass

async def heartbeat(c, req):
    await c.ws.send(protoassembler.get_resp_heartbeat())

HANDLERS = {
    'REQ_REGISTER':             onregister,
    'REQ_GET_ROOM_LIST':        getroomlist,
    'REQ_CREATE_ROOM':          oncreateroom,
    'REQ_JOIN_ROOM_AS_PLAYER':  joinroom_asplayer,
    'REQ_JOIN_ROOM_AS_VIEWER':  joinroom_asviewer,
    'REQ_QUIT_ROOM':            quitroom,
    'REQ_GET_ROOM_PLAYER_LIST': get_room_player_list,
    'REQ_GET_ROOM_VIEWER_LIST': get_room_viewer_list,
    'REQ_SEND_CHAT':            send_chat,
    'REQ_SEND_ANSWER':          send_answer,
    'REQ_ROUND_START':          roundstart,
    'REQ_ROUND_OVER':           roundover,
    'REQ_DRAW':                 draw,

    'REQ_HEARTBEAT':            heartbeat,
}

async def onconnected(ws):
    print('register ws: ', ws)
    if ws in CLIENTS:
        return
    c = client(ws)
    CLIENTS[ws] = c
    await ws.send(protoassembler.get_resp_onconnected(c.id))

async def ondisconnected(ws, quitroom=True):
    print('unregister ws: ', ws)
    if ws not in CLIENTS:
        return
    c = CLIENTS[ws]
    # NAMES.remove(c.name)
    if quitroom:
        if c.room is not None:
            r = ROOMS[c.room]
            if r.host == c:
                # need to delete room and notify players and viewers in the room
                for viewer in r.viewers:
                    viewer.room = None
                await broadcastmsg(r.viewers, protoassembler.get_resp_quit_room(0))
                for player in r.players:
                    player.room = None
                await broadcastmsg(r.players, protoassembler.get_resp_quit_room(0))
                del ROOMS[c.room]
                updatesortedroom()
            else:
                r.quitroom(c)

    del CLIENTS[ws]

async def onmessage(ws, msg):
    print(ws, msg)
    try:
        c = CLIENTS[ws]
        # if c.name is not None:
            # print(c.name)
        req = json.loads(msg)
        if type(req['PROTO']) is not str:
            raise Exception('PROTO not found in incoming message')
    
        if req['PROTO'] not in HANDLERS:
            raise Exception('PROTO handler not found, PROTO -> [{proto}]'.format(req['PROTO']))
        
        await HANDLERS[req['PROTO']](c, req)
    except websockets.exceptions.ConnectionClosed:
        ondisconnected(ws)
    except:
        await ws.send(protoassembler.get_resp_handle_req_failed())
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

