import numpy as np
import cv2
import pygame
from pygame.locals import *
import socket

CAR_IP = "192.168.31.120"
CONTROL_PORT = 8004
STREAM_PORT = 8005

class CollectTrainingData(object):

    def __init__(self):
        print("Request car control ...")
        self.control_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_conn.connect((CAR_IP, CONTROL_PORT))
        print("Connect successfully!")
        print("Request camera images ...")
        self.stream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_conn.connect((CAR_IP, STREAM_PORT))
        self.stream_conn = self.stream_conn.makefile('rb')
        print("Connect successfully!")
        # connect tag
        self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        pygame.init()

        # define game handler
        display_width = 320
        display_height = 240
        gameDisplay = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption('simulation')

        self.collect_image()

    def collect_image(self):
        saved_frame = 0
        total_frame = 0
        clock = pygame.time.Clock()
        # collect images for training
        print('Start collecting images...')
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')
        # label_array = np.zeros((1, 3), 'float')

        # stream video frames one by one
        try:
            stream_bytes = b' '
            frame = 1
            while self.send_inst:
                stream_bytes += self.stream_conn.read(1024)
                first = bytearray(stream_bytes).find(b'\xff\xd8')
                last = bytearray(stream_bytes).find(b'\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
                    # select lower half of the image
                    roi = image[120:240, :]
                    # save streamed images
                    #cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), image)
                    cv2.imshow('roi_image', roi)
                    cv2.imshow('image', image)
                    # reshape the roi image into one row array
                    temp_array = roi.reshape(1, 38400).astype(np.float32)
                    frame += 1
                    total_frame += 1
                    # get input from human driver
                    clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            key_input = pygame.key.get_pressed()
                            if key_input[pygame.K_d]:
                                print("Forward Right")
                                self.control_conn.sendall('rightO'.encode())
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[1]))
                                saved_frame += 1
                            elif key_input[pygame.K_a]:
                                print("Forward Left")
                                self.control_conn.sendall('leftO'.encode())
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[0]))
                                saved_frame += 1
                            elif key_input[pygame.K_w]:
                                print("Forward")
                                self.control_conn.sendall('upO'.encode())
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[2]))
                            elif key_input[pygame.K_s]:
                                print("Stop")
                                self.control_conn.sendall('stopO'.encode())
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[3]))
                            # elif key_input[pygame.K_RIGHT]:
                            #     print("Right")
                            #     self.control_conn.sendall('rightO')
                            #     image_array = np.vstack((image_array, temp_array))
                            #     label_array = np.vstack((label_array, self.k[1]))
                            #     saved_frame += 1

                            # elif key_input[pygame.K_LEFT]:
                            #     print("Left")
                            #     self.control_conn.sendall('leftO')
                            #     image_array = np.vstack((image_array, temp_array))
                            #     label_array = np.vstack((label_array, self.k[0]))
                            #     saved_frame += 1
                            elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                                print('exit')
                                self.control_conn.sendall('clean'.encode())
                                self.send_inst = False
                                break
                        elif event.type == pygame.KEYUP:
                            print('0')

            # save training images and labels
            train = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            np.savez('./training_data/test.npz', train=train, train_labels=train_labels)

            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print('Streaming duration:', time0)

            print(train.shape)
            print(train_labels.shape)
            print('Total frame:', total_frame)
            print('Saved frame:', saved_frame)
            print('Dropped frame', total_frame - saved_frame)

        finally:
            self.stream_conn.close()
            #self.server_socket.close()
            #self.gpio_socket.close()
            self.control_conn.close()


if __name__ == '__main__':
    CollectTrainingData()
