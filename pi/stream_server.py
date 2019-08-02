import io
import socket
import struct
import time
# import picamera
import cv2
from PIL import Image

SERVER_IP = "192.168.31.120"#socket.gethostname()
SERVER_PORT = 8005

# create socket and bind host
server_socket = socket.socket()
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(0)
# accept a single connection
print("(%s,%d): waiting for connecting ..." %(SERVER_IP,SERVER_PORT))
connection = server_socket.accept()[0].makefile('wb')
print("connect successfully!")

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
    #client_socket.close()
    server_socket.close()
