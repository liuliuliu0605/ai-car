import io
import socket
import struct
import time
# import picamera
import cv2
from PIL import Image


# create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.31.100', 8000))
print("connect to: ", '192.168.31.100')
connection = client_socket.makefile('wb')
cap = cv2.VideoCapture(0)
ret = cap.set(3, 320)  # frame width
ret = cap.set(4, 240)  # frame height
#cap.set(15, 0.2)  # exposure

try:
    # with picamera.PiCamera() as camera:
    while cap.isOpened():
        rc, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        jpg = Image.fromarray(imgRGB)
        start = time.time()
        stream = io.BytesIO()  # 10 frames/sec
        jpg.save(stream, format='JPEG')
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        stream.seek(0)
        connection.write(stream.read())
        if time.time() - start > 600:
            break
        stream.seek(0)
        stream.truncate()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
