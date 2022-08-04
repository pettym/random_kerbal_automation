from evdev import InputDevice, list_devices
from evdev import ecodes
from evdev import ff

import asyncio





class BaseJoystick:
    def __init__(self, path):
        self._path = path
        self._dev = InputDevice(path)

        self.values = dict()

    async def reader(self, device):
        async for event in device.async_read_loop():
            if event.type == 3:
                self.values[event.code] = event.value


    async def asyncmain(self):
        task = asyncio.create_task(self.reader(self._dev))
        while True:
            print(f'\r  {self.values}      ',end='',flush=True)
            await asyncio.sleep(0.1)
        await task

    def __call__(self):
        asyncio.run(self.asyncmain())


if __name__ == "__main__":
    js = BaseJoystick('/dev/input/event21')
    js()
