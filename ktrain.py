#!/usr/bin/python
from Adafruit_PWM_Servo_Driver import PWM
import math
import random
import RPi.GPIO as GPIO
import time
from gps import *
import threading

_debug = True
_counter = 0
_p_idx = -1
_log = open('./gps.log', 'r')

_unit_state = [False] * 16
_prev_unit_state = [True] * 16
_anime = 0
_anime_type = -1

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

_pwm = PWM(0x40)

#--------------------------------------------------------------------------------------------
class GpsPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.current_value = None

    def get_current_value(self):
        return self.current_value

    def run(self):
        try:
            while True:
                self.current_value = self.session.next()
                time.sleep(5) # tune this, you might not get values that quickly
        except StopIteration:
            pass

#--------------------------------------------------------------------------------------------
def getDistance(lon_a, lat_a, lon_b, lat_b):

    #print str(lon_a) +' '+ str(lat_a) +' '+ str(lon_b) +' '+  str(lat_b)

    if lon_a == lon_b and lat_a == lat_b:
        return 0

    from_x = lon_a * math.pi / 180;
    from_y = lat_a * math.pi / 180;
    to_x = lon_b * math.pi / 180;
    to_y = lat_b * math.pi / 180;

    deg = math.sin(from_y) * math.sin(to_y) + math.cos(from_y) * math.cos(to_y) * math.cos(to_x - from_x);
    dist = 6378140 * (math.atan( - deg / math.sqrt(-deg * deg + 1)) + math.pi / 2);
    return dist;#in m

#--------------------------------------------------------------------------------------------
def findPlace(lon, lat):

    #print '{0} {1}'.format(lon, lat)

    places = open('./places.csv', 'r')
    for place in places:
        #print place
        pos = place.split(',')
        #print pos
        d = getDistance(float(lon), float(lat), float(pos[2]), float(pos[3]));
        #print d
        if d < 200:
            #print pos[1]
            return int(pos[0])
    return

#--------------------------------------------------------------------------------------------
def isSwitchPressed():

    input_state = GPIO.input(18)
    return not(input_state)


#--------------------------------------------------------------------------------------------
def animate():
    global _unit_state
    global _prev_unit_state
    global _anime
    global _anime_type
    i = 0

    speed = 3
    if _anime_type == 0: #wave
        if _anime % speed == 0:
            i = (_anime / speed) % 16
            if i==0 and _anime > speed * 16 * 4:
                resetState()
            else:
                _unit_state[i] = True
                i -= 3
                if i < 0: i += 16
                _unit_state[i] = False

    elif _anime_type == 1: #rwave
        if _anime % speed == 0:
            i = (_anime / speed) % 16
            if i==0 and _anime > speed * 16 * 4:
                resetState()
            else:
                i = 15-i
                _unit_state[i] = True
                i += 3
                if i > 15: i -= 16
                _unit_state[i] = False

    elif _anime_type == 2: #hit
        speed = 20
        if _anime % speed == 0:
            if _anime > speed * 6:
                resetState()
            else:
                for idx in range(0, len(_unit_state)):
                    if (idx+(_anime / speed)) %2 == 0:
                        _unit_state[idx] = True
                    else:
                        _unit_state[idx] = False
                    
    elif _anime_type == 3: #cross
        if _anime % speed == 0:
            i = (_anime / speed) % 8
            if i==0 and _anime > speed * 8 * 4:
                resetState()
            else:
                _unit_state[i] = True
                _unit_state[15-i] = True
                i -= 2
                if i < 0: i += 8
                _unit_state[i] = False
                _unit_state[15-i] = False

    elif _anime_type == 4: #rcross
        if _anime % speed == 0:
            i = (_anime / speed) % 8
            if i==0 and _anime > speed * 8 * 4:
                resetState()
            else:
                i = 7-i
                _unit_state[i] = True
                _unit_state[15-i] = True
                i += 2
                if i > 7: i -= 8
                _unit_state[i] = False
                _unit_state[15-i] = False

    elif _anime_type == 5: #random
        speed = 10
        if _anime % speed == 0:
            if _anime > speed * 10:
                resetState()
            else:
                for idx in range(0, len(_unit_state)):
                    if random.randint(0, 1)==0:
                        _unit_state[idx] = True
                    else:
                        _unit_state[idx] = False

    #print _unit_state
    for st in _unit_state:
        if st == True: print '*',
        if st == False: print '_',
    print ''

    for idx in range(0, len(_unit_state)):
        if  not(_unit_state[idx] == _prev_unit_state[idx]):
            moveServo(idx)
        _prev_unit_state[idx] = _unit_state[idx]
        
    _anime += 1
    return

#--------------------------------------------------------------------------------------------
def moveServo(idx):
    global _unit_state
    global _pwm
    #print 'servo {0} to {1}'.format(idx, _unit_state[idx])
    
    servoMin = 150  # Min pulse length out of 4096
    servoMax = 600  # Max pulse length out of 4096
    if _unit_state[idx]:
        _pwm.setPWM(idx, 0, servoMax)
    else:
        _pwm.setPWM(idx, 0, servoMin)

#--------------------------------------------------------------------------------------------
def checkPlace():

    global _debug
    global _log
    global _session
    global _gpsp

    if _debug:
        line = _log.readline()
        if line:
            vals = line.split(',')
            return findPlace(vals[1], vals[0])
        else :
            return -1
    else:
        report = _gpsp.get_current_value();
        #report = _session.next()
        if report and report.keys()[0] == 'epx' :
            return findPlace(report['lon'], report['lat'])
        else:
            return -1

#--------------------------------------------------------------------------------------------
def resetState():
    global _anime
    global _anime_type
    global _unit_state 

    _unit_state = [False] * 16
    _anime = 0
    _anime_type = -1
    print 'resetState'
    return

#--------------------------------------------------------------------------------------------
def changeState():
    global _anime
    global _anime_type

    _anime = 0
    _anime_type = random.randint(0, 5) #todo
    print 'changeState {0}'.format(_anime_type) 
    return

#--------------------------------------------------------------------------------------------
def playSound(_p_idx):
    return

#--------------------------------------------------------------------------------------------
def mainloop():
    #print 'loop'
    global _counter
    global _p_idx

    _counter += 1
    #print _counter

    switch = isSwitchPressed()
    if switch:
        #print 'switch pressed'
        changeState()
        playSound(-1)
    else:
        if _counter % 5 == 0: #TODO
            #print 'check position'
            p_idx = checkPlace()
            if p_idx > 0 and _p_idx != p_idx:
                _p_idx = p_idx
                print 'place changed {0}'.format(_p_idx)
                changeState()
                playSound(_p_idx)

    animate()
    return

#--------------------------------------------------------------------------------------------
def init():
    return

#--------------------------------------------------------------------------------------------
# entry point

_gpsp = GpsPoller()
_gpsp.daemon = True
_gpsp.start()
init()
while True:
    mainloop()
    time.sleep(1.0/20.0) #20fps

#--------------------------------------------------------------------------------------------


    

