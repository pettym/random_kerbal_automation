#!/usr/bin/env python3


#apt install python3-automaton
#from automaton import machines

# apt install python3-transitions
from transitions import Machine, State

states = [

    State(name='unknown'),
    
    State(name='pre_launch'),
    State(name='launching'),
    State(name='landed'),
    State(name='splashed'),
    State(name='flying'),
    State(name='sub_orbital'),
    State(name='orbiting'),
    State(name='docked'),
    State(name='escaping'),
    
]

transitions = [
    {'trigger': 'launch', 'source': 'pre_launch', 'dest': 'launching' }
]


class Ship(object):

    def on_enter_pre_launch(self):
        print("Pre Launch State")

    def on_enter_launching(self):
        print("hello")





if __name__ == '__main__':
    s = Ship()
    machine = Machine(model=s, states=states, transitions=transitions)
