import asyncio
import websockets
from websockets import ServerConnection
import logging
from threading import Thread

class WebSocketHandler(logging.Handler):
    clients: set[ServerConnection] = set()
    loop = asyncio.new_event_loop()

    def emit(self, record):
        print("sending message")
        log_entry = self.format(record)
        # for client in self.clients:
        #     self.loop.create_task(client.send(log_entry))
        tasks = [self.loop.create_task(client.send(log_entry)) for client in self.clients]
        for i in tasks:
            await i

async def handler(websocket: ServerConnection):
    WebSocketHandler.clients.add(websocket)
    try:
        async for message in websocket:
            logging.info(f"Получено сообщение: {message}")
            await websocket.send(f"Сервер получил: {message}")
    finally:
        WebSocketHandler.clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8001):
        await asyncio.Future()

def run() -> Thread:
    t = Thread(target=asyncio.run, args=[main()])
    t.start()
    return t