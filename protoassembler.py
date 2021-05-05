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

def get_resp_roundstart(errcode):
    resp = {
        'PROTO': 'RESP_ROUNDSTART',
        'ERRCODE': errcode,
    }
    return json.dumps(resp)

def get_resp_roundover(errcode):
    resp = {
        'PROTO': 'RESP_ROUNDOVER',
        'ERRCODE': errcode,
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

def get_broadcast_player_joined(c):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_JOINED',
        'PLAYER': c.getinfoobject(),
    }
    return json.dumps(resp)

def get_broadcast_viewer_joined(c):
    resp = {
        'PROTO': 'BROADCAST_VIEWER_JOINED',
        'VIEWER': c.getinfoobject(),
    }
    return json.dumps(resp)

def get_broadcast_player_exit(c):
    resp = {
        'PROTO': 'BROADCAST_PLAYER_EXIT',
        'PLAYER': c.getinfoobject(),
    }
    return json.dumps(resp)

def get_broadcast_viewer_exit(c):
    resp = {
        'PROTO': 'BROADCAST_VIEWER_EXIT',
        'VIEWER': c.getinfoobject(),
    }
    return json.dumps(resp)

def get_broadcast_roundstart():
    resp = {
        'PROTO': 'BROADCAST_ROUNDSTART',
    }
    return json.dumps(resp)

def get_broadcast_roundover(correctlist):
    resp = {
        'PROTO': 'BROADCAST_ROUNDOVER',
        'CORRECTPLAYERS': correctlist,
    }
    return json.dumps(resp)