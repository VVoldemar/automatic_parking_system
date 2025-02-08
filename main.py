from threading import Thread
from Camera import Camera
from WebServer import start_web_server
from MQTTServer import MQTTServer
from Core import Core
from LiftController import LiftController
from Websockets import WebSocketHandler

import asyncio
import logging
import Websockets

def main():
    camera: Camera | None = None
    server: MQTTServer | None = None
    lift: LiftController | None = None
    flask_thread: Thread | None = None
    core: Core | None = None

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)

    ws_handler = WebSocketHandler()
    ws_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(formatter)
    ws_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(ws_handler)
    logger.addHandler(console_handler)

    try:
        camera = Camera()
        flask_thread = start_web_server(camera)

        server = MQTTServer()
        lift = LiftController()

        core = Core(camera, lift, server)

        logging.info("Application started")
        flask_thread.join()
    finally:
        logging.info("Application stopping")
        if camera:
            camera.clean_up()
        if lift:
            lift.clean_up()
        if server:
            server._client.disconnect()
        logging.info("Application stopped")

if __name__ == "__main__":
    asyncio.run(Websockets.main())
    main()
