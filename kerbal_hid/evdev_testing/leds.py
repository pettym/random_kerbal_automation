#!/usr/bin/env python3

import glob
import time

path = "/sys/devices/pci0000:00/0000:00:01.3/0000:03:00.0/usb1/1-10/1-10.3/1-10.3:1.3/0003:054C:09CC.000A/leds"

colors = {
'red': glob.glob(f'{path}/*red/brightness')[0],
'green':glob.glob(f'{path}/*green/brightness')[0],
'blue':glob.glob(f'{path}/*blue/brightness')[0],
'global': glob.glob(f'{path}/*global/brightness')[0],
    }


def write(paths, value):
    value = str(int(value))

    if isinstance(paths, str): paths = [paths]

    for path in paths:    
        with open(path, 'w') as file:
            file.write(value)


red = colors['red']
green = colors['green']
blue = colors['blue']

for _ in range(20):
    write([red, green], 255)
    time.sleep(0.3)
    write([red, green], 0)
    time.sleep(0.3)
    
