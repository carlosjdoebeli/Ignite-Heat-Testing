# Debug module for writing to a log file and/or printing messages over serial
# Created by: Mark Ma (mma@precision-nano.com)
# Created on: 06 Oct 2018

import board
import busio
import supervisor
import math
from pni_libs.helpers import *

class DebugException(Exception):
    def __init__(self, message):
        super().__init__(message)
        print(message)

class Debug:
    kVersionMajor = 1
    kVersionMinor = 0
    kVersion = [kVersionMajor,kVersionMinor]
    kMaxMessageLength = 49
    DATA = -1
    OFF = 0
    FATAL = 1
    ERROR = 2
    INFO = 3
    DEBUG = 4
    ALL = 5
    _configured = False
    _log_filename = None
    _log_file = None
    _can_write_to_file = False
    _print_data = True
    severity_strings = { OFF: "OFF", FATAL: "FATAL",
                         ERROR: "ERROR", DEBUG: "DEBUG",
                         INFO: "INFO", ALL: "ALL",
                         DATA: "DATA"}
    debug_level = 3
    program_start_time = 0
    begun = False

    def __init__(self):
        error_msg = "This module is not designed to be used as an instance, " \
            "call the class functions directly"
        Debug.msg(error_msg, Debug.FATAL, "Debug")
        raise ValueError("The debug class cannot be instanced")

    def _isSerialConnected():
        return supervisor.runtime.serial_connected

    def begin(debug_level = INFO, log_filename = None):
        Debug.begun = True
        Debug.setDebugLevel(debug_level)
        Debug.setProgramStartTime(millis())
        Debug.printHeader()
        Debug.msg("Debug configured", Debug.INFO, "Debug")
        if (log_filename is not None):
            Debug.msg("Logging to {}".format(log_filename), Debug.INFO, "Debug")
            Debug.setLogFilename(log_filename)

    # Define the filename of the log file, and opens it for writing
    def setLogFilename(log_filename):
        try:
            Debug._log_filename = log_filename
            Debug._log_file = open(Debug._log_filename, "rw")
            Debug._can_write_to_file = True
        except OSError:
            Debug.msg("Cannot access onboard storage",
                      Debug.ERROR, "Debug")
            Debug.msg("Onboard logging disabled when USB is connected",
                      Debug.INFO, "Debug")

    def disableLogToFile():
        if (Debug._can_write_to_file):
            Debug._can_write_to_file = False
            Debug.msg("Logging to storage is disabled.",
                      Debug.INFO, "Debug")
        else:
            Debug.msg("Logging to storage was not turned on",
                      Debug.INFO, "Debug")
            Debug.msg("will do nothing.",
                      Debug.INFO, "Debug")


    def setDebugLevel(debug_level):
        Debug.debug_level = debug_level

    def setPrintData(print_data):
        Debug._print_data = print_data

    def getDebugLevel():
        return Debug.debug_level

    def setProgramStartTime(start_time):
        Debug.program_start_time = start_time

    def _has_begun():
        return Debug.begun

    def printHeader():
        if (Debug._has_begun() == False):
            return
        header_str = "{:^8}|{:^8}|{:^50}|{:^10}".format("TIME",
            "TYPE", "MESSAGE", "SOURCE")
        line_str = "{:-^80}".format("")
        if (Debug._isSerialConnected()):
            print(header_str)
            print(line_str)
        if (Debug._can_write_to_file == True):
            Debug._log_file.write(header_str)
            Debug._log_file.write("\n")
            Debug._log_file.write(line_str)
            Debug._log_file.write("\n")

    def msg(debug_message, msg_debug_level, source=None):
        if ((msg_debug_level == Debug.DATA) and (not Debug._print_data)):
            return
        elif (Debug._has_begun() == False):
            return
        if (msg_debug_level <= Debug.debug_level):
            message_length = len(debug_message)
            n_messages = math.ceil(message_length / Debug.kMaxMessageLength)
            for i in range(0, n_messages):
                msg_start_idx = i * Debug.kMaxMessageLength
                msg_end_idx = msg_start_idx + Debug.kMaxMessageLength
                line_wrap_char = ''
                if (msg_end_idx > (message_length)):
                    msg_end_idx = message_length
                else:
                    line_wrap_char = '-'
                Debug._msg(debug_message[msg_start_idx:msg_end_idx]+line_wrap_char,
                    msg_debug_level, source=source)

    def _msg(debug_message, msg_debug_level, source=None):
        time_since_start = millis() - Debug.program_start_time
        if (source is None):
            source = "Not Given"
        debug_str = "{:0>8.0f}|{:<8}|{:<50}|{:<10}".format(time_since_start,
            Debug.severity_strings[msg_debug_level], debug_message, source)
        if (Debug._isSerialConnected()):
            print(debug_str)
        if (Debug._can_write_to_file == True):
            Debug._log_file.write(debug_str)
            Debug._log_file.write("\n")
