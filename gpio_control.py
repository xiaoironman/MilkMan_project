import RPi.GPIO as GPIO
import time


def relay_control_high(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    GPIO.output(port, GPIO.HIGH)
    time.sleep(1)


def relay_control_low(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    GPIO.output(port, GPIO.LOW)
    time.sleep(1)


def check_locked(ports):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    state = False
    for port in ports:
        GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        state = GPIO.input(port)
        if not state:
            break

    if state:
        print('Status: Door is Closed!')
        return True
    else:
        print('Status: Door is Open!')
        return False

