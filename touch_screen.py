import time

import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import subprocess

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
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
        self.bottle_number = 3
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

    pass


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


kv = Builder.load_file("my.kv")
# kv = Builder.load_file("milkman_widgets.kv")


class MainGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)
        self.cols = 2 # We define the amount of columns to be 2
        self.first_button = Button(text="Clean on the screen to start the recycling process :)")
        self.unlock_button = Button(text='UNLOCK')
        self.unlock_button.bind(on_press=self.on_press_unlock)
        self.add_widget(self.unlock_button)

        self.print_button = Button(text='Print Discount Code')
        self.print_button.bind(on_press=self.on_press_print)
        self.add_widget(self.print_button)

    def on_press_unlock(self, instance):

        button_name = self.unlock_button.text
        print(button_name, ' button Pressed')
        if button_name == 'UNLOCK':
            # relay_control_high(18)
            self.unlock_button.text = 'LOCK'
        else:
            # relay_control_low(18)
            self.unlock_button.text = 'UNLOCK'

    def on_press_print(self, instance):
        # printer_print('This is working!')
        code1 = '"This is working!"'

        # code2 = 'This is still working!'
        command = 'sudo python3 printer_control.py ' + code1
        # command = 'python printer_control.py ' + code1
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)


class MilkManRecycleApp(App):
    def build(self):
        return kv
        # return MainGrid()


if __name__ == '__main__':
    MilkManRecycleApp().run()
