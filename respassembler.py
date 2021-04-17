import json


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

def get_resp_create_room(errcode, roomid=0):
    resp = {
        'PROTO': 'RESP_CREATE_ROOM',
        'ERRCODE': errcode,
        'ROOMID': roomid
    }
    return json.dumps(resp)


def get_resp_join_room_as_player(errcode, roomid=0):
    resp = {
        'PROTO': 'RESP_JOIN_ROOM_AS_PLAYER',
        'ERRCODE': errcode,
        'ROOMID': roomid,
    }
    return json.dumps(resp)

def get_resp_join_room_as_viewer(errcode, roomid=0):
    resp = {
        'PROTO': 'RESP_JOIN_ROOM_AS_VIEWER',
        'ERRCODE': errcode,
        'ROOMID': roomid,
    }
    return json.dumps(resp)

def get_resp_quit_room(errcode):
    resp = {
        'PROTO': 'RESP_QUIT_ROOM',
        'ERRCODE': errcode,
    }
    return json.dumps(resp)

def get_resp_heartbeat():
    return '{"PROTO": "RESP_HEARTBEAT"}'

def get_resp_handle_req_failed():
    return '{"PROTO": "RESP_HANDLE_REQ_FAILED"}'