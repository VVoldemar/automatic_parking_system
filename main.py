from Camera import Camera
from WebServer import start_web_server


def main():
    camera = Camera()
    flask_thread = start_web_server(camera)
    flask_thread.join()


if __name__ == "__main__":
    main()