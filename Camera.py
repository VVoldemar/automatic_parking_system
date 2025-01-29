from cv2 import VideoCapture, QRCodeDetector
import cv2
from threading import Thread
from time import sleep


class Camera:
    camera: VideoCapture
    detector = QRCodeDetector()

    thread: Thread

    last_img: bytes
    last_detection: str

    def __init__(self, camera_id = 0):
        self.camera = VideoCapture(camera_id)

        cam_ret, _ = self.camera.read()
        if not cam_ret:
            print("camera bruhnulas")
            exit(228)

        self.thread = Thread(target=self.capture)
        self.thread.start()

    def capture(self):
        while True:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                frame.shape = (480, 640, 3)

                ret_qr, decoded_info, points, _ = self.detector.detectAndDecodeMulti(frame)
                if ret_qr:
                    for s, p in zip(decoded_info, points):
                        if s:
                            print(s)
                            color = (0, 255, 0)
                            self.last_detection = s
                        else:
                            color = (0, 0, 255)
                        passtypeint = p.astype(int)

                        frame = cv2.polylines(frame, [passtypeint], True, color, 4)
                        frame = cv2.putText(frame, s, (passtypeint[0][0], passtypeint[0][1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

                img = cv2.imencode('.jpeg', frame)
                data = img[1].tobytes()

                if data != None:
                        self.last_img = data

                sleep(0.1)
                

            except Exception as e:
                print("An exception occured:", e)

    def get_frame(self) -> bytes:
        # print("waiting for frame")
        while not self.last_img:
            sleep(0.005)
        # print("done")

        ret = self.last_img
        self.last_img = None
        return ret
    
    def get_detection(self) -> str:
        # print("waiting for detection")
        while not self.last_detection:
            sleep(0.005)
        # print("done")

        ret = self.last_detection
        self.last_detection = None
        return ret