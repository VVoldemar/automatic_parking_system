from Camera import Camera
from WebServer import start_web_server
from SocketServer import SocketServer

from MQTTServer import MQTTServer


def main():
    camera = Camera()
    flask_thread = start_web_server(camera)

    server = MQTTServer()

    flask_thread.join()
    server._client.disconnect()


if __name__ == "__main__":
    main()