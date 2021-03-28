import asyncio
import websockets

async def hello():
    uri = "ws://127.0.0.1:12013"
    async with websockets.connect(uri) as ws:
        greeting = input('send greeting')
        await ws.send(greeting)
        srvgreeting = await ws.recv()
        print('greeting from srv: ', srvgreeting)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(hello())

    