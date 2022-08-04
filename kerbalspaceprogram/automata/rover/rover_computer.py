#!/usr/bin/python3

import logging
import krpc

from transitions import Machine, State
from pid import PID

from math import sin, cos, atan2
from math import degrees, radians


def heading_error(value, target):
    a1, a2 = radians(target), radians(value)
    
    err = atan2(sin(a1-a2), cos(a1-a2))
    return -degrees(err)

def speed_error(value, target):

    error =  target - value

    if target == 0 and abs(error) < 0.2:
        return 0

    return error

    

states = [
    State(name='no_connection'),
    State(name='inactive'),
    State(name='active'),
    State(name='stop', ignore_invalid_triggers=True),
    State(name='timewarp'),
]

transitions = [
    #{'trigger': 'abort', 'source': '*', 'dest': 'stop', 'conditions': 'is_inactive' ,'after': 'disable_abort_event'},
    {'trigger': 'abort', 'source': '*', 'dest': 'stop', 'unless': 'is_stop'},
    {'trigger': 'cancel_abort', 'source': '*', 'dest': 'inactive', 'unless': 'is_no_connection'},
    

]

    


class RoverComputer:
    def __init__(self):
        self.conn = None
        self.vessel = None
        self.flight = None

        self.ut = 0
        self.clock = None
        self.controllers = {
            'CruiseControl': PID( gains=(0.2, 0, 0), limits=(0,1) ),
            'HillDecent': PID( gains=(0.9, 0, 1), limits=(-2, 0) ),
##            'AutoSteer': PID( gains=(0.025, 0, 0), limits=(-1, 1) ),
            }

    def __getitem__(self, key):
        return self.controllers.get(key)

            

    def connect(self, connection=None):
        if connection:
            self.conn = conn = connection
        else:
            self.conn = conn = krpc.connect(name='rover')
            
        vessel = self.vessel = conn.space_center.active_vessel        
        ref_frame = vessel.orbit.body.reference_frame        
        flight = self.flight = vessel.flight(ref_frame)
        self.setup_pid_controllers()
        self.to_inactive()

        
    def setup_pid_controllers(self):
        pid = self.controllers['CruiseControl']
        if pid:
            pid.input = lambda: self.flight.speed
            pid.callback = lambda value: setattr(self.vessel.control, 'wheel_throttle', value)
            pid.calculate_error = speed_error

        pid = self['HillDecent']
        if pid:
            pid.input = lambda: self.flight.speed
            pid.callback = lambda value: setattr(self.vessel.control, 'brakes', bool(value))

        pid = self['AutoSteer']
        if pid:
            pid.input = lambda: self.vessel.flight(self.vessel.surface_reference_frame).heading
            pid.callback = lambda value: setattr(self.vessel.control, 'wheel_steering', value)
            pid.calculate_error = heading_error

            

    def start_clock(self):
        conn = self.conn
        self.ut = conn.space_center.ut
        clock = self.clock = conn.add_stream(getattr, conn.space_center, 'ut')
        
        clock.add_callback(self)
        clock.rate = 10
        clock.start()

        
    def on_exit_no_connection(self):
        conn = self.conn
        vessel = self.vessel

        stream = conn.add_stream(getattr, vessel.control, 'abort')
        stream.add_callback(self.abort_button_update)
        stream.start()

    def on_enter_active(self):
        vessel = self.vessel
        vessel.control.brakes = False



    def __call__(self, ut):
        delta = ut - self.ut
        self.ut = ut


        for name, pid in self.controllers.items():
            pid( pid.input(), delta )
        

    def final(self):
        print(f'Current State: {self.state}')

        
    def abort_button_update(self, value):
        if value: self.abort()
        else: self.cancel_abort()
        

    def on_enter_stop(self):
        self.vessel.control.brakes = True

    def on_enter_active(self):
        self.start_clock()

    def on_exit_active(self):
        if self.clock: self.clock.remove()
        self.clock = None

        for name, pid in self.controllers.items():
            pid.reset()
        
        

def make_rover_computer():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('transitions').setLevel(logging.INFO)
    
    rover = RoverComputer()
    
    rover_state_machine = Machine(
        model=rover, states=states, transitions=transitions,
        initial='no_connection', finalize_event='final'
    )

    return rover
    

if __name__ == '__main__':
    
    rover = make_rover_computer()
    rover.connect()
    conn = rover.conn
    
