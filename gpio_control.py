import RPi.GPIO as GPIO
import time


def relay_control_high(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    print("Door opened")
    GPIO.output(port, GPIO.HIGH)
    time.sleep(1)


def relay_control_low(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    print("Door closed")
    GPIO.output(port, GPIO.LOW)
    time.sleep(1)


def check_locked(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    state = GPIO.input(port)
    if state:
        print('Status: Door is Closed!')
        return True
    else:
        print('Status: Door is Open!')
        return False


def get_weight():
    # TODO: receive data from weighing machine
    return 750
