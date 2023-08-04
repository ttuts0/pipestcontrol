from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import random
import time
import classify2
import publisher
import subscriber

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
        print('pest detected')
    else:
        green.on()
        print('friend detected')

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
    file.write(f'{timestamp}')
    file.close()

def get_motion_data_from_file(file_path):
    motion_data = {}
    with open(file_path, 'r') as file:
        for line in file:
            if 'detected at :' in line:
                parts = line.strip().split(' ')
                if len(parts) >= 6:
                    timestamp = parts[-2] + ' ' + parts[-1]
                    hour = timestamp.split(':')[0]
                    motion_data[hour] = motion_data.get(hour, 0) + 1
    return motion_data

def detected_motion(is_pest):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    if is_pest:
        client.publish('pestbusterai/motion', payload='pest,'+f'{timestamp}', qos=0, retain=False)

    else:
        client.publish('pestbusterai/motion', payload='friend,'+f'{timestamp}', qos=0, retain=False)

pir.when_motion = motion_detected 
pir.when_no_motion = no_motion

pause()                                                                                                          