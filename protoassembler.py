#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

def get_resp_onconnected(id):
    resp = {
        'PROTO': 'RESP_ONCONNECTED',
        'ID': id,
    }
    return json.dumps(resp)

def get_resp_register(errcode):
    resp = {
        'PROTO': 'RESP_REGISTER',
        'ERRCODE': errcode
    }
    return json.dumps(resp)

def get_resp_get_room_list(errcode, rooms):
    resp = None
    if rooms is None:
        resp = {
            'PROTO': 'RESP_GET_ROOM_LIST',
            'ERRCODE': errcode,
        }
    else:
        resp = {
            'PROTO': 'RESP_GET_ROOM_LIST',
            'ERRCODE': errcode,
            'ROOMS': rooms,
        }
    return json.dumps(resp)

def get_resp_create_room(errcode, roominfo):
    resp = {
        'PROTO': 'RESP_CREATE_ROOM',
        'ERRCODE': errcode,
        'ROOMINFO': roominfo,
    }
    return json.dumps(resp)

def get_resp_join_random_room(errcode, roominfo=None):
    resp = {
        'PROTO': 'RESP_JOIN_RANDOM_ROOM',
        'ERRCODE': errcode,
        'ROOMINFO': roominfo
    }
    return json.dumps(resp)


def get_resp_join_room_as_player(errcode, roominfo=None):
    resp = {
        'PROTO': 'RESP_JOIN_ROOM_AS_PLAYER',
        'ERRCODE': errcode,
        'ROOMINFO': roominfo,
    }
    return json.dumps(resp)

def get_resp_join_room_as_viewer(errcode, roominfo=None):
    resp = {
        'PROTO': 'RESP_JOIN_ROOM_AS_VIEWER',
        'ERRCODE': errcode,
        'ROOMINFO': roominfo,
    }
    return json.dumps(resp)

def get_resp_ready_for_play(errcode):
    resp = {
        'PROTO': 'RESP_READY_FOR_PLAY',
        'ERRCODE': errcode
    }
    return json.dumps(resp)

def get_resp_cancel_ready(errcode):
    resp = {
        'PROTO': 'RESP_CANCEL_READY',
        'ERRCODE': errcode
    }
    return json.dumps(resp)

def get_resp_start_round(errcode):
    resp = {
        'PROTO': 'RESP_START_ROUND',
        'ERRCODE': errcode
    }
    return json.dumps(resp)

def get_resp_quit_room(errcode):
    resp = {
        'PROTO': 'RESP_QUIT_ROOM',
        'ERRCODE': errcode,
    }
    return json.dumps(resp)

def get_resp_get_room_player_list(errcode, infolsit):
    resp = {
        'PROTO': 'RESP_GET_ROOM_PLAYER_LIST',
        'ERRCODE': errcode,
        'PLAYERLIST': infolsit,
    }
    return json.dumps(resp)

def get_resp_get_room_viewer_list(errcode, infolist):
    resp = {
        'PROTO': 'RESP_GET_ROOM_VIEWER_LIST',
        'ERRCODE': errcode,
        'VIEWERLIST': infolist,
    }
    return json.dumps(resp)

def get_resp_send_answer(errcode, iscorrect):
    resp = {
        'PROTO': 'RESP_SEND_ANDWER',
        'ERRCODE': errcode,
        'ISCORRECT': iscorrect,
    }
    return json.dumps(resp)

def get_resp_heartbeat():
    return '{"PROTO": "RESP_HEARTBEAT"}'

def get_resp_handle_req_failed():
    return '{"PROTO": "RESP_HANDLE_REQ_FAILED"}'



def get_broadcast_chat(msg):
    resp = {
        'PROTO': 'BORADCAST_CHAT',
        'MSG': msg,
    }
    return json.dumps(resp)

def get_broadcast_player_joined(statinfo):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_JOINED',
        'PLAYERSTAT': statinfo,
    }
    return json.dumps(resp)

def get_broadcast_player_ready(statinfo):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_READY',
        'PLAYERSTAT': statinfo
    }
    return json.dumps(resp)

def get_broadcast_player_cancel_ready(statinfo):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_CANCEL_READY',
        'PLAYERSTAT': statinfo
    }
    return json.dumps(resp)

def get_broadcast_player_exit(c):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_EXIT',
        'PLAYER': c.getinfo(),
    }
    return json.dumps(resp)

def get_broadcast_viewer_joined(c):
    resp = {
        'PROTO': 'BROADCAST_VIEWER_JOINED',
        'VIEWER': c.getinfo(),
    }
    return json.dumps(resp)

def get_broadcast_viewer_exit(c):
    resp = {
        'PROTO': 'BROADCAST_VIEWER_EXIT',
        'VIEWER': c.getinfo(),
    }
    return json.dumps(resp)

def get_broadcast_nextdrawer(drawerstat):
    resp = {
        'PROTO': 'BROADCAST_NEXTDRAWER',
        'DRAWERSTAT': drawerstat,
    }
    return json.dumps(resp)

def get_broadcast_roundstart(roundinfo):
    resp = {
        'PROTO': 'BROADCAST_ROUNDSTART',
        'ROUNDINFO': roundinfo
    }
    return json.dumps(resp)

def get_broadcast_roundover(correctlist, answer):
    resp = {
        'PROTO': 'BROADCAST_ROUNDOVER',
        'CORRECTPLAYERSTATS': correctlist,
        'ANSWER': answer
        # 'NEXTDRAWERSTAT': nextdrawerstat
    }
    return json.dumps(resp)

def get_broadcast_answer_correct(playerinfo):
    resp = {
        'PROTO': 'BROADCAST_ANSWER_CORRECT',
        'PLAYER': playerinfo
    }
    return json.dumps(resp)

def get_broadcast_answer_wrong(playerinfo, answer):
    resp = {
        'PROTO': 'BROADCAST_ANSWER_WRONG',
        'PLAYER': playerinfo,
        'ANSWER': answer
    }
    return json.dumps(resp)

def get_broadcast_player_stat_update(playerstats):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_STAT_UPDATE',
        'PLAYERSTATS': playerstats
    }
    return json.dumps(resp)

def get_broadcast_match_over(rank):
    resp = {
        'PROTO': 'BROADCAST_MATCH_OVER',
        'RANK': rank
    }
    return json.dumps(resp)

# notifys
def get_notify_round_answer(answer):
    resp = {
        'PROTO': 'NOTIFY_ROUND_ANSWER',
        'ANSWER': answer
    }
    return json.dumps(resp)


