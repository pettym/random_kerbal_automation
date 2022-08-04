
import krpc
from time import sleep
import threading

# Flight Direction:
"""
Direction Orbit:
 [ X, Z, Y ]
 [ Radial Out, Normal, Prograde ]
Direction Surface:
 [ Up/Down, North/South, East/West ]


"""

if __name__ == "__main__":
    
    conn = krpc.connect(name='default')
    
    sc = conn.space_center
    v = vessel = sc.active_vessel
    obt_a_frame = vessel.orbit.body.non_rotating_reference_frame
    obt_b_frame = vessel.orbit.body.orbital_reference_frame
    srf_frame = vessel.surface_reference_frame

    flight = vessel.flight(vessel.orbit.body.reference_frame)

    ###
    print('Time, vertical_speed, surface_altitude, horizontal_speed')
    while True:
        data = [sc.ut, flight.vertical_speed, flight.surface_altitude, flight.horizontal_speed]
        #data.append(sum(abs(v) for v in flight.drag))
        
        
        print(','.join(str(line) for line in data ))
        sleep(0.02001)

        

    
