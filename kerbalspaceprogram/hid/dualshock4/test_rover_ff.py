import time
import krpc
from multiprocessing import Process, Event

from dualshock4.kspmode import KSPTest as RoverFF

def stream_vessel(conn, callback):
    vessel = conn.add_stream(getattr, conn.space_center, 'active_vessel')
    vessel.rate = 2
    vessel.add_callback(callback)
    vessel.start()
    return vessel

def stream_soi(conn, callback):
    vessel = conn.space_center.active_vessel
    soi = conn.add_stream(getattr, vessel.orbit, 'body')
    soi.rate = 1
    soi.add_callback(callback)
    soi.start()
    return soi
    
class Flight:
    scene_name = 'flight'
    def __init__(self):
        self.conn = krpc.connect(name=self.scene_name)
        self.enabled = False
        
        self.vessel = None
        self.active_vessel = None

        print('flight scene starting')
        self.rover_ff = None

    def vessel_callback(self, vessel):
        print(f"[callback] active vessel: {vessel.name}")
        self.active_vessel  = vessel

        if vessel.type.name == 'rover':
            self.rover_ff = RoverFF(vessel)
            print('activate rover ff')
        else:
            self.rover_ff = None


    def __enter__(self):
        self.vessel = stream_vessel(self.conn, self.vessel_callback)
        
    def __exit__(self, *args, **kwargs):
        self.vessel.remove()

    def __call__(self):
        if not self.conn.krpc.paused:
            if self.rover_ff:
                self.rover_ff()

            f = self.active_vessel.flight(self.active_vessel.orbit.body.reference_frame)
            speed = int(round(f.speed * 2.236936, 0))
        
            print(f'\r {str(speed).rjust(4)} mph', end='       ', flush=True)

            



def scene_wrapper(module, stop):
    module = module()
    with module:    
        while not stop.is_set():
            module()
            time.sleep(0.2)
    
class Core:
    _modules = [ Flight ]
    
    def __init__(self):
        self.conn = krpc.connect(name='default')
        self.scene = None
        self.modules = { mod.scene_name:mod for mod in self._modules }

    def begin_scene(self, scene_name):
        stop_event = Event()
        proc = Process(target=scene_wrapper, args=(self.modules[scene_name], stop_event))
        proc.start()
        return proc, stop_event


    def __call__(self):
        conn = self.conn
        
        with conn.stream(getattr, conn.krpc, 'current_game_scene') as scene:
            scene.rate = 3
            with scene.condition:
                while True:
                    active = scene()
                    print(f'Current Scene: {active.name}')

                    if active.name in self.modules:
                        proc, stop = self.begin_scene(active.name)   
                        scene.wait()
                        print("<Scene transition>")
                        stop.set()
                        proc.join()
                    else:
                        scene.wait()
        

                



if __name__ == "__main__":
    core = Core()
    core()


