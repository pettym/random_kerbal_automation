from evdev import InputDevice, list_devices
from evdev import ecodes
from evdev import ff

import time


##    def sharp_deflection(self):
##        dev = self.device
##        print("Sharp Deflection")
##        
##        rumble = ff.Rumble(strong_magnitude=0xffff, weak_magnitude=0xffff)
##        duration_ms = 120
##        delay_ms = 40
##        repeat_count = 2
##        effect = ff.Effect(
##            ecodes.FF_RUMBLE, self.effects.get('sharp_deflection_r', -1), 0x0,
##            ff.Trigger(0,0),
##            ff.Replay(duration_ms, delay_ms),
##            ff.EffectType(ff_rumble_effect=rumble),
##        )
##        effect_id = dev.upload_effect(effect)
##        self.effects['sharp_deflection_r'] = effect_id        
##        dev.write(ecodes.EV_FF, effect_id, repeat_count)
##
##        time.sleep(0.12)
##
##        envelope = ff.Envelope(attach_length=155, attack_level=0x0000, fade_length=100, fade_level=0x0f00)
##        peri = ff.Periodic(envelope=envelope, magnitude=0x4fff, phase=0, waveform=ecodes.FF_TRIANGLE)
##        effect = ff.Effect(
##            ecodes.FF_PERIODIC, self.effects.get('sharp_deflection_p', -1), 0x4000,
##            ff.Trigger(0,0),
##            ff.Replay(length=400, delay=100),
##            ff.EffectType(ff_periodic_effect=peri),
##        )
##        repeat_count = 1
##        effect_id = dev.upload_effect(effect)
##        self.effects['sharp_deflection_p'] = effect_id
##        dev.write(ecodes.EV_FF, effect_id, repeat_count)
##
##
##        
##    def soft_deflection(self):
##        dev = self.device
##        print("Soft Deflection")
##        
##        envelope = ff.Envelope(attach_length=300, attack_level=0x00f0, fade_length=600, fade_level=0x00f0)
##        peri = ff.Periodic(envelope=envelope, magnitude=0x0fff, waveform=ecodes.FF_SINE)
##        effect = ff.Effect(
##            ecodes.FF_PERIODIC, self.effects.get('soft_deflection_p', -1), 0x4000,
##            ff.Trigger(0,0),
##            ff.Replay(length=900, delay=100),
##            ff.EffectType(ff_periodic_effect=peri),
##        )
##        repeat_count = 1
##        effect_id = dev.upload_effect(effect)
##        self.effects['soft_delection_p'] = effect_id
##        dev.write(ecodes.EV_FF, effect_id, repeat_count)
##
##
##    def wheel_slip(self, intensity=0.5):
##        dev = self.device
##        print("Wheel Slip")
##        
##        rumble = ff.Rumble(strong_magnitude=0x0, weak_magnitude=0x0fff )
##        duration_ms = 140 - int(intensity*80)
##        delay_ms = 75 #+ int(intensity*80)
##        repeat_count = 4
##        
##        effect = ff.Effect(
##            ecodes.FF_RUMBLE, self.effects.get('moon_rumble', -1), 0x0,
##            ff.Trigger(0,0),
##            ff.Replay(duration_ms, delay_ms),
##            ff.EffectType(ff_rumble_effect=rumble),
##        )
##        effect_id = dev.upload_effect(effect)
##        self.effects['moon_rumble'] = effect_id
##
##        dev.write(ecodes.EV_FF, effect_id, repeat_count)
##
##    def test(self):
##        dev = self.device
##        print("test")
##        
##        envelope = ff.Envelope(attach_length=300, attack_level=0x00f0, fade_length=600, fade_level=0x00f0)
##        peri = ff.Periodic(envelope=envelope, magnitude=0x0fff, waveform=ecodes.FF_SINE)
##        effect = ff.Effect(
##            ecodes.FF_PERIODIC, self.effects.get('test_p', -1), 0x4000,
##            ff.Trigger(0,0),
##            ff.Replay(length=900, delay=100),
##            ff.EffectType(ff_periodic_effect=peri),
##        )
##        repeat_count = 1
##        effect_id = dev.upload_effect(effect)
##        self.effects['test_p'] = effect_id
##        dev.write(ecodes.EV_FF, effect_id, repeat_count)


class FFEffect:
    effect_name = 'test'

    def __init__(self, device):
        self.device = device
        self.upload_slot = -1
        self.intensity = 0.5
        self.next_start = 0

        self.upload()


    def craft(self, slot_num, level):
        return ff.Effect(
            ecodes.FF_RUMBLE, slot_num, 0,
            ff.Trigger(0,0),
            ff.Replay(300, 0),
            ff.EffectType(ff_rumble_effect=ff.Rumble(
                strong_magnitude=0x0, weak_magnitude=int(0xffff * level)
                ))
            )

    def upload(self):
        slot = self.device.upload_effect(
            self.craft(self.upload_slot, self.intensity)
            )
        self.upload_slot = slot


    def __call__(self, intensity=0.5):
        if intensity > 1: intensity = 1
        if intensity < 0: intensity = 0
        
        if intensity != self.intensity:
            self.intensity = intensity
            self.upload()

        self.device.write(ecodes.EV_FF, self.upload_slot, 1)
        



class WheelSlip(FFEffect):
    name = 'wheel_slip'
    
    def craft(self, slot_num, level):
        return ff.Effect(
            ecodes.FF_RUMBLE, slot_num, 0,
            ff.Trigger(0,0),
            ff.Replay(300, 0),
            ff.EffectType(ff_rumble_effect=ff.Rumble(
                strong_magnitude=0x0, weak_magnitude=int(0xffff * level)
                ))
            )



class FFControl:
    _effects = [ WheelSlip ]
    def __init__(self, device_path='/dev/input/by-id/usb-Sony_Interactive_Entertainment_Wireless_Controller-if03-event-joystick'):
        dev = InputDevice(device_path)
        self.device = dev
        
        self.effects = { fx.name:fx(dev) for fx in self._effects }

    def __getitem__(self, key):
        return self.effects[key]
    
    @property
    def ff_options(self):
        return  { k:v for k,v in ecodes.FF.items() if k in self.device.capabilities()[21] }

    @staticmethod
    def percent_to_value(percent, max_value=0xffff):
        assert (percent>=0) and (percent<=1)
        return int(round(max_value * percent))

    def set_gain(self, percent):              
        self.device.write(
            ecodes.EV_FF,
            ecodes.FF_GAIN,
            self.percent_to_value(percent)
        )
    



        



if __name__ == '__main__':
    f = FFControl()
    dev = f.device

    test = FFEffect(dev)

    
    
