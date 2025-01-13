import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol

camera_id = 0
delay = 1
window_name = 'OpenCV pyzbar'

cap = cv2.VideoCapture(camera_id)
decoder = cv2.QRCodeDetector()
# cv2.resizeWindow(window_name, 840, 640)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if ret:
        ret_qr, decoded_info, points, _ = decoder.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                if s:
                    print(s)
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
        cv2.imshow(window_name, frame)

        # qrs = decode(frame, symbols=[ZBarSymbol.QRCODE])
        # print(qrs, len(qrs))
        # for d in qrs:
        #     s = d.data.decode()
        #     print(s)
        #     frame = cv2.rectangle(frame, (d.rect.left, d.rect.top),
        #                           (d.rect.left + d.rect.width, d.rect.top + d.rect.height), (255, 0, 0), 3)
        #     frame = cv2.polylines(frame, [np.array(d.polygon)], True, (0, 255, 0), 2)
        #     frame = cv2.putText(frame, s, (d.rect.left, d.rect.top + d.rect.height),
        #                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        # cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)