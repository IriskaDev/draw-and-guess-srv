import asyncio
import websockets

async def hello():
    uri = "ws://127.0.0.1:12013"
    async with websockets.connect(uri, ping_interval=10) as ws:
        while True:
            # msg = input('send message: \n')
            msg = 'client2msg'
            await ws.send(msg)
            recvmsg = await ws.recv()
            print ('recv msg: ', recvmsg)
            await asyncio.sleep(5)

        # greeting = input('send greeting:\n')
        # await ws.send(greeting)
        # srvgreeting = await ws.recv()
        # print('greeting from srv: ', srvgreeting)
        # message = input('send message:\n')
        # await ws.send(message)
        # srvmessage = await ws.recv()
        # print('message from srv: ', srvmessage)

async def communicate(ws, msg):
    while True:
        print('send message: ', msg)
        await ws.send(msg)
        await asyncio.sleep(5)

if __name__ == "__main__":
    # url = "ws://127.0.0.1:12013"
    # ws = websockets.connect(url, ping_interval=10)
    # loop = asyncio.get_event_loop()
    # loop.call_later(5, stop)
    # task = loop.create_task(communicate(ws, 'client1msg'))
    # try:
    #     loop.run_until_complete(task)
    # except asyncio.CancelledError:
    #     pass
        # task = loop.create_task(periodi)
    asyncio.get_event_loop().run_until_complete(hello())

    