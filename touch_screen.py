import time

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

import subprocess
# from gpio_control import relay_control_high, relay_control_low
# from printer_control import printer_print
# from gpio_control import check_locked


class MainWindow(Screen):

    def update_status(self):
        # Only two options here: "Locked" or "Not Locked"
        # TODO: Add method to check if door is locked (inside gpio_control)
        self.status = "Locked"

    def trigger_popup(self):
            popup_lock_door()


class SecondWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.get_bottle_number()
        self.button_text = 'CONFIRM'

    def get_bottle_number(self):
        self.bottle_number = 0
        # TODO: algorithm to detect number of bottles
        self.label_text = "You have put inside {} bottles, please confirm to print the discount code:".format(self.bottle_number)

    def get_code_and_print(self):
        # TODO: algorithm to generate a discount code
        self.code = 1234567898765
        self.label_text = "Your discount code is:  {}".format(self.code)
        command = 'sudo python3 printer_control.py ' + str(self.code)
        # command = 'python printer_control.py ' + code1
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def wait_5s(self):
        time.sleep(5)

    def change_button_text(self):
        if self.button_text == 'CONFIRM':
            self.button_text = 'Go Back'
        else:
            self.button_text = 'CONFIRM'


class ThirdWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class P(FloatLayout):
    pass


def popup_lock_door():
    show = P() # Create a new instance of the P class
    popupWindow = Popup(title="Warning", content=show, size_hint=(None,None),size=(400,400))
    # Create the popup window
    popupWindow.open() # show the popup


class MilkManRecycleApp(App):
    def build(self):
        pass


if __name__ == '__main__':
    MilkManRecycleApp().run()
