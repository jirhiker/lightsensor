# ===============================================================================
# Copyright 2016 ross
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

# ============= standard library imports ========================
import visa
import re
# ============= local library imports  ==========================
from base_sensor import BaseLightSensor

REGEX = re.compile(r'^(NDCV)(?P<value>(\+|-)\d+\.\d+E(\+|-)\d+)')

class Keithley196LightSensor(BaseLightSensor):
    primary_address = 7

    def _setup(self):
        self._dev.write('REN 7{:02n}'.format(self.primary_address))

    def _dev_factory(self):
        rm = visa.ResourceManager()
        return rm.open_resource(self.address)

    def _read_value(self):
        v = self._dev.read()
        m = REGEX.match(v)
        if m:
            return m.group('value')

if __name__ == '__main__':
    k = Keithley196LightSensor()
    k.init()
    print k.read_value()
# ============= EOF =============================================
