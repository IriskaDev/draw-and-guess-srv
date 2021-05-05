
# STRUCT

### CLIENTINFO
``` json
{
    "ID": identifier,
    "NAME": name,
    "ICON": head icon,
}
```

### ROOMINFO
``` json
{
    "ID": identifier,
    "NAME": roomname,
    "HOST": CLIENTINFO of host,
    "PLAYERCOUNT": player num,
    "VIEWERCOUNT": viewer num,
    "MAXPLAYER": max player of this room,
    "MAXVIEWER": max viewer of this room,
    "NEEDPWD": is password needed,
}
```


# REQ <---> RESP

### 连接后
* RESP
``` json
{
    "PROTO": "RESP_ONCONNECTED",
    "ID": identifier,
}
```

### 注册
* REQ
``` json
{
    "PROTO": "REQ_REGISTER",
    "NAME": player nick name,
    "ICON": player head icon,
}
```
* RESP
``` json
{
    "PROTO": "RESP_REGISTER",
    "ERRCODE": error code,
}
```

### 获取房间列表
* REQ
``` json
{
    "PROTO": "REQ_GET_ROOM_LIST",
}
```
* RESP
``` json
{
    "PROTO": "RESP_GET_ROOM_LIST",
    "ERRCODE": error code,
    "ROOMS": [
        ROOMINFO, 
        ...
    ]
}
```

### 创建房间
* REQ
``` json
{
    "PROTO": "REQ_CREATE_ROOM",
    "NAME": room name,
    "PWD": password if needed,
}
```
* RESP
``` json
{
    "PROTO": "RESP_CREATE_ROOM",
    "ERRCODE": error code,
    "ROOMINFO": ROOMINFO,
}
```

### 以玩家身份进入房间
* REQ
``` json
{
    "PROTO": "REQ_JOIN_ROOM_AS_PLAYER",
    "ROOMID": room id,
    "PWD": password if needed,
}
```
* RESP
``` json
{
    "PROTO": "RESP_JOIN_ROOM_AS_PLAYER",
    "ERRCODE": error code,
    "ROOMINFO": ROOMINFO,
}
```

### 以观众身份进入房间
* REQ
``` json
{
    "PROTO": "REQ_JOIN_ROOM_AS_VIEWER",
    "ROOMID": room id,
    "PWD": password if needed,
}
```
* RESP
``` json
{
    "PROTO": "RESP_JOIN_ROOM_AS_VIEWER",
    "ERRCODE": error code,
    "ROOMINFO": ROOMINFO
}
```

### 退出房间
* REQ
``` json
{
    "PROTO": "REQ_QUIT_ROOM",
}
```
* RESP
``` json
{
    "PROTO": "RESP_QUIT_ROOM",
    "ERRCODE": error code,
}
```

### 获取房间玩家信息列表
* REQ
``` json
{
    "PROTO": "REQ_GET_ROOM_PLAYER_LIST",
}
```
* RESP
``` json
{
    "PROTO": "RESP_GET_ROOM_PLAYER_LIST",
    "ERRCODE": error code,
    "PLAYERLIST": [
        CLIENTINFO,
        ...
    ]
}
```

### 获取房间观众信息列表
* REQ
``` json
{
    "PROTO": "REQ_GET_ROOM_VIEWER_LIST",
}
```
* RESP
``` json
{
    "PROTO": "RESP_GET_ROOM_VIEWER_LIST",
    "ERRCODE": error code,
    "VIEWERLIST": [
        CLIENTINFO,
        ...
    ]
}
```

### 发送聊天信息
* REQ
``` json
{
    "PROTO": "REQ_SEND_CHAT",
    "MSG": chat message,
}
```
* RESP
``` json
no response
```


### 发送答案
* REQ
``` json
{
    "PROTO": "REQ_SEND_ANSWER",
    "ANSWER": answer,
}
```
* RESP
``` json
{
    "PROTO": "RESP_SEND_ANSWER",
    "ERRCODE": error code,
    "ISCORRECT": is answer correct,
}
```

### 开始一轮游戏
* REQ
``` json
{
    "PROTO": "REQ_ROUND_START",
    "ANSWER": answer to this round,
}
```
* RESP
``` json
{
    "PROTO": "RESP_ROUND_START",
    "ERRCODE": error code,
}
```

### 结束一轮游戏
* REQ
``` json
{
    "PROTO": "REQ_ROUND_OVER",
}
```
* RESP
``` json
{
    "PROTO": "RESP_ROUND_OVER",
    "ERRCODE": error code,
}
```

### 绘画
* REQ
``` json
undefined
```
* RESP
``` json
undefined
```

### 心跳
* REQ
``` json
{
    "PROTO": "REQ_HEARTBEAT",
}
```
* RESP
``` json
{
    "PROTO": "RESP_HEARTBEAT",
}
```

### 通用
#### 请求处理失败
* RESP
``` json
{
    "PROTO": "RESP_HANDLE_REQ_FAILED"
}
```


# BROADCAST

## 房间内广播
### 聊天信息广播
``` json
{
    "PROTO": "BROADCAST_CHAT",
    "MSG": chat message,
}
```

### 玩家进房广播
``` json
{
    "PROTO": "BROADCAST_PLAYER_JOINED",
    "PLAYER": CLIENTINFO,
}
```

### 观众进房广播
``` json
{
    "PROTO": "BROADCAST_VIEWER_JOINED",
    "VIEWER": CLIENTINFO,
}
```

### 玩家退房广播
``` json
{
    "PROTO": "BROADCAST_PLAYER_EXIT",
    "PLAYER": CLIENTINFO,
}
```

### 观众退房广播
``` json
{
    "PROTO": "BROADCAST_VIEWER_EXIT",
    "VIEWER": CLIENTINFO,
}
```

### 一轮游戏开始广播
``` json
{
    "PROTO": "BROADCAST_ROUNDSTART",
}
```

### 一轮游戏结束广播
``` json
{
    "PROTO": "BROADCAST_ROUNDOVER",
    "CORRECTPLAYERS": [
        CLIENTINFO, ...  // sorted by tm that player sent his correct answer
    ]
}
```

