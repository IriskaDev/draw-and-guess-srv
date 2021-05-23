#!/usr/bin/env python
# -*- coding: utf-8 -*-

import builtins
import sys
import asyncio
import websockets
import json
import math
import time
import protoassembler
from configmgr import configmgr
from room import room
from client import client
from roommgr import roommgr
from clientmgr import clientmgr

# ws - client
CLIENTS = dict()
# NAMES = set()

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
                    await processroundover(r)

                if r.isempty():
                    roommgr().removeroom(r.id)

    del CLIENTS[ws]

async def broadcastmsg(clientlist, msg):
    for c in clientlist:
        try:
            await c.ws.send(msg)
        except websockets.exceptions.ConnectionClosed:
            ondisconnected(c.ws, False)
        except:
            print('error: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])

async def processroundover(r):
    r.roundover()
    clist = r.getbroadcastclientlist()
    await broadcastmsg(clist, protoassembler.get_broadcast_roundover(r.getroundcorrectplayerstatlist(), r.answer))
    if not r.isinmatch():
        await broadcastmsg(clist, protoassembler.get_broadcast_match_over(r.getrankinfo()))
    else:
        await broadcastmsg(clist, protoassembler.get_broadcast_nextdrawer(r.getdrawerstat().getinfo()))
        drawerstat = r.getdrawerstat()
        answer = r.getanswer()
        try:
            await drawerstat.player.ws.send(protoassembler.get_notify_round_answer(answer))
        except websockets.exceptions.connectionclosed:
            print('error: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])
            ondisconnected(drawerstat.player.ws, True)
            await processroundover(r)
        except:
            print('error: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])
            await processroundover(r)


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
    
    if 'ICON' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(2, None))
        return

    ricon = req['ICON']
    if type(ricon) is not str:
        await c.ws.send(protoassembler.get_resp_create_room(2, None))
        return
    
    if 'MAXPLAYERS' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(3, None))
        return

    maxplayers = req['MAXPLAYERS']
    if type(maxplayers) is not int and type(maxplayers) is not float:
        await c.ws.send(protoassembler.get_resp_create_room(3, None))
        return
    maxplayers = int(maxplayers)

    if 'MATCHOVERSCORE' not in req:
        await c.ws.send(protoassembler.get_resp_create_room(4, None))
        return
    
    matchoverscore = req['MATCHOVERSCORE']
    if type(matchoverscore) is not int and type(matchoverscore) is not float:
        await c.ws.send(protoassembler.get_resp_create_room(4, None))
        return
    matchoverscore = int(matchoverscore)
    

    if c.room is not None:
        await c.ws.send(protoassembler.get_resp_create_room(5, None))
        return
    
    r = None
    if 'PWD' in req:
        r = roommgr().createroom(rname, ricon, maxplayers, matchoverscore, req['PWD'])
    else:
        r = roommgr().createroom(rname, ricon, maxplayers, matchoverscore, None)

    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_create_room(0, r.getroombriefinfo()))

async def joinrandomroom(c, req):
    if c.room is not None and roommgr().roomexists(c.room):
        await c.ws.send(protoassembler.get_resp_join_random_room(1))
        return
    r = roommgr().getjoinalbleroom()
    if r is None:
        await c.ws.send(protoassembler.get_resp_join_random_room(2))
        return
    l = r.getbroadcastclientlist()
    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_join_random_room(0, r.getroominfo()))
    await broadcastmsg(l, protoassembler.get_broadcast_player_joined(r.getplayerstat(c).getinfo()))

async def joinroom_asplayer(c, req):
    if c.room is not None and roommgr().roomexists(c.room):
        await c.ws.send(protoassembler.get_resp_join_room_as_player(8))
        return

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
    
    if r.isinmatch():
        await c.ws.send(protoassembler.get_resp_join_room_as_player(6, None))
        return
    
    if r.isplayerfull():
        await c.ws.send(protoassembler.get_resp_join_room_as_player(7, None))
        return
    
    l = r.getbroadcastclientlist()
    r.joinasplayer(c)
    await c.ws.send(protoassembler.get_resp_join_room_as_player(0, r.getroominfo()))
    await broadcastmsg(l, protoassembler.get_broadcast_player_joined(r.getplayerstat(c).getinfo()))

async def joinroom_asviewer(c, req):
    if c.room is not None and roommgr().roomexists(c.room):
        await c.ws.send(protoassembler.get_resp_join_room_as_viewer(6))
        return

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
    
    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_ready_for_play(3))
        return
    
    if r.clientisviewer(c):
        await c.ws.send(protoassembler.get_resp_ready_for_play(4))
        return
    
    if r.isinmatch():
        await c.ws.send(protoassembler.get_resp_ready_for_play(5))
        return
    
    r.setplayerready(c, True)
    await c.ws.send(protoassembler.get_resp_ready_for_play(0))
    l = r.getbroadcastclientlist()
    await broadcastmsg(l, protoassembler.get_broadcast_player_ready(r.getplayerstat(c).getinfo()))
    if r.playercount() >= configmgr().getminplayers() and r.isallready():
        r.gennewquestion()
        r.matchstart()
        await broadcastmsg(l, protoassembler.get_broadcast_nextdrawer(r.getdrawerstat().getinfo()))

        drawerstat = r.getdrawerstat()
        answer = r.getanswer()
        try:
            await drawerstat.player.ws.send(protoassembler.get_notify_round_answer(answer))
        except websockets.exceptions.connectionclosed:
            print('error: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])
            ondisconnected(drawerstat.player.ws, True)
            await processroundover(r)
        except:
            print('error: \n', sys.exc_info()[0], '\n', sys.exc_info()[1])
            await processroundover(r)

async def oncancelready(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_cancel_ready(1))
        return

    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_cancel_ready(2))
        return
    
    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_cancel_ready(3))
        return
    
    if r.clientisviewer(c):
        await c.ws.send(protoassembler.get_resp_cancel_ready(4))
        return
    
    if r.isinmatch():
        await c.ws.send(protoassembler.get_resp_cancel_ready(5))
        return
    
    r.setplayerready(c, False)
    await c.ws.send(protoassembler.get_resp_cancel_ready(0))
    l = r.getbroadcastclientlist()
    await broadcastmsg(l, protoassembler.get_broadcast_player_cancel_ready(r.getplayerstat(c).getinfo()))
    

async def startround(c, req):
    if c.room is None:
        await c.ws.send(protoassembler.get_resp_start_round(1))
        return

    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_start_round(2))
        return

    r = roommgr().getroom(c.room)
    if not r.clientinroom(c):
        c.room = None
        await c.ws.send(protoassembler.get_resp_start_round(3))
        return
    
    isviewer = r.clientisviewer(c)
    isdrawer = r.clientisdrawer(c)
    if isviewer or not isdrawer:
        await c.ws.send(protoassembler.get_resp_start_round(4))
        return
    
    if r.isinround():
        await c.ws.send(protoassembler.get_resp_start_round(5))
        return
    
    if not r.isinmatch():
        await c.ws.send(protoassembler.get_resp_start_round(6))
        return
    
    if not r.isallready():
        await c.ws.send(protoassembler.get_resp_start_round(7))
        return
    
    r.roundstart()
    await c.ws.send(protoassembler.get_resp_start_round(0))
    l = r.getbroadcastclientlist()
    await broadcastmsg(l, protoassembler.get_broadcast_roundstart(r.getcurrentroundinfo()))


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
        await processroundover(r)

    if r.isempty():
        roommgr().removeroom(r.id)

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
        await c.ws.send(protoassembler.get_resp_send_answer(1, False))
        return

    if not roommgr().roomexists(c.room):
        c.room = None
        await c.ws.send(protoassembler.get_resp_send_answer(2, False))
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
        playerstat = r.getplayerstat(c)
        drawerstat = r.getdrawerstat()
        await c.ws.send(protoassembler.get_resp_send_answer(0, True))
        await broadcastmsg(l, protoassembler.get_broadcast_answer_correct(c.getinfo()))
        await broadcastmsg(l, protoassembler.get_broadcast_player_stat_update([playerstat.getinfo(), drawerstat.getinfo()]))
        if r.isallplayercorrect():
            await processroundover(r)

async def draw(c, req):
    pass

async def heartbeat(c, req):
    await c.ws.send(protoassembler.get_resp_heartbeat())

HANDLERS = {
    'REQ_REGISTER':             onregister,
    'REQ_GET_ROOM_LIST':        getroomlist,
    'REQ_CREATE_ROOM':          oncreateroom,
    'REQ_JOIN_RANDOM_ROOM':     joinrandomroom,
    'REQ_JOIN_ROOM_AS_PLAYER':  joinroom_asplayer,
    'REQ_JOIN_ROOM_AS_VIEWER':  joinroom_asviewer,
    'REQ_READY_FOR_PLAY':       onreadyforplay,
    'REQ_CANCEL_READY':         oncancelready,
    'REQ_START_ROUND':          startround,
    'REQ_QUIT_ROOM':            quitroom,
    'REQ_SEND_CHAT':            send_chat,
    'REQ_SEND_ANSWER':          send_answer,
    'REQ_DRAW':                 draw,

    'REQ_HEARTBEAT':            heartbeat,
}

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

async def update(tickcount, tm):
    # print (tickcount, tm)
    l = roommgr().update(tickcount, tm)
    for r in l:
        await processroundover(r)



async def ticker(delay):
    i = 0
    while True:
        yield i
        await asyncio.sleep(delay)
        i += 1

async def runticker():
    async for i in ticker(configmgr().gettickinterval()):
        tm = time.time()
        await update(i, tm)

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
