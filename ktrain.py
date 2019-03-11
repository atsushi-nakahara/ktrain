#!/usr/bin/python
from Adafruit_PWM_Servo_Driver import PWM
import os
import math
import random
import RPi.GPIO as GPIO
import time
from gps import *
import threading
import logging
import Queue

_path = '/home/pi/ktrain/'
_debug = False
_counter = 0
_p_idx = -1
_log = open('{0}gps_nagara.log'.format(_path), 'r')

_unit_num = 16 #TODO
_unit_state = [False] * _unit_num
_prev_unit_state = [True] * _unit_num
_anime = 0
_anime_type = -1
_switch = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#_pwm = PWM(0x40, False)
_pwm = [PWM(0x40, False), PWM(0x41, False)]
_pwm[0].setPWMFreq(60)  # Set frequency to 60 Hzw
_pwm[1].setPWMFreq(60)

logging.basicConfig(
    level=logging.DEBUG,
    filename='{0}ktrain.log'.format(_path),
    format="%(asctime)s %(levelname)s %(message)s")

logging.info('start ktrain...')
os.system('omxplayer {0}sounds/b{1}.wav &'.format(_path, 4))

_queue = Queue.Queue(1) #TODO
_places = open('{0}places.csv'.format(_path), 'r')

#--------------------------------------------------------------------------------------------
class GpsPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #self.session = gps(mode=WATCH_ENABLE)
        self.session = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
        self.current_value = None

    '''
    def get_current_value(self):
        return self.current_value
    '''

    def run(self):
        global _queue        
        try:
            while True:
                #self.current_value = self.session.next()
                _queue.put(self.session.next())
                time.sleep(0.5) # tune this, you might not get values that quickly
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

    global _path
    global _places
    #print '{0} {1}'.format(lon, lat)

    #places = open('{0}places.csv'.format(_path), 'r')
    _places.seek(0)
    for place in _places:
        #print place
        pos = place.split(',')
        #print pos
        d = getDistance(float(lon), float(lat), float(pos[2]), float(pos[3]));
        #print d
        if d < 800:#org 200
            #print pos[1]
            return int(pos[0])
    return

#--------------------------------------------------------------------------------------------
def isSwitchPressed():

    global _switch
    input_state = not(GPIO.input(18))

    if _switch == False and input_state == True:
        _switch = input_state
        logging.info('switch pressed...')
        return True
    else:
        _switch = input_state
        return False
 

#--------------------------------------------------------------------------------------------
def animate():
    global _unit_state
    global _prev_unit_state
    global _anime
    global _anime_type
    global _unit_num
    i = 0

    speed = 8
    if _anime_type == 0: #wave
        if _anime % speed == 0:
            i = (_anime / speed) % _unit_num
            if i==0 and _anime > speed * _unit_num * 2:
                resetState()
            else:
                _unit_state[i] = True
                i -= 3
                if i < 0: i += _unit_num
                _unit_state[i] = False

    elif _anime_type == 1: #rwave
        if _anime % speed == 0:
            i = (_anime / speed) % _unit_num
            if i==0 and _anime > speed * _unit_num * 2:
                resetState()
            else:
                i = _unit_num-1-i
                _unit_state[i] = True
                i += 3
                if i > _unit_num-1: i -= _unit_num
                _unit_state[i] = False

    elif _anime_type == 2: #hit
        speed = 40
        if _anime % speed == 0:
            if _anime > speed * 4:
                resetState()
            else:
                for idx in range(0, len(_unit_state)):
                    if (idx+(_anime / speed)) %2 == 0:
                        _unit_state[idx] = True
                    else:
                        _unit_state[idx] = False
                    
    elif _anime_type == 3: #cross
        speed = 10
        if _anime % speed == 0:
            i = (_anime / speed) % (_unit_num/2)
            if i==0 and _anime > speed * _unit_num:
                resetState()
            else:
                _unit_state[i] = True
                _unit_state[_unit_num-1-i] = True
                i -= 2
                if i < 0: i += _unit_num/2
                _unit_state[i] = False
                _unit_state[_unit_num-1-i] = False

    elif _anime_type == 4: #rcross
        speed = 10
        if _anime % speed == 0:
            i = (_anime / speed) % (_unit_num/2)
            if i==0 and _anime > speed * _unit_num:
                resetState()
            else:
                i = _unit_num/2-1-i
                _unit_state[i] = True
                _unit_state[_unit_num-1-i] = True
                i += 2
                if i > _unit_num/2-1: i -= _unit_num/2
                _unit_state[i] = False
                _unit_state[_unit_num-1-i] = False

    elif _anime_type == 5: #random
        speed = 30
        if _anime % speed == 0:
            if _anime > speed * 10:
                resetState()
            else:
                for idx in range(0, len(_unit_state)):
                    if random.randint(0, 1)==0:
                        _unit_state[idx] = True
                    else:
                        _unit_state[idx] = False


    '''
    for st in _unit_state:
        if st == True: print '*',
        if st == False: print '_',
    print ''
    '''

    for idx in range(0, len(_unit_state)):
        if  not(_unit_state[idx] == _prev_unit_state[idx]):
            moveServo(0, idx)
            moveServo(1, idx)
        _prev_unit_state[idx] = _unit_state[idx]
        
    _anime += 1
    return

#--------------------------------------------------------------------------------------------
def moveServo(group, idx):
    global _unit_state
    global _pwm
    #print 'servo {0} to {1}'.format(idx, _unit_state[idx])
    
    servoMin = 150  # Min pulse length out of 4096
    servoMax = 400  # Max pulse length out of 4096
    if _unit_state[idx]:
        _pwm[group].setPWM(idx, 0, servoMax)
    else:
        _pwm[group].setPWM(idx, 0, servoMin)

#--------------------------------------------------------------------------------------------
def checkPlace():

    global _debug
    global _log
    global _session
    global _gpsp
    global _queue

    if _debug:
        line = _log.readline()
        if line:
            vals = line.split(',')
            return findPlace(vals[1], vals[0])
        else :
            return -1
    else:
        #report = _gpsp.get_current_value();
        report = None
        if _queue.empty()==False: report = _queue.get(False); #print report;
        #report = _session.next()
        if report and report.keys()[0] == 'epx' :
            print("%f, %f, %s" % (report['lon'], report['lat'], report['time']))
            return findPlace(report['lon'], report['lat'])
        else:
            print('no queue...')
            return -1

#--------------------------------------------------------------------------------------------
def resetState():
    global _anime
    global _anime_type
    global _unit_state 
    global _prev_unit_state 
    global _unit_num

    _unit_state = [False] * _unit_num
    _prev_unit_state = [True] * _unit_num
    _anime = 0
    _anime_type = -1
    print 'resetState'
    return

#--------------------------------------------------------------------------------------------
def changeState():
    
    global _anime_type

    resetState()
    _anime_type = random.randint(0, 5) #todo
    #_anime_type = 4
    print 'changeState {0}'.format(_anime_type) 

    return

#--------------------------------------------------------------------------------------------
def playSound(p_idx):
    global _path
    #os.system('omxplayer {0}test.mp3 &'.format(_path, p_idx))
    if p_idx > 0:
        os.system('omxplayer {0}sounds/{1}.wav &'.format(_path, p_idx))
    else:
        rand = random.randint(1, 6)
        os.system('omxplayer {0}sounds/b{1}.wav &'.format(_path, rand))
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
        if _counter % (20*60*2) == 0:
            changeState()
            playSound(-1)
        
        if _counter % 5 == 0: #TODO
            #print 'check position'
            p_idx = checkPlace()
            if p_idx > 0 and _p_idx != p_idx:
                _p_idx = p_idx
                print 'place changed {0}'.format(_p_idx)
                logging.info('place changed {0}'.format(_p_idx))
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


    

