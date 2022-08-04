
import krpc

from time import sleep
from math import ceil





def _m(vessel, rdv):
    dvr = vessel.available_thrust / vessel.mass

    if rdv > dvr:
        throttle = 1
    else:
        throttle = (rdv / dvr) / 2

    vessel.control.throttle = throttle
    


def maneuver(vessel, node, ap):

    dvr = vessel.available_thrust / vessel.mass

    dv_error = 1.2
    previous_dv = node.remaining_delta_v * dv_error
    
    
    while node.remaining_delta_v > 0.05:
        if node.remaining_delta_v > previous_dv:
            print("[ERROR] DeltaV Rise!")
            break
        previous_dv = node.remaining_delta_v * dv_error
        
        _m(vessel, node.remaining_delta_v)
        #sleep(0.2)
        sleep(0.1)
        
        if node not in vessel.control.nodes:
            print('[!] node removed manually')
            vessel.control.throttle = 0
            vessel.auto_pilot.disengage()
            break
        else:
            ap.target_direction = node.remaining_burn_vector(vessel.surface_reference_frame)

        
            
        
    else:
        node.remove()        
    vessel.control.throttle = 0
    vessel.auto_pilot.disengage()


def run(space_center):
    vessel = space_center.active_vessel
    ref_frame = vessel.surface_reference_frame

    ap = vessel.auto_pilot
    ap.reference_frame = ref_frame


    while vessel.control.nodes:
        nodes = vessel.control.nodes
        nodes.sort(key=lambda n:n.ut)
        node = nodes[0]


        print("Pointing Craft In Direction")
        ap.target_direction = node.burn_vector(ref_frame)
        ap.engage()
        ap.wait()
        print("done!")
        sleep(2)
            
        

        backoff = node.remaining_delta_v / (vessel.available_thrust / vessel.mass)
        if backoff < 2:
            backoff = 2
        backoff = ceil(backoff)/2

        ap.disengage()
        
        target_time = node.ut - backoff
        print("Warping")
        space_center.warp_to(target_time-10)
        print("waiting")
        ap.target_direction = node.remaining_burn_vector(ref_frame)
        ap.engage()
        sleep(target_time - space_center.ut)
        ap.target_direction = node.remaining_burn_vector(ref_frame)
        print("Running")
        try:
            maneuver(vessel, node, ap)
        except KeyboardInterrupt:
            vessel.control.throttle = 0
            vessel.auto_pilot.disengage()

    print("\n\n===Done===")

        


if __name__ == "__main__":
    conn = krpc.connect(name='default')
    try:
        while True:
            input("Press Enter To Run")
            run(conn.space_center)
    except:
        conn.space_center.active_vessel.control.throttle = 0
        conn.space_center.active_vessel.auto_pilot.disengage()

    sc = conn.space_center
    v = sc.active_vessel

    
