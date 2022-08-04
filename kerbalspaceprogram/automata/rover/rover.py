#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QLCDNumber, QPushButton, QCheckBox, QSpinBox, QComboBox, QSlider

import krpc

from pid import PID, FilteredPID
from rover_computer import make_rover_computer

import scipy
import numpy as np
from scipy.signal import butter, lfilter
from math import floor, ceil
from time import sleep




class RoverWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('rover.ui', self)

        self.hertz = hertz = 50
        self.conn = None
        self.ut = 0.0
        
        self.computer = make_rover_computer()
        self.setup_controls()
        self.setup_krpc()

        
    def setup_krpc(self):
        self.conn = krpc.connect(name='rover')
        self.computer.connect(self.conn)

        vessel = self.conn.space_center.active_vessel        
        ref_frame = vessel.orbit.body.reference_frame        
        flight = vessel.flight(ref_frame)

        heading = int(vessel.flight(vessel.surface_reference_frame).heading)
        self.TargetHeading.setValue(float(heading))

        stream = self.conn.add_stream(getattr, flight, 'speed')
        stream.add_callback(self.SpeedDisplay.display)
        stream.rate = 0
        stream.start()

    def setup_controls(self):
        controls = self.findChild(QGroupBox, 'ControlGroup')
        self.controls = controls

##        cc_enable = controls.findChild(QCheckBox, 'CruiseControlEnable')
##        cc_enable.stateChanged.connect(self.cc_toggle)


        self.Activate.clicked.connect(lambda x: self.computer.to_active())
        self.Deactivate.clicked.connect(lambda x: self.computer.to_inactive())
        self.FullStop.clicked.connect(lambda x: self.computer.abort())

        self.CruiseSpeed.valueChanged.connect(self.update_cruise_speed)
        self.CruiseSpeed.valueChanged.connect(self.computer['CruiseControl'].change_setpoint)
        self.CruiseControlEnable.stateChanged.connect(self.computer['CruiseControl'].enable)

        self.HillSpeed.setDisabled(True)
        if self.computer.controllers.get('HillDecent'):
            self.HillSpeed.valueChanged.connect(self.computer['HillDecent'].change_setpoint)
            self.HillControlEnable.stateChanged.connect(self.computer['HillDecent'].enable)
            self.HillSpeedSlider.valueChanged.connect(self.update_hill_slider)

##        self.TargetHeading.valueChanged.connect(self.computer['AutoSteer'].change_setpoint)
##        self.TargetHeading.valueChanged.connect(self.update_target_heading)


        
        
        
        

    def update_cruise_speed(self, value):
        hill_speed = value + self.HillSpeedSlider.value()
        self.HillSpeed.setValue(hill_speed)

    def update_hill_slider(self, value):
        hill_speed = value + self.CruiseSpeed.value()
        self.HillSpeed.setValue(hill_speed)

    def update_target_heading(self, value):
        if value == 360:
            self.TargetHeading.setValue(0)

        if value == -1:
            self.TargetHeading.setValue(359)



                

            

            
            

        

        






if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = RoverWindow()    
    window.show()
    sys.exit(app.exec_()) 
