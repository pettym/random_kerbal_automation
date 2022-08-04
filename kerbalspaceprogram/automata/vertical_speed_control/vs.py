#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QCheckBox, QLCDNumber, QPushButton, QSpinBox, QDoubleSpinBox

import krpc
from pid_quad import PID, FilteredPID

import scipy
import numpy as np
from scipy.signal import butter, lfilter
from math import floor, ceil
from time import sleep




class AvionicsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('vs.ui', self)

        self.hertz = hertz = 50
        self.conn = None
        self.stream = None
        self.ut = 0.0
        self.update_ut = 1.0
        
        self.previous_vertical_speed = 0.0
        self.change_rate = 0.0
        self.iir_filter = None
        self.fir_filter = None

##        self.make_filter(cutoff=10, order=1, filter_size=20) # This is for testing only        

        self.setup_pid_controllers = self.setup_default_pid_controllers
##        self.setup_pid_controllers = self.setup_quadcopter_pid_controllers
        


        

        self.setup_pid_controllers()
        self.setup_controls()
        self.setup_krpc(self.step)


    def setup_default_pid_controllers(self):
        self.throttle_pid = PID(setpoint=0, limits=(0,15),integral_limits=(0,10), gains=(5, 1, 0.001))       
        self.rate_pid = PID(setpoint=0, limits=(-0.5, 2),  gains=(0.5, 0, 0))

##    def setup_quadcopter_pid_controllers(self):
##        self.throttle_pid = PID(setpoint=0, limits=(0,10),integral_limits=(0,10), gains=(5, 1, 0.005))
##        self.rate_pid = PID(setpoint=0, limits=(-0.5, 2), gains=(0.55, 0, 0))



    def make_filter(self, cutoff, order, filter_size):
        hertz = self.hertz        
        nyquist = hertz/2
        normal_cutoff = cutoff/nyquist
        self.iir_filter = butter(order, normal_cutoff, btype='low', analog=False)
        self.rate_data = np.zeros(filter_size)

    def setup_controls(self):
        controls = self.findChild(QGroupBox, 'ControlGroup')
        self.controls = controls

        enabled = controls.findChild(QCheckBox, 'Enable')
        enabled.stateChanged.connect(self.toggle)

        display = controls.findChild(QLCDNumber, 'Output')
        self.display = display
        
        climb_rate = controls.findChild(QDoubleSpinBox, 'ClimbRate')
        zero_out = controls.findChild(QPushButton, 'ZeroOut')
        decrement_btn = controls.findChild(QPushButton, 'decrement')
        increment_btn = controls.findChild(QPushButton, 'increment')
        radial = controls.findChild(QPushButton, 'RadialOut')
        reset_integral = controls.findChild(QPushButton, 'ResetIntegral')


        climb_rate.valueChanged.connect(self.update_climb_rate)
        self.climb_rate_input = climb_rate
        
        zero_out.clicked.connect(self.zero_out_func)
        decrement_btn.clicked.connect(self.decrement_func)
        increment_btn.clicked.connect(self.increment_func)
        radial.clicked.connect(self.radial_out_func)
        reset_integral.clicked.connect(self.reset_integral_func)
        

    def setup_krpc(self, callback):
        if not self.conn:
            self.conn = krpc.connect(name='vs')
      
        self.ut = self.conn.space_center.ut

        self.vessel = vessel = self.conn.space_center.active_vessel        
        ref_frame = vessel.orbit.body.orbital_reference_frame        
        flight = vessel.flight(ref_frame)

        vessel.control.sas = True
        sleep(0.1)
        vessel.control.sas_mode = self.conn.space_center.SASMode.radial

        stream = self.conn.add_stream(getattr, flight, 'vertical_speed')
        stream.add_callback(callback)
        stream.rate = 0
        stream.start()
        self.stream = stream
        
    def update_climb_rate(self, value):
        self.rate_pid.change_setpoint(value)

    def zero_out_func(self):
        self.climb_rate_input.setValue(0.0)

    def decrement_func(self):
        cr = self.climb_rate_input
        cr.setValue(cr.value() - 0.1)
        
    def increment_func(self):
        cr = self.climb_rate_input
        cr.setValue(cr.value() + 0.1)

    def radial_out_func(self):
        self.vessel.control.sas_mode = self.conn.space_center.SASMode.radial

    def reset_integral_func(self):
        self.throttle_pid.integral = 0
        self.rate_pid.integral = 0

    def toggle(self, value):
        print(f'{value}')
        if value:
            self.setup_pid_controllers()
            self.previous_vertical_speed = 0.0
            self.change_rate = 0.0
            self.setup_krpc(self.step)
            self.update_climb_rate(self.climb_rate_input.value())
        else:
            if self.stream:
                self.stream.remove()
        
    def step(self, vertical_speed):

        self.display.display(vertical_speed)
        
        throttle_pid = self.throttle_pid
        rate_pid = self.rate_pid
        
        ut = self.conn.space_center.ut
        delta = ut - self.ut
        self.ut = ut

        if delta > 0:
            value = rate_pid(vertical_speed, delta)
            throttle_pid.setpoint = value

            change_rate = vertical_speed - self.previous_vertical_speed
            self.previous_vertical_speed = vertical_speed
            change_rate / delta

            if self.iir_filter:
                rate_data = np.roll(self.rate_data, -1)
                rate_data[-1] = change_rate
                self.rate_data = rate_data
                b,a = self.iir_filter
                change_rate = lfilter(b,a,rate_data)[-1]

       
            throttle = throttle_pid(change_rate, delta)
            self.vessel.control.throttle = (throttle/10)

            if ut > self.update_ut:
                print(f'Throttle PID: {throttle_pid}')
                print(f'Rate PID:     {rate_pid}')
                print('')
                self.update_ut = ut + 1

            
            

        

        






if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = AvionicsWindow()    
    window.show()
    sys.exit(app.exec_()) 
