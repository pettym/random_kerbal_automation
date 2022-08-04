from collections import deque
from sys import stderr

import scipy
import numpy as np
from scipy.signal import butter, lfilter



class PID:
    def __init__(self, setpoint=0, gains=(1,1,1), limits=(-1,1), integral_limits=None, auto_reset_integral=True):
        self.setpoint = setpoint
        self.gains = gains
        self.limits = limits

        if integral_limits:
            self.integral_limits = integral_limits
        else:
            self.integral_limits = limits

        self.auto_reset_integral = auto_reset_integral

        self.integral = 0
        self.previous_deriv = 0
        self.output = 0
        self.callout = lambda v,t:None

    def __repr__(self):
        digits = 4
        output = str(round(self.output, digits)).ljust(digits+2, '0')
        integral = str(round(self.integral, digits)).ljust(digits+2, '0')
        deriv = str(round(self.previous_deriv, digits)).ljust(digits+2, '0')
        return f'{output=}\t{integral=}\t{deriv=}'

    def change_setpoint(self, new_setpoint):
##        if new_setpoint != self.setpoint:
##            print(f"Setpoint Changed: {new_setpoint}",file=stderr)
        self.setpoint = new_setpoint


    def step(self, error, dt):
        if dt == 0:
            print("warning Zero Delta",file=stderr)
            return self.output
            
        Kp, Ki, Kd = self.gains
        low, high = self.limits
        i_low, i_high = self.integral_limits

        # Kp
        proportional = error * Kp

        # Ki
        integral = self.integral + ((error*Ki)*dt)       
        integral = max(i_low, min(i_high, integral))

        if self.auto_reset_integral:
            if (self.integral >= i_high) and (integral < i_high):
                print('Integral auto reset', file=stderr)
                integral = 0

            
        self.integral = integral

        # Kd
        derivative = ((error*Kd)-self.previous_deriv) / dt
        self.previous_deriv = (error*Kd)

        output = (proportional + integral + derivative)
        output = max(low, min(high, output))
        self.output = output
        return output


    def __call__(self, value, delta):
        error = self.setpoint - value
        output = self.step(error, delta)
        self.callout(output, delta)
        return output
        




class FilteredPID(PID):
    def __init__(self, setpoint=0, gains=(1,1,1), limits=(-1,1), integral_limits=None):
        super().__init__(setpoint, gains, limits, integral_limits)

       
        self.make_filter()


    def make_filter(self, cutoff=4.0, order=3, hertz=50, filter_size=None):

        if not filter_size: filter_size = hertz

        self.hertz = hertz
        nyquist = hertz/2
        normal_cutoff = cutoff/nyquist
        self.iir_filter = butter(order, normal_cutoff, btype='low', analog=False)

        self.data = np.zeros(filter_size)
        


    def __call__(self, value, delta):
        error = self.setpoint - value
        output = self.step(error, delta)

        data = self.data
        data = np.roll(data, -1)
        data[-1] = output
        self.data = data

        b, a = self.iir_filter
        return lfilter(b, a, data)[-1]
    









        
