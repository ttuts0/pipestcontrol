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
client.publish('pestbusterai/general', payload='connected', qos=0, retain=False)

#when motion is detected, classifies as pest or friend and send image
def motion_detected():
    is_pest, image_location = classify2.search_for_pest()
    publisher.send_pic(image_location, client, is_pest)
    print(image_location)
   
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

# Function to handle no motion event, turns white light on 
def no_motion():
    red.off()
    green.off()
    white.on()

# Function to log motion events with timestamps   
def motion_log(is_pest: bool):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    file=open(log, 'a')
    if is_pest:
        file.write('pest ')
    else:
        file.write('friend ')        
    file.write(f'{timestamp}')
    file.close()

# Function to publish MQTT messages about detected motion to topic motion 
def detected_motion(is_pest):
    timestamp = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    if is_pest:
        client.publish('pestbusterai/motion', payload='pest ,'+f'{timestamp}', qos=0, retain=False)

    else:
        client.publish('pestbusterai/motion', payload='friend ,'+f'{timestamp}', qos=0, retain=False)

pir.when_motion = motion_detected 
pir.when_no_motion = no_motion

pause()
 