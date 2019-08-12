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

    def __init__(self, **kw):
        super().__init__(**kw)
        self.door_locked = False

    def update_status(self):
        # Only two options here: "Locked" or "Not Locked"
        # TODO: Add method to check if door is locked (inside gpio_control)
        self.door_locked = not self.door_locked # this is a mock up for demonstration
        return self.door_locked

    # Create a popup window in the MainWindow to warn the user that the door is not locked yet
    def trigger_popup(self):
            popup_lock_door()


class SecondWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        # Detect number of bottles as soon as the second window is to be generated
        self.get_bottle_number()
        # Create a handle for the kv file to change the text on the button, initialize it with "CONFIRM"
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
        # run the printer by subprocess, after the CONFIRM button is clicked (check kv file)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def wait_5s(self):
        time.sleep(5)

    def change_button_text(self):
        # Whenever the customer has confirmed the printing, change the button to "GO BACK"
        if self.button_text == 'CONFIRM':
            self.button_text = 'Go Back'
        else:
            self.button_text = 'CONFIRM'


class WindowManager(ScreenManager):
    pass


class P(FloatLayout):
    pass


# Popup window creation, the content is an instance (called "show") of the class "P" (that is a FloatLayout)
def popup_lock_door():
    # Create an instance of the P class
    show = P()
    # Create the popup window
    popupWindow = Popup(title="Warning", content=show, size_hint=(None,None),size=(400,300))
    # show the popup
    popupWindow.open()


class MilkManRecycleApp(App):
    # Main app starts, this script will automatically check the widgets in the milkmanrecycle.kv file
    def build(self):
        pass


if __name__ == '__main__':
    #
    MilkManRecycleApp().run()
