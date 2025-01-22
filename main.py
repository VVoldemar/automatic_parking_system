from cv2 import VideoCapture, QRCodeDetector
import cv2
from flask import Flask, render_template, Response
# from qreader import QReader
import numpy as np
from numpy.typing import NDArray

# qreader = QReader()

camera_id = 0
camera = VideoCapture(camera_id)

cam_ret, _ = camera.read()
if not cam_ret:
    print("camera bruhnulas")
    exit(228)

detector = QRCodeDetector()

app = Flask(__name__)
# print(__name__)

@app.route("/")
def main_page():
    return render_template("stream.html")

def gen():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        frame.shape = (480, 640, 3)

        # info: dict[str, np.ndarray | float | tuple[float | int, float | int]] = None
        # decoded_str: str | None = None
        # decoded_str, info = qreader.detect_and_decode(frame, True)

        # for text, qr_data in zip(decoded_str, info):
        #     # xyxy = qr_data["bbox_xyxy"]
        #     # xyxy = list(map(int, xyxy))
        #     # xyxy = [np.array([
        #     #     [xyxy[0], xyxy[1]],
        #     #     [xyxy[0], xyxy[2]],
        #     #     [xyxy[1], xyxy[1]],
        #     #     [xyxy[1], xyxy[2]],
        #     # ])]
        #     # polygon_xy = qr_data["polygon_xy"]
        #     padded_quad_xy: NDArray = qr_data["padded_quad_xy"]
        #     center = qr_data["cxcy"]
        #     center = list(map(int, center))

        #     # padded_quad_xy.shape
        #     # print(padded_quad_xy.shape, padded_quad_xy.dtype, padded_quad_xy)
        #     # padded_quad_xy.astype(int)
        #     # print(text, padded_quad_xy, center)
            
        #     if text:
        #         color = (0, 255, 0)
        #         frame = cv2.putText(frame, text, center, cv2.FONT_HERSHEY_SIMPLEX,
        #                             2, color, 2, cv2.LINE_AA)
        #         print(text)
        #     else:
        #         color = (0, 0, 255)

        #     frame = cv2.polylines(frame, [padded_quad_xy.astype(int)], True, color, 4)


        ret_qr, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                if s:
                    print(s)
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                passtypeint = p.astype(int)

                frame = cv2.polylines(frame, [passtypeint], True, color, 4)
                frame = cv2.putText(frame, s, (passtypeint[0][0], passtypeint[0][1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

        # print(frame, type(frame), frame.shape)

        img = cv2.imencode('.jpeg', frame)
        # print(img)

        data = img[1].tobytes()
        yield (b'--frame\r\n'
			   b'Content-Type: image/png\r\n\r\n' + data + b'\r\n')

@app.route("/video_feed")
def video_feed():
	return Response(gen(),
		mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run("0.0.0.0", 80)