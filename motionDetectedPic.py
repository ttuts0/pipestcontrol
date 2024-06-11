import time
from gpiozero import MotionSensor
from picamera2 import Picamera2
import cv2
from Object_Detection_Files import object_ident

pir = MotionSensor(4)

picam2 = Picamera2()

pic_num = 0
while True:
    pir.wait_for_motion()
    print("Motion detected!")

    img_name = f"test{pic_num}.jpg"
    picam2.start()
    picam2.capture_file(img_name)
    print(f"Image captured: {img_name}")

    img = cv2.imread(img_name)
    img, objectInfo = object_ident.getObjects(img, 0.45, 0.2, objects = ["cat","dog"])     
    if objectInfo:
        print("Detected objects:")
        for box, className in objectInfo:
            print(f"- {className}: {box}")
    else: 
        print("No objects detected.")
    
    pic_num += 1

