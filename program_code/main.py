from threading import Thread
from program_code.Camera import Camera
from WebServer import start_web_server
from MQTTServer import MQTTServer
from program_code.Core import Core
from program_code.LiftController import LiftController
from WebSockets import WebSocketHandler
from time import sleep

import logging
import WebSockets
import os

def main():
    camera: Camera | None = None
    server: MQTTServer | None = None
    lift: LiftController | None = None
    flask_thread: Thread | None = None
    core: Core | None = None
    web_socket: Thread |  None = None

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)

    ws_handler = WebSocketHandler()
    ws_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(formatter)
    ws_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(ws_handler)
    logger.addHandler(console_handler)

    logging.info("starting...")

    try:
        camera = Camera()
        server = MQTTServer()
        lift = LiftController()

        core = Core(camera, lift, server)
        flask_thread = start_web_server(camera, core)

        web_socket = WebSockets.run()

        logging.info("Application started")
        core.thread.join()
    finally:
        logging.info("Application stopping")
        if camera:
            camera.clean_up()
        if lift:
            lift.clean_up()
        if server:
            server._client.disconnect()
        logging.info("Application stopped")

        sleep(1)
        os.system(f"kill {os.getpid()}")
    

if __name__ == "__main__":
    main()
