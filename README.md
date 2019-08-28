## Overview
This project aims to 

## Dependencies

* keras
* tensorflow
* sklearn
* opencv-python
* numpy
* pygame

## Materials

* RaspberryPi 3 B+
* OpenCV Camera module
It's compatible with all usb cameras.
* Wireless network card
The car automatically connects wifi called "GMX"(password: netlab523) with ip 192.168.31.120. For controlling the car, you need to set port forwarding for router. For example, 172.18.233.73:8004(WAN_IP:EXTERNAL_PORT) mapping to 192.168.31.120:8004(LAN_IP:INTERNAL_PORT) means you can control the car with ip address of 172.18.233.73:8004.

## Usage

* Generating training data
Use collect_training_data module to control car in real time and generate images named with(seq_label). The original images are saved in the folder of training_data and numpy-format data is also saved.

* Learning from training data
The module cnn_training is an example to show how to train dataset. The training model should be saved into the folder of model.

* Auto Driving
Use driver module to drive car automatically. The method of load_model and predict should be reloaded according to your model.

