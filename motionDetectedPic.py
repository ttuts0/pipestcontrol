import os
import requests
from datetime import datetime
from gpiozero import MotionSensor, LED
from picamera2 import Picamera2
from Object_Detection_Files import object_ident
import publisher
import cv2
from signal import pause
import time

# Initialize the PIR sensor and LEDs
pir = MotionSensor(4)  # GPIO4
red = LED(16)
white = LED(17)
green = LED(27)
log = 'motionTimeLog.txt'
detected_pics_folder = 'detected_pics'
picam2 = Picamera2()

# Ensure the detected_pics folder exists
if not os.path.exists(detected_pics_folder):
    os.makedirs(detected_pics_folder)

# Determine the next available picture number
pic_num = 0
existing_pics = [int(filename.split('.')[0][4:]) for filename in os.listdir(detected_pics_folder) if filename.startswith('test')]
if existing_pics:
    pic_num = max(existing_pics) + 1

# Create MQTT client
client = publisher.create_client()

# Function to handle motion detected event
def motion_detected():
    global pic_num

    # Turn off white light and start the camera
    white.off()
    time.sleep(0.1)  # Short delay to ensure light is off

    try:
        img_name = f"{detected_pics_folder}/test{pic_num}.jpg"
        picam2.start()
        time.sleep(2)  # Delay to ensure the camera has started
        picam2.capture_file(img_name)
        picam2.stop()
        print(f"Image captured: {img_name}")

        # Load the image and perform object detection
        img = cv2.imread(img_name)
        img, objectInfo = object_ident.getObjects(img, 0.45, 0.2, objects=["cat", "dog", "person", "cow", "bird", "bear"])

        if not objectInfo:
            # No objects detected, delete the image and return
            os.remove(img_name)
            print("No objects detected.")
            return

        is_pest = False
        detected_object = None

        # Classify detected objects as friend or pest
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
            log_file.write(f"{detected_object}, {img_name}, {current_time}\n")
            print(f"{detected_object}, {img_name}, {current_time}")

        # Publish MQTT message
        classification = "pest" if is_pest else "friend"
        payload = f"{detected_object}, {classification}, {current_time}"
        client.publish("pestbusterai/motion", payload=payload, qos=0, retain=False)

        # Upload image to server
        upload_image(img_name, detected_object, classification, current_time)

        pic_num += 1
    except Exception as e:
        print(f"Error during motion detection: {e}")

    finally:
        # Ensure LEDs are turned off after processing
        white.off()
        red.off()
        green.off()

    return is_pest

# Function to upload image to server
def upload_image(image_path, detected_object, classification, timestamp):
    try:
        url = 'http://192.168.1.9:5000/upload_image'
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            data = {
                'critter_name': detected_object,
                'critter_type': classification,
                'detection_time': timestamp
            }

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            print(f"Image uploaded: {image_path}")
    except Exception as e:
        print(f"Error uploading image: {e}")

# Function to handle no motion event, turns white light on
def no_motion():
    red.off()
    green.off()
    white.on()

# Set up event handlers for PIR sensor
pir.when_motion = motion_detected
pir.when_no_motion = no_motion

# Start the GPIO event loop
pause()
