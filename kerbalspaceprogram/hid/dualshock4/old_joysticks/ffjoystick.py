from evdev import InputDevice, list_devices
from evdev import ecodes
from evdev import ff

from time import sleep

from basejoystick import BaseJoystick

"""
0   deg  ->  0x0000 (down)
90  deg  ->  0x4000 (left)
180 deg  ->  0x8000 (up)
270 deg  ->  0xC000 (right)

constant_levels:

16383 (halfway)  --> level=

"""

class FFJoystick(BaseJoystick):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effects = dict()
    
    @property
    def ff_options(self):
        return  { k:v for k,v in ecodes.FF.items() if k in self._dev.capabilities()[21] }

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
      

    def rumble(self):
        dev = self._dev
        
        rumble = ff.Rumble(strong_magnitude=0x7fff, weak_magnitude=0x7fff)        
        duration_ms = 250
        delay_ms = 250
        repeat_count = 1
        effect = ff.Effect(
            ecodes.FF_RUMBLE, self.effects.get('rumble', -1), 0x8000,
            ff.Trigger(0,0),
            ff.Replay(duration_ms, delay_ms),
            ff.EffectType(ff_rumble_effect=rumble),
        )
        effect_id = dev.upload_effect(effect)
        self.effects['rumble'] = effect_id        
        dev.write(ecodes.EV_FF, effect_id, repeat_count)


    def constant(self, level=0x7fff, direction=0x8000):
        dev = self._dev
        
        envelope = ff.Envelope(attach_length=0, attack_level=0x0000, fade_length=200, fade_level=0x0000)
        const = ff.Constant(ff_envelope=envelope, level=level)
        effect = ff.Effect(
            ecodes.FF_CONSTANT, self.effects.get('constant', -1), direction,
            ff.Trigger(7,2),
            ff.Replay(length=5000, delay=0),
            ff.EffectType(ff_constant_effect=const),
        )
        repeat_count = 1
        effect_id = dev.upload_effect(effect)
        self.effects['constant'] = effect_id
        dev.write(ecodes.EV_FF, effect_id, repeat_count)
        
        #dev.erase_effect(effect_id)
        
        
    def periodic(self):
        dev = self._dev
        
        envelope = ff.Envelope(attach_length=0, attack_level=0x7fff, fade_length=200, fade_level=0x0000)
        peri = ff.Periodic(ff_envelope=envelope, magnitude=0x2fff, offset=0xf000, period=550, waveform=ecodes.FF_SINE)
        effect = ff.Effect(
            ecodes.FF_PERIODIC, self.effects.get('periodic', -1), 0x4000,
            ff.Trigger(0,0),
            ff.Replay(length=10000, delay=100),
            ff.EffectType(ff_periodic_effect=peri),
        )
        repeat_count = 1
        effect_id = dev.upload_effect(effect)
        self.effects['periodic'] = effect_id
        self._dev.write(ecodes.EV_FF, effect_id, repeat_count)
        

# ff.Periodic(custom_data, custom_len, envelope, magnitude, offset, period, phase, waveform)
# dev.write(etype, code, value)

   
    
