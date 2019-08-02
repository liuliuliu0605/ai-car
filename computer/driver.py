import threading
import socketserver
import cv2
import numpy as np
import math
import socket
import time
import pygame

CAR_IP = "192.168.31.120"
CONTROL_PORT = 8004
STREAM_PORT = 8005

class CarControl(object):

    def __init__(self):
        print('Request car control ...')
        self.control_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_conn.connect((CAR_IP, CONTROL_PORT))
        print('Connect successfully!')
        self.pre_cmd = ''

    def steer(self, prediction):
        # 0: left, 1: right, 2: up, 3: stop
        if prediction == 2:
            self.control_conn.send('upO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'upO'
            print("Forward")
        elif prediction == 0:
            self.control_conn.send('leftO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'leftO'
            print("Left")
        elif prediction == 1:
            self.control_conn.send('rightO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'rightO'
            print("Right")
        elif prediction == 3:
            self.control_conn.send('stopO'.encode())
            # time.sleep(1)
            self.pre_cmd = 'stopO'
            print("Stop")
        else:
            # self.stop()
            # time.sleep(1.5)
            self.control_conn.send(self.pre_cmd.encode())
            print('stop')

    def __del__(self):
        time.sleep(1)
        self.control_conn.send('cleanO'.encode())
        self.control_conn.close()


class VideoStream(object):

    def __init__(self):
        print("Request camera images ...")
        self.stream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_conn.connect((CAR_IP, STREAM_PORT))
        self.stream_conn = self.stream_conn.makefile('rb')
        print("Connect successfully!")

    def __del__(self):
        self.stream_conn.close()


class AutoDriver(threading.Thread):

    def __init__(self):
        super(AutoDriver, self).__init__()
        #self.daemon = True  # Allow main to exit even if still running.
        self.paused = False
        self.stoped = False
        self.state = threading.Condition()
        self.car_control = CarControl()
        self.video_stream = VideoStream()
        self.model = None
        self.action_dict = {0: 'left', 1: 'right', 2: 'up', 3: 'stop'}

    def load_model(self, filename):
        pass

    def driver(self, half_image):
        # use self.model to predict car action
        # 0: left, 1: right, 2: up, 3: stop

        return 2

    def run(self):
        print("Start driving...")
        stream_bytes = b''
        n = 0
        try:
            while not self.stoped:
                with self.state:  # 在该条件下操作
                    stream_bytes += self.video_stream.stream_conn.read(1024)
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
                        # cv2.imwrite('image.jpeg', image)
                        # cv2.imwrite('mlp_image.jpeg', half_gray)
                        prediction = self.driver(half_gray)
                        self.car_control.steer(prediction)
                        #print(self.action_dict[prediction])
                    if self.paused:
                        self.state.wait()  # Block execution until notified.
            cv2.destroyAllWindows()
        finally:
            print("Connection closed.")

    def resume(self):  # 用来恢复/启动run
        with self.state:  # 在该条件下操作
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

    def pause(self):  # 用来暂停run
        with self.state:  # 在该条件下操作
            self.paused = True  # Block self
            time.sleep(1)
            self.car_control.steer(3)

    def stop(self):  # 用来暂停run
        with self.state:  # 在该条件下操作
            self.stoped = True
            time.sleep(1)
            self.car_control.steer(3)
            self.state.notify()


if __name__ == '__main__':
    car = AutoDriver()
    car.start()
    #time.sleep(3)
    #car.pause()
    #time.sleep(5)
    #car.resume()

    pygame.init()
    display_width = 320
    display_height = 240
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('simulation')
    print('Press q to exit and other key to pause/resume car.')
    send_inst = True
    while send_inst:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_input = pygame.key.get_pressed()
                if key_input[pygame.K_q]:
                    print('exit')
                    car.stop()
                    send_inst = False
                    break
                elif car.paused:
                    car.resume()
                else:
                    car.pause()


