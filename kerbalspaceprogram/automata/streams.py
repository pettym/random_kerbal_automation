
import krpc
import queue
import sys

from time import sleep
from pprint import pprint

import threading


##if __name__ == "__main__":
##    
##    conn = krpc.connect(name='default')
##    
##    sc = conn.space_center
##    v = vessel = sc.active_vessel
##    obt_a_frame = vessel.orbit.body.non_rotating_reference_frame
##    obt_b_frame = vessel.orbit.body.orbital_reference_frame
##    srf_frame = vessel.surface_reference_frame
##
##    flight = vessel.flight(vessel.orbit.body.reference_frame)




class DataStream:
    def __init__(self, hertz=1):
        self.conn = None
        self.timestamp = None
        self.output = queue.Queue(maxsize=4)
        self.clock = None
        self.streams = dict()
        self.hertz = hertz
        

        self.connect()

    def connect(self):
        self.conn = conn = krpc.connect(name='StreamWrapper')

        stream = conn.add_stream(getattr, conn.space_center, 'ut')
        stream.rate = self.hertz
        self.clock = stream
        self.create_streams()        
        self.start()       

    def start(self):
        self.clock.add_callback(self.step)
        self.clock.start()
        
    def stop(self):
        self.clock.remove_callback(self.step)


    def create_streams(self):
        conn = self.conn
        vessel = conn.space_center.active_vessel

        srf_flight = vessel.flight(vessel.surface_reference_frame)      
        keys = ['pitch', 'roll', 'heading', 'angle_of_attack', 'sideslip_angle']
        for key in keys:
            stream = conn.add_stream(getattr, srf_flight, key)
            stream.rate = self.hertz
            self.streams[key] = stream
            stream.start(wait=False)

        srf2_flight = vessel.flight(vessel.orbit.body.reference_frame)
        keys = ['vertical_speed', 'horizontal_speed', 'speed']
        for key in keys:
            stream = conn.add_stream(getattr, srf2_flight, key)
            stream.rate = self.hertz
            self.streams[key] = stream
            stream.start(wait=False)

        #Temporary Delay. Make this smarter lol
        sleep(2)

        
        
    def step(self, timestamp):
        if timestamp == self.timestamp:
            return None
        if self.conn.space_center.rails_warp_factor > 0:
            self.timestamp = timestamp
            return None

        
        data = {'timestamp': timestamp }
        for key, stream in self.streams.items():
            data[key] = stream()


        self.timestamp = timestamp
        output = self.output
        if output.full():
            output.get_nowait()
        output.put_nowait(data)


    def __call__(self):
        return self.output.get()

            
if __name__ == '__main__':
    ds = DataStream(hertz=0)

    timestamp = ds.output.get()['timestamp']
    avg_delta = 0
    while True:
        value = ds.output.get()
        delta = value['timestamp'] - timestamp
        avg_delta = (avg_delta + delta)/2
        print(f'{round(avg_delta,6)}\t\t{delta}')
        timestamp = value['timestamp']

            
        
        

    
