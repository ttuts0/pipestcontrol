import os
import time
from gpiozero import MotionSensor, LED
from datetime import datetime
from signal import pause
import cv2
from picamera2 import Picamera2
from Object_Detection_Files import object_ident
import publisher

# Initialize the PIR sensor and LEDs
pir = MotionSensor(4)  # GPIO4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'

# Create folder for detected pictures if it doesn't exist
if not os.path.exists("detected_pics"):
    os.makedirs("detected_pics")

picam2 = Picamera2()
pic_num = 0

# Create client function
client = publisher.create_client()
client.publish('pestbusterai/general', payload='connected', qos=0, retain=False)

# Function to handle motion detected event
def motion_detected():
    global pic_num

    # Capture the image
    img_name = f"detected_pics/test{pic_num}.jpg"
    picam2.start()
    picam2.capture_file(img_name)
    picam2.stop()
    print(f"Image captured: {img_name}")

    # Load the image and perform object detection
    img = cv2.imread(img_name)
    img, objectInfo = object_ident.getObjects(img, 0.45, 0.2, objects=["cat", "dog", "person", "cow", "bird", "bear"])

    is_pest = False
    detected_object = None

    # Classify detected objects as friend or pest
    if objectInfo:
        for box, className in objectInfo:
            detected_object = className
            if className in ["cat", "dog", "person"]:
                is_pest = False
                print(f"Friend detected: {className}")
                green.on()
                break
            elif className in ["cow", "bear", "bird"]:
                is_pest = True
                print(f"Pest detected: {className}")
                red.on()
                break

    # Log the information
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    with open(log, 'a') as log_file:
        if objectInfo:
            log_file.write(f"{detected_object}, {img_name}, {current_time}\n")
            print(f"{detected_object}, {img_name}, {current_time}")
        else:
            log_file.write(f"No objects detected, {img_name}, {current_time}\n")
            print(f"No objects detected, {img_name}, {current_time}")

    if detected_object:
        detected_motion(is_pest, detected_object, current_time)
        
    pic_num += 1
    white.off()
    return is_pest

# Function to handle no motion event, turns white light on
def no_motion():
    red.off()
    green.off()
    white.on()

# Function to publish MQTT messages about detected motion to topic motion
def detected_motion(is_pest, detected_object, timestamp):
    classification = "pest" if is_pest else "friend"
    payload = f"{detected_object}, {classification}, {timestamp}"
    client.publish('pestbusterai/motion', payload=payload, qos=0, retain=False)

pir.when_motion = motion_detected
pir.when_no_motion = no_motion

pause()

