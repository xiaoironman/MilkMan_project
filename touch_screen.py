import time
import os

import serial
from kivy.config import Config
from kivy.core.window import Window
import logging

Config.set('graphics', 'fullscreen', 'auto')
Config.set("graphics", "show_cursor", 0)
Config.set("kivy", "keyboard_mode", 'dock')
Config.write()
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

from gpio_control import check_locked, relay_control_high, relay_control_low
from printer_control import gen_qr_main

import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create file handler which logs even debug messages
fh = logging.FileHandler('main.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

# Constants definition:
# GPIO port for relay switch control
RELAY_CONTROL = 18
# GPIO port for door detection sensor input
Door_DETECTION = [17, 27]
# Unit weight of an empty bottle
GLASS_WEIGHT = 0.639565
# Secret key of AES encoding for QR code
QR_SECRET_KEY = 'ASDFasdmseriq234'
# Default length of the code (include "M" and "K" at the beginning and the end)
DEFAULT_CODE_LENGTH = 15
# Administrator's password
ADMIN_PASSWORD = 'woshiguanliyuan'


def open_door():
    logger.info('Door Opened!')
    relay_control_high(RELAY_CONTROL)
    time.sleep(5)
    relay_control_low(RELAY_CONTROL)
    logger.info('Door Closed!')


def get_current_weight(ser):
    w = -1
    ser.reset_input_buffer()
    try:
        for i in range(100):
            x = ser.readline()
            x = x.decode('ascii')
            if not 'M' in x and i > 3:
                w = float(x[1:9])
                break
    except ValueError:
        print('Please make sure that the scale is properly connected!')
    return w


class MainWindow(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.door_locked = True
        self.image1 = os.path.join('pics', 'logo.jpg')
        self.image2 = os.path.join('pics', 'labels.png')

    def update_status(self):
        # Only two options here: "Locked" or "Not Locked"
        self.door_locked = int(check_locked(Door_DETECTION))  # Use port 11 and 13 (GPIO-17 & 27) to detect if door open
        return self.door_locked

    # Create a popup window in the MainWindow to warn the user that the door is not locked yet
    def trigger_popup(self):
        popup_lock_door()

    def trigger_popup_admin(self):
        popup_admin()

    # Use port 12 (GPIO-18) to control the relay switch to open or close the door
    def open_door(self):
        open_door()


class SecondWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Detect number of bottles as soon as the second window is to be generated
        # self.get_bottle_number()
        self.state = 0
        self.bottle_number = 0
        self.label_text = ''
        self.image1 = os.path.join('pics', 'logo.jpg')
        self.image_wrong = os.path.join('pics', 'wrong.png')
        # Create a handle for the kv file to change the text on the button, initialize it with "CONFIRM"
        self.button_text = 'Confirmer'

    def for_on_pre_enter(self):
        self.state = 0
        self.bottle_number = 0
        self.label_text = self.get_bottle_number()
        # Create a handle for the kv file to change the text on the button, initialize it with "CONFIRM"
        self.button_text = 'Confirmer'

    def state_increase(self):
        self.state += 1

    def get_bottle_number(self):
        # Algorithm to detect number of bottles
        global old_weight
        global ser
        print('Old weight is: ' + str(old_weight))
        logger.info('Old weight is: ' + str(old_weight))
        weight_copy = old_weight
        # Here the global variable "old_weight" value will change again!
        print('Now updating weight!...')
        current_weight = get_current_weight(ser)
        print('New weight is: ' + str(current_weight))
        logger.info('New weight is: ' + str(current_weight))
        self.bottle_number = round((current_weight - weight_copy) / GLASS_WEIGHT)
        print('Number of bottles detected: ' + str(self.bottle_number))
        logger.info('Number of bottles detected: ' + str(self.bottle_number))
        old_weight = current_weight
        if self.bottle_number in [0, 1]:
            self.label_text = "Vous avez retourné {} bouteille, appuyez sur confirmer pour obtenir votre coupon de " \
                              "consigne:".format(self.bottle_number)
        else:
            self.label_text = "Vous avez retourné {} bouteilles, appuyez sur confirmer pour obtenir votre coupon de " \
                              "consigne:".format(self.bottle_number)
        return self.label_text

    # In order to print out the QR code using the prinetr (currently not used yet)
    def get_code_and_print(self):
        # TODO: algorithm to generate a discount code
        self.code = 1234567898765
        self.qr_name = gen_qr_main(QR_SECRET_KEY, 3, code_length=DEFAULT_CODE_LENGTH)
        command = 'sudo python3 printer_control.py ' + str(self.code)
        # run the printer by subprocess, after the CONFIRM button is clicked (check kv file)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def show_qr(self):
        if self.bottle_number < 0:
            logger.warning('Negative bottle numbers ({}) have been detected!'.format(self.bottle_number))
            return self.image_wrong
        elif self.bottle_number == 0:
            return self.image1
        else:
            qr_filename = gen_qr_main(QR_SECRET_KEY, self.bottle_number, code_length=DEFAULT_CODE_LENGTH)
            logger.info('\"{}\" has been created for {} bottles.'.format(qr_filename, self.bottle_number))
            return qr_filename


class WindowManager(ScreenManager):
    pass


class P(FloatLayout):
    pass


class P_admin(FloatLayout):
    credential = ObjectProperty(None)
    kbContainer = ObjectProperty()

    def __init__(self, **kwargs):
        super(P_admin, self).__init__(**kwargs)
        # Select keyboard layout from ['azerty', 'de', 'de_CH', 'en_US', 'fr_CH', 'qwerty', 'qwertz']
        self.set_layout('en_US')
        self._keyboard = None

    def set_layout(self, layout):
        """ Change the keyboard layout to the one specified by *layout*. """
        kb = Window.request_keyboard(None, self)
        if kb.widget:
            # If the current configuration supports Virtual Keyboards, this
            # widget will be a kivy.uix.vkeyboard.VKeyboard instance.
            self._keyboard = kb.widget
            self._keyboard.layout = layout
        else:
            self._keyboard = kb

    def check_credentials(self):
        if self.credential.text == ADMIN_PASSWORD:
            logger.info('Admin entered correct password')
        else:
            logger.info('Admin entered wrong password!')
        return self.credential.text == ADMIN_PASSWORD

    def open_lock(self):
        open_door()


# Popup window creation, the content is an instance (called "show") of the class "P" (that is a FloatLayout)
def popup_lock_door():
    # Create an instance of the P class
    show = P()
    # Create the popup window
    popupWindow = Popup(title="Warning", content=show, size_hint=(None, None), size=(400, 300))
    # show the popup
    popupWindow.open()


def popup_admin():
    # Create an instance of the P class
    show = P_admin()
    # Create the popup window
    popupWindow = Popup(title="Admin Login", content=show, size_hint=(None, None), size=(400, 300),
                        pos_hint={'x': 0.25, 'y': 0.5})
    # show the popup
    popupWindow.open()


class MilkManRecycleApp(App):
    # Main app starts, this script will automatically check the widgets in the milkmanrecycle.kv file
    def build(self):
        pass


if __name__ == '__main__':
    logger.info('New session started!')
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    except (serial.serialutil.SerialException, FileNotFoundError):
        logger.error('Serial connection to the scale failed!')
        logger.info('Current session Finished')
        print('Serial connection between Raspberry Pi and the scale failed!')
    else:
        old_weight = get_current_weight(ser)
        # Edit milkmanrecycle.kv to change the GUI settings
        if not os.path.isdir('./QRs'):
            os.mkdir('QRs')
            logger.info('Software run first time! Creating QRs folder')
        MilkManRecycleApp().run()
        logger.info('Current session Finished')
