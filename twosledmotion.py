from gpiozero import MotionSensor, LED
from signal import pause

pir = MotionSensor(4)
led1 = LED(16)
led2 = LED(17)  

def turn_on_leds():
    led1.on()
    led2.off()

def turn_off_leds():
    led1.off()
    led2.on()

pir.when_motion = turn_on_leds
pir.when_no_motion = turn_off_leds