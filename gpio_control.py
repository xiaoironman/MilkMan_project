import RPi.GPIO as GPIO
import time


def relay_control_high(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    print("LED on")
    GPIO.output(port, GPIO.HIGH)
    time.sleep(1)


def relay_control_low(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    print("LED off")
    GPIO.output(port, GPIO.LOW)
    time.sleep(1)

