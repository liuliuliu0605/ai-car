#!/usr/bin/env python3
# -*- coding：utf-8 -*-
import threading
import cv2
import numpy as np
import time
import os
import pygame
import sys
sys.path.append("..")

from computer.car_control import CarControl
from computer.video_stream import VideoStream

CAR_IP = "192.168.31.120"
CONTROL_PORT = 8004
STREAM_PORT = 8005


class AutoDriver(threading.Thread):
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

    def load_model(self, model_name):
        """Load model in model directory for predicting later."""
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
        try:
            for image in self.video_stream:
                with self.state:
                    cv2.imshow('image', image)
                    cv2.waitKey(1)
                    prediction = self.predict(image)
                    print(self.car_control.commands[prediction])
                    self.car_control.steer(prediction)
                    if self.paused:
                        print("paused.....")
                        self.state.wait()           # Block execution until notified.
                if self.stoped:                     # Exit execution
                    break
            #cv2.destroyAllWindows()
        except Exception as e:
            self.car_control.close()

    def resume(self):
        """Resume auto driving thread"""
        with self.state:
            print("res")
            self.paused = False
            self.state.notify()     # Unblock self if waiting.

    def pause(self):
        """Pause auto driving thread"""
        with self.state:
            self.paused = True      # Block self
        time.sleep(1)
        self.car_control.steer('stop')


    def stop(self):
        """Stop auto driving thread"""
        with self.state:
            self.stoped = True
            self.state.notify()
            self.car_control.steer('stop')


if __name__ == '__main__':
    car = AutoDriver()
    car.load_model('cnn_320_240.h5')
    car.start()
    pygame.init()
    display_width = 200
    display_height = 200
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('simulation')
    print('Press q to exit and other key to pause/resume car.')
    send_inst = True
    try:
        while send_inst:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    key_input = pygame.key.get_pressed()
                    if key_input[pygame.K_q]:
                        print('exit')
                        car.stop()
                        car.car_control.close()
                        send_inst = False
                        break
                    elif car.paused:
                        car.resume()
                    else:
                        car.pause()
    except ConnectionResetError:
        pass



