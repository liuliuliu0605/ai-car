#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
This code is used to control car to move such as left, right,
up and stop.
Client-Server mode is used here and control server is listening
port 8004 in default at car side.
"""

import RPi.GPIO as GPIO  
import time
import socket


SERVER_IP = "192.168.31.120"#socket.gethostname()
SERVER_PORT = 8004
 
PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24

BtnPin = 19
Gpin = 5
Rpin = 6

L_Motor = None
R_Motor = None

class rpiGPIOHelper(object):
	"""Control car to move."""

	@classmethod
	def inital(cls):
		print("Initial rpiGPIOHelper ...")
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
		GPIO.setup(Gpin, GPIO.OUT)  # Set Green Led Pin mode to output
		GPIO.setup(Rpin, GPIO.OUT)  # Set Red Led Pin mode to output
		GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set BtnPin's mode is input, and pull up to high level(3.3V)
		GPIO.setup(AIN2, GPIO.OUT)
		GPIO.setup(AIN1, GPIO.OUT)
		GPIO.setup(PWMA, GPIO.OUT)
		GPIO.setup(BIN1, GPIO.OUT)
		GPIO.setup(BIN2, GPIO.OUT)
		GPIO.setup(PWMB, GPIO.OUT)

		global L_Motor, R_Motor
		L_Motor = GPIO.PWM(PWMA, 100)
		L_Motor.start(0)
		R_Motor = GPIO.PWM(PWMB, 100)
		R_Motor.start(0)
		print("Done!")

	@classmethod
	def up(cls, speed=30, t_time=0.1):
		"""Move forwards with speed(30 in default) lasting
		for t_time(0.1 in default) seconds at least."""
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2, False)
		GPIO.output(AIN1, True)
		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2, False)
		GPIO.output(BIN1, True)
		time.sleep(t_time)

	@classmethod
	def stop(cls, t_time=0.1):
		"""Stop lasting for t_time(0.1 in default) seconds
		at least."""
		L_Motor.ChangeDutyCycle(0)
		GPIO.output(AIN2, False)
		GPIO.output(AIN1, False)
		R_Motor.ChangeDutyCycle(0)
		GPIO.output(BIN2, False)
		GPIO.output(BIN1, False)
		time.sleep(t_time)

	@classmethod
	def down(cls, speed=20, t_time=0.1):
		"""Move backwards with speed(20 in default) lasting
		for t_time(0.1 in default) seconds at least."""
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2, True)
		GPIO.output(AIN1, False)
		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2, True)
		GPIO.output(BIN1, False)
		time.sleep(t_time)

	@classmethod
	def left(cls, speed=25, t_time=0.1):
		"""Turn left with speed(25 in default) lasting
		for t_time(0.1 in default) seconds at least."""
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2, True)
		GPIO.output(AIN1, False)
		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2, False)
		GPIO.output(BIN1, True)
		time.sleep(t_time)

	@classmethod
	def right(cls, speed=25, t_time=0.1):
		"""Turn right with speed(25 in default) lasting
		for t_time(0.1 in default) seconds at least."""
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2, False)
		GPIO.output(AIN1, True)
		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2, True)
		GPIO.output(BIN1, False)
		time.sleep(t_time)

	@classmethod
	def clean(cls):
		"""Clean """
		print("Clean up rpiGPIOHelper ...")
		GPIO.cleanup()
		print("Done !")


def keysacn():
	"""Function key to start something."""
	val = GPIO.input(BtnPin)
	while GPIO.input(BtnPin) == False:
		val = GPIO.input(BtnPin)
	while GPIO.input(BtnPin) == True:
		time.sleep(0.01)
		val = GPIO.input(BtnPin)
		if val == True:
			GPIO.output(Rpin, 1)
			while GPIO.input(BtnPin) == False:
				GPIO.output(Rpin, 0)
		else:
			GPIO.output(Rpin, 0)


# ============server socket================ #
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)
# ============server socket================ #

rpiGPIOHelper.inital()

while True:
	print("%s: Control server(%s:%s) is waiting for connecting ..." % (
		time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
		SERVER_IP,
		SERVER_PORT))
	conn, addr = server_socket.accept()
	print("%s: Connect successfully!(from %s)" % (
		time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), addr[0]))
	recv_turn = True
	try:
		while recv_turn:
			pre_data = conn.recv(1024).decode()		# move commands: e.g. upOupOupOdownO
			if pre_data == 'CLOSE':					# receive socket close command from client
				break
			data = pre_data.split('O')[0]			# choose the first command
			if not data:
				continue
			print(pre_data, data)
			func = getattr(rpiGPIOHelper, data)		# move according to command
			func()
	except KeyboardInterrupt:
		# When 'Ctrl+C' is pressed, control server will be closed.
		print("%s: Control server is closed by hand." %
			  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		rpiGPIOHelper.clean()
		conn.close()
		server_socket.close()
		break
	except ConnectionResetError:
		# When socket is reset, control server will wait for another client.
		print("%s: Connection is lost abnormally." %
			  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		rpiGPIOHelper.stop()
		conn.close()
	except Exception as e:
		print("%s: Something is wrong ..." %
			  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		print(e)
		rpiGPIOHelper.clean()
		conn.close()
		server_socket.clean()
	else:
		# When server receive socket close command from client.
		rpiGPIOHelper.stop()
		conn.close()
		print("%s: Client request to close connection." %
			  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
