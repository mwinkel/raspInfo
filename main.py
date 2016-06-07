from time import strftime

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from traffic import fritzController

kivy.require('1.0.7')


class Widgets(Widget):
    pass


class RaspInfoApp(App):
    kv_directory = 'gui'
    time = StringProperty()
    date = StringProperty()
    traffic = StringProperty()


    def updatePerSecond(self, *args):
        self.time = strftime("%H:%M:%S")
        self.date = strftime("%d.%m.%Y")
        pass

    def updatePerHour(self, *args):
        fc = fritzController()
        self.traffic = ""

        for data in fc.getTrafficInfo():
            self.traffic += str(data) + "\n"
        pass

    def build(self):
        Clock.schedule_interval(self.updatePerSecond, 1)
        Clock.schedule_interval(self.updatePerHour, 60)
        self.updatePerHour()
        return FloatLayout()

    def closeApp(self, *largs):
        print "close"
        self.stop()


if __name__ == '__main__':
    RaspInfoApp().run()