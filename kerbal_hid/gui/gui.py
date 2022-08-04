#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QLCDNumber, QPushButton, QCheckBox, QSpinBox, QComboBox, QSlider

from PyQt5 import QtOpenGL
from PyQt5.QtOpenGL import *

import krpc

##from pid import PID, FilteredPID


import scipy
import numpy as np
from scipy.signal import butter, lfilter
from math import floor, ceil
from time import sleep




class HIDWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('hid.ui', self)

        self.opengl_test()


    def opengl_test(self):
        gl = self.openGLWidget
        gl.initializeGL()

        frame = gl.grabFramebuffer()
        frame.load('/home/wm/python/kerbal_hid/gui/test.jpg')
        gl.update()
        gl.paintGL()
   
            

            
            

        

        






if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = HIDWindow()
    gl = window.openGLWidget
    window.show()
    sys.exit(app.exec_())
