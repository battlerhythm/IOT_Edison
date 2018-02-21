#! usr/bin/env python
import mraa
import pyupm_i2clcd as lcd
from math import log

switch_pin_number = 8
switch = mraa.Gpio(switch_pin_number)
switch.dir(mraa.DIR_IN)

def temp():
    B = 4275
    R0 = 100000
    try:
        tempSensor = mraa.Aio(1)
        a = tempSensor.read()
        R = 1023.0 / a - 1.0
        R = R0 * R
        v = 1.0/(log(R/R0)/B+1/298.15)-273.15
        print (v), "is the current temperature"
        return v

    except KeyboardInterrupt:
        return None

while (1):
    # Initialize Jhd1313m1 at 0x3E (LCD_ADDRESS) and 0x62 (RGB_ADDRESS)
    myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)

    myLcd.setCursor(0,0)
    # RGB Blue
    #myLcd.setColor(53, 39, 249)

    # RGB Red
    myLcd.setColor(255, 0, 0)

    if(switch.read()):
        t = temp()
        myLcd.write('Temp')
        myLcd.setCursor(1,2)
        myLcd.write(str(t))
