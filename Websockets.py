import asyncio
import websockets
import logging

class WebSocketHandler(logging.Handler):
    clients = set()

    def emit(self, record):
        log_entry = self.format(record)
        for client in self.clients:
            asyncio.create_task(client.send(log_entry))

async def handler(websocket):
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
