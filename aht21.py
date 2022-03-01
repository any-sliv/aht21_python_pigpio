"""The MIT License (MIT)
Copyright © 2022 
Maciej Sliwinski https://github.com/any-sliv/aht21_python_pigpio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

import pigpio
import time

class AHT21:
    _i2cAddr = 0x38

    def __init__(self, i2cNumber):
        """AHT21 constructor. Returns True/False as a result of initalization."""

        self.pi = pigpio.pi()
        self.handle = self.pi.i2c_open(i2cNumber, self._i2cAddr)
        assert(self.handle)

        self._calibrate()

    def _write(self, data):
        self.pi.i2c_write_device(self.handle, bytearray(data))

    def _read(self, reg, len):
        return self.pi.i2c_read_i2c_block_data(self.handle, reg, len)[1]

    def _calibrate(self):
        cal_cmd = [0xbe, 0x08, 0x00]
        self._write(cal_cmd)
        #todo delay perf counter?? need 50 useconds 
        time.sleep(0.01)
        self._write([0x71]) # get status register
        res = self._read(self._i2cAddr, 1)
        if not res[0] & 0x68 == 0x08:
            print("Error calibrating.")
            return False
        else:
            print("Calibrating ok.")
            return True

    def Read(self):
        """Returns tuple (temp, humidity). Blocking delay at readout. """
        read_cmd = [0xac, 0x33, 0x00]
        self._write(read_cmd)
        #todo delay perf counter?? need 80ms 
        time.sleep(0.1)

        res = self._read(self._i2cAddr, 6)

        calc_hum = ((res[1] << 16) | (res[2] << 8) | res[3]) >> 4;
        calc_temp = ((res[3] & 0x0F) << 16) | (res[4] << 8) | res[5];

        rh = calc_hum * 100 / 1048576;
        temp = calc_temp * 200 / 1048576 - 50;

        return (temp, rh)