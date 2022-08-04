import itertools

import krpc
from time import sleep


# Flight Direction:
"""
Direction Orbit:
 [ X, Z, Y ]
 [ Radial Out, Normal, Prograde ]
Direction Surface:
 [ Up/Down, North/South, East/West ]

"""

def test(*args, **kwargs):
    print(kwargs)

if __name__ == "__main__":
    conn = krpc.connect(name='default') 
    sc = conn.space_center
    v = vessel = sc.active_vessel

##    wheels = v.parts.wheels
##    while not sleep(1):
##        print('===')
##        for wheel in wheels:            
##            if wheel.grounded: grounded = '1'
##            else: grounded = '-'                
##            deflection = round(wheel.deflection, 1)
##            
##            print(f'{wheel.part.tag}: {grounded}/{deflection}')

    modules = [ wheel.part.modules for wheel in vessel.parts.wheels ]
    
    modules = [ mod for mod in itertools.chain(*modules) if "WheelSuspension" in mod.name ]

    modules = [ mod for mod in modules if mod.fields ]

    delay = 2
    while True:
        for spring in [2]:
            for m in modules:
                m.set_field_float('Spring Strength', spring)
            sleep(delay)
        
        
    







 
