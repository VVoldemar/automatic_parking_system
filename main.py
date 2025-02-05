from pickle import NONE
from threading import Thread
from Camera import Camera
from WebServer import start_web_server
from MQTTServer import MQTTServer
from Core import Core
from LiftController import LiftController


def main():
    camera: Camera | None = None
    server: MQTTServer | None = None
    lift: LiftController | None = None
    flask_thread: Thread | None = None
    core: Core | None = None
    try:
        camera = Camera()
        flask_thread = start_web_server(camera)

        server = MQTTServer()
        lift = LiftController()

        core = Core(camera, lift, server)

        print("started")
        flask_thread.join()
    finally:
        print("stopping")
        if camera:
            camera.clean_up()
        if lift:
            lift.clean_up()
        if server:
            server._client.disconnect()



if __name__ == "__main__":
    main()