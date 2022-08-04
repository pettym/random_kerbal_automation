from evdev import InputDevice, list_devices
from evdev import ecodes
from evdev import ff

import asyncio

import krpc




class KSPJoystick:
    def __init__(self, path):
        self._path = path
        self._dev = InputDevice(path)

        self.values = dict()
        self.effects = dict()

        self.conn = krpc.connect()
        self.vessel = self.conn.space_center.active_vessel
        self.control = self.vessel.control

    @staticmethod
    def percent_to_value(percent, max_value=0xffff):
        assert (percent>=0) and (percent<=1)
        return int(round(max_value * percent))

    def set_autocenter_force(self, percent):              
        self._dev.write(
            ecodes.EV_FF,
            ecodes.FF_AUTOCENTER,
            self.percent_to_value(percent)
        )


    def set_ff_gain(self, percent):              
        self._dev.write(
            ecodes.EV_FF,
            ecodes.FF_GAIN,
            self.percent_to_value(percent)
        )
      

    def constant(self, level=0x7fff, direction=0x8000, nameofthing='constant'):
        dev = self._dev
        
        envelope = ff.Envelope(attach_length=0, attack_level=0x0000, fade_length=0, fade_level=0x0000)
        const = ff.Constant(ff_envelope=envelope, level=level)
        effect = ff.Effect(
            ecodes.FF_CONSTANT, self.effects.get(nameofthing, -1), direction,
            ff.Trigger(0,0),
            ff.Replay(length=110, delay=0),
            ff.EffectType(ff_constant_effect=const),
        )
        repeat_count = 1
        effect_id = dev.upload_effect(effect)
        self.effects[nameofthing] = effect_id
        dev.write(ecodes.EV_FF, effect_id, repeat_count)
         

    async def reader(self, device):
        async for event in device.async_read_loop():
            if event.type == 3:
                if abs(event.value) > 15:
                    self.values[event.code] = event.value
                else:
                    self.values[event.code] = 0


    async def asyncmain(self):
        base_feedback = 0x3fff
        c = self.control
        task0 = asyncio.create_task(self.reader(self._dev))

        while True:
            for i in range(5):
                c.throttle = abs(self.values.get(6,0) - 127) / 127
                c.pitch = (self.values.get(1, 0)/512)            
                c.roll = (self.values.get(0,0)/512)
                c.yaw = (self.values.get(5,0)/32)
                await asyncio.sleep(0.01)

            pv = c.pitch
            if pv > 0:
                self.constant(level=int(base_feedback*(pv)), direction=0x0001, nameofthing='con1')
            else:
                self.constant(level=int(base_feedback*abs(pv)), direction=0x8000, nameofthing='con1')

            rv = c.roll
            if rv > 0:
                self.constant(level=int(base_feedback*(rv)), direction=0xc000, nameofthing='con2')
            else:
                self.constant(level=int(base_feedback*abs(rv)), direction=0x4000, nameofthing='con2')
    

        await task0


    def __call__(self):
        asyncio.run(self.asyncmain())


if __name__ == "__main__":
    js = KSPJoystick('/dev/input/event21')
    dev = js._dev
    c = js.vessel.control

    js.set_ff_gain(0.5)
    js.set_autocenter_force(0.9)
    dev.write(ecodes.EV_FF, ecodes.FF_DAMPER, 0xffff)
    dev.write(ecodes.EV_FF, ecodes.FF_INERTIA, 0)
    js()







