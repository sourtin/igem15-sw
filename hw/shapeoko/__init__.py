#!/usr/bin/env python
"""shapeoko module
      Driver: defines a driver to interface with the shapeoko's
              marlin firmware in gcode over a serial port
      XY: defines an XY stage object which can be used with
          the rest of the library
      Empty: a blank head for testing purposes so that
             the stage can be moved around"""

from .interface import XY
from .driver import Shapeoko as Driver
Empty = XY.Empty
Axes = Driver.Axes

