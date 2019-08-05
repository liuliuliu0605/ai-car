#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
This code is used to stream car camera.
Client-Server mode is used here and stream server is listening
port 8005 in default at car side. The default frame resolution
is 160 * 120 (with, height).
"""
import io
import socket
import struct
import time
# import picamera
import cv2
from PIL import Image

#from signal import signal, SIGPIPE, SIG_DFL
#signal(SIGPIPE, SIG_DFL)

SERVER_IP = "192.168.31.120"
SERVER_PORT = 8005
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ============server socket================ #
server_socket = socket.socket()
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)
# ============server socket================ #

cap = cv2.VideoCapture(0)
ret = cap.set(3, FRAME_WIDTH)   # frame width
ret = cap.set(4, FRAME_HEIGHT)  # frame height
# ret = cap.set(15, 0.2)          # exposure, may not be supported

while True:
    print("%s: Stream server(%s:%s) is waiting for connecting ..." % (
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        SERVER_IP,
        SERVER_PORT))
    _connection, addr = server_socket.accept()
    connection = _connection.makefile('wb')
    print("%s: Connect successfully!(from %s)" % (
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), addr[0]))
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
    except KeyboardInterrupt:
        # When 'Ctrl+C' is pressed, stream server will be closed.
        print("%s: Stream server is closed by hand." %
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        connection.close()
        server_socket.close()
        break
    except ConnectionResetError:
        # When socket is reset, stream server will wait for another client.
        print("%s: Connection is lost abnormally." %
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # connection.close()        # the sentence will cause BrokenPipeError
    except BrokenPipeError:
        print("%s: Client request to close connection." %
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    except Exception as e:
        # other exception will end the server main routine.
        print("%s: Something is wrong ..." %
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(e)
        connection.close()
        server_socket.close()
        break
