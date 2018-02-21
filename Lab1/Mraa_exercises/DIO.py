import mraa
import time
switch_pin_number=8
buzz_pin_number=6
switch = mraa.Gpio(switch_pin_number)
buzz = mraa.Gpio(buzz_pin_number)
switch.dir(mraa.DIR_IN)
buzz.dir(mraa.DIR_OUT)
print "Press Ctrl+C to escape.."
try:
        buzz.write(1)   # switch on the buzzer
        time.sleep(1) # puts system to sleep for 0.2sec before switching
        buzz.write(0)   # switch off buzzer
except KeyboardInterrupt:
    exit
