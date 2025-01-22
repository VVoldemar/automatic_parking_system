import cv2
import numpy as np
from numpy.typing import NDArray
from pyzbar.pyzbar import decode, ZBarSymbol
from qreader import QReader

print("starting")
qreader = QReader()

camera_id = 0
delay = 1
window_name = 'OpenCV pyzbar'

cap = cv2.VideoCapture(camera_id)
# cv2.resizeWindow(window_name, 840, 640)
print("started")
while True:
    ret, frame = cap.read()
    # frame = cv2.flip(frame, 1)

    if ret:
        # QReader


        info: dict[str, np.ndarray | float | tuple[float | int, float | int]] = None
        decoded_str: str | None = None
        decoded_str, info = qreader.detect_and_decode(frame, True)

        for text, qr_data in zip(decoded_str, info):
            # xyxy = qr_data["bbox_xyxy"]
            # xyxy = list(map(int, xyxy))
            # xyxy = [np.array([
            #     [xyxy[0], xyxy[1]],
            #     [xyxy[0], xyxy[2]],
            #     [xyxy[1], xyxy[1]],
            #     [xyxy[1], xyxy[2]],
            # ])]
            # polygon_xy = qr_data["polygon_xy"]
            padded_quad_xy: NDArray = qr_data["padded_quad_xy"]
            center = qr_data["cxcy"]
            center = list(map(int, center))

            # padded_quad_xy.shape
            # print(padded_quad_xy.shape, padded_quad_xy.dtype, padded_quad_xy)
            # padded_quad_xy.astype(int)
            print(text, padded_quad_xy, center)
            
            if text:
                color = (0, 255, 0)
                frame = cv2.putText(frame, text, center, cv2.FONT_HERSHEY_SIMPLEX,
                                    2, color, 2, cv2.LINE_AA)
                print(text)
            else:
                color = (0, 0, 255)

            frame = cv2.polylines(frame, [padded_quad_xy.astype(int)], True, color, 4)


        # cv2
        
        # ret_qr, decoded_info, points, _ = decoder.detectAndDecodeMulti(frame)
        # if ret_qr:
        #     for s, p in zip(decoded_info, points):
        #         if s:
        #             print(s)
        #             color = (0, 255, 0)
        #         else:
        #             color = (0, 0, 255)
        #         frame = cv2.polylines(frame, [p.astype(int)], True, color, 4)
        #         frame = cv2.putText(frame, s, [p.astype(int)][0], 
        #                             cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        


        # zbar

        # qrs = decode(frame, symbols=[ZBarSymbol.QRCODE])
        # print(qrs, len(qrs))
        # for d in qrs:
        #     s = d.data.decode()
        #     frame = cv2.rectangle(frame, (d.rect.left, d.rect.top),
        #                           (d.rect.left + d.rect.width, d.rect.top + d.rect.height), (255, 0, 0), 3)
        #     pos = [np.array(d.polygon)]
        #     print(s, pos)
        #     frame = cv2.polylines(frame, pos, True, (0, 255, 0), 2)
        #     frame = cv2.putText(frame, s, (d.rect.left, d.rect.top + d.rect.height),
        #                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)


        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)