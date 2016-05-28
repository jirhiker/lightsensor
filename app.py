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
from chaco.chaco_plot_editor import ChacoPlotItem
from pyface.timer.timer import Timer
from traits.api import HasTraits, Int, Float, Instance, Array, Enum, Bool, Button, Str, List
from traitsui.api import View, Item, HGroup, Handler, spring, Group, UItem, EnumEditor
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData

# ============= standard library imports ========================
import glob
import time
import os
from numpy import hstack, r_, ones, convolve, asarray

# ============= local library imports  ==========================

# adapted from https://github.com/enthought/chaco/blob/master/examples/demo/advanced/data_stream.py
from paths import unique_path
from sensor import LightSensor

PERIOD = 250

def smooth(x, window_len=6, window='hanning'):
    """
    avaliable windows=['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    """
    x = asarray(x)
    s = r_[2 * x[0] - x[window_len - 1::-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = ones(window_len, 'd')
    else:
        mod = __import__('numpy', fromlist=[window])
        func = getattr(mod, window)
        w = func(window_len)

    y = convolve(w / w.sum(), s, mode='same')
    return y[window_len:-window_len + 1]


class Viewer(HasTraits):
    """
    """

    def __init__(self, *args, **kw):
        super(Viewer, self).__init__(*args, **kw)

        self.pd = ArrayPlotData()
        self.pd.set_data('index', [])
        self.pd.set_data('sindex', [])

        self.pd.set_data('intensity', [])
        self.pd.set_data('sintensity', [])

        self.plot = Plot(data=self.pd)
        self.plot.value_range.tight_bounds = False
        self.plot.value_range.margin = 0.25
        self.plot.plot(('index','intensity'), type='scatter', marker='circle', marker_size=1.5)
        self.plot.plot(('sindex','sintensity'), color='green', line_width=1.5)

    def traits_view(self):
        v = View(UItem('plot', editor=ComponentEditor()))
        return v


class Controller(HasTraits):
    # A reference to the plot viewer object
    viewer = Instance(Viewer)

    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)
    window = Float
    recording = Bool
    record_button = Button
    stop_button = Button
    port = Str
    ports = List
    view = View(HGroup(UItem('record_button', enabled_when='not _recording and device'),
                       UItem('stop_button', enabled_when='_recording and device'),
                       Item('window'),
                       UItem('port', editor=EnumEditor(name='ports'))),
                buttons=["OK", "Cancel"])
    device = Instance(LightSensor)
    start_time = 0
    _recording = Bool(False)

    def _port_changed(self):
        if self.port:
            self.start_time = time.time()
            if self.device:
                self.device.close()

            dev = LightSensor(address=self.port)
            dev.init()
            self.device = dev

    def _window_changed(self):
        self.max_num_points = int(self.window*1000/float(PERIOD))

    def timer_tick(self, *args):
        """
        Callback function that should get called based on a timer tick.  This
        will generate a new random data point and set it on the `.data` array
        of our viewer object.
        """
        if not self.device:
            return

        # Generate a new number and increment the tick count
        t = time.time()
        ct = t - self.start_time
        v = self.device.read_value()
        if v is None:
            return

        data = self.viewer.pd
        index = data.get_data('index')
        value1 = data.get_data('intensity')

        value1 = hstack((value1[-self.max_num_points + 1:], [v]))
        index = hstack((index[-self.max_num_points + 1:], [ct]))

        data.set_data('intensity', value1)
        data.set_data('index', index)

        if len(index)>11:
            y = smooth(value1)
            data.set_data('sintensity', y)
            data.set_data('sindex', index)

        if self._recording:
            with open(self._path, 'a') as rfile:
                rfile.write('{},{},{}\n'.format(t, ct, v))

    def _record_button_fired(self):
        root = os.path.join(os.path.expanduser('~'), 'Desktop', 'lightsensor_data')
        if not os.path.isdir(root):
            os.mkdir(root)

        self._path = unique_path(root, 'data')
        self._recording = True

    def _stop_button_fired(self):
        self._recording = False


class LSHandler(Handler):
    def closed(self, info, is_ok):
        """ Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()
        return


class LightSensorApplication(HasTraits):
    controller = Instance(Controller)
    viewer = Instance(Viewer, ())
    timer = Instance(Timer)
    view = View(Item('controller', style='custom', show_label=False),
                Item('viewer', style='custom', show_label=False),
                title='LightSensor App',
                handler=LSHandler,
                resizable=True)

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(PERIOD, self.controller.timer_tick)
        return super(LightSensorApplication, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(PERIOD, self.controller.timer_tick)
        return super(LightSensorApplication, self).configure_traits(*args, **kws)

    def _controller_default(self):
        ports = glob.glob('/dev/tty.usb*')
        return Controller(viewer=self.viewer,
                          window=500,
                          ports=ports)


if __name__ == '__main__':
    app = LightSensorApplication()
    app.configure_traits()
# ============= EOF =============================================
