# Module to drive an RS485 transceiver
# Created by: Mark Ma (mma@precision-nano.com)
# Created on: 07 Oct 2018

import board
import busio
import digitalio
from pni_libs.helpers import *
from pni_libs.debug import *

class RS485Error (Exception):
    def __init__(self, message):
        super().__init__(message)
        print(message)

class RS485TransferError (Exception):
    def __init__(self, message):
        super().__init__(message)
        print(message)

class RS485_Transceiver:
    def __init__(self, baud, tx, rx, rts, timeout = 100):
        self._is_sending = False
        self._transaction_in_progress = False
        self._cmd_timeout = timeout
        self._io_timeout = 5
        self._eol = "\r"
        self._port = None
        self._rts_pin = None
        self._response = None
        self._response_ready = False
        self._ready_to_send = False
        self._debug_source_str = "rs485"
        self._receiveTimer = chronometer(self._cmd_timeout)
        self._message = None
        self._wait_for_reply = False
        self.send_timer = chronometer()
        self._baudrate = baud
        if (is_hardware_uart(tx,rx)):
            self._port = busio.UART(tx, rx, baudrate=baud, timeout=self._io_timeout)
            self._rts_pin = digitalio.DigitalInOut(rts)
            self._rts_pin.direction = digitalio.Direction.OUTPUT
            self._transceiverSendMode(False)

    def update(self):
        if (self._transaction_in_progress and self._receiveTimer.isDone()):
            self._response = self._receive()
            self._receiveTimer.reset()
            if (self._response is not None):
                self._responseReady = True
            else:
                Debug.msg("Did not received an expected response",
                    Debug.ERROR, source = self._debug_source_str)
                raise RS485TransferError("Did not received an expected response")
        elif ((self._transaction_in_progress == False) and (self._ready_to_send)):
            self._send(self._message, self._wait_for_reply)

    def setReceiveTimeout(self, timeout):
        self._cmd_timeout = timeout

    def setEOL(self, eol):
        self._eol = eol

    def send(self, message, wait_for_reply):
        self._ready_to_send = True
        self._message = message
        self._wait_for_reply = wait_for_reply

    def _send(self, message, wait_for_reply):
        if (self._transaction_in_progress == False):
            self._ready_to_send = False
            self._responseReady = False
            self._transaction_in_progress = True
            msg_length = len(message)
            self._transceiverSendMode(True)
            delay(1)
            n_written = self._port.write(bytearray(message + self._eol))
            # self._port.write(bytearray(self._eol))
            delay(self.delayLength(msg_length))
            delay(1)
            self._transceiverSendMode(False)
            self._port.reset_input_buffer()
            if (wait_for_reply):
                self._receiveTimer.setAndGo(self._cmd_timeout)
            else:
                self._transaction_in_progress = False
            Debug.msg("Message sent: " + message,
                Debug.DEBUG, source = self._debug_source_str)
        else:
            Debug.msg("Cannot send, another transmission is already in progress",
                Debug.ERROR, source = self._debug_source_str)

    def isResponseReady(self):
        return self._response_ready

    def getResponse(self):
        self._response_ready = False
        return self._response

    def delayLength(self, msg_length):
        # correction factor of 1.2 is applied
        return msg_length * 8 / self._baudrate * 1000 * 1.2

    def isOpen(self):
        open = False
        if (self._port is not None):
            open = True
        return open

    def isBusy(self):
        return self._transaction_in_progress

    def _receive(self):
        response_str = None
        response = self._port.read(64)
        if (response is not None):
            response_str = ''.join([chr(b) for b in response])
            self._response_ready = True
            Debug.msg("Message received: " + response_str,
                Debug.DEBUG, source = self._debug_source_str)
        else:
            Debug.msg("Did not receive an reply to a previous command",
                Debug.ERROR, source = self._debug_source_str)
        self._transaction_in_progress = False
        return response_str

    def getTransceiverMode(self):
        mode = None
        if (self._rts_pin is not None):
            mode =  self._rts_pin.value
        else:
            Debug.msg("The RTS pin has not been configured", Debug.ERROR,
                source = self._debug_source_str)
        return mode

    def _transceiverSendMode(self, mode):
        if (self._rts_pin is not None):
            self._rts_pin.value = mode
        else:
            Debug.msg("Can't set pin to send mode, pin not configured.", Debug.ERROR,
                source = self._debug_source_str)
