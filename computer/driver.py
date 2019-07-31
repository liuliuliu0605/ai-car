import threading
import socketserver
import cv2
import numpy as np
import math
import socket
import time

SERVER_IP = "192.168.31.100"

class CarControl(object):

    def __init__(self):
        self.__data = 'I am pi'
        self.gpio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gpio_socket.bind((SERVER_IP, 8004))
        self.gpio_socket.listen(0)
        print('waiting for car to connect ...')
        self.conn2, self.addr = self.gpio_socket.accept()
        print('connect successfully!')
        self.pre_cmd = ''

    def steer(self, prediction):
        if prediction == 2:
            self.conn2.send('upO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'upO'
            print("Forward")
        elif prediction == 0:
            self.conn2.send('leftO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'leftO'
            print("Left")
        elif prediction == 1:
            self.conn2.send('rightO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'rightO'
            print("Right")
        else:
            # self.stop()
            # time.sleep(1.5)
            self.conn2.send(self.pre_cmd.encode())
            print('stop')

    def stop(self):
        # self.conn2.sendall('clean')
        time.sleep(1)


class VideoStreamHandler(socketserver.StreamRequestHandler):

    def __init__(self):
        super(socketserver.StreamRequestHandler, self).__init__()
        self.rc_car = CarControl()

    def handle(self):
        print("receive video capture from: ", self.client_address)
        stream_bytes = b''
        n = 0
        try:
            while True:
                stream_bytes += self.rfile.read(1024)
                first = bytearray(stream_bytes).find(b'\xff\xd8')
                last = bytearray(stream_bytes).find(b'\xff\xd9')
                if first != -1 and last != -1:
                    n += 1
                    print('get image %d' % n)
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), -1)

                    # lower half of the image
                    half_gray = gray[120:240, :]

                    #cv2.imwrite('image.jpeg', image)
                    #cv2.imwrite('mlp_image.jpeg', half_gray)

            cv2.destroyAllWindows()
        finally:
            print("Connection closed on thread 1")


def server_thread(host, port):
    print("Server %s listen on port % d" %(host, port))
    server = socketserver.TCPServer((host, port), VideoStreamHandler)
    server.serve_forever()


class ThreadServer(object):

    def __init__(self):
        video_thread = threading.Thread(target=server_thread(SERVER_IP, 8000))
        video_thread.start()


if __name__ == '__main__':
    ThreadServer()
