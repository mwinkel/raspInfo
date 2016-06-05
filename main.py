import kivy
import time
from time import strftime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty
from kivy.uix.widget import Widget

kivy.require('1.0.7')


class Widgets(Widget):
    pass


class RaspInfoApp(App):
    kv_directory = 'gui'
    time = StringProperty()
    date = StringProperty()

    def update(self, *args):
        self.time = strftime("%H:%M:%S")
        self.date = strftime("%x")
        pass

    def build(self):
        Clock.schedule_interval(self.update, 1)
        return FloatLayout()

    def closeApp(self, *largs):
        print "close"
        self.stop()


if __name__ == '__main__':
    RaspInfoApp().run()