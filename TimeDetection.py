from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import random
import time
import classify

pir = MotionSensor(4)#gpio4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'


def motion_detected():#turn on red
    is_pest = classify.search_for_pest()
    print(is_pest)
    if is_pest:
        red.on()  
        print("pest detected")
    else:
        green.on()
        print("friend detected")
    motion_log(is_pest)
    white.off()
    

# def pest_or_friend():
#     return random.choice([True, False])
 
def no_motion():#TURN OFF
    red.off()
    green.off()
    white.on()
    
def motion_log(is_pest: bool):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    file=open(log, 'a')
    if is_pest:
        file.write('pest ')
    else:
        file.write('friend ')        
    file.write(f'detected at : {timestamp}\n')
    file.close()


pir.when_motion = motion_detected 
pir.when_no_motion = no_motion

pause()