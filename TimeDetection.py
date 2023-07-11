from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import random

pir = MotionSensor(4)#gpio4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'
is_pest=True


def pest_or_friend():
    is_pest = random.choice(True, False)

def motion_detected():#turn on red
    if is_pest:
        red.on()
        print("pest detected")
    else:
        green.on()
        print("friend detected")
    motion_log(is_pest)
    white.off()

def no_motion():#TURN OFF
    red.off()
    green.off()
    white.on()
    
def motion_log(is_pest: bool):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    file=open(log, 'a')
    file.write(f'Motion detected at : {timestamp}\n')
    file.close()

pir.when_motion = motion_detected 
pir.when_no_motion = no_motion

pause()