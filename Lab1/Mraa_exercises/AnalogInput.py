#!/usr/bin/env python
import mraa
from math import log
def temp():
    B=4275
    R0=100000
    try:
        tempSensor = mraa.Aio(1)
        a=tempSensor.read()
        R = 1023.0/a-1.0
        R=R0*R
        v=1.0/(log(R/R0)/B+1/298.15)-273.15
        print (v), "is the current temperature"
        return v
    except KeyboardInterrupt:
        return None
