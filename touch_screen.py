import logging
import time
import os
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

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
weight = 1001

def change_weight():
    global weight
    weight += 1


# from gpio_control import relay_control_high, relay_control_low
# from printer_control import printer_print
# from gpio_control import check_locked


class MainWindow(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.door_locked = True
        self.image1 = os.path.join('pics', 'logo.jpg')
        self.image2 = os.path.join('pics', 'labels.png')

    def update_status(self):
        # Only two options here: "Locked" or "Not Locked"
        # TODO: Add method to check if door is locked (inside gpio_control)
        # TODO: Remember to keep track of the weight when opening the door!
        # self.door_locked = not self.door_locked # this is a mock up for demonstration
        change_weight()
        return self.door_locked

    # Create a popup window in the MainWindow to warn the user that the door is not locked yet
    def trigger_popup(self):
        popup_lock_door()

    def trigger_popup_admin(self):
        popup_admin()


class SecondWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Detect number of bottles as soon as the second window is to be generated
        self.state = 0
        self.bottle_number = 0
        self.label_text = ''
        self.image1 = os.path.join('pics', 'cows.jpg')
        # Create a handle for the kv file to change the text on the button, initialize it with "CONFIRM"
        self.button_text = 'CONFIRM'

    def for_on_pre_enter(self):
        self.state = 0
        self.bottle_number = 0
        self.label_text = self.get_bottle_number()
        self.button_text = 'CONFIRM'

    def state_increase(self):
        self.state += 1

    def get_bottle_number(self):
        print('weight is: {}'.format(weight))
        logger.info('weight is: {}'.format(weight))
        self.bottle_number = 0
        # TODO: algorithm to detect number of bottles
        self.label_text = "Vous avez déposé {} bouteille(s). Appuyez sur confirmer pour obtenir votre coupon de consigne.".format(
            self.bottle_number)
        return self.label_text

    # In order to print out the QR code using the prinetr (currently not used yet)
    def get_code_and_print(self):
        # TODO: algorithm to generate a discount code
        self.code = 1234567898765
        self.qr_name = gen_qr_main('ASDFasdmseriq234', 3)
        command = 'sudo python3 printer_control.py ' + str(self.code)
        # run the printer by subprocess, after the CONFIRM button is clicked (check kv file)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def show_qr(self):
        return self.image1 if self.bottle_number == 0 else gen_qr_main('ASDFasdmseriq234', self.bottle_number)


class WindowManager(ScreenManager):
    pass


class P(FloatLayout):
    pass


class P_admin(FloatLayout):
    credential = ObjectProperty(None)

    def check_credentials(self):
        if self.credential.text == 'woshiguanliyuan':
            logger.info('Admin entered correct password')
        else:
            logger.info('Admin entered wrong password!')
        return self.credential.text == 'woshiguanliyuan'

    def open_lock(self):
        pass


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
    popupWindow = Popup(title="Admin Login", content=show, size_hint=(None, None), size=(400, 300))
    # show the popup
    popupWindow.open()


class MilkManRecycleApp(App):
    # Main app starts, this script will automatically check the widgets in the milkmanrecycle.kv file
    def build(self):
        pass


if __name__ == '__main__':
    # Edit milkmanrecycle.kv to change the GUI settings
    if not os.path.isdir('./QRs'):
        os.mkdir('QRs')
    logger.info('New session started!')
    MilkManRecycleApp().run()
    logger.info('Current session Finished')
