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
from kivy.clock import Clock
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
# Time to keep the magnetic lock in open status (should be enough for the action of opening door)
OPEN_LOCK_DELAY = 5
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
# Check if it's the admin or normal user opened the door
OPENED_BY_ADMIN = False
# Scan frequency and max wait time for checking if the admin has closed the door properly
SCAN_FREQ = 1  # Seconds
MAX_ADMIN_WAIT = 300  # Iterations, so 30 * 10 = 300 seconds = 5 minutes
# Parameter for the countdown on second window after pressing CONFIRM
MAX_SECONDS = 60
UPDATE_INTERVAL = 1


def open_door():
    logger.info('Door Opened!')
    relay_control_high(RELAY_CONTROL)
    time.sleep(OPEN_LOCK_DELAY)
    relay_control_low(RELAY_CONTROL)
    logger.info('Door Closed!')


def get_current_weight(ser):
    w = -1
    ser.reset_input_buffer()
    try:
        for i in range(100):
            x = ser.readline()
            x = x.decode('ascii')
            if 'M' not in x and i > 3:
                w = float(x[1:9])
                break
    except ValueError:
        print('Please make sure that the scale is properly connected!')
    if w == -1:
        print('*' * 50)
        print('Scale Connection Error!')
        logger.warning('*' * 50 + '\nScale Connection Error!')
        raise serial.SerialException
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
        self.seconds = MAX_SECONDS
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
        self.seconds = MAX_SECONDS

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

    def label_countdown(self):
        self.count_down_clock = Clock.schedule_interval(self.update_label, UPDATE_INTERVAL)
        return 'Page closing in {} seconds'.format(self.seconds)

    def update_label(self, *args):
        self.seconds -= UPDATE_INTERVAL
        self.ids.label_countdown.text = 'Cette page se fermera dans {} secondes'.format(self.seconds)
        if self.seconds < 1:
            self.reset()

    def stop_counter(self):
        self.seconds = MAX_SECONDS
        self.count_down_clock.cancel()

    def reset(self):
        self.ids.btn.text = "CONFIRM"
        self.ids.label_countdown.text = ''
        self.ids.qr_image.source = self.image1
        self.stop_counter()
        self.manager.current = 'main'

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
        self.kb = Window.request_keyboard(None, self)
        # Select keyboard layout from ['azerty', 'de', 'de_CH', 'en_US', 'fr_CH', 'qwerty', 'qwertz']
        self.set_layout('en_US')
        self._keyboard = None

    def set_layout(self, layout):
        """ Change the keyboard layout to the one specified by *layout*. """
        if self.kb.widget:
            # If the current configuration supports Virtual Keyboards, this
            # widget will be a kivy.uix.vkeyboard.VKeyboard instance.
            self._keyboard = self.kb.widget
            self._keyboard.layout = layout
        else:
            self._keyboard = self.kb
        self.kb.release()

    def check_credentials(self):
        if self.credential.text == ADMIN_PASSWORD:
            logger.info('Admin entered correct password')
        else:
            logger.info('Admin entered wrong password!')
        res = self.credential.text == ADMIN_PASSWORD
        # global OPENED_BY_ADMIN
        # OPENED_BY_ADMIN = res
        return res

    def open_lock(self):
        open_door()

    def update_weight(self):
        for i in range(int(MAX_ADMIN_WAIT / SCAN_FREQ)):
            if check_locked(Door_DETECTION):

                # # If it is opened by the admin, now return to the default state
                # global OPENED_BY_ADMIN
                # OPENED_BY_ADMIN = False

                # Update the weight of the recycle box (so it will not influence the next customer)
                global old_weight
                global ser
                logger.info('The weight BEFORE the administrator emptied the box: ' + str(old_weight))
                old_copy = old_weight
                old_weight = get_current_weight(ser)
                logger.info('The weight AFTER the administrator emptied the box: ' + str(old_weight))
                logger.info('The admin has taken out {} bottles'.format(round((old_weight - old_copy) / GLASS_WEIGHT)))
                break
            else:
                if i > 0:
                    logger.info('Door still open after {} seconds'.format(i * SCAN_FREQ))
                time.sleep(SCAN_FREQ)

        # Check if the Admin forgot to close the door
        if not check_locked(Door_DETECTION):
            logger.warning('The administrator forgot to close the door!')
            # TODO: more actions can be taken, such as beeping


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
    # In case the serial port is not immediately ready right after the raspberry pi reboot
    time.sleep(10)
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
        print('Launching software with initial weight: ' + str(old_weight) + ' kg')
        # Edit milkmanrecycle.kv to change the GUI settings
        if not os.path.isdir('./QRs'):
            os.mkdir('QRs')
            logger.info('Software run first time! Creating QRs folder')
        MilkManRecycleApp().run()
        logger.info('Current session Finished')
