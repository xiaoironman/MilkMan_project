import kivy

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
# from gpio_control import relay_control_high, relay_control_low
# from printer_control import printer_print


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
        print('Printer printing discount codes!')


class main_window(FloatLayout):
    pass



class MilkManRecycleApp(App):
    def build(self):
        # return a Button() as a root widget
        return MainGrid()
        # return Label(text="Clean on the screen to start the recycling process :)")


if __name__ == '__main__':
    MilkManRecycleApp().run()
