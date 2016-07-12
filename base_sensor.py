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
from pyface.message_dialog import warning
from traits.api import HasTraits, Str
# ============= standard library imports ========================
from random import random
# ============= local library imports  ==========================


class BaseLightSensor(HasTraits):
    address = Str

    _dev = None
    _simulation = False

    def init(self):
        try:
            self._dev = self._dev_factory()
        except BaseException, e:
            print e
            warning(None, 'Invalid device address. {}. Entering simulation mode'.format(self.address))
            self._simulation = True
            return

        self._setup()

    def close(self):
        pass

    def read_value(self):
        if self._simulation:
            return 10 * random()
        v = self._read_value()

        if v:
            return float(v)

    def _setup(self):
        pass

    def _dev_factory(self):
        raise NotImplementedError

    def _read_value(self):
        raise NotImplementedError

# ============= EOF =============================================
