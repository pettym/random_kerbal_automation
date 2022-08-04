
import asyncio
import time
import statistics

import krpc
try:
    from .forces import FFControl, FFEffect
except ModuleNotFoundError:
    from forces import FFControl, FFEffect
    

class KSPTest:
    def __init__(self, vessel, gain=0.75):

        self.vessel = vessel
        self.ffc = FFControl()
        self.ffc.set_gain(gain)
        


    def __call__(self):
        wheels = self.vessel.parts.wheels

        slip_effect = self.ffc['wheel_slip']
        
        slip = max( w.slip for w in wheels)
        slip = round(slip,3)
        if slip >= 0.1:
            slip_effect(slip/2)
            #print(f'\r{slip}', end='   ', flush=True)            
        time.sleep(0.2)
  





if __name__ == "__main__":
    gain = 0.75
    rpc = krpc.connect()
    flight = rpc.krpc.GameScene.flight
    while True:
        if rpc.krpc.current_game_scene != flight:
            time.sleep(1)
            continue
        try:
            print("Starting Rover FF")
            ksp = KSPTest(rpc.space_center.active_vessel, gain=gain)
            while True:
                ksp()
        except KeyboardInterrupt:
            break
        except Exception as e:
            pass
    







