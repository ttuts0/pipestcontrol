from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import random

pir = MotionSensor(4)#gpio4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'

def turn_on_red():#turn on red
    val=random.randint(0,10)
    print(val)
    if val>5:
        green.on()
    else:
        red.on()
    motion_log()
    white.off()

def turn_off_red():#TURN OFF
    red.off()
    green.off()
    white.on()
    
def motion_log():
    timestamp = datetime.now().strftime('%H:%M:%S')
    file=open(log, 'a')
    file.write(f'Motion detected at : {timestamp}\n')
    file.close()

pir.when_motion = turn_on_red 
pir.when_no_motion = turn_off_red

pause()