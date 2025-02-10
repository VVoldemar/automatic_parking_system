import asyncio
from asyncio import AbstractEventLoop
import websockets
from websockets import ServerConnection
import logging
from threading import Thread



loop: AbstractEventLoop

class WebSocketHandler(logging.Handler):
    clients: set[ServerConnection] = set()

    def emit(self, record):
        # print(f"sending message to {self.clients}")
        log_entry = self.format(record)
        for client in self.clients:
            loop.create_task(client.send(log_entry))
        # tasks = [self.loop.create_task(client.send(log_entry)) for client in self.clients]
        # for i in tasks:
        #     await i

async def handler(websocket: ServerConnection):
    WebSocketHandler.clients.add(websocket)
    try:
        async for message in websocket:
            logging.info(f"Получено сообщение: {message}")
            await websocket.send(f"Сервер получил: {message}")
    finally:
        WebSocketHandler.clients.remove(websocket)

async def main():
    global loop
    loop = asyncio.get_event_loop()
    async with websockets.serve(handler, "0.0.0.0", 8001):
        await asyncio.Future()

def run() -> Thread:
    t = Thread(target=asyncio.run, args=[main()], daemon=False)
    t.start()
    return t