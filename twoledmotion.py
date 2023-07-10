from gpiozero import MotionSensor, LED
from signal import pause

pir = MotionSensor(4)
led = LED(16)
ledtwo = LED(17)

pir.when_motion = led.on
pir.when_no_motion = led.off
 
pir.when_motion = ledtwo.off
pir.when_no_motion = ledtwo.on

pause()