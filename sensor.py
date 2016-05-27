# ===============================================================================
# Copyright 2016 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
from random import random

from pyface.message_dialog import warning
from traits.api import HasTraits, Str

# ============= standard library imports ========================
import serial
import time


# ============= local library imports  ==========================


class LightSensor(HasTraits):
    address = Str

    _dev = None
    _simulation = False

    def init(self):
        addr=self.address
        try:
            self._dev = serial.Serial(addr, baudrate=115200)
        except OSError:
            warning(None, 'Invalid device address. {}. Entering simulation mode'.format(addr))
            self._simulation = True

    def close(self):
        self._dev.close()

    def read_value(self):
        if self._simulation:
            return 10 * random()

        st = time.time()
        timeout = 5
        dev = self._dev
        while 1:
            inw = dev.inWaiting()
            if inw:
                break

            if time.time() - st > timeout:
                return
            time.sleep(0.01)

        resp = dev.readline()
        resp = resp.strip()
        if resp:
            return float(resp)

# ============= EOF =============================================
# # ===============================================================================
# # Copyright 2016 Jake Ross
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# # http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# # ===============================================================================
#
# # ============= enthought library imports =======================
# # ============= standard library imports ========================
# from numpy import random
# import time
# import serial
# import matplotlib.pyplot as plt
#
# # ============= local library imports  ==========================
#
#
# # ========Configuration==========================================
# ADDRESS = 'usbmodem1411'
# DURATION = 500
# PATH = '/Users/ross/Desktop/light.csv'
# USE_PLOT = True
#
#
# # ===============================================================
#
# class LightSensor:
#     def __init__(self):
#         addr = '/dev/tty.{}'.format(ADDRESS)
#         self._handle = serial.Serial(addr)
#
#     def collect(self, p, duration):
#         """
#
#         :param duration: in seconds
#         :return:
#         """
#         if USE_PLOT:
#             ts, data0s, data1s, luxs = [], [], [], []
#             plotargs = self._plot(ts, data0s, data1s, luxs)
#
#         st = time.time()
#         with open(p, 'w') as wfile:
#
#             while time.time() - st < duration:
#                 ct = time.time() - st
#                 args = self._read()
#
#                 if args is not None:
#                     data0, data1, lux, status = args
#                     if USE_PLOT:
#                         ts.append(ct)
#                         data0s.append(data0)
#                         data1s.append(data1)
#                         luxs.append(lux)
#                         self._update_plot_data(ts, data0s, data1s, luxs, plotargs)
#
#                     line = '{},{},{},{},{}\n'.format(ct, data0, data1, lux, status)
#                     print 'row={}'.format(line.strip())
#                     wfile.write(line)
#                 time.sleep(0.01)
#
#         if USE_PLOT:
#             plt.ioff()
#             plt.show()
#
#     def _update_plot_data(self, ts, data0, data1, luxs, plotargs):
#         ax0, ax1, ax2, p0, p1, p2 = plotargs
#         p0.set_xdata(ts)
#         p0.set_ydata(data0)
#         self._set_limits(ax0, data0)
#
#         p1.set_xdata(ts)
#         p1.set_ydata(data1)
#         self._set_limits(ax1, data1)
#
#         p2.set_xdata(ts)
#         p2.set_ydata(luxs)
#         self._set_limits(ax2, luxs)
#
#         tmi, tma = min(ts), max(ts)
#         ax0.set_xlim(tmi, tma)
#         ax1.set_xlim(tmi, tma)
#         ax2.set_xlim(tmi, tma)
#         plt.draw()
#         plt.pause(0.0001)
#
#     def _set_limits(self, ax, y):
#         ymi, yma = min(y), max(y)
#         pad = (yma - ymi) * 0.1
#         ax.set_ylim(ymi - pad, yma + pad)
#
#     def _plot(self, ts, y0, y1, lxs):
#
#         plt.ion()
#
#         fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(7, 9))
#
#         ax0.set_title('Light Sensor')
#
#         p0, = ax0.plot(ts, y0)
#         p1, = ax1.plot(ts, y1)
#         p2, = ax2.plot(ts, lxs)
#
#         ax0.set_ylabel('Data0')
#         ax1.set_ylabel('Data1')
#         ax2.set_ylabel('Lux')
#
#         ax2.set_xlabel('Time(s)')
#         return ax0, ax1, ax2, p0, p1, p2
#
#     def _read(self):
#         # return random.rand(4)
#
#         st = time.time()
#         timeout = 5
#         while 1:
#             inw = self._handle.inWaiting()
#             if inw:
#                 break
#
#             if time.time() - st > timeout:
#                 return
#             time.sleep(0.01)
#
#         resp = self._handle.readline()
#         resp = resp.strip()
#         if resp:
#             return float(resp.strip()), 0, 0, 0
#             # return data0, data1, lux, status
#             # args = resp.split(' ')
#             # try:
#             #     if args[0] == 'data0:' and args[2] == 'data1:' and args[4] == 'lux:':
#             #         data0 = args[1]
#             #         data1 = args[3]
#             #         lux = args[5]
#             #         status = args[6]
#             #         return data0, data1, lux, status
#             # except IndexError, e:
#             #     print e
#             #     pass
#
#
# if __name__ == '__main__':
#     ls = LightSensor()
#     ls.collect(PATH, DURATION)

# ============= EOF =============================================
