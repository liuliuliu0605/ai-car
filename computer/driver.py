#!/usr/bin/env python3
# -*- coding：utf-8 -*-
import threading
import cv2
import numpy as np
import time
import os
import pygame
import getopt
import sys
sys.path.append("..")

from computer.car_control import CarControl
from computer.video_stream import VideoStream

CAR_IP = "192.168.31.120"
CONTROL_PORT = 8004
STREAM_PORT = 8005


class AutoDriver(object):
    """Drive car according to deep learning model.

    To use this class, user need to overload function load_model() to
    load specific model, and we take keras as an example. Also, function
    predict should be overloaded to predict the output of image. The prediction
    type is integer and class CarControl will transform it to specific movement
    which can be referred with class variable "commands" in CarControl.
    """

    def __init__(self):
        super(AutoDriver, self).__init__()
        #self.daemon = True  # Allow main to exit even if still running.
        self.state = threading.Condition()
        self.car_control = CarControl(CAR_IP, CONTROL_PORT)
        self.video_stream = VideoStream(CAR_IP, STREAM_PORT)
        self.paused = False                 # pause auto driving if true
        self.stoped = False                 # stop and exit if true
        self.model = None                   # model used to predict car movement
        self.width = None                   # image input width for model
        self.height = None                  # image input height for model
        self.depth = None                   # image input depth for model
        pygame.init()
        display_width = 200
        display_height = 200
        gameDisplay = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption('simulation')

    def load_model(self):
        """Load model in model directory for predicting later."""
        model_name = 'cnn_320_240.h5'
        print("Loading %s ..." % model_name)
        from keras.models import load_model
        self.model = load_model(os.path.join('model', model_name))
        _, self.height, self.width, self.depth = self.model.input_shape
        self.model.predict(np.zeros((1, self.height, self.width, self.depth)))
        print('Done!')

    def predict(self, img):
        """Predict car movement according to img with model loaded

        Args:
            img: image with any width and height and it should be transformed
            into the resolution used in model loaded, probably cv2.resize().

        Returns:
            int: the command id
        """
        #ret, half_image = cv2.threshold(half_image, 127, 255, cv2.THRESH_BINARY)
        img_processed = cv2.resize(img, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        img_ndarray = np.asarray(img_processed, dtype='float64') / 255.
        img_ndarray = img_ndarray.reshape(-1, self.height, self.width, self.depth)
        resp = self.model.predict(img_ndarray)[0]
        prediction = int(resp.argmax(-1))
        #print(resp, prediction)
        return prediction

    def run(self):
        """Start auto driving."""
        print("Start driving ...")
        print('Press q to exit and other key to pause/resume car.')
        try:
            for image in self.video_stream:
                cv2.imshow('image', image)
                cv2.waitKey(1)
                if not self.paused:
                    prediction = self.predict(image)
                    print(self.car_control.commands[prediction])
                    self.car_control.steer(prediction)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        key_input = pygame.key.get_pressed()
                        if key_input[pygame.K_q]:
                            print('exit')
                            car.stop()
                            car.car_control.close()
                            break
                        elif car.paused:
                            car.resume()
                        else:
                            car.pause()
                if self.stoped:
                    break
        except Exception as e:
            print(e)
            self.car_control.close()

    def resume(self):
        """Resume auto driving thread"""
        self.paused = False

    def pause(self):
        """Pause auto driving thread"""
        self.paused = True
        time.sleep(1)
        self.car_control.steer('stop')


    def stop(self):
        """Stop auto driving thread"""
        self.stoped = True


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:s:", ["ip=", "controlport=", "streamport="])
    except getopt.GetoptError:
        print('driver.py -i <car_ip> -c <control_port> -s <stream_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('driver.py -i <car_ip> -c <control_port> -s <stream_port>')
            sys.exit()
        elif opt in ("-i", "--ip"):
            CAR_IP = arg
        elif opt in ("-c", "--controlport"):
            CONTROL_PORT = int(arg)
        elif opt in ("-s", "--streamport"):
            STREAM_PORT = int(arg)
    print("Car IP: %s, Control Port: %d, Stream Port: %d" %(CAR_IP, CONTROL_PORT, STREAM_PORT))
    car = AutoDriver()
    car.load_model()
    car.run()


