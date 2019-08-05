#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
This code is used to collect training data manually.
The control server and stream server are running in the car and
waiting for connection. The default frame resolution
is 160 * 120 (with, height).
"""
import numpy as np
import cv2
import pygame
import socket

from computer.car_control import CarControl
from computer.video_stream import VideoStream

CAR_IP = "192.168.31.120"
CONTROL_PORT = 8004
STREAM_PORT = 8005
WIDTH = 320
HEIGHT = 240


class CollectTrainingData(object):
    """Collect training data by controlling car manually."""

    def __init__(self):

        print("Connect AI Car(%s) ..." % CAR_IP)
        self.car = CarControl(CAR_IP, CONTROL_PORT)
        self.video = VideoStream(CAR_IP, STREAM_PORT)
        print("Done!")
        self.send_inst = True
        pygame.init()
        display_width = 200         # game handler width
        display_height = 200        # game handler width
        gameDisplay = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption('simulation')
        self.collect_image()

    def collect_image(self):

        saved_frame = 0
        # clock = pygame.time.Clock()
        e1 = cv2.getTickCount()
        image_array = np.zeros((HEIGHT, WIDTH))
        label_num = len(self.car.commands)
        label_array = np.zeros((1, label_num), 'float')
        label_one_hot = np.zeros((label_num, label_num), 'float')
        for i in range(label_num):
            label_one_hot[i, i] = 1
        # collect video frames one by one
        print('Start collecting images ...')
        try:
            is_stop = False
            for image in self.video:
                cv2.imshow('image', image)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        key_input = pygame.key.get_pressed()
                        command_id = -1
                        if key_input[pygame.K_d]:
                            command_id = self.car.steer('turn right')
                        elif key_input[pygame.K_a]:
                            command_id = self.car.steer('turn left')
                        elif key_input[pygame.K_w]:
                            command_id = self.car.steer('move forward')
                        elif key_input[pygame.K_s]:
                            command_id = self.car.steer('stop')
                        elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                            self.car.close()
                            is_stop = True
                            break
                        # save image for training data
                        if command_id != -1 and command_id != 3:
                            cv2.imwrite('training_data/images/%d_%d.jpg' %
                                        (saved_frame, command_id), image)
                            image_array = np.vstack((image_array, image))
                            label_array = np.vstack((label_array, label_one_hot[command_id]))
                            saved_frame += 1
                    elif event.type == pygame.KEYUP:
                        print('0')
                if is_stop:
                    break

            # save training images and labels except for the first one
            image_array = image_array.reshape(-1, HEIGHT, WIDTH)
            train_data = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            np.savez('training_data/npz/train.npz', train_data=train_data, train_labels=train_labels)

            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print('Streaming duration:', time0)
            print(train_data.shape)
            print(train_labels.shape)
            print('Total frame:', self.video.total_frame)
            print('Saved frame:', saved_frame)
            print('Dropped frame', self.video.total_frame - saved_frame)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    CollectTrainingData()
