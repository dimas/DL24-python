import time
import math
from datetime import time as tm

GET_OUTPUT = 0x10
GET_VOLTAGE = 0x11
GET_CURRENT = 0x12
GET_TIME = 0x13
GET_CAP_AH = 0x14
CAP_WH = 0x15
GET_TEMP = 0x16
GET_LIM_CURR = 0x17
GET_LIM_VOLT = 0x18
GET_TIMER = 0x19

SET_OUTPUT = 0x01
SET_CURRENT_LIMIT = 0x02
SET_VOLTAGE_CUTOFF = 0x03
SET_TIMER = 0x04
RESET_STATS = 0x05

def hex(v):
    return "%02x" % v

def dump(b):
    print(' '.join(map(hex, b)))

class DL24:

    def __init__(self, device):
        self.device = device

    def enable(self):
        self.__writeInt(SET_OUTPUT, 0x0100)

    def disable(self):
        self.__writeInt(SET_OUTPUT, 0x0000)


    def getCurrent(self):
        return self.__readInt(GET_CURRENT) / 1000.

    def getTargetCurrent(self):
        return self.__readInt(GET_LIM_CURR) / 100.

    def setTargetCurrent(self, value):
        self.__writeFloat(SET_CURRENT_LIMIT, value)


    def getVoltage(self):
        return self.__readInt(GET_VOLTAGE) / 1000.

    def getCutoffVoltage(self):
        return self.__readInt(GET_LIM_VOLT) / 100.

    def setCutoffVoltage(self, value):
        self.__writeFloat(SET_VOLTAGE_CUTOFF, value)



    def resetStats(self):
        self.__writeInt(RESET_STATS, 0)


    def getCapacity(self):
        return self.__readInt(GET_CAP_AH) / 1000.


    def getTime(self):
        return self.__readTime(GET_TIME)


    def getTimer(self):
        return self.__readTime(GET_TIMER)

    def setTimer(self, value):
        if value is None:
            seconds = 0
        else:
            seconds = value.second + value.minute * 60 + value.hour * 3600

        self.__writeInt(SET_TIMER, seconds)


    def __sendCommand(self, command, data):
        frame = bytearray([0xB1, 0xB2, command, *data, 0xB6])
        self.device.write(frame)

    def __receiveResponse(self, start_bytes, len_bytes):
        pattern = bytearray(start_bytes)
        pattern_len = len(pattern)
        buf = bytearray()

        # Wait for data mtching the pattern to arrive
        while True:
            buf += self.device.read()

            # Search for our pattern in the buffer
            start = None
            i = 0
            for i in range(len(buf) - pattern_len):
                if buf[i:i+pattern_len] == pattern:
                    start = i
                    break

            if start is not None:
                buf = buf[start:]
                break

            buf = buf[-pattern_len:]

        while len(buf) < len_bytes:
            buf += self.device.read(len_bytes - len(buf))

#        dump(buf)
        return buf

    def __readValue(self, command):
        self.__sendCommand(command, [0, 0])
        ret = self.__receiveResponse([0xCA, 0xCB], 7)

        if ret[5] != 0xCE or ret[6] != 0xCF:
            print("Receive error")
            return None

        return ret

    def __readInt(self, command):
        ret = self.__readValue(command)
        return int.from_bytes(ret[2:5], byteorder='big')

    def __readTime(self, command):
        ret = self.__readValue(command)
        return tm(ret[2], ret[3], ret[4])

    def __writeValue(self, command, data):
        self.__sendCommand(command, data)
        self.__receiveResponse([0x6F], 1)

    def __writeInt(self, command, value):
        self.__writeValue(command, value.to_bytes(2, byteorder='big'))

    def __writeFloat(self, command, value):
        f, i = math.modf(value)
        self.__writeValue(command, [int(i), round(f * 100)])


