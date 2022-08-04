
import krpc

from time import sleep
from math import ceil, isclose





def _m(vessel, rdv):
    dvr = vessel.available_thrust / vessel.mass

    if rdv > dvr:
        throttle = 1
    else:
        throttle = (rdv / dvr) / 2

    vessel.control.throttle = throttle
    


def maneuver(vessel, node):
    sasm = vessel.control.sas_mode.__class__
    vessel.control.sas_mode = sasm(1)

    dvr = vessel.available_thrust / vessel.mass
    while node.remaining_delta_v > 0.05:        
        _m(vessel, node.remaining_delta_v)
        #sleep(0.2)
        sleep(0.1)
        
        if node not in vessel.control.nodes:
            print('[!] node removed manually')
            break
        
    else:
        node.remove()        
    vessel.control.throttle = 0


def run(space_center, direction_margin=0.05):
        
    vessel = space_center.active_vessel  
    while vessel.control.nodes:
        nodes = vessel.control.nodes
        nodes.sort(key=lambda n:n.ut)
        node = nodes[0]

        print("Pointing craft in direction")
        sasm = vessel.control.sas_mode.__class__
        vessel.control.sas_mode = sasm(1)           

        try:
            while True:
                sleep(2)
                dirs = zip(
                    vessel.direction(vessel.orbital_reference_frame),
                    node.direction(vessel.orbital_reference_frame)
                )
                #if all( ((d1-d2) < direction_margin) and ((d1-d2) > -direction_margin) for d1, d2 in dirs ):
                if all( isclose(d1, d2, abs_tol=direction_margin) for d1, d2 in dirs):
                    break
        except KeyboardInterrupt:
            input("Continue with maneuver? (Control-C or Enter)")
        print("done!")
        sleep(2)
            
        

        backoff = node.remaining_delta_v / (vessel.available_thrust / vessel.mass)
        if backoff < 2:
            backoff = 2
        backoff = ceil(backoff)/2
        
        target_time = node.ut - backoff
        print("Warping")
        space_center.warp_to(target_time-10)
        print("waiting")
        sleep(target_time - space_center.ut)
        print("Running")
        try:
            maneuver(vessel, node)
        except KeyboardInterrupt:
            vessel.control.throttle = 0

    print("\n\n===Done===")

        


if __name__ == "__main__":
    conn = krpc.connect(name='default')

    direction_margin = 0.08
    print(f"Direction Error Margin: {direction_margin}")
    
    while True:
        input("Press Enter To Run")
        run(conn.space_center, direction_margin)    
    sc = conn.space_center
    v = sc.active_vessel

    
