from gpiozero import MotionSensor, LED
from signal import pause

pir = MotionSensor(4)#gpio4
red = LED(16)#red
white = LED(17)  #white

def turn_on_red():#turn on red
    red.on()
    white.off()

def turn_off_red():#TURN OFF
    red.off()
    white.on()

pir.when_motion = turn_on_red
pir.when_no_motion = turn_off_red

pause()