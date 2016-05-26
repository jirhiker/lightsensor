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

# ============= standard library imports ========================
import glob
import time
import os
from numpy import hstack

# ============= local library imports  ==========================

# adapted from https://github.com/enthought/chaco/blob/master/examples/demo/advanced/data_stream.py
from paths import unique_path
from sensor import LightSensor


class Viewer(HasTraits):
    """ This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a
    Chaco plot.
    """
    index = Array

    data = Array

    view = View(ChacoPlotItem("index", "data",
                              # type_trait="plot_type",
                              resizable=True,
                              x_label="Time",
                              y_label="Signal",
                              color="blue",
                              bgcolor="white",
                              border_visible=True,
                              border_width=1,
                              padding_bg_color="lightgray",
                              width=800,
                              height=380,
                              marker_size=2,
                              show_label=False),
                resizable=True,
                buttons=["OK"],
                width=800, height=500)


class Controller(HasTraits):
    # A reference to the plot viewer object
    viewer = Instance(Viewer)

    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)
    window = Float(10)
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
        self.max_num_points = int(self.window * 10)

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
        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        cur_index = self.viewer.index
        new_data = hstack((cur_data[-self.max_num_points + 1:], [v]))
        new_index = hstack((cur_index[-self.max_num_points + 1:], [ct]))
        self.viewer.index = new_index
        self.viewer.data = new_data

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
                handler=LSHandler,
                resizable=True)

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(100, self.controller.timer_tick)
        return super(LightSensorApplication, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(100, self.controller.timer_tick)
        return super(LightSensorApplication, self).configure_traits(*args, **kws)

    def _controller_default(self):
        ports = glob.glob('/dev/tty.usb*')
        return Controller(viewer=self.viewer,
                          ports=ports+['foo'])


if __name__ == '__main__':
    app = LightSensorApplication()
    app.configure_traits()
# ============= EOF =============================================
# """
# Visualization of simulated live data stream
#
# Shows how Chaco and Traits can be used to easily build a data
# acquisition and visualization system.
#
# Two frames are opened: one has the plot and allows configuration of
# various plot properties, and one which simulates controls for the hardware
# device from which the data is being acquired; in this case, it is a mockup
# random number generator whose mean and standard deviation can be controlled
# by the user.
# """
#
# # Major library imports
# import numpy as np
#
# # Enthought imports
# from traits.api import (Array, Callable, Enum, Float, HasTraits, Instance, Int,
#                         Trait)
# from traitsui.api import Group, HGroup, Item, View, spring, Handler
# from pyface.timer.api import Timer
#
# # Chaco imports
# from chaco.chaco_plot_editor import ChacoPlotItem
#
#
# class Viewer(HasTraits):
#     """ This class just contains the two data arrays that will be updated
#     by the Controller.  The visualization/editor for this class is a
#     Chaco plot.
#     """
#     index = Array
#
#     data = Array
#
#     plot_type = Enum("line", "scatter")
#
#     view = View(ChacoPlotItem("index", "data",
#                               type_trait="plot_type",
#                               resizable=True,
#                               x_label="Time",
#                               y_label="Signal",
#                               color="blue",
#                               bgcolor="white",
#                               border_visible=True,
#                               border_width=1,
#                               padding_bg_color="lightgray",
#                               width=800,
#                               height=380,
#                               marker_size=2,
#                               show_label=False),
#                 HGroup(spring, Item("plot_type", style='custom'), spring),
#                 resizable = True,
#                 buttons = ["OK"],
#                 width=800, height=500)
#
#
# class Controller(HasTraits):
#
#     # A reference to the plot viewer object
#     viewer = Instance(Viewer)
#
#     # Some parameters controller the random signal that will be generated
#     distribution_type = Enum("normal", "lognormal")
#     mean = Float(0.0)
#     stddev = Float(1.0)
#
#     # The max number of data points to accumulate and show in the plot
#     max_num_points = Int(100)
#
#     # The number of data points we have received; we need to keep track of
#     # this in order to generate the correct x axis data series.
#     num_ticks = Int(0)
#
#     # private reference to the random number generator.  this syntax
#     # just means that self._generator should be initialized to
#     # random.normal, which is a random number function, and in the future
#     # it can be set to any callable object.
#     _generator = Trait(np.random.normal, Callable)
#
#     view = View(Group('distribution_type',
#                       'mean',
#                       'stddev',
#                       'max_num_points',
#                       orientation="vertical"),
#                       buttons=["OK", "Cancel"])
#
#     def timer_tick(self, *args):
#         """
#         Callback function that should get called based on a timer tick.  This
#         will generate a new random data point and set it on the `.data` array
#         of our viewer object.
#         """
#         # Generate a new number and increment the tick count
#         new_val = self._generator(self.mean, self.stddev)
#         self.num_ticks += 1
#
#         # grab the existing data, truncate it, and append the new point.
#         # This isn't the most efficient thing in the world but it works.
#         cur_data = self.viewer.data
#         new_data = np.hstack((cur_data[-self.max_num_points+1:], [new_val]))
#         new_index = np.arange(self.num_ticks - len(new_data) + 1,
#                               self.num_ticks + 0.01)
#
#         self.viewer.index = new_index
#         self.viewer.data = new_data
#         return
#
#     def _distribution_type_changed(self):
#         # This listens for a change in the type of distribution to use.
#         if self.distribution_type == "normal":
#             self._generator = np.random.normal
#         else:
#             self._generator = np.random.lognormal
#
#
# class DemoHandler(Handler):
#
#     def closed(self, info, is_ok):
#         """ Handles a dialog-based user interface being closed by the user.
#         Overridden here to stop the timer once the window is destroyed.
#         """
#
#         info.object.timer.Stop()
#         return
#
#
# class Demo(HasTraits):
#     controller = Instance(Controller)
#     viewer = Instance(Viewer, ())
#     timer = Instance(Timer)
#     view = View(Item('controller', style='custom', show_label=False),
#                 Item('viewer', style='custom', show_label=False),
#                 handler=DemoHandler,
#                 resizable=True)
#
#     def edit_traits(self, *args, **kws):
#         # Start up the timer! We should do this only when the demo actually
#         # starts and not when the demo object is created.
#         self.timer=Timer(100, self.controller.timer_tick)
#         return super(Demo, self).edit_traits(*args, **kws)
#
#     def configure_traits(self, *args, **kws):
#         # Start up the timer! We should do this only when the demo actually
#         # starts and not when the demo object is created.
#         self.timer=Timer(100, self.controller.timer_tick)
#         return super(Demo, self).configure_traits(*args, **kws)
#
#     def _controller_default(self):
#         return Controller(viewer=self.viewer)
#
#
# # NOTE: examples/demo/demo.py looks for a 'demo' or 'popup' or 'modal popup'
# # keyword when it executes this file, and displays a view for it.
# popup=Demo()
#
#
# if __name__ == "__main__":
#     popup.configure_traits()
