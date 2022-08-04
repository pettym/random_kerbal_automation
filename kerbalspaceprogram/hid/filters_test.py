#!/usr/bin/python3

import scipy
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import butter, lfilter


def filter_test(data, cutoff, sps, order=3):
    nyq = sps/2
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)


hertz = 60
t = np.linspace(0,100,num=100*hertz)
data = np.sin(t)
data += np.random.randn(len(data))*0.2


filtered = filter_test(data, 2.0, hertz)





fig, ax = plt.subplots()
ax.plot(data)
ax.plot(filtered+2)
fig.show()
