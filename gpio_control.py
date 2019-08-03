import RPi.GPIO as GPIO
import time

def relay_control(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port, GPIO.OUT)
    print("LED on")
    GPIO.output(port, GPIO.HIGH)
    time.sleep(5)
    print("LED off")
    GPIO.output(port, GPIO.LOW)
