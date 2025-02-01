from Camera import Camera
from WebServer import start_web_server
from MQTTServer import MQTTServer
from Core import Core
from LiftController import LiftController


def main():
    camera = Camera()
    flask_thread = start_web_server(camera)

    server = MQTTServer()

    lift = LiftController()
    core = Core(camera, lift, server)

    flask_thread.join()
    server._client.disconnect()


if __name__ == "__main__":
    main()