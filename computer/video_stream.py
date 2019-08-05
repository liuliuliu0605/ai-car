#!/usr/bin/env python3
# -*- coding：utf-8 -*-
import socket
import cv2
import numpy as np


class VideoStream(object):
    """Connect car stream sever and get images in real time."""

    def __init__(self, car_ip, stream_port):
        print("Connect video stream ...")
        self.stream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_conn.connect((car_ip, stream_port))
        self.stream_conn = self.stream_conn.makefile('rb')
        self.stream_bytes = b' '
        self.total_frame = 0
        print("Done!")

    def __next__(self):
        """The next frame from car camera"""
        while True:
            self.stream_bytes += self.stream_conn.read(1024)
            first = bytearray(self.stream_bytes).find(b'\xff\xd8')
            last = bytearray(self.stream_bytes).find(b'\xff\xd9')
            if first != -1 and last != -1:
                jpg = self.stream_bytes[first:last + 2]
                self.stream_bytes = self.stream_bytes[last + 2:]
                image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
                self.total_frame += 1
                return image

    def __iter__(self):
        return self

    def __del__(self):
        self.stream_conn.close()
