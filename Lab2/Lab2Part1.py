# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu

#! usr/bin/env python
import mraa
import pyupm_i2clcd as lcd
import time
import json as simplejson

from math import log
from firebase import firebase

switch_pin_number = 8
switch = mraa.Gpio(switch_pin_number)
switch.dir(mraa.DIR_IN)

firebase = firebase.FirebaseApplication('https://iot-lab2-32ed3.firebaseio.com/',None)
result  = firebase.get('',None)

def temp():
    B = 4275
    R0 = 100000
    tempSensor = mraa.Aio(1)
    a = tempSensor.read()
    R = 1023.0 / a - 1.0
    R = R0 * R
    v = 1.0/(log(R/R0)/B+1/298.15)-273.15
    print(str(v) + " is the current temperature")
    return v

while (True):
    try:
        # Initialize Jhd1313m1 at 0x3E (LCD_ADDRESS) and 0x62 (RGB_ADDRESS)
        myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
        myLcd.setColor(255, 0, 0) # RGB Color
        if(switch.read()):
            t = temp()
            myLcd.setCursor(0,0)
            myLcd.write('Current Temp')
            myLcd.setCursor(1,2)
            myLcd.write(str(t))

            # Firebase update
            record = {'temperature':t}
            post = firebase.post('', record)

    except KeyboardInterrupt:
        break
