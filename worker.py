#!/usr/bin/env python

import sys
import asyncio
import websockets
import json
import math
import time
import protoassembler
from configmgr import configmgr
from singleton import singleton
from room import room
from client import client
from roommgr import roommgr
from clientmgr import clientmgr

# ws - client
CLIENTS = dict()
# NAMES = set()

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

    c.name = req['NAME']
    c.icon = req['ICON']
    await c.ws.send(protoassembler.get_resp_register(0))

async def getroomlist(c, req):
    infolist = roommgr().getsortedroomlist()
    await c.ws.send(protoassembler.get_resp_get_room_list(0, infolist))

async def oncreateroom(c, req):
    if 'NAME' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(1, None))
        return
    rname = req['NAME']
    if type(rname) is not str:
        await c.ws.send(protoassembler.get_resp_create_room(1, None))
        return
    
    if 'MAXPLAYERS' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(2, None))
        return

    maxplayers = req['MAXPLAYERS']
    if type(maxplayers) is not int and type(maxplayers) is not float:
        await c.ws.send(protoassembler.get_resp_create_room(2, None))
        return
    maxplayers = int(maxplayers)

    if 'MAXSCORE' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(3, None))
        return
    
    maxscore = req['MAXSCORE']
    if type(maxscore) is not int and type(maxscore) is not float:
        await c.ws.send(protoassembler.get_resp_create_room(3, None))
        return
    maxscore = int(maxscore)
    

    if c.room is not None:
        await c.ws.send(protoassembler.get_resp_create_room(4, None))
        return
    
    r = None
    if 'PWD' in req:
        r = roommgr().createroom(rname, maxplayers, maxscore, req['PWD'])
    else:
        r = roommgr().createroom(rname, maxplayers, maxscore, None)

    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_create_room(0, r.getroombriefinfo()))


async def joinroom_asplayer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(protoassembler.get_resp_join_room_as_player(1, None))
        return
    roomid = req['ROOMID']
    if not roommgr().roomexists(roomid):
        await c.ws.send(protoassembler.get_resp_join_room_as_player(2, None))
        return
    r = roommgr().getroom(roomid)
    if r.isplayerfull():
        await c.ws.send(protoassembler.get_resp_join_room_as_player(3, None))
        return

    if r.clientinroom(c):
        await c.ws.send(protoassembler.get_resp_join_room_as_player(4, None))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(protoassembler.get_resp_join_room_as_player(5, None))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(protoassembler.get_resp_join_room_as_player(5, None))
            return
    
    l = r.getbroadcastclientlist()
    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_join_room_as_player(0, r.getroominfo()))
    await broadcastmsg(l, protoassembler.get_broadcast_player_joined(r.getplayerstat(c).getinfo()))

async def joinroom_asviewer(c, req):
    if 'ROOMID' not in req:
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(1, None))
        return
    roomid = req['ROOMID']
    if not roommgr().roomexists(roomid):
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(2, None))
        return
    r = roommgr().getroom(roomid)
    if r.isviewerfull():
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(3, None))
        return
    if r.clientinroom(c):
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(4, None))
        return
    
    if r.pwd is not None:
        if 'PWD' not in req:
            await c.ws.send(protoassembler.get_resp_join_room_as_viewer(5, None))
            return
        pwd = req['PWD']
        if pwd != r.pwd:
            await c.ws.send(protoassembler.get_resp_join_room_as_viewer(5, None))
            return
    
    l = r.getbroadcastclientlist()
    r.joinasviewer(c)
    await c.ws.send(protoassembler.get_resp_join_room_as_viewer(0, r.getroominfo()))
    await broadcastmsg(l, protoassembler.get_broadcast_viewer_joined(c))

async def onreadyforplay(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_ready_for_play(1))
        return
    
    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_ready_for_play(2))
        return
    
    r = roommgr.getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_ready_for_play(3))
        return
    
    if r.clientisviewer(c):
        await c.ws.send(protoassembler.get_resp_ready_for_play(4))
        return
    
    allready = r.setplayerready(c)
    l = r.getbroadcastclientlist()
    await broadcastmsg(l, protoassembler.get_broadcast_player_ready(r.getplayerstat().getinfo()))
    if allready:
        # allready means roundstarted
        # broadcast roundstart
        # tell the drawer what answer is
        broadcastmsg(l, protoassembler.get_broadcast_roundstart(r.getcurrentroundinfo()))
        drawer = r.getdrawer()
        answer = r.getanswer()
        try:
            drawer.ws.send(protoassembler.get_notify_round_answer(answer))
        except:
            # if any thing wrong, should stop round
            pass


async def quitroom(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_quit_room(1))
        return
    
    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_quit_room(2))
        return
    
    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_quit_room(1))
        return
    
    isviewer = r.clientisviewer(c)
    isdrawer = r.clientisdrawer(c)
    r.quitroom(c)
    await c.ws.send(protoassembler.get_resp_quit_room(0))
    if isviewer:
        await broadcastmsg(r.getbroadcastclientlist(), protoassembler.get_broadcast_viewer_exit(c))
    else:
        await broadcastmsg(r.getbroadcastclientlist(), protoassembler.get_broadcast_player_exit(c))

    if isdrawer and r.isinround():
        # should stop round
        r.roundover()
        # broadcast things

    if r.isempty():
        # remove room
        roommgr().removeroom(r.id)


async def get_room_player_list(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_get_room_player_list(1, None))
        return
    
    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_player_list(2, None))
        return

    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_player_list(3, None))
        return
    
    await c.ws.send(protoassembler.get_resp_get_room_player_list(0, r.getplayerinfolist()))
    
async def get_room_viewer_list(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(1, None))
        return
    
    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(2, None))
        return
    
    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_get_room_viewer_list(3, None))
        return
    
    await c.ws.send(protoassembler.get_resp_get_room_viewer_list(0, r.getviewerinfolist()))

async def send_chat(c, req):
    if c.room is None:
        return

    if not roommgr().roomexists(c.room):
        return

    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        return
    
    msg = req['MSG']
    if type(msg) is not str:
        return
    if len(msg) <= 0:
        return
    
    await broadcastmsg(r.getbroadcastclientlist(), msg)
    

async def send_answer(c, req):
    if c.room is None:
        c.ws.send(protoassembler.get_resp_send_answer(1, False))
        return

    if not roommgr().roomexists(c.room):
        c.room = None
        c.ws.send(protoassembler.get_resp_send_answer(2, False))
        return
    
    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_send_answer(3, False))
        return

    if r.clientisviewer(c):
        await c.ws.send(protoassembler.get_resp_send_answer(4, False))
        return
    
    if r.clientisdrawer(c):
        await c.ws.send(protoassembler.get_resp_send_answer(5, False))
        return
    
    if not r.isinround():
        await c.ws.send(protoassembler.get_resp_send_answer(6, False))
        return
    
    if r.answer is None:
        await c.ws.send(protoassembler.get_resp_send_answer(7, False))
        return

    answer = req['ANSWER']
    l = r.getbroadcastclientlist()
    if answer != r.answer:
        await c.ws.send(protoassembler.get_resp_send_answer(0, False))
        await broadcastmsg(l, protoassembler.get_broadcast_answer_wrong(c.getinfo(), answer))
    else:
        r.playeranswercorrect(c)
        await c.ws.send(protoassembler.get_resp_send_answer(0, True))
        await broadcastmsg(l, protoassembler.get_broadcast_answer_correct(c.getinfo()))

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
    'REQ_READY_FOR_PLAY':       onreadyforplay,
    'REQ_QUIT_ROOM':            quitroom,
    'REQ_GET_ROOM_PLAYER_LIST': get_room_player_list,
    'REQ_GET_ROOM_VIEWER_LIST': get_room_viewer_list,
    'REQ_SEND_CHAT':            send_chat,
    'REQ_SEND_ANSWER':          send_answer,
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
    if quitroom:
        if c.room is not None:
            if roommgr().roomexists(c.room):
                r = roommgr().getroom(c.room)
                isviewer = r.clientisviewer(c)
                isdrawer = r.clientisdrawer(c)
                r.quitroom(c)
                if isviewer:
                    await broadcastmsg(r.getbroadcastclientlist(), protoassembler.get_broadcast_viewer_exit(c))
                else:
                    await broadcastmsg(r.getbroadcastclientlist(), protoassembler.get_broadcast_player_exit(c))

                if isdrawer and r.isinround():
                    r.roundover()
                    # boradcast

                if r.isempty():
                    roommgr().removeroom(r.id)

    del CLIENTS[ws]

async def onmessage(ws, msg):
    print(ws, msg)
    try:
        c = CLIENTS[ws]
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


async def handler(ws, _):
    await onconnected(ws)
    try:
        while True:
            msg = await ws.recv()
            await onmessage(ws, msg)
    finally:
        await ondisconnected(ws)

def update(tickcount, tm):
    # print ("tick ", tickcount, tm)
    pass

async def ticker(delay):
    i = 0
    while True:
        yield i
        await asyncio.sleep(delay)
        i += 1

async def runticker():
    async for i in ticker(configmgr().gettickinterval()):
        tm = time.time()
        update(i, tm)

def start():
    port = int(configmgr().getport())
    ip = configmgr().getip()
    print (ip, port)
    srv = websockets.serve(handler, ip, port=port, ping_interval=10, compression=None)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        srv
    )
    loop.run_until_complete(
        runticker()
    )
    loop.run_forever()
