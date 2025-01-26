from threading import Thread
from Camera import Camera
from flask import Flask, render_template, Response, request
import os

def start_web_server(camera: Camera = None) -> Thread:
    if not camera:
        camera = Camera()

    app = Flask(__name__)

    def start():
        app.run("0.0.0.0", 80)

    @app.route("/")
    def main_page():
        return render_template("stream.html")

    def gen():
        while True:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n')

    @app.route("/video_feed")
    def video_feed():
        return Response(gen(),
            mimetype="multipart/x-mixed-replace; boundary=frame")
    
    @app.route("/shutdown")
    def shutdown():
        f = request.environ.get('werkzeug.server.shutdown')
        if not f:
            os._exit(0)
            
        f()

    flask_thread = Thread(target=start)
    flask_thread.start()

    return flask_thread