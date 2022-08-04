#!/usr/bin/python3

from math import pi, tau, sqrt

class Orbit:

    def __init__(self, soi):
        pass

        





G = 6.674*(10**-1)

#u = 6.5138398*(10**10) #Mun
u = 3.5316000*(10**12) #Kerbin
u = 1.9620000*(10**12) # Laythe


if __name__ == '__main__':
##    sma = 3463334
##    ecc = 0.0
##    pe = ap = 2863334
##    radius = 600000

    day = 21549.325
    t = (52980.879)/2
    
    sma = ((u*(t)**2)/(4*pi**2))**(1/3)
