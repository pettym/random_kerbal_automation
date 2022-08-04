#!/usr/bin/env python3


import time
import evdev

from pprint import pprint

from evdev import UInput, ecodes
from evdev import AbsInfo
from evdev import ecodes as e

#value=0, min=0, max=255, fuzz=0, flat=0, resolution=0

caps = {
    ecodes.EV_ABS: [
    #(ecodes.ABS_X, AbsInfo(0, -32767, 32767, 0, 0, 0)),
    (ecodes.ABS_X, AbsInfo(0, -1024, 1024, 0, 0, 0)),
        ]
}


dev = UInput(caps, name='testing', version=0x3)


        
while True:
    for value in list(range(-1024,1024))+list(range(1024,-1024,-1)):
        dev.write(ecodes.EV_ABS, ecodes.ABS_X, value)
        dev.syn()
        time.sleep(0.01)
