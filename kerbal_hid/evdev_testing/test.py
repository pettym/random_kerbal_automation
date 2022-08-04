#!/usr/bin/env python3


import time
import struct

import evdev
from evdev import ecodes

from pprint import pprint






def test(event):
    name = ecodes.bytype[event.type][event.code]
    if isinstance(name, list): name = name[0]
    return (name, event.value)

def value_print(data):
    keys = sorted(data.keys())
    out = ((str(key), str(data[key])) for key in keys)
    out = [ f"{value.rjust(3)} : {key}" for key,value in out ]
    
    print("\n\n" + "\n".join(out))






device_path = '/dev/input/by-id/usb-Sony_Interactive_Entertainment_Wireless_Controller-if03-event-joystick'
#device_path = '/dev/input/js0'
device = evdev.InputDevice(device_path)

caps = device.capabilities(verbose=True)


key_list = ['ABS_RX','ABS_RY','ABS_RZ','ABS_X','ABS_Y','ABS_Z']
data = list()
x = None

try:
    for event in device.read_loop():
        key, value = test(event)
        if key == 'ABS_RZ': x = event
        if key == 'SYN_REPORT': data.append(x)
except KeyboardInterrupt:
    with open('filter_testing/record.floats', 'wb') as file:
        for line in data:
            if line:
                _ = file.write(struct.pack('<f', line.value))
    



##buffer = dict()
##interval = 1/30
##t = time.time() + interval
##for event in device.read_loop():
##    key, value = test(event)
##    if key == 'SYN_REPORT': data.append(event.timestamp())
##    buffer.update({key:value})
##    
##    if time.time() > t:
##        value_print(buffer)
##        t = time.time()+interval
        
        
        
        
