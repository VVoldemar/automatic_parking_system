import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print(f"Получено сообщение: {message}")
        await websocket.send(f"Сервер получил: {message}")

async def main():
    async with websockets.serve(handler, "localhost", 8001):
        await asyncio.Future()

asyncio.run(main())
