# Created by: Justin Myles jmyles@precision-nano.com
# Created on: 08 Oct 2018
# Edited by Carlos Doebeli for Ignite

import board
import busio
import digitalio
from teThermistor import *
from pni_libs.helpers import *
from pni_libs.debug import *
from pni_libs.rs485 import *

class application:

    def __init__(self):
        self.te_thermistors = ([
            TeThermistor(board.A5, 3, pullup_resistor=3272
                         , probe_offset=0.2),  # BB row 6, ID:
            # TeThermistor(board.A4, 4, pullup_resistor = 3278
            #         , probe_offset = 0.2), #BB row 7, ID:
            # TeThermistor(board.A3, 3, pullup_resistor = 3247
            #         , probe_offset = -0.2), #BB row 8, ID:
            TeThermistor(board.A2, 2, pullup_resistor=3299
                         , probe_offset=0.1),  # BB row 9, ID:
            TeThermistor(board.A1, 1, pullup_resistor=3279
                         , probe_offset=0.1),  # BB row 10, ID:
            TeThermistor(board.A0, 0, pullup_resistor=3298
                         , probe_offset=-0.2),  # BB row 11, ID:
        ])

        self.switch_pin = digitalio.DigitalInOut(board.D12)
        self.switch_pin.direction = digitalio.Direction.INPUT
        self.switch_pin.pull = digitalio.Pull.UP
        self.started = False
        self.process_timeout = chronometer()

    def setup(self):
        Debug.begin(debug_level=Debug.DEBUG)
        for t in self.te_thermistors:
            UpdateHelper.register(t.update)
        application.set_chrono(self.process_timeout, 3000)

    def loop(self):
        if self.started:
            UpdateHelper.update()

        if self.process_timeout.isDone():
            # When the switch is on, the switch pin's value is low
            if not self.switch_pin.value and not self.started:
                delay(20)
                if not self.switch_pin.value:
                    self.started = True
                    Debug.msg("STARTING RECORDING", Debug.DATA, source="START")
            elif self.switch_pin.value and self.started:
                delay(20)
                if self.switch_pin.value:
                    self.started = False
                    Debug.msg("TEST FINISHED", Debug.DATA, source="FINISH")
            application.set_chrono(self.process_timeout, 500)

    def set_chrono(chrono, time):
        if chrono.isRunning():
            chrono.reset()
            Debug.msg("RESETTING CHRONO",
                    Debug.DEBUG, source="CHRONOMETER")
        chrono.setAndGo(time)


if __name__ == "__main__":
    neopixel_off()
    app = application()
    app.setup()
    print("MCU Ready")
    while True:
        app.loop()
