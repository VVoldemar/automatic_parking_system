from threading import Thread
from Camera import Camera
from flask import Flask, render_template, Response, request, send_from_directory
from typing import Any, Union
from time import time, sleep
from WebSockets import WebSocketHandler
import WebSockets
import logging
import sys

def start_web_server(camera: Union[Camera, None] = None, core_hint: Any = None) -> Union[Thread, None]:
    app = Flask(__name__)

    if sys.platform == "linux":
        from Core import Core
        if not isinstance(core_hint, Core):
            return None
        core: Core = core_hint

        @app.route("/api/move_vertical")
        def move_vertical():
            steps = request.args.get("steps", type=int)
            if steps == None:
                return app.response_class(status=401)
            tasks = [motor.run_go_steps(steps) for motor in core.lift.vertical_motors]
            for i in tasks:
                i.join()
            return app.response_class(status=200)
        
        @app.route("/api/rotate")
        def rotate():
            steps = request.args.get("steps", type=int)
            if steps == None:
                return app.response_class(status=401)
            core.lift.horizontal_motor.go_steps(steps)
            return app.response_class(status=200)
    
        @app.route("/api/shutdown")
        def shutdown():
            core.should_shutdown = True
    
        @app.route("/api/activate")
        def activate():
            core.is_active = True
            core.camera.last_detection = None
            return app.response_class(status=200)
        
        @app.route("/api/deactivate")
        def deactivate():
            core.is_active = False
            return app.response_class(status=200)

    if not camera:
        camera = Camera()

    def start():
        app.run("0.0.0.0", 80)

    @app.route('/', defaults={'path': 'index.html'})
    @app.route("/<path:path>")
    def main_page(path):
        return send_from_directory("web", path)

    @app.route("/stream")
    def camera_page():
        return render_template("stream.html")

    def gen():
        while True:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n')


    @app.route("/video_feed")
    def video_feed():
        return Response(gen(),
            mimetype="multipart/x-mixed-replace; boundary=frame")

    flask_thread = Thread(target=start)
    flask_thread.start()

    logging.info("Web server started")
    return flask_thread

if __name__ == "__main__":
    def run_test_log_spam():

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        ws_handler = WebSocketHandler()
        ws_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(message)s', datefmt='%H:%M:%S')
        ws_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        
        logger.addHandler(ws_handler)
        logger.addHandler(console_handler)

        while True:
            logging.info(time())
            sleep(2)


    t = start_web_server()
    WebSockets.run()
    Thread(target=run_test_log_spam).start()

    if t:
        t.join()