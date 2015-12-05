import math
import random

_counter = 0;
_p_idx = -1
_log = open('./gps.log', 'r')

_unit_state = [False] * 16
_anime = 0
_anime_type = 0

#--------------------------------------------------------------------------------------------
def getDistance(lon_a, lat_a, lon_b, lat_b):

    #print str(lon_a) +' '+ str(lat_a) +' '+ str(lon_b) +' '+  str(lat_b)

    if lon_a == lon_b and lat_a == lat_b:
        return 0

    from_x = lon_a * math.pi / 180;
    from_y = lat_a * math.pi / 180;
    #to_x = lon_b * math.pi / 180;
    #to_y = lat_b * math.pi / 180;
    to_y = lon_b * math.pi / 180;
    to_x = lat_b * math.pi / 180;

    #print str(from_x) +' '+ str(from_y) +' '+ str(to_x) +' '+  str(to_y)

    deg = math.sin(from_y) * math.sin(to_y) + math.cos(from_y) * math.cos(to_y) * math.cos(to_x - from_x);
    dist = 6378140 * (math.atan( - deg / math.sqrt(-deg * deg + 1)) + math.pi / 2);
    return dist;#in m

#--------------------------------------------------------------------------------------------
def findPlace(lon, lat):
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
    return False

#--------------------------------------------------------------------------------------------
def animate():
    global _unit_state
    global _anime
    global _anime_type

    if _anime_type == 0: #wave
        speed = 400 #todo
        if _anime % speed == 0:
            i = (_anime / speed) % 16
            _unit_state[i] = True
            i -= 3
            if i < 0: i+16
            _unit_state[i] = False
    elif _anime_type == 1: #rwave
        speed = 400 #todo
        if _anime % speed == 0:
            i = (_anime / speed) % 16
            i = 15-i
            _unit_state[i] = True
            i -= 3
            if i < 0: i+16
            _unit_state[i] = False


    #print _unit_state
    for st in _unit_state:
        if st == True: print '*',
        if st == False: print '_',
    print ''

    _anime += 1
    return

#--------------------------------------------------------------------------------------------
def checkPlace():
    global _log
    line = _log.readline()
    if line:
        vals = line.split(',')
        return findPlace(vals[0], vals[1])
    else :
        return -1


#--------------------------------------------------------------------------------------------
def changeState():
    global _anime
    global _anime_type

    _anime = 0
    _anime_type = random.randint(0, 1) #todo
    print 'changeState'
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
        print 'switch pressed'
        changeState()
        playSound(-1)
    else:
        if _counter % 500 == 0: #TODO
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

init()
while True:
    mainloop()



    

