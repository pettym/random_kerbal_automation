
import time

import evdev
from evdev import InputDevice
from evdev import ecodes
from evdev import ff

from os import path
from collections import defaultdict
from pprint import pprint


dev = InputDevice('/dev/input/by-id/usb-Sony_Interactive_Entertainment_Wireless_Controller-if03-event-joystick')
#/sys/class/input/event20
#./device/device




def gather(dev):
    endtime = time.time()+0.2
    data = list()

    values = dict()

    for event in dev.read_loop():
        label = ecodes.bytype[event.type][event.code]

        if event.type in {0, 4}:
            continue

        if event.type in {3}:
            values[label] = event.value


        #print(f'{label}  {event}')

        if time.time() > endtime:
            print("\n"*5)
            pprint(values)
            endtime = time.time()+0.2



if __name__ == '__main__':
    data = gather(dev)

    


