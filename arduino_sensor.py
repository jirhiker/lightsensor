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
# ============= standard library imports ========================
import serial
import time

# ============= local library imports  ==========================
from base_sensor import BaseLightSensor


class ArduinoLightSensor(BaseLightSensor):
    def close(self):
        self._dev.close()

    def _dev_factory(self):
        return serial.Serial(self.address, baudrate=115200)

    def _read_value(self):
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
        return resp.strip()


# ============= EOF =============================================
