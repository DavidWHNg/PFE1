
from psychopy import core, event, gui, visual, parallel, prefs
import time, serial
RENS_pulse_int = 0.1 # interval length for RENS on/off signals (e.g. 0.1 = 0.2s per pulse) NOTE; likely only 1 decimal place precision

s = serial.Serial('COM3', baudrate=128000, timeout=0.01)
s.write(b'WRITE 0\n')

win = visual.Window(
    size=(1920, 1080), fullscr= True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")
 
visual.TextStim(win,
                text="Please let the experimenter know when you begin to feel the RENS",
                color="white",
                height=25,
                pos=(0, 0),
                wrapWidth=600
                ).draw()

win.flip()
    

calib_finish = False
countdown_timer = core.CountdownTimer(300)
RENS_timer = countdown_timer.getTime() + RENS_pulse_int

while calib_finish == False:
    keys_pressed = event.getKeys()  
    if 'space' in keys_pressed:  # Check for "spacebar" to end calibration
        calib_finish = True
    if countdown_timer.getTime() < RENS_timer - RENS_pulse_int:
        s.write(b'WRITE 128\n')
    if countdown_timer.getTime() < RENS_timer - RENS_pulse_int*2:
        s.write(b'WRITE 0\n')
        RENS_timer = countdown_timer.getTime() 

s.write(b'WRITE 0\n')
core.quit()