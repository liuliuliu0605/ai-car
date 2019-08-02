#!/usr/bin/python  
# coding=utf-8  
#本段代码实现树莓派智能小车运动轨迹控制
#代码使用的树莓派GPIO是用的BOARD编码方式。 
import RPi.GPIO as GPIO  
import time  
import sys
import socket

SERVER_IP = "192.168.31.120"#socket.gethostname()
SERVER_PORT = 8004
 
PWMA   = 18
AIN1   = 22
AIN2   = 27

PWMB   = 23
BIN1   = 25
BIN2   = 24

BtnPin  = 19
Gpin    = 5
Rpin    = 6

class rpiGPIOHelper(object):
	def __init__(self):
		print("start recving command data......")
		self.__data = "pi"
		
	def up(self,speed=30,t_time=0.5):
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2,False)#AIN2
		GPIO.output(AIN1,True) #AIN1

		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2,False)#BIN2
		GPIO.output(BIN1,True) #BIN1
		time.sleep(t_time)
			
	def stop(self,t_time=0.5):
		L_Motor.ChangeDutyCycle(0)
		GPIO.output(AIN2,False)#AIN2
		GPIO.output(AIN1,False) #AIN1

		R_Motor.ChangeDutyCycle(0)
		GPIO.output(BIN2,False)#BIN2
		GPIO.output(BIN1,False) #BIN1
		time.sleep(t_time)
			
	def down(self,speed=30,t_time=0.5):
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2,True)#AIN2
		GPIO.output(AIN1,False) #AIN1

		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2,True)#BIN2
		GPIO.output(BIN1,False) #BIN1
		time.sleep(t_time)

	def left(self,speed=30,t_time=0.5):
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2,True)#AIN2
		GPIO.output(AIN1,False) #AIN1

		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2,False)#BIN2
		GPIO.output(BIN1,True) #BIN1
		time.sleep(t_time)

	def right(self,speed=30,t_time=0.5):
		L_Motor.ChangeDutyCycle(speed)
		GPIO.output(AIN2,False)#AIN2
		GPIO.output(AIN1,True) #AIN1

		R_Motor.ChangeDutyCycle(speed)
		GPIO.output(BIN2,True)#BIN2
		GPIO.output(BIN1,False) #BIN1
		time.sleep(t_time)
		
	def clean(self):
		global recv_turn
		self.stop()
		GPIO.cleanup()
		recv_turn = False
		print("Clean Done!!!!")
			
def keysacn():
	val = GPIO.input(BtnPin)
	while GPIO.input(BtnPin) == False:
		val = GPIO.input(BtnPin)
	while GPIO.input(BtnPin) == True:
		time.sleep(0.01)
		val = GPIO.input(BtnPin)
		if val == True:
			GPIO.output(Rpin,1)
			while GPIO.input(BtnPin) == False:
				GPIO.output(Rpin,0)
		else:
			GPIO.output(Rpin,0)
			
def setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
	GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
	GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V) 
		
	GPIO.setup(AIN2,GPIO.OUT)
	GPIO.setup(AIN1,GPIO.OUT)
	GPIO.setup(PWMA,GPIO.OUT)

	GPIO.setup(BIN1,GPIO.OUT)
	GPIO.setup(BIN2,GPIO.OUT)
	GPIO.setup(PWMB,GPIO.OUT)

setup()
# keysacn()
L_Motor = GPIO.PWM(PWMA, 100)
L_Motor.start(0)
R_Motor = GPIO.PWM(PWMB, 100)
R_Motor.start(0)
gpio_helper = rpiGPIOHelper()

# ============socket================ #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(0)
# ============socket================ #

while True:
	print("(%s,%d): waiting for connecting ..." % (SERVER_IP, SERVER_PORT))
	conn, addr = s.accept()
	print("connect successfully! ")
	recv_turn = True
	try:
		while recv_turn:
			#pre_data = s.recv(1024).decode()
			pre_data = conn.recv(1024).decode()
			print(pre_data)
			data = pre_data.split('O')[0]
			if not data: continue
			func = getattr(gpio_helper,data)
			func()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		gpio_helper.clean()
		break
	finally:
		print("Lose connection.")
		conn.close()
		setup()
s.close()
