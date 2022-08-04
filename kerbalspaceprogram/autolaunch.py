
import krpc

import time
from time import sleep
import random

# Flight Direction:
"""
Direction Orbit:
 [ X, Z, Y ]
 [ Radial Out, Normal, Prograde ]
Direction Surface:
 [ Up/Down, North/South, East/West ]

"""




def leaving_atmosphere(vessel):
    for part in vessel.parts.fairings:
        if not part.jettisoned:
            part.jettison()
    sleep(10)

    parts = vessel.parts.antennas+vessel.parts.solar_panels
    parts = [ part for part in parts if part.deployable and not part.deployed ]
    random.shuffle(parts)
    for part in parts:
        part.deployed = True
        sleep(random.random())

def autostage(vessel):
    num = vessel.control.current_stage-1
    res = vessel.resources_in_decouple_stage(num)

    checked_resources = ['LiquidFuel', 'SolidFuel']
    depleted = [ res.amount(name) <= 0 for name in checked_resources if res.has_resource(name) ]

    
    if any(depleted):
    #if all(depleted):
        print(f"Autostage! {num+1} -> {num}")
        vessel.control.activate_next_stage()
        time.sleep(2)
        
    
            
    

if __name__ == "__main__":
    conn = krpc.connect(name='default')
    sc = conn.space_center
    v = sc.active_vessel

    if v.situation.name == 'pre_launch':
        flight = v.flight()
        
        v.control.throttle = 1
        v.control.sas = True
        print("[Standby] - Pre-Launch")

        while v.situation.name == 'pre_launch':
            time.sleep(0.2)
        
        while True:
            sleep(0.2)            
            
            if flight.mean_altitude > 68000:
                print("Running...")
                leaving_atmosphere(v)
                print("==Done==")
                break

            autostage(v)
            







 
