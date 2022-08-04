from evdev import InputDevice, list_devices, UInput
from evdev import categorize, ecodes
from evdev import ff

from pprint import pprint



















if __name__ == '__main__':
    #device_path = '/dev/input/by-id/usb-Sony_Interactive_Entertainment_Wireless_Controller-if03-event-joystick'
    device_path = '/dev/input/by-id/usb-Saitek_Saitek_Pro_Flight_Quadrant-event-joystick'
    dev = InputDevice(device_path)

    data = {}

    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            data[event.code] = str(event.value).rjust(3)
            print(data)
                
     
