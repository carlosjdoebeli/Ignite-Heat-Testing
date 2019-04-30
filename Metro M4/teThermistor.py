
import board
import busio
import digitalio
import math
from analogio import AnalogIn
from pni_libs.helpers import *
from pni_libs.debug import *
from pni_libs.rs485 import *

class TeThermistor:

    TEMP_TABLE = ([
            32650.9,31030.8,29500.5,28054.4,26687.5,25395,24172.5,23015.9,
            21921.2,20884.7,19903.2,18973.3,18092.2,17256.9,16464.9,15713.7,
            15000.9,14324.5,13682.3,13072.6,12493.3,11943,11419.9,10922.7,
            10449.8,10000,9572,9164.7,8777,8407.7,8056.1,7721,7401.7,7097.3,
            6807.1,6530.3,6266.2,6014.3,5773.8,5544.2,5325,5115.6,4915.6,
            4724.4,4541.7,4367,4200,4040.2,3887.4,3741.1,3601.1,3467,3338.7,
            3215.8,3098,2985.2,2877,2773.3,2673.9,2578.6,2487.1,2399.4,2315.2,
            2234.4,2156.8,2082.3,2010.8,1942.1,1876,1812.6,1751.6,1693,1636.6,
            1582.4,1530.2,1480.1,1431.8,1385.3,1340.6,1297.5,1256.1,1216.1,
            1177.7,1140.6,1104.9,1070.5,1037.3,1005.3,974.4,944.7,916,888.3,
            861.5,835.8,810.9,786.8,763.6,741.2,719.6,698.6,678.4,658.9,640,
            621.8,604.2,587.1,570.6,554.6,539.2,524.3,509.8,495.9,482.3,469.2,
            456.5,444.2,432.3,420.8,409.7,398.8,388.4,378.2,368.3,358.8,349.5,
            340.6
            ])

    def __init__(self, pin, id, pullup_resistor=3300, probe_offset=0.0, loop_time=500):
        self.pullup_resistor = pullup_resistor
        self.pin = AnalogIn(pin)
        self._data_str = "Thermistor " + str(id) + " temp"
        self.chrono = chronometer()
        self.chrono.setAndGo(loop_time)
        self._temp_offset = probe_offset

    def update(self):
        if self.chrono.isDone():
            try:
                temp = self.getTemp() + self._temp_offset
                Debug.msg(str(temp),
                        Debug.DATA, source=self._data_str)
            except ValueError:
                #just do nothing if the value is outside of 0 - 120
                pass
            self.chrono.setAndGo(TeThermistor.LOOP_TIME)

    def getTemp(self):
        V = self.getVoltage()
        resistance = ((V * self.pullup_resistor)
                / (self.pin.reference_voltage * 1000 - V))
        return self.tempLookup(resistance)

    #return voltage in millivolts
    def getVoltage(self):
        return (self.pin.value * self.pin.reference_voltage * 1000) / 65535

    #simple binary search
    def tempLookup(self, resistance):
        err = "resistance value is not contained within table"
        L = 0
        length = len(TeThermistor.TEMP_TABLE)
        R = length - 1

        while L <= R:
            mid = math.floor((L + R) / 2)
            if TeThermistor.TEMP_TABLE[mid] > resistance:
                if mid == length - 1:
                    raise ValueError(err)
                elif TeThermistor.TEMP_TABLE[mid + 1] < resistance:
                    return self.linearize(mid, resistance)
                L = mid + 1
            elif TeThermistor.TEMP_TABLE[mid] < resistance:
                if mid == 0:
                    raise ValueError(err)
                elif TeThermistor.TEMP_TABLE[mid - 1] > resistance:
                    return self.linearize(mid - 1, resistance)
                R = mid - 1
            else:
                return mid
        raise ValueError(err)

    def linearize(self, lowIndex, resistance):
        return lowIndex + float((TeThermistor.TEMP_TABLE[lowIndex] - resistance)
                / (TeThermistor.TEMP_TABLE[lowIndex]
                - TeThermistor.TEMP_TABLE[lowIndex + 1]))
