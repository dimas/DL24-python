import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import DL24

import unittest
from datetime import time as tm

class DL24TestCase(unittest.TestCase):

    def setUp(self):
        self.device = FakeSerial()
        self.dl24 = DL24.DL24(self.device)

    def test_getCurrent(self):
        self.device.respond(self.bytes2('b1 b2 12 00 00 b6'), self.bytes2('ca cb 00 00 79 ce cf'))

        self.assertEqual(self.dl24.getCurrent(), 0.121)

    def test_getVoltage(self):
        self.device.respond(self.bytes2('b1 b2 11 00 00 b6'), self.bytes2('ca cb 00 0f 8e ce cf'))

        self.assertEqual(self.dl24.getVoltage(), 3.982)

    def test_getCapacity(self):
        self.device.respond(self.bytes2('b1 b2 14 00 00 b6'), self.bytes2('ca cb 00 00 02 ce cf'))

        self.assertEqual(self.dl24.getCapacity(), 0.002)

    def test_getTime(self):
        self.device.respond(self.bytes2('b1 b2 13 00 00 b6'), self.bytes2('ca cb 01 02 03 ce cf'))

        self.assertEqual(self.dl24.getTime(), tm(1, 2, 3))

    def test_getTimer(self):
        self.device.respond(self.bytes2('b1 b2 19 00 00 b6'), self.bytes2('ca cb 01 02 03 ce cf'))

        self.assertEqual(self.dl24.getTimer(), tm(1, 2, 3))

    def test_setTimer(self):
        command = self.bytes2('b1 b2 04 0e 8b b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.setTimer(tm(1, 2, 3))

        self.assertEqual(self.device.get_output(), command)

    def test_setTimer_None(self):
        command = self.bytes2('b1 b2 04 00 00 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.setTimer(None)

        self.assertEqual(self.device.get_output(), command)

    def test_getCutoffVoltage(self):
        self.device.respond(self.bytes2('b1 b2 18 00 00 b6'), self.bytes2('ca cb 00 00 78 ce cf'))

        self.assertEqual(self.dl24.getCutoffVoltage(), 1.2)

    def test_setCutoffVoltage(self):
        command = self.bytes2('b1 b2 03 01 14 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.setCutoffVoltage(1.2)

        self.assertEqual(self.device.get_output(), command)

    def test_getTargetCurrent(self):
        self.device.respond(self.bytes2('b1 b2 17 00 00 b6'), self.bytes2('ca cb 00 00 78 ce cf'))

        self.assertEqual(self.dl24.getTargetCurrent(), 1.2)

    def test_setTargetCurrent(self):
        command = self.bytes2('b1 b2 02 01 14 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.setTargetCurrent(1.2)

        self.assertEqual(self.device.get_output(), command)

    def test_resetStats(self):
        command = self.bytes2('b1 b2 05 00 00 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.resetStats()

        self.assertEqual(self.device.get_output(), command)

    def test_enable(self):
        command = self.bytes2('b1 b2 01 01 00 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.enable()

        self.assertEqual(self.device.get_output(), command)

    def test_disable(self):
        command = self.bytes2('b1 b2 01 00 00 b6')
        self.device.respond(command, self.bytes2('b6'))

        self.dl24.disable()

        self.assertEqual(self.device.get_output(), command)


    def test_unsolicited_data_is_ignored(self):
        # DL24 sends some data evert second.  I do not know the format and meaning of it but the DL24 class should
        # be prepared to deal with it (and ignore it) when waiting for a response to the command it sends
        unsolicited = self.bytes2('ff 55 01 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 15 00 00 00 00 3c 00 00 00 00 10')

        self.device.respond(self.bytes2('b1 b2 11 00 00 b6'), unsolicited + self.bytes2('ca cb 00 00 79 ce cf'))

        self.assertEqual(self.dl24.getVoltage(), 0.121)


    # Shame on me but I did not find how to do private static methods inside a class in Python...
    def bytes2(self, hex_string):
        return bytearray(int(i, 16) for i in hex_string.split(' '))
      


class FakeSerial:
    def __init__(self):
        self.send_buf = bytearray()
        self.recv_buf = bytearray()
        self.request = None
        self.response = None
        self.recv_buf += bytearray([0x6F])


    def write(self, data):
        self.send_buf += bytearray(data)

        if self.request is not None and self.request in self.send_buf:
            self.recv_buf += self.response
            self.request = self.response = None

    def read(self):
        return self.recv_buf

    def get_output(self):
        return self.send_buf

    def respond(self, request_data, response_data):
        self.request = request_data
        self.response = response_data
        pass

if __name__ == '__main__':
    unittest.main()

