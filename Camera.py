from cv2 import VideoCapture, QRCodeDetector
import cv2
from threading import Thread
from time import sleep
from typing import Union
import logging

class Camera:
    camera: VideoCapture
    detector = QRCodeDetector()

    thread: Thread

    last_img: Union[bytes, None]
    last_detection: Union[str, None]

    def __init__(self, camera_id = 0):
        self.camera = VideoCapture(camera_id)

        cam_ret, _ = self.camera.read()
        if not cam_ret:
            logging.error("Camera initialization failed")
            exit(228)

        self.thread = Thread(target=self.capture)
        self.thread.start()

        self.last_detection = None
        self.last_img = None

        logging.info("Camera initialized")

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
                            logging.info(f"Detected QR code: {s}")
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

            except Exception as e:
                logging.error(f"An exception occurred: {e}")

    def get_frame(self) -> bytes:
        while not self.last_img:
            sleep(0.005)

        ret = self.last_img
        self.last_img = None
        logging.debug("Frame retrieved")
        return ret
    
    def get_detection(self) -> str:
        while not self.last_detection:
            sleep(0.005)

        ret = self.last_detection
        self.last_detection = None
        logging.debug("Detection retrieved")
        return ret
    
    def clean_up(self):
        self.camera.release()
        logging.info("Camera released")
    
if __name__ == "__main__":
    camera = Camera()
    while True:
        print(f"got frame {len(camera.get_frame())} len")