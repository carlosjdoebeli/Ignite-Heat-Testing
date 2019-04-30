# This files contains some simple helper functions
# Created by: Mark Ma (mma@precision-nano.com)
# Created on: 23 Sept 2018

import board
import time
import math
import microcontroller
import busio
import neopixel_write
import digitalio

kHelperVersionMajor = 1
kHelperVersionMinor = 1
kVersion = [kHelperVersionMajor, kHelperVersionMinor]

def millis():
    return time.monotonic() * 1000.0

def delay(time_ms):
    time_s = time_ms/1000.0
    time.sleep(time_s)

def delay_us(time_us):
    microcontroller.delay_us(time_us)

# Function copied from https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
def is_hardware_uart(tx, rx):
    try:
        p = busio.UART(tx, rx)
        p.deinit()
        return True
    except ValueError:
        return False

# Function copied from https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
def get_unique_pins():
    exclude = ['NEOPIXEL', 'APA102_MOSI', 'APA102_SCK']
    pins = [pin for pin in [
        getattr(board, p) for p in dir(board) if p not in exclude]
            if isinstance(pin, microcontroller.Pin)]
    unique = []
    for p in pins:
        if p not in unique:
            unique.append(p)
    return unique

# Function copied from https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
def list_hardware_uart_pins():
    for tx_pin in get_unique_pins():
        for rx_pin in get_unique_pins():
            if rx_pin is tx_pin:
                continue
            else:
                if is_hardware_uart(tx_pin, rx_pin):
                    print("TX pin:", tx_pin, "\t RX pin:", rx_pin)
                else:
                    pass

def neopixel_off():
    pin = digitalio.DigitalInOut(board.NEOPIXEL)
    pin.direction = digitalio.Direction.OUTPUT
    pixel_off = bytearray([0, 0, 0])
    neopixel_write.neopixel_write(pin, pixel_off)

class UpdateHelper:
    _update_function_list = []

    def register(function):
        UpdateHelper._update_function_list.append(function)

    def update():
        for f in UpdateHelper._update_function_list:
            f()

class ChronoException(Exception):
    def __init__(self, message):
        super().__init__(message)
        print(message)

class chronometer:
    def __init__(self, time_length_ms=None):
        self.reset()
        if (time_length_ms):
            self.set(time_length_ms)

    def _update(self):
        self.current_time = millis()
        if(self.is_running):
            if (self.end_time < self.current_time):
                self.is_done = True

    def isDone(self):
        self._update()
        if (self.is_running and self.is_done):
            self.is_running = False
        return self.is_done

    def isRunning(self):
        return self.is_running

    def set(self,time_length_ms):
        if (not self.isRunning()):
            self.reset()
            self.time_length_ms = time_length_ms
            self.start_time = millis()
            self.end_time = self.start_time + time_length_ms
            self.is_done = False
        else:
            raise ChronoException("Chrono is already running.")

    def setAndGo(self, time_length_ms):
        self.set(time_length_ms)
        self.start()

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def restart(self):
        if (self.time_length_ms is not None):
            self.setAndGo(self.time_length_ms)
        else:
            raise ChronoException("Chrono has not been set yet.")

    def reset(self):
        self.start_time = millis()
        self.current_time = millis()
        self.end_time = 0
        self.is_running = False
        self.is_done = False
        self.time_length_ms = None
