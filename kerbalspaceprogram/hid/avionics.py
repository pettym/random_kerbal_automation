#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QSlider, QAbstractSlider, QDial, QScrollBar, QProgressBar, QPushButton, QCheckBox
from PyQt5.QtWidgets import QLCDNumber

import krpc


def const_wrapper(func, const):
    return lambda :func(const)

class AvionicsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('test.ui', self)

        self.conn = None
        self.inputs = dict()

        self.controls = self.findChild(QGroupBox, 'ControlGroup')
        assert self.controls

        self.ap = self.findChild(QGroupBox, 'AutopilotGroup')
        assert self.ap
        self.ap_dict = dict()
        self.setup_autopliot_group()
        

        self.timer = QTimer(self)


    def setup_autopliot_group(self):
        ap = self.ap
        
        
        for num in range(1,2+1):
            group = ap.findChild(QGroupBox, f'groupBox_ap{num}')

            decrement = group.findChild(QPushButton, f'decrement_{num}')
            decrement.clicked.connect(const_wrapper(self.decrement_ap, num))
            increment = group.findChild(QPushButton, f'increment_{num}')
            increment.clicked.connect(const_wrapper(self.increment_ap, num))
            enabled = group.findChild(QCheckBox, f'ap_checkBox_{num}')
            enabled.clicked.connect(const_wrapper(self.state_change, num))
            display = group.findChild(QLCDNumber, f'ap_display_{num}')

            self.ap_dict[num] = {
                    'value': 0,
                    'display': display,
                    'enabled': enabled
                }

    def decrement_ap(self, group_num):
        #print(f'decrement {group_num}')
        value = self.ap_dict[group_num]['value'] - 1
        self.ap_dict[group_num]['value'] = value        
        self.ap_dict[group_num]['display'].display(value)

    def increment_ap(self, group_num):
        #print(f'increment {group_num}')
        value = self.ap_dict[group_num]['value'] + 1
        self.ap_dict[group_num]['value'] = value        
        self.ap_dict[group_num]['display'].display(value)

    def state_change(self, group_num):
        state = self.ap_dict[group_num]['enabled'].isChecked()
        print(f'istate change {group_num}: {state}')
        

        






if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = AvionicsWindow()    
    window.show()
    sys.exit(app.exec_()) 
