import time
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

from gpio_control import check_locked, relay_control_high, relay_control_low
from printer_control import gen_qr_main

import subprocess


# from gpio_control import relay_control_high, relay_control_low
# from printer_control import printer_print
# from gpio_control import check_locked


class MainWindow(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.door_locked = True
        self.image1 = os.path.join('pics', 'cows.jpg')
        self.image2 = os.path.join('pics', 'logo.jpg')

    def update_status(self):
        # Only two options here: "Locked" or "Not Locked"
        # TODO: Add method to check if door is locked (inside gpio_control)
        # TODO: Remember to keep track of the weight when opening the door!
        self.door_locked = check_locked(17)  # Use port 11 (GPIO-17) to detect if door open
        # self.door_locked = not self.door_locked  # this is a mock up for demonstration
        return self.door_locked

    # Create a popup window in the MainWindow to warn the user that the door is not locked yet
    def trigger_popup(self):
        popup_lock_door()

    # Use port 12 (GPIO-18) to control the relay switchto open or close the door
    def open_door(self):
        relay_control_high(18)

    def close_door(self):
        relay_control_low(18)


class SecondWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Detect number of bottles as soon as the second window is to be generated
        self.get_bottle_number()
        self.state = 0
        self.bottle_number = 0
        self.label_text = ' '
        self.image1 = os.path.join('pics', 'cows.jpg')
        # Create a handle for the kv file to change the text on the button, initialize it with "CONFIRM"
        self.button_text = 'CONFIRM'

    def state_increase(self):
        self.state += 1

    def get_bottle_number(self):
        self.bottle_number = 0
        # TODO: algorithm to detect number of bottles
        self.label_text = "You have put inside {} bottles, please confirm to get the QR code:".format(
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


# Popup window creation, the content is an instance (called "show") of the class "P" (that is a FloatLayout)
def popup_lock_door():
    # Create an instance of the P class
    show = P()
    # Create the popup window
    popupWindow = Popup(title="Warning", content=show, size_hint=(None, None), size=(400, 300))
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
    MilkManRecycleApp().run()
