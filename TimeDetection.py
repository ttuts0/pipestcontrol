from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import random
import time
import classify2
import publisher

pir = MotionSensor(4)#gpio4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'              

#create client function
client = publisher.create_client()
#client.publish('pestbusterai/motion', payload='hello', qos=0, retain=False)
client.publish('pestbusterai/general', payload='connected', qos=0, retain=False)

def motion_detected():#turn on red
    is_pest = classify2.search_for_pest()
   
    if is_pest:
        red.on()  
        print("pest detected")
    else:
        green.on()
        print("friend detected")
    motion_log(is_pest)
    detected_motion(is_pest)
    
    white.off()
    return is_pest

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
    
def detected_motion(is_pest):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    if is_pest:
        client.publish('pestbusterai/motion', payload='pest '+f'detected at : {timestamp}\n', qos=0, retain=False)
    else:
        client.publish('pestbusterai/motion', payload='friend '+f'detected at : {timestamp}\n', qos=0, retain=False)
pir.when_motion = motion_detected 
pir.when_no_motion = no_motion

pause()