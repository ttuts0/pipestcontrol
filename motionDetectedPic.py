import time
from gpiozero import MotionSensor
from picamera2 import Picamera2, Preview
from time import sleep
#from examples.lite.examples.object_detection.raspberry_pi import detect

pir = MotionSensor(4)
picam2 = Picamera2()
#picam2.rotation = 180

#camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
#picam2.configure(camera_config)
picam2.start_and_capture_file(name="first.jpg", delay=1, show_preview=True)

pic_num = 0
while True:
    pir.wait_for_motion()
    print("Motion detected!")

#     picam2.start_preview(Preview.QTGL)
    picam2.start_and_capture_file(name=f"test{pic_num}.jpg")
    
    pic_num+=1

    #picam2.capture_file("test1.jpg")


