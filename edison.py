# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu


import mraa
import pyupm_i2clcd as lcd
import pexpect
import time

SWITCH_PIN_NUMBER = 8
BUZZER_PIN_NUMBER = 6
TEMPERATURE_SENSOR_PIN_NUMBER = 1
WICED_ADDRESS = "00:10:18:01:1E:4B"


# Configuring the switch and buzzer as GPIO interfaces
switch = mraa.Gpio(SWITCH_PIN_NUMBER)
buzzer = mraa.Gpio(BUZZER_PIN_NUMBER)
temperature_sensor = mraa.Aio(TEMPERATURE_SENSOR_PIN_NUMBER)
lcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
wiced_con = None

# Configuring the switch and buzzer as input & output respectively
switch.dir(mraa.DIR_IN)
buzzer.dir(mraa.DIR_OUT)


def _enable_ble_sensors(con):    
    cmd = 'char-write-req 0x2b 0x01'
    con.sendline(cmd) 

def _ble_bytes_to_tmp006(v):
    objT = (v[1]<<8)+v[0]
    ambT = (v[3]<<8)+v[2]
    targetT = calcTmpTarget(objT, ambT)

def ble_initialize():
    global wiced_con
    con = pexpect.spawn('gatttool -b ' + WICED_ADDRESS + ' --interactive')
    con.expect('\[LE\]>', timeout=600)
    print "Preparing to connect. You might need to press the side button..."
    con.sendline('connect')
    # test for success of connect
    con.expect('Connection successful.*\[LE\]>')
    print "Connected."
    _enable_ble_sensors(con)
    wiced_con = con


def ble_get_measurements():
    con = wiced_con
    values = {}
    prefix = "Notification handle = 0x002a value: 34 "
    con.expect(prefix+'.. .. .. .. .. ..')
    print(con.after[len(prefix):])
    temp_bytes = con.after[len(prefix):][-5:]
    temp_bytes = temp_bytes.split(' ')
    temp_bytes = list(reversed(temp_bytes))
    temp_bytes = ''.join(temp_bytes)
    values["tmp006"] = int(temp_bytes,16)/10.0
    return values
    # TODO: read other values from sensor too
    # prefix = "Notification handle = 0x002a value: 0b "
    # con.expect(prefix+'.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..')
    # print(con.after[len(prefix):])

def ble_get_tmp006():
    if wiced_con is None:
        raise ValueError("Initialize the WICED device first.")
    print(_char_read_hnd(wiced_con,0x2a))
    try:
        pnum = wiced_con.expect('Notification handle = .*? \r', timeout=4)
    except pexpect.TIMEOUT:
        print "TIMEOUT exception!"
        return None
    if pnum==0:
        hxstr = wiced_con.after.split()[3:]
        handle = long(float.fromhex(hxstr[0]))            
    else:
        print "TIMEOUT!!"
    return _ble_bytes_to_tmp006([long(float.fromhex(n)) for n in hxstr[2:]])

def get_switch():
    return switch.read()

def set_buzz(buzz):
    buzzer.write(1 if buzz else 0)

def set_lcd(string):
    lcd.setCursor(0,0)
    lcd.write(string)

def get_temperature():
    B = 4275
    R0 = 100000
    a = temperature_sensor.read()
    R = 1023.0 / a - 1.0
    R = R0 * R
    v = 1.0/(log(R/R0)/B+1/298.15)-273.15
    return v

if __name__ == "__main__":
    ble_initialize()
    while True:
        values = ble_get_measurements()
        set_lcd(str(values["tmp006"]))
        time.sleep(1)