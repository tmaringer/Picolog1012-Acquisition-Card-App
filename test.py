#
# Copyright (C) 2019 Pico Technology Ltd. See LICENSE file for terms.
#
# PL1000 SINGLE MODE EXAMPLE
# This example opens a pl1000 device, sets up the device for capturing data from channel 1.
# Then this example collect a sample from channel 1 and displays it on the console.

import ctypes
import numpy as np
from picosdk.pl1000 import pl1000 as pl
import pyqtgraph as pg
import pyqtgraph.exporters
from picosdk.functions import adc2mVpl1000, assert_pico_ok
from time import sleep
from time import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# open PicoLog 1000 device
status["openUnit"] = pl.pl1000OpenUnit(ctypes.byref(chandle))
assert_pico_ok(status["openUnit"])
try:
    # set sampling interval
    status["SetDo"] = pl.pl1000SetDo(chandle, 1, 1)
    usForBlock = ctypes.c_uint32(100000)
    noOfValues = ctypes.c_uint32(10000)
    channels = ctypes.c_int16(9)
    status["setInterval"] = pl.pl1000SetInterval(chandle, ctypes.byref(usForBlock), noOfValues, ctypes.byref(channels), 1)
    assert_pico_ok(status["setInterval"])
    print(usForBlock.value)
    # start streaming
    mode = pl.PL1000_BLOCK_METHOD["BM_STREAM"]
    status["run"] = pl.pl1000Run(chandle, 10000, mode)
    sleep(usForBlock.value / 1000000)
    values = (ctypes.c_uint16 * noOfValues.value)()
    oveflow = ctypes.c_uint16()
    status["getValues"] = pl.pl1000GetValues(chandle, ctypes.byref(values), ctypes.byref(noOfValues), ctypes.byref(oveflow), None)
    # convert ADC counts data to mV
    maxADC = ctypes.c_uint16()
    status["maxValue"] = pl.pl1000MaxValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maxValue"])
    inputRange = 2500
    mVValues =  adc2mVpl1000(values, inputRange, maxADC)
    print(str(len(adc2mVpl1000(values, inputRange, maxADC))) + " elements")
    print(str(len(adc2mVpl1000(values, inputRange, maxADC))/(usForBlock.value/1000000)) + " S/s")
    # create time data
    array = np.array(mVValues)
    print(mVValues[0])
    array = (array - array[0])/(0.040*1000)
    interval = (0.000001 * usForBlock.value)/(noOfValues.value * 1)
    timeMs = np.linspace(0, (len(mVValues)) * interval, len(mVValues))
    status["SetDo"] = pl.pl1000SetDo(chandle, 0, 1)
    # plot data
    test = pg.plot()
    test.plot(timeMs, array)
    test.setLabel('bottom', "time", units='s')
    test.show()
    if __name__ == '__main__':
        import sys

        if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
            pg.QtGui.QApplication.exec_()
except:
    # close PicoLog 1000 device
    status["closeUnit"] = pl.pl1000CloseUnit(chandle)
    assert_pico_ok(status["closeUnit"])

    # display status returns
    print(status)
# close PicoLog 1000 device
status["closeUnit"] = pl.pl1000CloseUnit(chandle)
assert_pico_ok(status["closeUnit"])

# display status returns
print(status)